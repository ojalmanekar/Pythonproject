# charts.py -- the three required charts, drawn with matplotlib the week-6 way.
#
#   1. price with trades : the closing price, its 10-day moving average, a triangle up at
#                          every buy and a triangle down at every sell
#   2. equity curve      : cash + shares * close, day by day
#   3. drawdown          : how far the equity sits below its best so far, as a fraction
#
# Each chart has a title and labelled axes, is saved as a PNG in the charts/ folder, and is
# shown in a window that has to be closed before the desk carries on (plt.show() waits).

import os

import matplotlib
import matplotlib.pyplot as plt

import metrics

CHART_FOLDER = "charts"
MA_WINDOW = 10          # the moving average drawn on the price chart (same as the agent)


def _finish(filename):
    """Save the current chart to charts/<filename> and show it (if a screen exists)."""
    os.makedirs(CHART_FOLDER, exist_ok=True)
    path = os.path.join(CHART_FOLDER, filename)
    plt.tight_layout()
    plt.savefig(path)
    # On a machine with no screen matplotlib uses the "agg" backend, which cannot open a
    # window; there the PNG file is the chart.
    if matplotlib.get_backend().lower() != "agg":
        plt.show()
    plt.close()
    return path


def price_with_trades(market, trades, title_extra=""):
    """Chart 1: the closing price with the moving average and every buy and sell."""
    closes = market.closes()
    days = list(range(len(closes)))
    plt.figure(figsize=(10, 5))
    plt.plot(days, closes, color="gray", label="close")
    averages = metrics.moving_average(closes, MA_WINDOW)
    if len(averages) > 0:
        # averages[0] belongs to day MA_WINDOW - 1, so its x values start there
        plt.plot(list(range(MA_WINDOW - 1, len(closes))), averages, color="orange",
                 linewidth=1, label=str(MA_WINDOW) + "-day moving average")
    buy_days = []
    buy_prices = []
    sell_days = []
    sell_prices = []
    for trade in trades:
        if trade.action == "BUY":
            buy_days.append(trade.day)
            buy_prices.append(trade.price)
        else:
            sell_days.append(trade.day)
            sell_prices.append(trade.price)
    plt.scatter(buy_days, buy_prices, marker="^", color="green", label="buy", zorder=3)
    plt.scatter(sell_days, sell_prices, marker="v", color="red", label="sell", zorder=3)
    plt.title("Price with trades: " + market.ticker + title_extra)
    plt.xlabel("day")
    plt.ylabel("price")
    plt.legend()
    return _finish("price_" + market.ticker + ".png")


def equity_curve(result):
    """Chart 2: the value of cash plus shares, day by day."""
    plt.figure(figsize=(10, 5))
    plt.plot(list(range(len(result.equity))), result.equity, color="blue", label="equity")
    plt.axhline(result.equity[0], color="gray", linestyle="--", linewidth=1,
                label="starting value")
    plt.title("Equity curve: " + result.label())
    plt.xlabel("day")
    plt.ylabel("equity (cash + shares * close)")
    plt.legend()
    return _finish("equity_" + result.ticker + ".png")


def drawdown(result):
    """Chart 3: the drawdown, from 0 (at a new best) down to the worst fall."""
    series = metrics.drawdown_series(result.equity)
    plt.figure(figsize=(10, 5))
    plt.plot(list(range(len(series))), series, color="red")
    plt.fill_between(list(range(len(series))), series, 0, color="red", alpha=0.2)
    plt.title("Drawdown: " + result.label() + " (max " + str(round(-series.min() * 100, 1))
              + "%)")
    plt.xlabel("day")
    plt.ylabel("drawdown (fraction below best)")
    return _finish("drawdown_" + result.ticker + ".png")
