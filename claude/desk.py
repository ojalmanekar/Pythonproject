# desk.py -- the trading desk: a text menu, the same loop as the cafe register.
#
# Start it with no arguments:   python3 desk.py            (on Windows: python desk.py)
# or give the starting balances: python3 desk.py 5000 10    (cash 5000, 10 shares)
#
# The desk is the "authority": it owns the money (an Account) and validates every order,
# typed by hand or returned by an agent. A trade typed here fills at TODAY's close; the
# agent's back-test fills each order at TOMORROW's open (no look-ahead).

import sys
import time
import numpy as np
import pandas as pd

import market_data
import storage
from account import Account, OrderError
from agent import TradingAgent
from benchmarks import BuyAndHoldAgent, HoldAgent
from simulator import REGIMES, Trade, run_backtest

DESK_NAME = "MIS41110 trading desk"
DEFAULT_CASH = 10000.0
DEFAULT_SHARES = 0.0

MENU = """
================ """ + DESK_NAME + """ ================
 [1] Load dataset              [2] Set starting cash/shares
 [3] Step one day              [4] Manual buy
 [5] Manual sell               [6] Run agent to end
 [7] Show price chart          [8] Show equity + drawdown
 [9] Save / load               [0] Quit
====================================================="""

AGENTS = {
    "1": ("TradingAgent", TradingAgent),
    "2": ("BuyAndHoldAgent", BuyAndHoldAgent),
    "3": ("HoldAgent", HoldAgent),
}


class QuitDesk(Exception):
    """Raised when the input ends (Ctrl-D, or the end of a piped file): leave cleanly."""


def ask(prompt, default=""):
    """input() with a default answer, which also survives the end of the input."""
    try:
        answer = input(prompt)
    except EOFError:
        raise QuitDesk()
    answer = answer.strip()
    if answer == "":
        return default
    return answer


def ask_number(prompt, default, allow_minus_one=False):
    """Ask until the answer is a sensible number; returns a float.

    Turns away text ("abc"), NaN, infinity and negative numbers (except -1 where it means
    "all/max"), each with a message that says what was wrong."""
    while True:
        text = ask(prompt, str(default))
        try:
            value = float(text)
        except ValueError:
            print("  '" + text + "' is not a number -- try again")
            continue
        if value != value or value in (float("inf"), float("-inf")):
            print("  that is not a real amount -- try again")
            continue
        if allow_minus_one and value == -1:
            return value
        if value < 0:
            hint = " (or -1 for all/max)" if allow_minus_one else ""
            print("  the amount cannot be negative" + hint + " -- try again")
            continue
        if value > 1e12:
            print("  that amount is far too large -- try again")
            continue
        return value


class Desk:
    """The desk's state and one method per menu option."""

    def __init__(self, cash=DEFAULT_CASH, shares=DEFAULT_SHARES):
        self.start_cash = cash
        self.start_shares = shares
        self.market = None
        self.day = 0
        self.account = Account(cash, shares)
        self.manual_trades = []        # Trade objects for trades typed at the desk
        self.last_result = None        # the most recent agent run (a RunResult)
        self.last_event = "-"

    # ---------- helpers -----------------------------------------------------------------
    def price_today(self):
        return self.market.bars[self.day]["close"]

    def status(self):
        """The line printed after every action: the day and the balances."""
        if self.market is None:
            return ("no market loaded | cash " + str(round(self.account.cash, 2))
                    + " | shares " + str(round(self.account.shares, 2)))
        price = self.price_today()
        return ("day " + str(self.day) + "/" + str(len(self.market) - 1) + " | price "
                + str(round(price, 2)) + " | cash " + str(round(self.account.cash, 2))
                + " | shares " + str(round(self.account.shares, 2)) + " | equity "
                + str(round(self.account.equity(price), 2)))

    def need_market(self):
        if self.market is None:
            print("  load a dataset first (option 1)")
            return False
        return True

    # ---------- menu options ------------------------------------------------------------
    def load_dataset(self):
        tickers = market_data.available_tickers()
        hint = ", ".join(tickers) if tickers else "VOLT, ZNTH, NOVA, QBIT"
        ticker = ask("Ticker (e.g. " + hint + "): ")
        try:
            self.market = market_data.load_market(ticker)
        except market_data.DataError as error:
            print("  could not load it: " + str(error))
            return
        self.day = 0
        self.account = Account(self.start_cash, self.start_shares)
        self.manual_trades = []
        self.last_result = None
        print("Loaded " + str(self.market) + ".")
        if not self.market.news_found:
            print("  note: no news file for " + self.market.ticker
                  + ", so the agent sees no headlines on it")
        for warning in self.market.warnings[:5]:
            print("  warning: " + warning)
        if len(self.market.warnings) > 5:
            print("  ... and " + str(len(self.market.warnings) - 5) + " more warnings")
        self.last_event = "loaded " + self.market.ticker
        self.show_headlines()

    def set_balances(self):
        cash = ask_number("Starting cash [" + str(self.start_cash) + "]: ", self.start_cash)
        shares = ask_number("Starting shares [" + str(self.start_shares) + "]: ",
                            self.start_shares)
        self.start_cash = cash
        self.start_shares = shares
        self.account = Account(cash, shares)
        self.manual_trades = []
        self.day = 0
        self.last_event = "balances set: " + str(self.account)
        print("  starting balances set; the session starts again from day 0")

    def step_day(self):
        if not self.need_market():
            return
        if self.day >= len(self.market) - 1:
            print("  this is the last day of the data -- there is no next day")
            return
        self.day = self.day + 1
        self.last_event = "stepped to day " + str(self.day)
        self.show_headlines()

    def show_headlines(self):
        """Today's news and its sentiment score (the agent's own word list)."""
        if self.market is None or not self.market.news_found:
            return
        headlines = self.market.headlines_on(self.day)
        if not headlines:
            print("  no news today")
            return
        agent = TradingAgent()
        signal = agent.news_signal(headlines)
        mood = {1: "good", -1: "bad", 0: "neutral"}[signal]
        print("  news today (" + mood + "):")
        for headline in headlines:
            print("    - " + headline)

    def manual_trade(self, action):
        """Options 4 and 5: a trade typed at the desk fills at TODAY's close."""
        if not self.need_market():
            return
        word = "buy" if action == "BUY" else "sell"
        amount = ask_number("How many shares to " + word + " (-1 = all/max) [-1]: ", -1,
                            allow_minus_one=True)
        if amount != -1 and amount != int(amount):
            print("  shares are bought and sold whole -- try a whole number")
            return
        amount = int(amount)             # whole shares; -1.0 becomes -1
        price = self.price_today()
        shares_before = self.account.shares
        try:
            reply = self.account.execute((action, amount), price)
        except OrderError as error:
            print("  " + str(error))
            return
        moved = abs(self.account.shares - shares_before)
        if moved > 0:
            self.manual_trades.append(Trade(self.day, action, moved, price))
        self.last_event = action + " " + str(amount) + " -> " + reply
        print("-> " + reply)

    def run_agent(self):
        if not self.need_market():
            return
        print("  agents: [1] TradingAgent (ours)  [2] BuyAndHoldAgent  [3] HoldAgent")
        choice = ask("Which agent [1]: ", "1")
        if choice not in AGENTS:
            print("  no agent " + choice + " -- choose 1, 2 or 3")
            return
        print("  it sees: [1] price + news  [2] price only  [3] news only")
        seen = ask("Which [1]: ", "1")
        if seen not in REGIMES:
            print("  no option " + seen + " -- choose 1, 2 or 3")
            return
        name, agent_class = AGENTS[choice]
        regime, use_prices, use_news = REGIMES[seen]
        started = time.time()
        result = run_backtest(agent_class(), self.market, self.start_cash, self.start_shares,
                              use_prices, use_news, name)
        seconds = time.time() - started
        self.last_result = result
        print(result)
        print("  (" + str(len(result.equity)) + " days in " + str(round(seconds, 3)) + " s)")
        self.last_event = "ran " + result.label() + ": " + str(round(result.equity[-1], 2))

    def price_chart(self):
        if not self.need_market():
            return
        import charts                      # matplotlib loads only when a chart is wanted
        if self.last_result is not None:
            trades = self.last_result.trades
            extra = " (trades of " + self.last_result.name + ")"
        else:
            trades = self.manual_trades
            extra = " (your manual trades)"
        path = charts.price_with_trades(self.market, trades, extra)
        print("  saved " + path)

    def equity_charts(self):
        if self.last_result is None:
            print("  run an agent first (option 6): these charts show its run")
            return
        import charts
        print("  saved " + charts.equity_curve(self.last_result))
        print("  saved " + charts.drawdown(self.last_result))

    def save_or_load(self):
        choice = ask("[s]ave or [l]oad? ").lower()
        if choice.startswith("s"):
            self.save()
        elif choice.startswith("l"):
            self.load()
        else:
            print("  type s to save or l to load")

    def save(self):
        if self.market is None:
            print("  load a dataset first: there is no session to save")
            return
        storage.save_session({
            "ticker": self.market.ticker, "day": self.day,
            "cash": self.account.cash, "shares": self.account.shares,
            "start_cash": self.start_cash, "start_shares": self.start_shares,
        })
        print("Saved the session to " + storage.SESSION_FILE + ".")
        if self.last_result is not None:
            numbers = self.last_result.numbers()
            storage.append_result(self.last_result.label(), numbers["final_equity"],
                                  len(self.last_result.trades))
            storage.save_leaderboard(storage.load_results())
            print("Saved the run to " + storage.RESULTS_FILE + " and the leaderboard to "
                  + storage.LEADERBOARD_FILE + ".")
        self.last_event = "saved"

    def load(self):
        try:
            saved = storage.load_session()
            market = market_data.load_market(saved["ticker"])
        except (storage.StorageError, market_data.DataError) as error:
            print("  could not load: " + str(error))
            return
        if saved["day"] < 0 or saved["day"] >= len(market):
            print("  the saved day " + str(saved["day"]) + " is outside the data")
            return
        self.market = market
        self.day = saved["day"]
        self.start_cash = saved["start_cash"]
        self.start_shares = saved["start_shares"]
        self.account = Account(saved["cash"], saved["shares"])
        self.manual_trades = []
        self.last_result = None
        print("Loaded session: " + market.ticker + " day " + str(self.day) + ".")
        self.show_leaderboard()
        self.last_event = "loaded the saved session"

    def show_leaderboard(self):
        rows = storage.leaderboard_rows(storage.load_results())
        if not rows:
            print("Leaderboard: no saved runs yet.")
            return
        print("Leaderboard, best final equity first:")
        for rank, name, final in rows[:10]:
            print("  " + str(rank) + ". " + name + "  " + str(round(final, 2)))

    # ---------- the loop ----------------------------------------------------------------
    def run(self):
        print("Welcome. Starting cash " + str(self.start_cash) + ", shares "
              + str(self.start_shares) + ".")
        actions = {
            "1": self.load_dataset, "2": self.set_balances, "3": self.step_day,
            "4": lambda: self.manual_trade("BUY"), "5": lambda: self.manual_trade("SELL"),
            "6": self.run_agent, "7": self.price_chart, "8": self.equity_charts,
            "9": self.save_or_load,
        }
        while True:
            print(MENU)
            choice = ask("Choose: ")
            if choice == "0":
                print("Goodbye.")
                return
            if choice not in actions:
                print("  '" + choice + "' is not on the menu -- type a number from 0 to 9")
                continue
            try:
                actions[choice]()
            except QuitDesk:
                raise
            except Exception as error:     # a last safety net: report, keep the desk open
                print("  something went wrong: " + type(error).__name__ + ": " + str(error))
            print(self.status())
            print("  latest event: " + self.last_event)


def starting_balances(arguments):
    """Read optional starting cash and shares from the command line; defaults if absent."""
    cash = DEFAULT_CASH
    shares = DEFAULT_SHARES
    try:
        if len(arguments) > 1:
            cash = float(arguments[1])
        if len(arguments) > 2:
            shares = float(arguments[2])
        assert 0 <= cash < 1e12 and 0 <= shares < 1e12, "cash and shares must be sensible"
    except (ValueError, AssertionError) as error:
        print("Ignoring the command line (" + str(error) + "): using cash "
              + str(DEFAULT_CASH) + " and shares " + str(DEFAULT_SHARES) + ".")
        cash = DEFAULT_CASH
        shares = DEFAULT_SHARES
    return cash, shares


def main():
    cash, shares = starting_balances(sys.argv)
    desk = Desk(cash, shares)
    try:
        desk.run()
    except (QuitDesk, KeyboardInterrupt):
        print("\nGoodbye.")


if __name__ == "__main__":
    main()
