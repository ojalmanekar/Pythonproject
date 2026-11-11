# engine.py -- the ACCOUNT AND ENGINE piece: the money, the rules, and the day loop.
# Reference: <full name of the member responsible for this file>
#
# Three jobs, all about how a trade actually happens:
#   1. class Account: the AUTHORITY. Week 7's Register applied to the agent contract: one
#      object owns the balances (__cash and __shares, name-mangled), and the only way to
#      change them is execute(), which validates first and only then changes anything. It
#      answers every order with the contract's exact reply strings:
#          "ACCEPT"
#          "REJECT currency balance: <cash>"    (a buy the cash cannot pay for)
#          "REJECT stock owned: <shares>"       (a sale of more shares than we hold)
#          "REJECT bad order: <why>"            (not an order at all: our desk's own extra)
#   2. run_backtest(): THE LOOP (the brief's section 10), with no look-ahead. For each day
#      t except the last: hand the agent ONLY day t, take its order, fill it at the OPEN of
#      day t+1 through Account.execute, record equity at the close of day t+1.
#      BIG-O (rubric item 11): each of the n days is visited once with a fixed amount of
#      work, so a run is O(n).
#   3. BaseAgent, HoldAgent, BuyAndHoldAgent: two simple benchmark agents to compare ours
#      against (week 7's inheritance and abstraction, the MenuItem shape). agent.py must
#      stand alone, so our TradingAgent does not inherit from BaseAgent; it simply has the
#      same decide(), and run_backtest never asks which agent it holds: polymorphism.

# --- 1. imports --------------------------------------------------------------------------
import analytics

# --- 2. global constants ------------------------------------------------------------------
FEE = 0.001                          # 0.1% on every buy and every sell
ACTIONS = {"BUY", "SELL", "HOLD"}    # a set (week 4): we only ask "is it in there?"
DEFAULT_CASH = 10000.0
DEFAULT_SHARES = 0.0

# The three information regimes of the competition, as a dict: menu key -> (label, prices?,
# news?). A tuple per entry (week 4): fixed, read-only facts.
REGIMES = {"1": ("price + news", True, True),
           "2": ("price only", True, False),
           "3": ("news only", False, True)}


# --- 3. class declarations ----------------------------------------------------------------
# ---- 3a. the account: the only place money changes ----------------------------------------
class Account:
    def __init__(self, cash=DEFAULT_CASH, shares=DEFAULT_SHARES):
        # Coerce first, then validate (week 7's set_price shape): "5000" becomes 5000.0.
        cash = float(cash)
        shares = float(shares)
        if cash < 0:
            cash = 0.0                # a constructor protects the invariant: never < 0
        if shares < 0:
            shares = 0.0
        self.__cash = cash            # name-mangled: outsiders cannot touch the money
        self.__shares = shares

    # ---- the getters: reading is allowed, writing is not ----------------------------
    def get_cash(self):
        return self.__cash

    def get_shares(self):
        return self.__shares

    def get_equity(self, price):
        """What the account is worth at this price: cash + shares * price."""
        return self.__cash + self.__shares * price

    def __str__(self):
        return f"cash {self.__cash:.2f} | shares {self.__shares:g}"

    # ---- the one door the money moves through ---------------------------------------
    def execute(self, order, price):
        """Carry out one order at this price; return the reply string.

        order is a tuple (action, amount). An amount of -1 means "as many as the cash
        covers" for BUY and "everything I hold" for SELL."""
        # Validate the order itself before anything else (week 5: check, THEN mutate).
        action, amount, problem = check_order(order)
        if problem != "":
            return "REJECT bad order: " + problem
        if action == "HOLD":
            return "ACCEPT"
        if action == "BUY":
            return self.__buy(amount, price)
        return self.__sell(amount, price)

    def __buy(self, amount, price):
        """Private helper (two underscores): only execute() may call it."""
        if amount < 0:
            # As many WHOLE shares as the cash covers after the fee, rounded down:
            # 500 cash at 25 -> 500 / 25.025 = 19.98 -> 19 shares (20 would cost 500.50).
            amount = int(self.__cash / (price * (1 + FEE)))
            if amount * price * (1 + FEE) > self.__cash:   # guard against rounding up
                amount = amount - 1
        if amount <= 0:
            return "ACCEPT"                          # nothing to buy is not an error
        cost = amount * price * (1 + FEE)
        if cost > self.__cash:
            return "REJECT currency balance: " + str(round(self.__cash, 2))
        # Accepted: only now do the balances move.
        self.__cash = self.__cash - cost
        self.__shares = self.__shares + amount
        assert self.__cash >= 0, "a buy broke the cash invariant"   # week 5's assert
        return "ACCEPT"

    def __sell(self, amount, price):
        if amount < 0:
            amount = self.__shares                   # -1 means sell everything
        if amount <= 0:
            return "ACCEPT"
        if amount > self.__shares:
            return "REJECT stock owned: " + str(round(self.__shares, 2))
        self.__cash = self.__cash + amount * price * (1 - FEE)
        self.__shares = self.__shares - amount
        assert self.__shares >= 0, "a sale broke the shares invariant"
        return "ACCEPT"


# ---- 3b. the record of a run: one Trade per fill, one RunResult per run -------------------
class Trade:
    """One filled order: the day it filled, BUY or SELL, how many shares, at what price."""

    def __init__(self, day, action, quantity, price):
        self.day = day
        self.action = action
        self.quantity = quantity
        self.price = price

    def __str__(self):
        return f"day {self.day:>3}: {self.action:<4} {self.quantity:>6g} @ {self.price:>8.2f}"


class RunResult:
    """Everything one back-test produced: the equity curve, the trades and the numbers."""

    def __init__(self, agent_name, ticker, regime):
        self.agent_name = agent_name
        self.ticker = ticker
        self.regime = regime          # "price + news", "price only" or "news only"
        self.equity = []              # one value per day, day 0 included
        self.trades = []              # Trade objects, in order
        self.rejects = 0              # orders the account refused
        self.error = ""               # what stopped the run early, if anything
        self.most_in_shares = 0.0     # largest share of the money ever held in shares

    def label(self):
        """The name this run gets on the leaderboard."""
        return f"{self.agent_name} on {self.ticker} ({self.regime})"

    def numbers(self):
        return analytics.summary(self.equity)

    def __str__(self):
        n = self.numbers()
        return_pct, drawdown_pct = analytics.as_percent([n["total_return"], -n["max_drawdown"]])
        lines = [f"Ran {self.label()}:",
                 f"  {'final equity':<15} {n['final_equity']:>10.2f}",
                 f"  {'total return':<15} {return_pct:>9.1f}%",
                 f"  {'sharpe-like':<15} {n['sharpe_like']:>10.3f}",
                 f"  {'max drawdown':<15} {drawdown_pct:>9.1f}%",
                 f"  {'trades':<15} {len(self.trades):>10}",
                 f"  {'most in shares':<15} {self.most_in_shares * 100:>9.0f}%"]
        if self.rejects > 0:
            lines.append(f"  {'rejected':<15} {self.rejects:>10}")
        if self.error != "":
            lines.append(f"  STOPPED: {self.error}")
        return "\n".join(lines)


# ---- 3c. the benchmark agents: inheritance and abstraction --------------------------------
class BaseAgent:
    def __init__(self, name):
        self.name = name

    def decide(self, bar, headlines, cash, shares, last_response):
        raise NotImplementedError("every BaseAgent subclass must define decide()")

    def __str__(self):
        return f"{self.name} (benchmark)"


class HoldAgent(BaseAgent):
    """Never trades: the stub agent. Shows what doing nothing earns, exactly 0%."""

    def __init__(self):
        BaseAgent.__init__(self, "HoldAgent")

    def decide(self, bar, headlines, cash, shares, last_response):
        return ("HOLD", 0)


class BuyAndHoldAgent(BaseAgent):
    """Spends all its cash on day 0 and holds to the end: the market's own return."""

    def __init__(self):
        BaseAgent.__init__(self, "BuyAndHoldAgent")

    def decide(self, bar, headlines, cash, shares, last_response):
        if shares == 0 and cash > 0:
            return ("BUY", -1)
        return ("HOLD", 0)


# --- 4. function declarations ---------------------------------------------------------------
def check_order(order):
    """Return (action, amount, problem); problem is "" when the order is fine.

    A reply, not a raise (week 5's "raise, or reply?"): the caller reads the answer and
    carries on. try/except ValueError and TypeError catch amounts that are not numbers."""
    try:
        action, amount = order                       # tuple unpacking (week 4)
    except (TypeError, ValueError):
        return ("", 0, "an order is a pair (action, amount), got " + str(order)[:40])
    if action not in ACTIONS:
        return ("", 0, "the action must be BUY, SELL or HOLD, got " + str(action)[:20])
    try:
        amount = float(amount)                       # coerce first, as set_price does
    except (TypeError, ValueError, OverflowError):
        return ("", 0, "the amount must be a number, got " + str(amount)[:20])
    if amount != amount or abs(amount) == float("inf"):   # NaN is the one value != itself
        return ("", 0, "the amount must be a finite number")
    if amount == int(amount):
        amount = int(amount)                         # 5.0 shares is 5 shares
    return (action, amount, "")


def run_backtest(agent, market, cash, shares, use_prices, use_news, agent_name):
    """Run one agent over the whole market and return a RunResult.

    `agent` can be ANY object with a decide(bar, headlines, cash, shares, last_response)
    method: our TradingAgent or a benchmark. The loop never asks which one it holds --
    week 7's polymorphism (and week 5's duck typing).

    The account is a FRESH one, so a back-test never touches the desk's own session."""
    regime = "price + news"
    if use_prices and not use_news:
        regime = "price only"
    elif use_news and not use_prices:
        regime = "news only"
    result = RunResult(agent_name, market.ticker, regime)
    acct = Account(cash, shares)
    result.equity.append(acct.get_equity(market.close_on(0)))
    last_response = None

    for t in range(market.days() - 1):               # every day but the last
        # 1. What the agent may see. dict(...) and list(...) hand it COPIES (week 5's
        #    aliasing lesson): an agent that changed its bar could not damage our data.
        bar = None
        if use_prices:
            bar = dict(market.bars[t])
        headlines = None
        if use_news:
            headlines = list(market.headlines_on(t))

        # 2. Ask the agent. A crash inside it stops this run, not the desk.
        try:
            order = agent.decide(bar, headlines, acct.get_cash(), acct.get_shares(),
                                 last_response)
        except Exception as error:
            result.error = f"day {t}: the agent crashed: {type(error).__name__}: {error}"
            break

        # 3 and 4. Fill at TOMORROW's open, through the one door.
        fill_price = market.bars[t + 1]["open"]
        shares_before = acct.get_shares()
        last_response = acct.execute(order, fill_price)
        if last_response.startswith("REJECT bad order"):
            result.error = f"day {t}: {last_response}"
            break
        if last_response.startswith("REJECT"):
            result.rejects = result.rejects + 1
        moved = acct.get_shares() - shares_before
        if moved > 0:
            result.trades.append(Trade(t + 1, "BUY", moved, fill_price))
        elif moved < 0:
            result.trades.append(Trade(t + 1, "SELL", -moved, fill_price))

        # 5. The value of the account at tomorrow's close.
        close = market.close_on(t + 1)
        value = acct.get_equity(close)
        result.equity.append(value)
        if value > 0:
            result.most_in_shares = max(result.most_in_shares,
                                        acct.get_shares() * close / value)
    return result
