# Reference: Tanisha Jha


import matplotlib.pyplot as plt  # draws the charts
import numpy as np  # fast maths on lists of numbers

MA_WINDOW = 10  # moving average uses the last 10 days

# PART A: the numbers

def daily_returns(values):
    # % change from yesterday to today, e.g. 100 -> 110 = 0.10
    values = np.array(values, dtype=float)
    if len(values) < 2: # need 2 days to compare
        return np.array([])
    today = values[1:] # day 1 to the end
    yesterday = values[:-1] # day 0 to the second-last
    return today / yesterday - 1


def moving_average(values, window):
    # average of the last `window` days
    # OPTIMIZATION: running total, O(n) instead of re-adding the window every day, O(n x window)
    values = np.array(values, dtype=float)
    if window <= 0 or len(values) < window:
        return np.array([])
    averages = []
    total = 0.0
    for i in range(len(values)):
        total = total + values[i] # add the new day
        if i >= window:
            total = total - values[i - window] # remove the day that left
        if i >= window - 1: # once we have a full window
            averages.append(total / window)
    return np.array(averages)

def total_return(equity):
    # final / start - 1, e.g. 10000 -> 12500 = 0.25 (+25%)
    if len(equity) == 0 or equity[0] == 0:  # avoid dividing by zero
        return 0.0
    return float(equity[-1] / equity[0] - 1)

def drawdown_series(equity):
    # each day: how far below the best value so far (the peak)
    # e.g. 100, 120, 90, 110 -> 0, 0, -0.25, -0.083
    series = []
    peak = equity[0]
    for value in equity:
        if value > peak:
            peak = value # new best: raise the peak

        if peak <= 0:
            series.append(0.0) # empty account: avoid dividing by zero
        else:
            series.append((value - peak) / peak)
    return np.array(series)

def max_drawdown(equity):
    # the worst (biggest) fall from a peak
    if len(equity) == 0:
        return 0.0
    return float(drawdown_series(equity).min())

def sharpe_like(equity):
    # return compared to risk: average daily return / how much it jumps around (std)
    if len(equity) == 0 or min(equity) <= 0:
        return 0.0
    returns = daily_returns(equity)
    if len(returns) < 2 or returns.std() == 0: # no movement: avoid dividing by zero
        return 0.0
    return float(returns.mean() / returns.std())

def summary(equity):
    # all the results of one run in one dictionary
    return {"final_equity": float(equity[-1]),
            "total_return": total_return(equity),
            "max_drawdown": max_drawdown(equity),
            "sharpe_like": sharpe_like(equity)}

def in_percent(fractions):
    # 0.25 -> 25.0 (week 8: map + lambda)
    return list(map(lambda x: round(x * 100,2), fractions))

#  PART B: the 3 charts

def finish(save_path, show):
    # shared last step: save as PNG, show the window, close
    plt.tight_layout()
    plt.savefig(save_path)
    if show:
        plt.show()
    plt.close()
    return save_path

def price_with_trades(market, trades, title_extra="", show=True):
    closes = market.closes()
    days = list(range(len(closes)))
    plt.figure(figsize=(10,5))
    plt.plot(days, closes, color="gray", label="close")
    averages = moving_average(closes, MA_WINDOW)
    if len(averages) > 0:
        # the first average belongs to day 9, so the line starts there
        plt.plot(list(range(MA_WINDOW - 1, len(closes))), averages, color="orange",
                 label=f"{MA_WINDOW}-day moving average")
    buys = [trade for trade in trades if trade.action == "BUY"]
    sells = [trade for trade in trades if trade.action == "SELL"]
    # trades drawn on the day they FILLED, at the fill price (next day's open)
    plt.scatter([t.day for t in buys], [t.price for t in buys], marker="^",
                color="green", label="buy", zorder=3)
    plt.scatter([t.day for t in sells], [t.price for t in sells], marker="v",
                    color="red", label="sell", zorder=3)
    plt.title(f"Trading Commercials : {market.ticker}{title_extra}")
    plt.xlabel("day")
    plt.ylabel("price")
    plt.legend()
    return finish(f"price_{market.ticker}.png", show)

def equity_curve(result, show=True):
    plt.figure(figsize=(10, 5))
    plt.plot(list(range(len(result.equity))), result.equity, color="blue", label="equity")
    plt.axhline(result.equity[0], color="gray", linestyle="--", label="starting value") # dashed start line
    plt.title(f"Equity curve: {result.label()}")
    plt.xlabel("day")
    plt.ylabel("equity (cash + shares * close)")
    plt.legend()
    return finish(f"equity_{result.ticker}.png", show)

def drawdown(result, show=True):
    series = drawdown_series(result.equity)
    plt.figure(figsize=(10, 5))
    plt.plot(list(range(len(series))), series, color="red")
    plt.title(f"Drawdown: {result.label()} (max {-series.min() * 100:.1f}%)")
    plt.xlabel("day")
    plt.ylabel("drawdown (fraction below the best so far)")
    return finish(f"drawdown_{result.ticker}.png", show)