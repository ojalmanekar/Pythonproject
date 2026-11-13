# charts.py -- the three charts the brief asks for, drawn with matplotlib the week-6 way.
#
#   1. price with trades : the closing price in gray, its 10-day moving average, a triangle
#                          up at every buy and a triangle down at every sell (the
#                          time-series supplement's recipe: scatter, marker=, label=, legend)
#   2. equity curve      : cash + shares * close, day by day
#   3. drawdown          : how far the equity sits below its best so far
#
# Each chart has a title and labelled axes, is SAVED as a PNG beside the program (as
# cafe_w6b's sales_report saves sales_by_product.png), and is shown in a window when
# show=True. plt.show() waits until you close the window.

# --- 1. imports --------------------------------------------------------------------------
import matplotlib.pyplot as plt

import metrics

# --- 2. global constants ------------------------------------------------------------------
MA_WINDOW = 10        # the moving average drawn on the price chart (the agent's own window)


# --- 3. function declarations ---------------------------------------------------------------
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
    averages = metrics.moving_average(closes, MA_WINDOW)
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
    series = metrics.drawdown_series(result.equity)
    plt.figure(figsize=(10, 5))
    plt.plot(list(range(len(series))), series, color="red")
    plt.title(f"Drawdown: {result.label()} (max {-series.min() * 100:.1f}%)")
    plt.xlabel("day")
    plt.ylabel("drawdown (fraction below the best so far)")
    return finish(f"drawdown_{result.ticker}.png", show)
