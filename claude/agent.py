# agent.py -- our group's trading agent for the MIS41110 competition.
#
# WHAT IT TRADES ON (the two-sentence answer for the interview):
#   When it can read the news, it counts good and bad words in today's headlines and buys
#   when the news is good and sells when it is bad. When it can only see prices, it buys
#   after the price has dipped well below its 10-day moving average and sells once the
#   price is back above that average.
#
# HOW IT STAYS SAFE (why it does not "fall to half its best"):
#   * it never puts more than 70% of its money into shares (FRACTION_IN_SHARES);
#   * the further its money falls below its best value so far, the smaller it buys;
#   * if its money falls 25% below its best, it sells everything and waits 10 days.
#
# RULES THIS FILE FOLLOWS (project document 03):
#   * it imports nothing at all (only numpy/pandas/math/random would be allowed);
#   * it reads no files and asks for no input: the word list is written inside the file;
#   * it is deterministic: no randomness, so the same data always gives the same result;
#   * it never crashes when bar or headlines is None (the three competition regimes);
#   * it always returns a well-formed order: ("BUY", n), ("SELL", n) or ("HOLD", 0).

GROUP_CODE = "GXX-XXXX"       # <- replace with your group's code from the code email
# Group: <every member's full name, separated by commas>
# Reference: <the full name of this file's reference member>


# ---------------------------------------------------------------------------------------
# Settings. Every number the strategy uses lives here, so a live edit at the interview
# ("hold whenever cash is under 100", "use a 20-day average") is a one-line change.
# ---------------------------------------------------------------------------------------
FEE = 0.001                 # the desk charges 0.1% on every buy and every sell
FRACTION_IN_SHARES = 0.70   # at most 70% of our money goes into shares
MA_WINDOW = 10              # the moving average looks at the last 10 closing prices
DIP_NEEDED = 0.03           # "a dip" means the close is 3% or more below that average
SAFETY_MARGIN = 1.02        # size buys as if the price were 2% higher (we fill tomorrow)
STOP_LEVEL = 0.75           # sell everything if our money falls below 75% of its best
COOL_OFF_DAYS = 10          # after that stop, wait this many days before buying again
NO_BUY_LEVEL = 0.60         # below 60% of our best value we stop buying altogether

# The sentiment lexicon from sentiment_words.csv, written into the file because agent.py
# may not read files. +1 for a good word, -1 for a bad word; neutral words are left out
# because they add 0 to the score anyway.
WORD_SCORES = {
    "surge": 1, "rally": 1, "soar": 1, "gain": 1, "bullish": 1, "breakout": 1,
    "upgrade": 1, "beat": 1, "record": 1, "boom": 1, "jump": 1, "optimism": 1,
    "inflow": 1, "adoption": 1,
    "crash": -1, "plunge": -1, "slump": -1, "loss": -1, "bearish": -1, "selloff": -1,
    "downgrade": -1, "miss": -1, "fear": -1, "dump": -1, "drop": -1, "panic": -1,
    "outflow": -1, "ban": -1,
}


class TradingAgent:
    """Reads one day at a time and answers with one order (the "thinking" side).

    It never changes cash or shares itself: the desk (or the competition) owns the money
    and only tells the agent the truth through the cash and shares arguments."""

    def __init__(self):
        # The competition builds the agent as TradingAgent() with no arguments, so the
        # constructor takes none. Everything the agent must remember lives on self.
        self.closes = []            # every closing price seen so far (our own history)
        self.last_price = None      # the most recent price we know, or None
        self.previous_cash = None   # cash and shares at the previous call, used to work
        self.previous_shares = None  # out a fill price in the news-only run
        self.best_value = None      # the highest value our money has reached so far
        self.cool_off_left = 0      # days still to wait after the stop sold everything

    # -----------------------------------------------------------------------------------
    # The one method the contract requires.
    # -----------------------------------------------------------------------------------
    def decide(self, bar, headlines, cash, shares, last_response):
        """Called once per trading day. Returns one order: (action, amount)."""
        # 1. Remember what today tells us about the price.
        self.learn_price_from_fill(cash, shares)
        if bar is not None:
            self.closes.append(bar["close"])
            self.last_price = bar["close"]

        # 2. Work out today's signal: +1 means "be in shares", -1 "be out", 0 "no view".
        if headlines is not None:
            signal = self.news_signal(headlines)      # news-only and price+news runs
        elif bar is not None:
            signal = self.price_signal()              # price-only run
        else:
            return ("HOLD", 0)                        # nothing to read at all

        # 3. Safety first: the stop, then the cool-off that follows it.
        if self.last_price is not None:
            value = cash + shares * self.last_price
            if self.best_value is None or value > self.best_value:
                self.best_value = value
            if shares > 0 and value < STOP_LEVEL * self.best_value:
                self.cool_off_left = COOL_OFF_DAYS
                return ("SELL", -1)
        if self.cool_off_left > 0:
            self.cool_off_left = self.cool_off_left - 1
            return ("HOLD", 0)

        # 4. Act on the signal: sell everything on a bad signal, buy on a good one.
        if signal < 0 and shares > 0:
            return ("SELL", -1)
        if signal > 0 and shares == 0:
            return self.buy_order(cash)
        return ("HOLD", 0)

    # -----------------------------------------------------------------------------------
    # The two signals.
    # -----------------------------------------------------------------------------------
    def news_signal(self, headlines):
        """+1 if today's headlines hold more good words than bad, -1 if more bad, else 0.

        This is the week-4 review-scoring pattern: split each headline into words, look
        each word up in the score dict, add the scores up."""
        score = 0
        for headline in headlines:
            # "report token: QBIT set to bearish" -> the colon must not stick to a word
            cleaned = headline.lower().replace(":", " ").replace(",", " ")
            for word in cleaned.split():
                score = score + WORD_SCORES.get(word, 0)
        if score > 0:
            return 1
        if score < 0:
            return -1
        return 0

    def price_signal(self):
        """+1 after a dip of DIP_NEEDED below the moving average, -1 above the average.

        Our training markets tend to bounce back after a drop (the price "mean reverts"),
        so we buy weakness and sell once the price has recovered to its average."""
        average = self.moving_average(MA_WINDOW)
        if average is None:
            return 0                                   # not enough history yet
        distance = self.closes[-1] / average - 1      # e.g. -0.04 means 4% below
        if distance <= -DIP_NEEDED:
            return 1
        if distance > 0:
            return -1
        return 0

    def moving_average(self, window):
        """The mean of the last `window` closes, built by hand (no pandas .rolling)."""
        if len(self.closes) < window:
            return None
        total = 0.0
        for price in self.closes[-window:]:
            total = total + price
        return total / window

    # -----------------------------------------------------------------------------------
    # Sizing a buy.
    # -----------------------------------------------------------------------------------
    def buy_order(self, cash):
        """A buy of at most FRACTION_IN_SHARES of our money, smaller after losses."""
        if self.last_price is None:
            # News-only run, first buy: we have never seen a price, so we buy a single
            # share. Tomorrow the change in our cash tells us what one share costs.
            return ("BUY", 1)
        # How healthy are we? 1.0 at our best value, falling to 0.0 at NO_BUY_LEVEL.
        health = (cash / self.best_value - NO_BUY_LEVEL) / (1 - NO_BUY_LEVEL)
        if health > 1:
            health = 1
        if health < 0:
            health = 0
        money_to_use = FRACTION_IN_SHARES * health * cash
        cost_per_share = self.last_price * (1 + FEE) * SAFETY_MARGIN
        count = int(money_to_use / cost_per_share)    # whole shares, rounded down
        if count <= 0:
            return ("HOLD", 0)
        return ("BUY", count)

    def learn_price_from_fill(self, cash, shares):
        """In the news-only run there is no bar, so we work the price out of our last fill.

        If yesterday we held 0 shares and 9,500 cash, and today 5 shares and 9,000 cash,
        the fill cost 500 for 5 shares including the fee: price = 500 / (5 * 1.001)."""
        if self.previous_shares is not None:
            change = shares - self.previous_shares
            if change > 0:
                self.last_price = (self.previous_cash - cash) / (change * (1 + FEE))
            elif change < 0:
                self.last_price = (cash - self.previous_cash) / (-change * (1 - FEE))
        self.previous_cash = cash
        self.previous_shares = shares
