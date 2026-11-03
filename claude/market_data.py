# market_data.py -- loading the data files: prices, news and the sentiment word list.
#
# Everything that touches the data files lives here, and nothing here knows anything about
# trading. That keeps loading separate from strategy (rubric item 5): the desk asks this
# module for a Market, and the same code loads a training, practice or held-back market
# unchanged, because it reads the files exactly as they are given and never edits them.

import os

import numpy as np
import pandas as pd

# Where the data might be. The marker puts the data in data/training/ beside our files;
# the other folders are where practice and held-back markets are kept (project doc 06).
# We look beside the folder the program was started from AND beside this file itself, so
# the desk still finds the data when an editor such as PyCharm starts it from elsewhere.
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDERS = (
    "data/training/", "data/held_back/", "data/practice/", "../data/training/",
    os.path.join(HERE, "data", "training") + os.sep,
    os.path.join(HERE, "data", "held_back") + os.sep,
    os.path.join(os.path.dirname(HERE), "data", "training") + os.sep,
)
PRICE_COLUMNS = ("day", "open", "high", "low", "close", "volume")


class DataError(Exception):
    """A data file is missing or cannot be read. Inherits from Exception, so the desk can
    catch exactly this kind of problem and print its message instead of crashing."""


class Market:
    """One market: its ticker, its daily bars and its news, ready for the desk.

    bars is a list of dicts, one per day, in the exact shape the agent contract gives to
    decide(): {"open": .., "high": .., "low": .., "close": .., "volume": ..}.
    news is a dict from day number to that day's list of headlines."""

    def __init__(self, ticker, bars, news, news_found, warnings):
        self.ticker = ticker
        self.bars = bars
        self.news = news
        self.news_found = news_found   # False when there was no news file at all
        self.warnings = warnings       # problems that were fixed while loading

    def __len__(self):
        return len(self.bars)

    def __str__(self):
        return self.ticker + " (" + str(len(self.bars)) + " days)"

    def closes(self):
        """All closing prices as a numpy array: an array BEFORE anyone slices it."""
        values = []
        for bar in self.bars:
            values.append(bar["close"])
        return np.array(values)

    def headlines_on(self, day):
        """The headlines for one day: an empty list on a day without news."""
        return self.news.get(day, [])


def find_folder(ticker):
    """The first data folder holding this ticker's price file, or raise DataError."""
    for folder in DATA_FOLDERS:
        if os.path.isfile(folder + ticker + ".csv"):
            return folder
    # Practice weeks live one folder deeper, e.g. data/practice/W07/
    if os.path.isdir("data/practice"):
        for week in sorted(os.listdir("data/practice")):
            folder = "data/practice/" + week + "/"
            if os.path.isfile(folder + ticker + ".csv"):
                return folder
    raise DataError("no price file " + ticker + ".csv -- check the ticker's spelling, and "
                    "that a folder data/training/ holding the data sits beside desk.py "
                    "(looked in " + os.path.join(HERE, "data", "training") + ")")


def available_tickers():
    """Every ticker that has a price file in one of the data folders, sorted."""
    found = []
    for folder in DATA_FOLDERS:
        if not os.path.isdir(folder):
            continue
        for name in os.listdir(folder):
            if name.endswith(".csv") and name != "sentiment_words.csv":
                ticker = name[:-4]
                if ticker not in found:
                    found.append(ticker)
    found.sort()
    return found


def load_prices(path):
    """Read a <TICKER>.csv file into a list of bar dicts. Returns (bars, warnings).

    pandas reads the comma-separated file and its header row. We then check the columns,
    convert every value to a float, and repair any missing price by carrying the day
    before's close forward, so a damaged row never stops the desk."""
    try:
        frame = pd.read_csv(path)
    except FileNotFoundError:
        raise DataError("price file not found: " + path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
        raise DataError("cannot read " + path + ": " + str(error))

    missing = []
    for column in PRICE_COLUMNS:
        if column not in frame.columns:
            missing.append(column)
    if missing:
        raise DataError(path + " has no column " + ", ".join(missing)
                        + " -- the header must be day,open,high,low,close,volume")
    if len(frame) < 2:
        raise DataError(path + " needs at least two days of prices")

    # np.array(...) first, then work by position: never slice a raw pandas Series.
    columns = {}
    for name in ("open", "high", "low", "close", "volume"):
        columns[name] = np.array(pd.to_numeric(frame[name], errors="coerce"), dtype=float)

    bars = []
    warnings = []
    previous_close = None
    for i in range(len(frame)):
        bar = {}
        for name in ("open", "high", "low", "close", "volume"):
            value = columns[name][i]
            if value != value or value < 0:          # NaN (value != value) or negative
                if previous_close is None:
                    raise DataError(path + ": day " + str(i) + " has no usable " + name)
                value = 0.0 if name == "volume" else previous_close
                warnings.append("day " + str(i) + ": missing " + name + " filled in")
            bar[name] = float(value)
        bars.append(bar)
        previous_close = bar["close"]
    return bars, warnings


def load_news(path):
    """Read a <TICKER>_news.txt file into {day: [headline, ...]}. Returns (news, warnings).

    Plain-text reading, as in weeks 2 and 3: skip the header, split each line ONCE at the
    first comma (split(",", 1)), so a comma inside a headline can never break the line.
    A line that cannot be read is skipped with a warning rather than crashing."""
    news = {}
    warnings = []
    handle = open(path, encoding="utf-8")
    line_number = 0
    for line in handle:
        line_number = line_number + 1
        line = line.strip()
        if line == "" or line.startswith("day"):
            continue                                   # blank line or the header
        parts = line.split(",", 1)
        try:
            day = int(parts[0])
            headline = parts[1].strip()
        except (ValueError, IndexError):
            warnings.append("news line " + str(line_number) + " skipped: " + line[:40])
            continue
        if day not in news:
            news[day] = []
        news[day].append(headline)
    handle.close()
    return news, warnings


def load_lexicon(folder):
    """Read sentiment_words.csv into {word: score}; an empty dict if it is not there."""
    scores = {}
    try:
        handle = open(folder + "sentiment_words.csv", encoding="utf-8")
    except FileNotFoundError:
        return scores
    for line in handle:
        if line.startswith("word"):
            continue
        parts = line.strip().split(",")
        if len(parts) == 2:
            try:
                scores[parts[0]] = float(parts[1])
            except ValueError:
                continue
    handle.close()
    return scores


def load_market(ticker):
    """Load one market's prices and news. Raises DataError if the prices cannot be read.

    A missing NEWS file is not fatal: the market loads with no headlines and a warning,
    which is how the desk survives the news-missing case."""
    ticker = ticker.strip().upper()
    if ticker == "":
        raise DataError("no ticker given")
    folder = find_folder(ticker)
    bars, warnings = load_prices(folder + ticker + ".csv")
    news_path = folder + ticker + "_news.txt"
    try:
        news, news_warnings = load_news(news_path)
        news_found = True
        warnings = warnings + news_warnings
    except FileNotFoundError:
        news = {}
        news_found = False
        warnings.append("no news file " + news_path + ": the market loads without headlines")
    return Market(ticker, bars, news, news_found, warnings)
