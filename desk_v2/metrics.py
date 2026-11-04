# metrics.py -- the indicators and the three numbers of every run, built by hand.
#
# These are the time-series supplement's recipes (project document 09), in the vanilla,
# in-syllabus form: numpy slicing, loops and comprehensions. pandas' shortcuts
# (pct_change, shift, rolling, cumprod) were not taught and are not allowed in the
# submission, because they do the very work this file is marked on.
#
# Every function is PURE (week 8's word): numbers in, numbers out. Nothing prints, nothing
# reads a file, nothing outside is changed -- so each one can be tested on its own, which
# check_project.py does.

# --- 1. imports --------------------------------------------------------------------------
import numpy as np

# --- 2. global constants ------------------------------------------------------------------
# (none: every function takes what it needs as parameters -- week 2's "front door" rule)


# --- 3. function declarations ---------------------------------------------------------------
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
