# Reference : Paarth Bhardwaj


import analytics


FEE = 0.001  # 0.1% charged on every buy and every sell
ACTIONS = {"BUY", "SELL", "HOLD"}  # a set, because we only ever ask "is it in here?"
DEFAULT_CASH = 10000.0
DEFAULT_SHARES = 0.0


REGIMES = {"1": ("price + news", True, True),
           "2": ("price only", True, False),
           "3": ("news only", False, True)}



class Account:
    def __init__(self, cash=DEFAULT_CASH, shares=DEFAULT_SHARES):
        # Turn the inputs into numbers first, then check them ("5000" becomes 5000.0).
        cash = float(cash)
        shares = float(shares)
        if cash < 0:
            cash = 0.0  # never start with negative money
        if shares < 0:
            shares = 0.0
        self.__cash = cash  # double underscore: code outside can't change these
        self.__shares = shares

    # ---- getters: you can read the balances but not write them ----------------------
    def get_cash(self):
        return self.__cash

    def get_shares(self):
        return self.__shares

    def get_equity(self, price):
        return self.__cash + self.__shares * price

    def __str__(self):
        return f"cash {self.__cash:.2f} | shares {self.__shares:g}"

    # ---- the one door the money goes through ----------------------------------------
    def execute(self, order, price):

        # Check the order first, change nothing until it passes.
        action, amount, problem = check_order(order)
        if problem != "":
            return "REJECT bad order: " + problem
        if action == "HOLD":
            return "ACCEPT"
        if action == "BUY":
            return self.__buy(amount, price)
        return self.__sell(amount, price)

    def __buy(self, amount, price):
        """Private helper: only execute() calls this."""
        if amount < 0:
            amount = int(self.__cash / (price * (1 + FEE)))
            if amount * price * (1 + FEE) > self.__cash:  # safety check for rounding
                amount = amount - 1
        if amount <= 0:
            return "ACCEPT"  # nothing to buy isn't an error
        cost = amount * price * (1 + FEE)
        if cost > self.__cash:
            return "REJECT currency balance: " + str(round(self.__cash, 2))
        # The order is fine, so now the balances can change.
        self.__cash = self.__cash - cost
        self.__shares = self.__shares + amount
        assert self.__cash >= 0, "a buy broke the cash invariant"
        return "ACCEPT"

    def __sell(self, amount, price):
        if amount < 0:
            amount = self.__shares  # -1 means sell everything
        if amount <= 0:
            return "ACCEPT"
        if amount > self.__shares:
            return "REJECT stock owned: " + str(round(self.__shares, 2))
        self.__cash = self.__cash + amount * price * (1 - FEE)
        self.__shares = self.__shares - amount
        assert self.__shares >= 0, "a sale broke the shares invariant"
        return "ACCEPT"



class Trade:

    def __init__(self, day, action, quantity, price):
        self.day = day
        self.action = action
        self.quantity = quantity
        self.price = price

    def __str__(self):
        return f"day {self.day:>3}: {self.action:<4} {self.quantity:>6g} @ {self.price:>8.2f}"


class RunResult:


    def __init__(self, agent_name, ticker, regime):
        self.agent_name = agent_name
        self.ticker = ticker
        self.regime = regime  # "price + news", "price only" or "news only"
        self.equity = []  # one value per day, starting from day 0
        self.trades = []  # Trade objects in the order they happened
        self.rejects = 0  # how many orders the account refused
        self.error = ""  # what stopped the run early, if anything
        self.most_in_shares = 0.0  # the biggest share of our money ever held in shares

    def label(self):
        """The name this run gets on the leaderboard."""
        return f"{self.agent_name} on {self.ticker} ({self.regime})"

    def numbers(self):
        return analytics.summary(self.equity)

    def __str__(self):
        n = self.numbers()
        return_pct, drawdown_pct = analytics.in_percent([n["total_return"], -n["max_drawdown"]])
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



class BaseAgent:
    def __init__(self, name):
        self.name = name

    def decide(self, bar, headlines, cash, shares, last_response):
        raise NotImplementedError("every BaseAgent subclass must define decide()")

    def __str__(self):
        return f"{self.name} (benchmark)"


class HoldAgent(BaseAgent):

    def __init__(self):
        BaseAgent.__init__(self, "HoldAgent")

    def decide(self, bar, headlines, cash, shares, last_response):
        return ("HOLD", 0)


class BuyAndHoldAgent(BaseAgent):

    def __init__(self):
        BaseAgent.__init__(self, "BuyAndHoldAgent")

    def decide(self, bar, headlines, cash, shares, last_response):
        if shares == 0 and cash > 0:
            return ("BUY", -1)
        return ("HOLD", 0)


# --- 4. functions ---------------------------------------------------------------------------
def check_order(order):

    try:
        action, amount = order
    except (TypeError, ValueError):
        return ("", 0, "an order is a pair (action, amount), got " + str(order)[:40])
    if action not in ACTIONS:
        return ("", 0, "the action must be BUY, SELL or HOLD, got " + str(action)[:20])
    try:
        amount = float(amount)
    except (TypeError, ValueError, OverflowError):
        return ("", 0, "the amount must be a number, got " + str(amount)[:20])
    if amount != amount or abs(amount) == float("inf"):  # NaN is the only value that != itself
        return ("", 0, "the amount must be a finite number")
    if amount == int(amount):
        amount = int(amount)  # 5.0 shares is just 5 shares
    return (action, amount, "")


def run_backtest(agent, market, cash, shares, use_prices, use_news, agent_name):
    regime = "price + news"
    if use_prices and not use_news:
        regime = "price only"
    elif use_news and not use_prices:
        regime = "news only"
    result = RunResult(agent_name, market.ticker, regime)
    acct = Account(cash, shares)
    result.equity.append(acct.get_equity(market.close_on(0)))
    last_response = None

    for t in range(market.days() - 1):  # every day except the last
        # 1. Work out what the agent may see. We pass copies, so an agent that edits
        #    its data can't damage ours.
        bar = None
        if use_prices:
            bar = dict(market.bars[t])
        headlines = None
        if use_news:
            headlines = list(market.headlines_on(t))

        # 2. Ask the agent for an order. If it crashes, only this run stops.
        try:
            order = agent.decide(bar, headlines, acct.get_cash(), acct.get_shares(),
                                 last_response)
        except Exception as error:
            result.error = f"day {t}: the agent crashed: {type(error).__name__}: {error}"
            break

        # 3 and 4. Fill at tomorrow's open, through the account's one door.
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

        # 5. Record what the account is worth at tomorrow's close.
        close = market.close_on(t + 1)
        value = acct.get_equity(close)
        result.equity.append(value)
        if value > 0:
            result.most_in_shares = max(result.most_in_shares,
                                        acct.get_shares() * close / value)
    return result