# analytics.py -- the ANALYTICS AND CHARTS piece: the numbers of every run, and the pictures.
# Reference: <full name of the member responsible for this file>
#
# Part A, the numbers: the time-series supplement's recipes in the vanilla, in-syllabus
# form (numpy slicing, loops, comprehensions). pandas' shortcuts (pct_change, shift,
# rolling, cumprod) were not taught and are not allowed, because they do the very work
# this piece is marked on. Every function in part A is PURE (week 8): numbers in, numbers
# out, nothing printed or saved, so each can be tested on its own.
#
# Part B, the three charts the brief asks for, drawn with matplotlib the week-6 way:
#   1. price with trades : the closing price, its 10-day moving average, a triangle up at
#                          every buy and a triangle down at every sell
#   2. equity curve      : cash + shares * close, day by day
#   3. drawdown          : how far the equity sits below its best so far
# Each is SAVED as a PNG beside the program and shown in a window when show=True.

# --- 1. imports --------------------------------------------------------------------------
import matplotlib.pyplot as plt
import numpy as np

# --- 2. global constants ------------------------------------------------------------------
MA_WINDOW = 10        # the moving average drawn on the price chart (the agent's own window)


# --- 3. function declarations ---------------------------------------------------------------
# ---- part A: the numbers --------------------------------------------------------------------
def daily_returns(values):
    """Day-to-day returns: today / yesterday - 1, for every day after the first.

    The supplement's recipe: np.array FIRST, then two slices one step apart. Element i of
    values[1:] and of values[:-1] are the same pair of days."""
    values = np.array(values, dtype=float)
    if len(values) < 2:
        return np.array([])
    today = values[1:]
    yesterday = values[:-1]
    return today / yesterday - 1


def moving_average(values, window):
    """The mean of the last `window` values, moved forward one day at a time.

    The supplement writes it as  for i in range(window, len(closes) + 1):
                                     ma.append(closes[i - window:i].mean())
    which re-adds the whole window every day: O(n * window). Our ONE OPTIMIZATION (the
    complexity note's rubric item 11): keep a running total, add the day that enters and
    take away the day that leaves, so each day costs one addition and one subtraction and
    the whole series is O(n). Same numbers, to about fourteen digits.

    Element 0 of the result belongs to day window - 1."""
    values = np.array(values, dtype=float)
    if window <= 0 or len(values) < window:
        return np.array([])
    averages = []
    total = 0.0
    for i in range(len(values)):
        total = total + values[i]
        if i >= window:
            total = total - values[i - window]       # the day that left the window
        if i >= window - 1:
            averages.append(total / window)
    return np.array(averages)


def total_return(equity):
    """Final value over starting value, minus one: 0.25 means +25%."""
    if len(equity) == 0 or equity[0] == 0:
        return 0.0
    return float(equity[-1] / equity[0] - 1)


def drawdown_series(equity):
    """How far each day sits below the best value so far: 0 at a new best, else negative.

    The supplement's max-drawdown loop, keeping every day's value instead of the worst."""
    series = []
    peak = equity[0]
    for value in equity:
        if value > peak:
            peak = value
        if peak <= 0:
            series.append(0.0)               # an empty account (0 cash, 0 shares): no fall
        else:
            series.append((value - peak) / peak)
    return np.array(series)


def max_drawdown(equity):
    """The worst fall below a previous best: -0.16 is a 16% drawdown.

    The competition's gate, a fall to half the best value so far, is max_drawdown <= -0.5."""
    if len(equity) == 0:
        return 0.0
    return float(drawdown_series(equity).min())


def sharpe_like(equity):
    """The mean of the equity curve's daily returns over their standard deviation
    (the brief's section 10). numpy's .mean() and .std(), week 6's reductions. A curve that
    never moves has a standard deviation of 0, and we return 0 rather than divide by 0."""
    if len(equity) == 0 or min(equity) <= 0:
        return 0.0                           # a day worth 0 would mean dividing by 0
    returns = daily_returns(equity)
    if len(returns) < 2 or returns.std() == 0:
        return 0.0
    return float(returns.mean() / returns.std())


def summary(equity):
    """The run's numbers in one dict, ready to print or save."""
    return {"final_equity": float(equity[-1]),
            "total_return": total_return(equity),
            "max_drawdown": max_drawdown(equity),
            "sharpe_like": sharpe_like(equity)}


def as_percent(fractions):
    """[0.25, -0.1] -> [25.0, -10.0]: week 8's map + lambda, no loop in sight."""
    return list(map(lambda x: round(x * 100, 2), fractions))


# ---- part B: the charts ---------------------------------------------------------------------
def finish(save_path, show):
    """The shared last step of every chart: fit the labels, save, then show or close."""
    plt.tight_layout()
    plt.savefig(save_path)
    if show:
        plt.show()
    plt.close()
    return save_path


def price_with_trades(market, trades, title_extra="", show=True):
    """Chart 1: the closing price, its moving average, and every buy and sell."""
    closes = market.closes()
    days = list(range(len(closes)))
    plt.figure(figsize=(10, 5))
    plt.plot(days, closes, color="gray", label="close")
    averages = moving_average(closes, MA_WINDOW)
    if len(averages) > 0:
        # averages[0] belongs to day MA_WINDOW - 1, so its x values start there
        plt.plot(list(range(MA_WINDOW - 1, len(closes))), averages, color="orange",
                 label=f"{MA_WINDOW}-day moving average")
    # Split the trades with two list comprehensions with an if (week 4).
    buys = [trade for trade in trades if trade.action == "BUY"]
    sells = [trade for trade in trades if trade.action == "SELL"]
    plt.scatter([t.day for t in buys], [t.price for t in buys], marker="^",
                color="green", label="buy", zorder=3)
    plt.scatter([t.day for t in sells], [t.price for t in sells], marker="v",
                color="red", label="sell", zorder=3)
    plt.title(f"Price with trades: {market.ticker}{title_extra}")
    plt.xlabel("day")
    plt.ylabel("price")
    plt.legend()
    return finish(f"price_{market.ticker}.png", show)


def equity_curve(result, show=True):
    """Chart 2: the value of cash plus shares, day by day."""
    plt.figure(figsize=(10, 5))
    plt.plot(list(range(len(result.equity))), result.equity, color="blue", label="equity")
    plt.axhline(result.equity[0], color="gray", linestyle="--", label="starting value")
    plt.title(f"Equity curve: {result.label()}")
    plt.xlabel("day")
    plt.ylabel("equity (cash + shares * close)")
    plt.legend()
    return finish(f"equity_{result.ticker}.png", show)


def drawdown(result, show=True):
    """Chart 3: the drawdown, from 0 at a new best down to the worst fall."""
    series = drawdown_series(result.equity)
    plt.figure(figsize=(10, 5))
    plt.plot(list(range(len(series))), series, color="red")
    plt.title(f"Drawdown: {result.label()} (max {-series.min() * 100:.1f}%)")
    plt.xlabel("day")
    plt.ylabel("drawdown (fraction below the best so far)")
    return finish(f"drawdown_{result.ticker}.png", show)
