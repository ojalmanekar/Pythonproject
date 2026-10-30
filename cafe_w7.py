# cafe_w7.py -- "The Daily Grind", the Week 7 refactor (OOP).
#
# The Week-6 register's sale engine (cafe_w6b.complete_sale), reorganized around the THINGS
# in the problem:
#   - MenuItem (with Drink / Pastry subclasses)  -- inheritance + an abstract method
#   - Order                                       -- what a customer is buying
#   - Register                                    -- the AUTHORITATIVE register: owns the cash and
#                                                    the stock, validates every sale, accepts
#                                                    or rejects it. Nothing else may touch the
#                                                    money directly (name-mangled __cash/__stock).
#   - Cafe                                         -- ties it together.
#
# "Same money, same stock" is not a promise, it is a TEST: check_refactor.py runs the same
# orders through cafe_w6b.py's complete_sale and this file and asserts identical revenue and
# stock. A refactor that changes results is a bug, not a refactor.
#
# >>> THE PARALLEL TO YOUR PROJECT <<<
# The Register is the same shape as the trading project's authoritative account: one object
# owns the balances, everyone else must go through its accept/reject method. Learn the PATTERN
# here (authoritative validator + accept/reject reply); apply it to the agent contract yourself.
#
# OOP tools used are exactly the Week-7 set: class/__init__/self, inheritance via
# Base.__init__(self, ...) (not super()), an abstract method via raise NotImplementedError
# (not abc), name-mangled __private with get_ methods, and __str__.
#
# Run it:  python3 cafe_w7.py   (it needs no other file; week 8's cafe_w8.py imports it)

DISCOUNT_THRESHOLD = 10.0
DISCOUNT_RATE = 0.10


# --------------------------------------------------------------------------------------
# Menu items: a base class + two subclasses.
# --------------------------------------------------------------------------------------
class MenuItem:
    def __init__(self, name, price=0.0):
        self.name = name
        # Coerce here so MenuItem("tea", "2.2") works, the same move set_price makes below.
        # set_price ALSO validates; a constructor has nothing yet to protect.
        self.price = float(price)

    def set_price(self, new_price):
        """Change the price -- but never to a negative. The object protects itself."""
        new_price = float(new_price)     # coerce first ("3.5" is fine), THEN validate
        if new_price >= 0.0:
            self.price = new_price

    def kind(self):
        """What sort of item this is. Subclasses must say; the base refuses."""
        raise NotImplementedError("every MenuItem subclass must define kind()")

    def __str__(self):
        return f"{self.name} ({self.kind()}, {self.price:.2f})"


class Drink(MenuItem):
    def __init__(self, name, price):
        # We call the base constructor by name, MenuItem.__init__, not super(). This course
        # sticks to the explicit form; super() is the same idea -- you will meet it out in
        # the wild, so recognize it, we just do not require it.
        MenuItem.__init__(self, name, price)

    def kind(self):
        return "drink"


class Pastry(MenuItem):
    def __init__(self, name, price):
        MenuItem.__init__(self, name, price)

    def kind(self):
        return "pastry"


# --------------------------------------------------------------------------------------
# An order: a list of (item, quantity) lines.
# --------------------------------------------------------------------------------------
class Order:
    def __init__(self):
        self.lines = []

    def add(self, item, quantity):
        self.lines.append((item, quantity))

    def total(self):
        total = 0.0
        for item, quantity in self.lines:
            total = total + item.price * quantity
        return total

    def __str__(self):
        return f"Order of {len(self.lines)} line(s), total {self.total():.2f}"


# --------------------------------------------------------------------------------------
# The authoritative register. It OWNS the cash and the stock; it is the single source of truth.
# --------------------------------------------------------------------------------------
class Register:
    def __init__(self, cash, stock):
        self.__cash = cash          # name-mangled: outsiders cannot touch the money directly
        self.__stock = stock        # dict: item name -> units available

    def get_cash(self):
        return self.__cash

    def get_stock(self, name):
        return self.__stock.get(name, 0)

    def sell(self, order):
        """Try to complete a sale. Validate first; only then move stock and money.

        Returns (accepted, message). On rejection the message names the reason, the same
        idea as the trading account's reject reply that its agent must read and react to.
        """
        # Validate the whole order before changing anything.
        for item, quantity in order.lines:
            have = self.__stock.get(item.name, 0)
            if have < quantity:
                return (False, "REJECT stock: " + item.name + " " + str(have))

        # Accepted: take the stock, apply the discount, take the money.
        for item, quantity in order.lines:
            self.__stock[item.name] = self.__stock[item.name] - quantity
        paid = order.total()
        if paid > DISCOUNT_THRESHOLD:
            paid = paid * (1.0 - DISCOUNT_RATE)
        self.__cash = self.__cash + paid
        return (True, f"ACCEPT paid {paid:.2f}")

    # The TRY IT on page 40, typed live once the room has tried it: a method, since only
    # code inside the class can reach __stock, and a guard, as set_price has. The owner
    # calls it when a delivery comes in: register.restock("muffin", 5).
    def restock(self, name, quantity):
        """Add `quantity` units of `name` back into stock."""
        if quantity > 0:
            self.__stock[name] = self.__stock.get(name, 0) + quantity


# --------------------------------------------------------------------------------------
# The cafe: knows the menu, owns a register, serves customers.
# --------------------------------------------------------------------------------------
class Cafe:
    def __init__(self, cash):
        self.menu = {
            "espresso": Drink("espresso", 2.50),
            "latte": Drink("latte", 3.20),
            "cappuccino": Drink("cappuccino", 3.00),
            "tea": Drink("tea", 2.20),
            "croissant": Pastry("croissant", 2.80),
            "muffin": Pastry("muffin", 2.40),
        }
        stock = {"espresso": 50, "latte": 50, "cappuccino": 40,
                 "croissant": 20, "muffin": 15, "tea": 30}
        self.register = Register(cash, stock)

    def build_order(self, requests):
        """Turn a list of (name, quantity) requests into an Order of real menu items."""
        order = Order()
        for name, quantity in requests:
            order.add(self.menu[name], quantity)
        return order

    def serve(self, requests):
        # Reject the whole order if any item is not on the menu -- exactly like Week 6's
        # complete_sale "we don't sell X" rule. (Money and stock must match: check_refactor.py.)
        for name, quantity in requests:
            if name not in self.menu:
                return (False, "REJECT unknown item: " + name)
        order = self.build_order(requests)
        return self.register.sell(order)


def main():
    cafe = Cafe(cash=0.0)
    print("The Daily Grind (OOP edition). Menu:")
    for name in cafe.menu:
        print("  " + str(cafe.menu[name]))          # uses MenuItem.__str__ -> kind()

    # A normal order.
    accepted, message = cafe.serve([("latte", 2), ("croissant", 1)])
    print("\nOrder 1 -> " + message)

    # An order we can't fulfill (only 15 muffins in stock).
    accepted, message = cafe.serve([("muffin", 999)])
    print("Order 2 -> " + message)

    # An order for something we don't sell -> rejected whole, like the Week-6 register.
    accepted, message = cafe.serve([("wine", 1)])
    print("Order 3 -> " + message)

    print(f"\nCash in the register: {cafe.register.get_cash():.2f}")
    print(f"Muffins left: {cafe.register.get_stock('muffin')}")


if __name__ == "__main__":
    main()
