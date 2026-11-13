# account.py -- the AUTHORITATIVE account (the AUTHORITY side of the project).
#
# Week 7's Register, applied to the agent contract. One object owns the balances, and the
# only way to change them is its execute() method, which validates first and only then
# changes anything (week 5's "check before you mutate"). It answers every order with the
# exact reply strings of the agent contract:
#     "ACCEPT"
#     "REJECT currency balance: <cash>"    (a buy the cash cannot pay for)
#     "REJECT stock owned: <shares>"       (a sale of more shares than we hold)
#     "REJECT bad order: <why>"            (not an order at all: our desk's own extra)
# Like Register.sell, a refused order REPLIES instead of raising, and changes nothing.
#
# Encapsulation (week 7): the balances are name-mangled, __cash and __shares. There is a
# get_cash() and a get_shares(), and deliberately NO set_cash: money moves only through
# execute(), the one door with the rules on it.

# --- 1. imports --------------------------------------------------------------------------
# (none needed)

# --- 2. global constants ------------------------------------------------------------------
FEE = 0.001                          # 0.1% on every buy and every sell
ACTIONS = {"BUY", "SELL", "HOLD"}    # a set (week 4): we only ask "is it in there?"
DEFAULT_CASH = 10000.0
DEFAULT_SHARES = 0.0


# --- 3. class declaration -----------------------------------------------------------------
class Account:
    def __init__(self, cash=DEFAULT_CASH, shares=DEFAULT_SHARES):
        # Coerce first, then validate (week 7's set_price shape): "5000" becomes 5000.0.
        cash = float(cash)
        shares = float(shares)
        if cash < 0:
            cash = 0.0                # a constructor protects the invariant: never < 0
        if shares < 0:
            shares = 0.0
        self.__cash = cash            # name-mangled: outsiders cannot touch the money
        self.__shares = shares

    # ---- the getters: reading is allowed, writing is not ----------------------------
    def get_cash(self):
        return self.__cash

    def get_shares(self):
        return self.__shares

    def get_equity(self, price):
        """What the account is worth at this price: cash + shares * price."""
        return self.__cash + self.__shares * price

    def __str__(self):
        return f"cash {self.__cash:.2f} | shares {self.__shares:g}"

    # ---- the one door the money moves through ---------------------------------------
    def execute(self, order, price):
        """Carry out one order at this price; return the reply string.

        order is a tuple (action, amount). An amount of -1 means "as many as the cash
        covers" for BUY and "everything I hold" for SELL."""
        # Validate the order itself before anything else (week 5: check, THEN mutate).
        action, amount, problem = check_order(order)
        if problem != "":
            return "REJECT bad order: " + problem
        if action == "HOLD":
            return "ACCEPT"
        if action == "BUY":
            return self.__buy(amount, price)
        return self.__sell(amount, price)

    def __buy(self, amount, price):
        """Private helper (two underscores): only execute() may call it."""
        if amount < 0:
            # As many WHOLE shares as the cash covers after the fee, rounded down:
            # 500 cash at 25 -> 500 / 25.025 = 19.98 -> 19 shares (20 would cost 500.50).
            amount = int(self.__cash / (price * (1 + FEE)))
            if amount * price * (1 + FEE) > self.__cash:   # guard against rounding up
                amount = amount - 1
        if amount <= 0:
            return "ACCEPT"                          # nothing to buy is not an error
        cost = amount * price * (1 + FEE)
        if cost > self.__cash:
            return "REJECT currency balance: " + str(round(self.__cash, 2))
        # Accepted: only now do the balances move.
        self.__cash = self.__cash - cost
        self.__shares = self.__shares + amount
        assert self.__cash >= 0, "a buy broke the cash invariant"   # week 5's assert
        return "ACCEPT"

    def __sell(self, amount, price):
        if amount < 0:
            amount = self.__shares                   # -1 means sell everything
        if amount <= 0:
            return "ACCEPT"
        if amount > self.__shares:
            return "REJECT stock owned: " + str(round(self.__shares, 2))
        self.__cash = self.__cash + amount * price * (1 - FEE)
        self.__shares = self.__shares - amount
        assert self.__shares >= 0, "a sale broke the shares invariant"
        return "ACCEPT"


# --- 4. a plain function: is this a real order? ---------------------------------------------
def check_order(order):
    """Return (action, amount, problem); problem is "" when the order is fine.

    A reply, not a raise (week 5's "raise, or reply?"): the caller reads the answer and
    carries on. try/except ValueError and TypeError catch amounts that are not numbers."""
    try:
        action, amount = order                       # tuple unpacking (week 4)
    except (TypeError, ValueError):
        return ("", 0, "an order is a pair (action, amount), got " + str(order)[:40])
    if action not in ACTIONS:
        return ("", 0, "the action must be BUY, SELL or HOLD, got " + str(action)[:20])
    try:
        amount = float(amount)                       # coerce first, as set_price does
    except (TypeError, ValueError, OverflowError):
        return ("", 0, "the amount must be a number, got " + str(amount)[:20])
    if amount != amount or abs(amount) == float("inf"):   # NaN is the one value != itself
        return ("", 0, "the amount must be a finite number")
    if amount == int(amount):
        amount = int(amount)                         # 5.0 shares is 5 shares
    return (action, amount, "")
