# simulator.py -- the back-test: runs any agent over a whole market, one day at a time.
#
# THE LOOP (the brief's section 10), with no look-ahead. For each day t except the last:
#   1. hand the agent ONLY day t: its bar and/or its headlines, and the true balances;
#   2. the agent proposes one order;
#   3. the order fills at the OPEN of day t+1, the first price after the decision;
#   4. the Account (the authority) checks it, charges 0.1%, replies ACCEPT or REJECT;
#   5. record equity = cash + shares * close of day t+1.
#
# BIG-O (rubric item 11): the loop visits each of the n days once and does a fixed amount
# of work per day, so a run is O(n). No loop sits inside it over the history: the agent's
# own 10-day average is O(10) per day, a constant.

# --- 1. imports --------------------------------------------------------------------------
import account
import metrics

# --- 2. global constants ------------------------------------------------------------------
# The three information regimes of the competition, as a dict: menu key -> (label, prices?,
# news?). A tuple per entry (week 4): fixed, read-only facts.
REGIMES = {"1": ("price + news", True, True),
           "2": ("price only", True, False),
           "3": ("news only", False, True)}


# --- 3. class declarations ----------------------------------------------------------------
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
        return metrics.summary(self.equity)

    def __str__(self):
        n = self.numbers()
        return_pct, drawdown_pct = metrics.as_percent([n["total_return"], -n["max_drawdown"]])
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


# --- 4. function declarations ---------------------------------------------------------------
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
    acct = account.Account(cash, shares)
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
