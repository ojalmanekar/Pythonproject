# market_data.py -- loading the data: prices, news and the word list.
#
# Everything that touches the data files lives here, and nothing here knows how to trade:
# loading is kept apart from strategy (rubric item 5). The files are read exactly as they
# are given, every time, and never edited or converted (the dataset guide's rule), so the
# same code loads a training, practice or held-back market unchanged.
#
# The tools are the course's:
#   - prices: pandas read_csv with its header (week 6), then np.array(...) on each column
#     BEFORE any slicing (the time-series supplement's trap);
#   - news and word list: plain file reading, line by line (weeks 2 and 3), split(",", 1)
#     so a comma inside a headline can never break the line (the dataset guide);
#   - missing files: try/except FileNotFoundError (week 5), with a clear message.

# --- 1. imports --------------------------------------------------------------------------
import numpy as np
import pandas as pd

# --- 2. global constants ------------------------------------------------------------------
# Where a market's files may be. The course builds every path from one constant (week 4's
# DATA_DIR), so moving the data changes one line.
DATA_FOLDERS = ["data/training/", "data/practice/", "data/held_back/"]
LEXICON_FILE = "data/training/sentiment_words.csv"
PRICE_COLUMNS = ["open", "high", "low", "close", "volume"]


# --- 3. class declaration -----------------------------------------------------------------
class Market:
    """One loaded market: its ticker, its daily bars and its news."""

    def __init__(self, ticker, bars, news, news_found, notes):
        self.ticker = ticker            # e.g. "NOVA"
        self.bars = bars                # list of dicts, one per day, the shape decide() gets
        self.news = news                # dict: day number -> list of headlines
        self.news_found = news_found    # False when the market has no news file
        self.notes = notes              # list of problems fixed while loading

    def __str__(self):
        return f"{self.ticker} ({self.days()} days)"

    def days(self):
        return len(self.bars)

    def close_on(self, day):
        return self.bars[day]["close"]

    def headlines_on(self, day):
        """That day's headlines; an empty list on a day without news (week 4's .get)."""
        return self.news.get(day, [])

    def closes(self):
        """Every closing price as a numpy array, built with a list comprehension."""
        return np.array([bar["close"] for bar in self.bars])


# --- 4. function declarations ---------------------------------------------------------------
def find_price_file(ticker):
    """The path of <ticker>.csv in the first data folder that has it, or "" if none does.

    We just TRY to open each candidate and catch FileNotFoundError (week 5): no os module
    needed. A practice market is typed with its week folder, e.g. W07/ABCD."""
    for folder in DATA_FOLDERS:
        path = folder + ticker + ".csv"
        try:
            f = open(path)
            f.close()
            return path
        except FileNotFoundError:
            continue                     # not here: try the next folder
    return ""


def load_prices(path):
    """Read one <TICKER>.csv into a list of bar dicts. Returns (bars, notes).

    Raises ValueError with a clear message when the file cannot be used, so the desk can
    catch it and say what is wrong (week 5's raise ValueError("...") with a message)."""
    frame = pd.read_csv(path)            # comma-separated, with its header row (week 6)
    columns = {}
    for name in PRICE_COLUMNS:
        try:
            # np.array FIRST, then work by position: never slice a raw pandas Series.
            columns[name] = np.array(frame[name], dtype=float)
        except KeyError:
            raise ValueError(f"{path} has no '{name}' column: the header must be "
                             "day,open,high,low,close,volume")
        except ValueError:
            raise ValueError(f"{path}: the '{name}' column holds something that is not a number")
    if len(columns["close"]) < 2:
        raise ValueError(f"{path} needs at least two days of prices")

    bars = []
    notes = []
    previous_close = None
    # zip walks the five columns together, one day at a time; enumerate counts the days
    # (week 4's two looping helpers).
    for day, values in enumerate(zip(columns["open"], columns["high"], columns["low"],
                                     columns["close"], columns["volume"])):
        bar = {}
        for name, value in zip(PRICE_COLUMNS, values):
            if value != value or value < 0:          # NaN (an empty cell) or negative
                if previous_close is None:
                    raise ValueError(f"{path}: day {day} has no usable {name}")
                if name == "volume":
                    value = 0.0
                else:
                    value = previous_close           # carry yesterday's close forward
                notes.append(f"day {day}: missing {name} filled in")
            bar[name] = float(value)
        bars.append(bar)
        previous_close = bar["close"]
    return bars, notes


def load_news(path):
    """Read one <TICKER>_news.txt into {day: [headline, ...]}. Returns (news, notes).

    Lets FileNotFoundError through: load_market decides what a missing news file means."""
    news = {}
    notes = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line == "" or line.startswith("day"):
            continue                                 # a blank line or the header
        parts = line.split(",", 1)                   # split ONCE, at the first comma
        try:
            day = int(parts[0])
            headline = parts[1].strip()
        except (ValueError, IndexError):
            notes.append("skipped a news line: " + line[:40])
            continue
        if day not in news:
            news[day] = []
        news[day].append(headline)
    return news, notes


def load_market(ticker):
    """Load one market. Returns (market, message): market is None when it could not load.

    Like Register.sell, it replies instead of raising, so the desk prints the message and
    carries on."""
    ticker = ticker.strip().upper()
    if ticker == "":
        return None, "no ticker typed"
    path = find_price_file(ticker)
    if path == "":
        return None, (f"no price file {ticker}.csv in {', '.join(DATA_FOLDERS)} -- check "
                      "the spelling, and that the data folder sits beside desk.py "
                      "(the folder you run the program from)")
    try:
        bars, notes = load_prices(path)
    except ValueError as error:
        return None, str(error)

    news_path = path[:-4] + "_news.txt"              # NOVA.csv -> NOVA_news.txt
    try:
        news, news_notes = load_news(news_path)
        notes = notes + news_notes
        news_found = True
    except FileNotFoundError:
        news = {}
        news_found = False
        notes.append(f"no news file {news_path}: the market loads without headlines")

    name = ticker.split("/")[-1]                     # "W07/ABCD" -> "ABCD"
    market = Market(name, bars, news, news_found, notes)
    return market, f"Loaded {market}."


def load_lexicon(path=LEXICON_FILE):
    """sentiment_words.csv as a dict {word: score}; {} if the file is missing.

    The dataset guide's code, word for word: the week-4 lexicon pattern."""
    scores = {}
    try:
        for line in open(path, encoding="utf-8"):
            if line.startswith("word"):
                continue                             # skip the header
            parts = line.strip().split(",")
            if len(parts) == 2:
                scores[parts[0]] = float(parts[1])
    except (FileNotFoundError, ValueError):
        return {}
    return scores


def headline_score(headlines, lexicon):
    """Total score of a day's headlines with the lexicon: cafe_w4's review_scores idea."""
    score = 0.0
    for headline in headlines:
        for word in headline.lower().replace(":", " ").split():
            score = score + lexicon.get(word, 0.0)
    return score
