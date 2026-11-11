# agent.py -- our group's trading agent (the THINKING side of the project).
#
# What it trades on, in two sentences (the interview question):
#   When it can read the news, it scores today's headlines with the word list (the week-4
#   review-scoring pattern) and buys on good news, sells on bad news. When it sees only
#   prices, it buys after a dip of 3% below the 10-day moving average and sells once the
#   price is back above that average.
#
# How it stays safe: at most 70% of its money in shares, smaller buys after losses, and if
# its money falls 25% below its best it sells everything and waits 10 days.
#
# Rules this file keeps (agent contract, project document 03):
#   - it imports NOTHING (numpy, pandas, math and random would be allowed; we need none);
#   - it reads no file: the word list is typed in below as a dict;
#   - it uses no randomness, so the same data always gives the same result;
#   - decide() copes with bar = None (news-only run) and headlines = None (price-only run);
#   - it never touches the money: it only PROPOSES an order. The desk's Account (or the
#     competition) owns the cash and shares and answers ACCEPT or REJECT -- week 7's
#     authoritative Register pattern, seen from the customer's side.

# --- 1. imports --------------------------------------------------------------------------
# (none: agent.py must stand alone)

# --- 2. global constants ------------------------------------------------------------------
GROUP_CODE = "GXX-XXXX"       # <- replace with your group's code from the code email
# Group: <every member's full name, separated by commas>
# Reference: <the full name of this file's reference member>

# Every number the strategy uses is a CONSTANT in capitals (week 2's rule): a live edit at
# the interview ("use a 20-day average") is then a one-line change.
FEE = 0.001                 # the desk charges 0.1% on every buy and every sell
FRACTION_IN_SHARES = 0.70   # at most 70% of our money goes into shares
MA_WINDOW = 10              # the moving average looks at the last 10 closes
DIP_NEEDED = 0.03           # a "dip" is a close 3% or more below that average
SAFETY_MARGIN = 1.02        # size buys as if the price were 2% higher: we fill TOMORROW
STOP_LEVEL = 0.75           # sell everything if our money falls below 75% of its best
COOL_OFF_DAYS = 10          # after that stop, wait this many days before buying again
NO_BUY_LEVEL = 0.60         # below 60% of our best value we stop buying altogether

# The lexicon from sentiment_words.csv, typed in as a dict because agent.py may not read
# files. +1 good word, -1 bad word; the neutral words score 0, so they are left out and
# WORD_SCORES.get(word, 0) gives them 0 anyway (week 4's .get with a default).
WORD_SCORES = {
    "surge": 1, "rally": 1, "soar": 1, "gain": 1, "bullish": 1, "breakout": 1,
    "upgrade": 1, "beat": 1, "record": 1, "boom": 1, "jump": 1, "optimism": 1,
    "inflow": 1, "adoption": 1,
    "crash": -1, "plunge": -1, "slump": -1, "loss": -1, "bearish": -1, "selloff": -1,
    "downgrade": -1, "miss": -1, "fear": -1, "dump": -1, "drop": -1, "panic": -1,
    "outflow": -1, "ban": -1,
}


# --- 3. class declaration -----------------------------------------------------------------
class TradingAgent:
    """Reads one day at a time and answers with one order: ("BUY"|"SELL"|"HOLD", amount)."""

    def __init__(self):
        # The competition builds the agent as TradingAgent(), with no arguments. Every
        # attribute is created here, even as a placeholder (week 7's good practice), so a
        # reader finds all the agent's memory in one place.
        self.closes = []            # every closing price seen so far: our own history
        self.last_price = None      # the most recent price we know (None = none yet)
        self.previous_cash = None   # yesterday's balances, to work out a fill price
        self.previous_shares = None  # in the news-only run, where no bar arrives
        self.best_value = None      # the highest value our money has reached
        self.cool_off_left = 0      # days still to wait after the stop sold everything

    def __str__(self):
        return f"TradingAgent ({len(self.closes)} closes seen, best value {self.best_value})"

    # ---- the one method the contract requires ---------------------------------------
    def decide(self, bar, headlines, cash, shares, last_response):
        """Called once per trading day. Returns one order (action, amount)."""
        # 1. Remember what today tells us about the price.
        self.learn_price_from_fill(cash, shares)
        if bar is not None:
            self.closes.append(bar["close"])
            self.last_price = bar["close"]

        # 2. Today's signal: +1 "be in shares", -1 "be out", 0 "no view".
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

        # 4. Act: sell everything on a bad signal, buy on a good one, else hold.
        if signal < 0 and shares > 0:
            return ("SELL", -1)
        if signal > 0 and shares == 0:
            return self.buy_order(cash)
        return ("HOLD", 0)

    # ---- the two signals ------------------------------------------------------------
    def news_signal(self, headlines):
        """+1 if today's headlines hold more good words than bad, -1 if more bad, else 0.

        The week-4 review-scoring pattern: clean the text (lower, the colon off), split it
        into words, look each word up in the score dict and add the scores up."""
        score = 0
        for headline in headlines:
            words = headline.lower().replace(":", " ").replace(",", " ").split()
            score = score + sum([WORD_SCORES.get(word, 0) for word in words])
        if score > 0:
            return 1
        elif score < 0:
            return -1
        else:
            return 0

    def price_signal(self):
        """+1 after a dip of DIP_NEEDED below the moving average, -1 once above it, else 0.

        Our training markets tend to bounce back after a fall, so we buy weakness and sell
        once the price has recovered to its average."""
        average = self.moving_average(MA_WINDOW)
        if average is None:
            return 0                                  # fewer than 10 closes so far
        distance = self.closes[-1] / average - 1     # -0.04 means 4% below the average
        if distance <= -DIP_NEEDED:
            return 1
        elif distance > 0:
            return -1
        else:
            return 0

    def moving_average(self, window):
        """The mean of the last `window` closes, built by hand: a slice and a loop, no
        pandas .rolling (the library policy's method-level rule)."""
        if len(self.closes) < window:
            return None
        total = 0.0
        for price in self.closes[-window:]:
            total = total + price
        return total / window

    # ---- sizing a buy ---------------------------------------------------------------
    def buy_order(self, cash):
        """A buy of at most FRACTION_IN_SHARES of our money, smaller after losses."""
        if self.last_price is None:
            # News-only run, first buy: we have never seen a price, so buy ONE share.
            # Tomorrow the change in our cash tells us what a share costs.
            return ("BUY", 1)
        # health: 1.0 at our best value, falling to 0.0 at NO_BUY_LEVEL of it.
        health = (cash / self.best_value - NO_BUY_LEVEL) / (1 - NO_BUY_LEVEL)
        health = min(1.0, max(0.0, health))
        money_to_use = FRACTION_IN_SHARES * health * cash
        cost_per_share = self.last_price * (1 + FEE) * SAFETY_MARGIN
        count = int(money_to_use / cost_per_share)    # whole shares, rounded DOWN
        if count <= 0:
            return ("HOLD", 0)
        return ("BUY", count)

    def learn_price_from_fill(self, cash, shares):
        """In the news-only run no bar arrives, so we work the price out of our last fill.

        Yesterday 0 shares and 9500.00 cash, today 5 shares and 8999.50 cash: the fill cost
        500.50 for 5 shares, fee included, so the price was 500.50 / (5 * 1.001) = 100.00."""
        if self.previous_shares is not None:
            change = shares - self.previous_shares
            if change > 0:
                self.last_price = (self.previous_cash - cash) / (change * (1 + FEE))
            elif change < 0:
                self.last_price = (cash - self.previous_cash) / (-change * (1 - FEE))
        self.previous_cash = cash
        self.previous_shares = shares
