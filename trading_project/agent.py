GROUP_CODE = "G19-CKWQ"

FEE = 0.001
MAX_INVEST_FRACTION = 0.70
MA_WINDOW = 10
DIP_NEEDED = 0.03
SAFETY_MARGIN = 1.02
STOP_LEVEL = 0.75
COOL_OFF_DAYS = 10
NO_BUY_LEVEL = 0.60

WORD_SCORES = {
    "Surge": 1, "rally": 1, "soar": 1, "gain": 1, "bullish": 1, "breakout": 1,
    "upgrade": 1, "beat": 1, "record": 1, "boom": 1, "jump": 1, "optimism": 1,
    "inflow": 1, "adoption": 1,
    "crash": -1, "plunge": -1, "slump": -1, "loss": -1, "bearish": -1, "selloff": -1,
    "downgrade": -1, "miss": -1, "fear": -1, "dump": -1, "drop": -1, "panic": -1,
    "outflow": -1, "ban": -1,
}


class TradingAgent:
    def __init__(self):
        self.closes = []
        self.last_price = None
        self.previous_cash = None
        self.previous_shares = None
        self.best_value = None
        self.cool_off_left = 0

    def decide(self, bar, headlines, cash, shares, last_responses):
        self.learn_price_from_fill(cash, shares)

        if bar is not None:
            self.closes.append(bar["close"])
            self.last_price = bar["close"]

        if headlines is not None:
            signal = self.news_signal(headlines)
        elif bar is not None:
            signal = self.price_signal()
        else:
            return ("HOLD", 0)

        if self.last_price is not None:
            value = cash + shares * self.last_price
            if self.best_value is None or value > self.best_value:
                self.best_value = value
            if shares > 0 and value < self.best_value * STOP_LEVEL:
                self.cool_off_left = COOL_OFF_DAYS
                return ("SELL", -1)

        if self.cool_off_left > 0:
            self.cool_off_left -= 1
            return ("HOLD", 0)

        if signal < 0 and shares > 0:
            return ("SELL", -1)
        if signal > 0 and shares == 0:
            return self.buy_order(cash)
        return ("HOLD", 0)

    def news_signal(self, headlines):
        score = 0
        for headline in headlines:
            words = headline.lower().replace(":", " ").replace(",", " ").split()
            score += sum(WORD_SCORES.get(word, 0) for word in words)

        if score > 0:
            return 1
        elif score < 0:
            return -1
        return 0

    def price_signal(self):
        average = self.moving_average(MA_WINDOW)
        if average is None:
            return 0

        distance = self.close[-1] / average - 1
        if distance <= -DIP_NEEDED:
            return 1
        elif distance > 0:
            return -1
        return 0

    def moving_average(self, window):
        if len(self.closes) < window:
            return None

        total = 0.0
        for price in self.closes[-window:]:
            total += price
        return total / window

    def buy_order(self, cash):
        if self.last_price is None:
            return ("BUY", 1)

        health = (cash / self.best_value) - NO_BUY_LEVEL / (1 - NO_BUY_LEVEL)
        health = min(1.0, max(0.0, health))
        money_to_use = cash * MAX_INVEST_FRACTION * health
        cost_per_share = self.last_price * (1 + FEE) * SAFETY_MARGIN
        count = int(money_to_use / cost_per_share)

        if count <= 0:
            return ("HOLD", 0)
        return ("BUY", count)

    def learn_price_from_fill(self, cash, shares):
        if self.previous_shares is not None:
            change = shares - self.previous_shares
            if change > 0:
                self.last_price = (self.previous_cash - cash) / (change * (1 + FEE))
            elif change < 0:
                self.last_price = (cash - self.previous_cash) / (-change * (1 - FEE))

        self.previous_cash = cash
        self.previous_shares = shares