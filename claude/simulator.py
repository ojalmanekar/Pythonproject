# simulator.py -- the back-test: runs an agent over a whole market, one day at a time.
#
# THE LOOP (brief section 10), with no look-ahead:
#   for each day t except the last:
#       give the agent ONLY day t (its bar and/or its headlines) and the true balances
#       the agent returns one order
#       the order fills at the OPEN of day t+1, the first price after the decision
#       the account charges the 0.1% fee and replies ACCEPT or REJECT
#       record equity = cash + shares * close of day t+1
#
# COMPLEXITY: the loop visits each of the n days once and does a fixed amount of work per
# day, so a run is O(n) in the number of days (if the agent itself is O(1) per day).

from account import Account, OrderError
import metrics


class Trade:
    """One filled order: the day it filled, BUY or SELL, how many shares, at what price."""

    def __init__(self, day, action, quantity, price):
        self.day = day
        self.action = action
        self.quantity = quantity
        self.price = price

    def __str__(self):
        return ("day " + str(self.day) + ": " + self.action + " " + str(round(self.quantity, 2))
                + " @ " + str(round(self.price, 2)))


class RunResult:
    """Everything one back-test produced: the equity curve, the trades and the metrics."""

    def __init__(self, name, ticker, regime):
        self.name = name              # e.g. "TradingAgent"
        self.ticker = ticker          # e.g. "ZNTH"
        self.regime = regime          # "price + news", "price only" or "news only"
        self.equity = []              # one value per day, day 0 included
        self.trades = []              # Trade objects, in order
        self.rejects = 0              # how many orders the account refused
        self.error = ""               # what went wrong, if the agent crashed
        self.most_in_shares = 0.0     # the largest share of the money ever in shares

    def label(self):
        """The name this run is saved under on the leaderboard."""
        return self.name + " on " + self.ticker + " (" + self.regime + ")"

    def numbers(self):
        """The three numbers of the run (plus the final equity), from metrics.py."""
        return metrics.summary(self.equity)

    def __str__(self):
        numbers = self.numbers()
        lines = [
            "Ran " + self.name + " on " + self.ticker + " (" + self.regime + "):",
            "  final equity : " + str(round(numbers["final_equity"], 2)),
            "  total return : " + str(round(numbers["total_return"] * 100, 1)) + "%",
            "  sharpe-like  : " + str(round(numbers["sharpe_like"], 3)),
            "  max drawdown : " + str(round(-numbers["max_drawdown"] * 100, 1)) + "%",
            "  trades       : " + str(len(self.trades)),
            "  most in shares: " + str(round(self.most_in_shares * 100)) + "%",
        ]
        if self.rejects > 0:
            lines.append("  rejected     : " + str(self.rejects) + " orders")
        if self.error != "":
            lines.append("  STOPPED      : " + self.error)
        return "\n".join(lines)


REGIMES = {
    "1": ("price + news", True, True),
    "2": ("price only", True, False),
    "3": ("news only", False, True),
}


def run_backtest(agent, market, cash=10000.0, shares=0.0, use_prices=True, use_news=True,
                 name=None):
    """Run one agent over the whole market and return a RunResult.

    The agent object must have decide(bar, headlines, cash, shares, last_response). The
    account here is a fresh one: a back-test never touches the desk's own session."""
    if name is None:
        name = type(agent).__name__
    regime = "price + news" if (use_prices and use_news) else (
        "price only" if use_prices else "news only")
    result = RunResult(name, market.ticker, regime)
    account = Account(cash, shares)
    result.equity.append(account.equity(market.bars[0]["close"]))
    last_response = None

    for t in range(len(market.bars) - 1):        # every day but the last
        bar = market.bars[t] if use_prices else None
        if use_news:
            headlines = market.headlines_on(t)       # [] on a day without news
        else:
            headlines = None
        try:
            order = agent.decide(bar, headlines, account.cash, account.shares, last_response)
        except Exception as error:                   # the agent crashed: stop, say why
            result.error = ("day " + str(t) + ": the agent crashed: "
                            + type(error).__name__ + ": " + str(error))
            break

        fill_price = market.bars[t + 1]["open"]      # no look-ahead: tomorrow's open
        shares_before = account.shares
        try:
            last_response = account.execute(order, fill_price)
        except OrderError as error:
            result.error = "day " + str(t) + ": malformed order: " + str(error)
            break

        if last_response.startswith("REJECT"):
            result.rejects = result.rejects + 1
        moved = account.shares - shares_before
        if moved > 0:
            result.trades.append(Trade(t + 1, "BUY", moved, fill_price))
        elif moved < 0:
            result.trades.append(Trade(t + 1, "SELL", -moved, fill_price))

        close = market.bars[t + 1]["close"]
        value = account.equity(close)
        result.equity.append(value)
        if value > 0:
            in_shares = account.shares * close / value
            if in_shares > result.most_in_shares:
                result.most_in_shares = in_shares
    return result
