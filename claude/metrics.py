# metrics.py -- the indicators and the three numbers of every run, all built by hand.
#
# The library policy bans pandas' shortcuts (pct_change, shift, rolling, cumprod) because
# these are exactly the things we are marked on building, so every function below uses
# numpy slicing or a plain loop, the recipes of the time-series supplement (project
# document 09). Every function takes a list or array of numbers and returns numbers: no
# printing, no files, so each one can be tested on its own.
import matplotlib
import numpy as np


def daily_returns(values):
    """Day-to-day returns: (today / yesterday) - 1, for every day after the first.

    np.array FIRST, then slice by position. Slicing a raw pandas Series would line the
    two slices up by index label and silently give zeros (the trap in document 09)."""
    values = np.array(values, dtype=float)
    if len(values) < 2:
        return np.array([])
    today = values[1:]
    yesterday = values[:-1]
    return today / yesterday - 1


def moving_average(values, window):
    """The mean of the last `window` values, moved forward one day at a time.

    The result has len(values) - window + 1 entries: element 0 is the average of days
    0..window-1, so it belongs to day window-1. One pass with a running total: add the
    new day, take away the day that falls out of the window, which is O(n) instead of the
    O(n * window) of re-adding the whole window every day."""
    values = np.array(values, dtype=float)
    if window <= 0 or len(values) < window:
        return np.array([])
    averages = []
    total = 0.0
    for i in range(len(values)):
        total = total + values[i]
        if i >= window:
            total = total - values[i - window]
        if i >= window - 1:
            averages.append(total / window)
    return np.array(averages)


def total_return(equity):
    """Final value over starting value, minus one: 0.25 means +25%."""
    if len(equity) == 0 or equity[0] == 0:
        return 0.0
    return float(equity[-1] / equity[0] - 1)


def drawdown_series(equity):
    """How far each day sits below the best value so far, as a fraction (0 or negative)."""
    series = []
    peak = None
    for value in equity:
        if peak is None or value > peak:
            peak = value
        series.append((value - peak) / peak if peak > 0 else 0.0)
    return np.array(series)


def max_drawdown(equity):
    """The worst fall below a previous best: -0.16 means a 16% drawdown."""
    if len(equity) == 0:
        return 0.0
    return float(drawdown_series(equity).min())


def sharpe_like(equity):
    """The mean of the equity curve's daily returns over their standard deviation.

    numpy's std (population standard deviation), as the competition uses. A run that
    never moves has a standard deviation of 0, and we return 0 rather than divide by 0."""
    returns = daily_returns(equity)
    if len(returns) < 2:
        return 0.0
    spread = returns.std()
    if spread == 0:
        return 0.0
    return float(returns.mean() / spread)


def summary(equity):
    """The three numbers every run reports, in one dict."""
    return {
        "final_equity": float(equity[-1]) if len(equity) > 0 else 0.0,
        "total_return": total_return(equity),
        "max_drawdown": max_drawdown(equity),
        "sharpe_like": sharpe_like(equity),
    }
