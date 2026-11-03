# account.py -- the Account: the one place where money and shares change.
#
# This is the "authority" side of the project (the agent is the "thinking" side). Every
# order, typed by hand at the desk or returned by the agent, goes through execute(), which
# checks it, charges the 0.1% fee and answers with the exact strings of the agent
# contract: "ACCEPT", "REJECT currency balance: <cash>" or "REJECT stock owned: <shares>".
# An order fills whole or not at all, and a rejected order changes nothing.

import math
import numbers

FEE = 0.001     # 0.1% charged on every buy and every sell


class OrderError(Exception):
    """An order that is not an order at all: a wrong action, or an amount that is not a
    finite number. Raised so the desk can show a clear message."""


class Account:
    """Cash and shares, kept private behind methods (encapsulation): nothing outside this
    class writes to _cash or _shares directly."""

    def __init__(self, cash=10000.0, shares=0.0):
        if cash < 0 or shares < 0:
            raise ValueError("starting cash and shares cannot be negative")
        self._cash = float(cash)
        self._shares = float(shares)

    # Read-only views of the balances.
    @property
    def cash(self):
        return self._cash

    @property
    def shares(self):
        return self._shares

    def equity(self, price):
        """What the account is worth at this price: cash + shares * price."""
        return self._cash + self._shares * price

    def __str__(self):
        return "cash " + str(round(self._cash, 2)) + " | shares " + str(round(self._shares, 2))

    # -----------------------------------------------------------------------------------
    def execute(self, order, price):
        """Carry out one order at this price and return the reply string.

        order is a tuple (action, amount); amount -1 (or any negative) means "as many as
        possible" for BUY and "everything" for SELL."""
        action, amount = check_order(order)
        if action == "HOLD":
            return "ACCEPT"
        if action == "BUY":
            return self._buy(amount, price)
        return self._sell(amount, price)

    def _buy(self, amount, price):
        if amount < 0:
            # As many whole shares as the cash covers after the fee, rounded DOWN:
            # $500 at $25 -> 500 / 25.025 = 19.98 -> 19 shares (20 would cost 500.50).
            amount = int(self._cash / (price * (1 + FEE)))
            if amount * price * (1 + FEE) > self._cash:   # guard against rounding up
                amount = amount - 1
        if amount <= 0:
            return "ACCEPT"                           # nothing to buy: not an error
        cost = amount * price * (1 + FEE)
        if cost > self._cash:
            return "REJECT currency balance: " + str(round(self._cash, 2))
        self._cash = self._cash - cost
        self._shares = self._shares + amount
        return "ACCEPT"

    def _sell(self, amount, price):
        if amount < 0:
            amount = self._shares                     # -1 means sell everything
        if amount <= 0:
            return "ACCEPT"
        if amount > self._shares:
            return "REJECT stock owned: " + str(round(self._shares, 2))
        self._cash = self._cash + amount * price * (1 - FEE)
        self._shares = self._shares - amount
        return "ACCEPT"


def check_order(order):
    """Return (action, amount) as plain Python values, or raise OrderError.

    A count worked out with numpy (np.int64) is a real number and is accepted; NaN,
    infinity, text and a wrong action are not."""
    if not isinstance(order, (tuple, list)) or len(order) != 2:
        raise OrderError("an order must be (action, amount), got " + repr(order)[:60])
    action = order[0]
    amount = order[1]
    if action not in ("BUY", "SELL", "HOLD"):
        raise OrderError("the action must be BUY, SELL or HOLD, got " + repr(action)[:30])
    if isinstance(amount, bool) or not isinstance(amount, numbers.Real):
        raise OrderError("the amount must be a number, got " + repr(amount)[:30])
    try:
        finite = math.isfinite(amount)
    except OverflowError:
        finite = False
    if not finite:
        raise OrderError("the amount must be a finite number, got " + repr(amount)[:30])
    if isinstance(amount, numbers.Integral):
        return action, int(amount)
    return action, float(amount)
