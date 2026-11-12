# Reference: Sandra Merin Ronald

import numpy as np # Used for numerical operations and arrays
import pandas as pd # Used to read and work with CSV data

DATA_FOLDERS = ["data/training/", "data/practice/", "data/held_back/"]
WORD_LIST_FILE = "data/training/sentiment_words.csv"
PRICE_COLUMNS = ["open", "high", "low", "close", "volume"]


class Market: # creates a market class to store stock data and news

    def __init__(self, ticker, bars, news, news_found, notes): # initializes the market object and stores its data
        self.ticker = ticker
        self.bars = bars
        self.news = news
        self.news_found = news_found   # False when the market has no news file
        self.notes = notes             # list of problems fixed while loading

    def __str__(self):
        return f"{self.ticker} ({self.days()} days)"

    def days(self):
        return len(self.bars)  # returns the total number of trading days

    def close_on(self, day):
        return self.bars[day]["close"] # gets the closing price for a particular day

    def headlines_on(self, day):
        return self.news.get(day, []) # Returns the headlines for a day, or an empty list if none exist

    def closes(self): # Creates an array containing all closing prices
        return np.array([bar["close"] for bar in self.bars])


def find_price(ticker): # Searches the data folders for the stock price file
    for folder in DATA_FOLDERS:
        path = folder + ticker + ".csv"
        try:
            f = open(path)
            f.close()
            return path
        except FileNotFoundError: # Tries to open the file; moves to the next folder if it is missing
            continue
    return ""


def load_prices(path): # Reads the price file into a list of daily bars
    frame = pd.read_csv(path) # Reads the CSV file with its header row
    columns = {}
    for name in PRICE_COLUMNS:
        try:
            columns[name] = np.array(frame[name], dtype=float)
        except KeyError:
            raise ValueError(f"{path} has no '{name}' column: the header must be "
                             "day,open,high,low,close,volume")
        except ValueError:
            raise ValueError(f"{path}: the '{name}' column holds something that is not a number")
    if len(columns["close"]) < 2: # Checks that the dataset contains at least two days of prices
        raise ValueError(f"{path} needs at least two days of prices")

    bars = []
    notes = []
    previous_close = None
    # Combines price columns and loops through each day
    for day, values in enumerate(zip(columns["open"], columns["high"], columns["low"],
                                     columns["close"], columns["volume"])):
        bar = {}
        for name, value in zip(PRICE_COLUMNS, values):
            if value != value or value < 0: # Checks for missing or invalid negative values
                if previous_close is None:
                    raise ValueError(f"{path}: day {day} has no usable {name}")
                if name == "volume":
                    value = 0.0
                else:
                    value = previous_close   # Replaces missing prices with the previous day's closing price
                notes.append(f"day {day}: missing {name} filled in")
            bar[name] = float(value)
        bars.append(bar)
        previous_close = bar["close"]
    return bars, notes


def load_news(path):  # Loads news headlines from a text file
    news = {}
    notes = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line == "" or line.startswith("day"):
            continue
        parts = line.split(",", 1)
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


def load_market(ticker): # Loads stock prices and news for a market
    ticker = ticker.strip().upper()
    if ticker == "":
        return None, "no ticker typed"
    path = find_price(ticker)
    if path == "":
        return None, (f"no price file {ticker}.csv in {', '.join(DATA_FOLDERS)} -- check "
                      "the spelling, and that the data folder sits beside desk.py "
                      "(the folder you run the program from)")
    try:
        bars, notes = load_prices(path)
    except ValueError as error:
        return None, str(error)

    news_path = path[:-4] + "_news.txt"
    try:
        news, news_notes = load_news(news_path)
        notes = notes + news_notes
        news_found = True
    except FileNotFoundError:
        news = {}
        news_found = False
        notes.append(f"no news file {news_path}: the market loads without headlines")

    name = ticker.split("/")[-1]
    market = Market(name, bars, news, news_found, notes)
    return market, f"Loaded {market}."


def load_word_list(path=WORD_LIST_FILE): # Loads sentiment words and their scores from a CSV file
    scores = {}
    try:
        for line in open(path, encoding="utf-8"):
            if line.startswith("word"):
                continue
            parts = line.strip().split(",")
            if len(parts) == 2:
                scores[parts[0]] = float(parts[1])
    except (FileNotFoundError, ValueError):
        return {}
    return scores


def headline_score(headlines, word_scores): # Adds up the sentiment score of a day's headlines
    score = 0.0
    for headline in headlines:
        for word in headline.lower().replace(":", " ").split():
            score += word_scores.get(word, 0.0)
    return score
