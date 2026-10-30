# cafe_w6b.py -- "The Daily Grind", the Week 6 Friday version (grown from cafe_w6a.py).
#
# This week the register learns ANALYTICS -- with pandas:
#   - [8] Sales report: read the whole term's transactions.csv (the words survive
#     now!), total revenue per product, and save the chart (sales_by_product.png);
#   - plus the midweek "tidy-up experiment": order_total() + complete_sale() -- the
#     register's sale, extracted into ONE authoritative function (validate first, then
#     mutate). Wiring it into take_order() would mean reworking half this file...
#     which is exactly Week 7's lecture: refactor the register into classes.
#     check_refactor.py proves the Week-7 classes move the same money and stock as it.
#
# Since Week 6, typing menu at the product prompt lists each product, its price and what
# is left: a feature asked for in Week 4.
#
# Run it from its own folder, register_sayings.py and data/ beside it:  python3 cafe_w6b.py

# --- 1. imports ------------------------------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import register_sayings

# --- 2. global constants (data structures stay inside main -- avoid globals!) -----------
DATA_DIR = "data/"

MENU = {"espresso": 2.50, "latte": 3.20, "cappuccino": 3.00,
        "croissant": 2.80, "muffin": 2.40, "tea": 2.20}

DISCOUNT_THRESHOLD = 10.0
DISCOUNT_RATE = 0.10

OPENING_HOUR = 8   # the first column of hourly_items.csv is the 08:00 hour
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


# --- 3. function declarations ------------------------------------------------------------
def apply_discount(total):
    """Happy-hour rule: a percentage off orders over the threshold."""
    if total > DISCOUNT_THRESHOLD:
        return total * (1.0 - DISCOUNT_RATE)
    else:
        return total


def receipt_line(product, price, quantity):
    """One aligned receipt row."""
    return f"{product:<12} x {quantity:>2} {price * quantity:>8.2f}"


def show_menu(stock):
    """The menu at the counter: each product, its price, and what is left today."""
    print(f"  {' Menu ':-^34}")
    for product in MENU:
        if stock[product] == 0:
            left = "sold out"
        else:
            left = f"{stock[product]} left"
        print(f"  {product:<12} {MENU[product]:>6.2f}   {left}")


def ask_quantity(product, available):
    """The unkillable prompt: keep asking until we get a valid, in-stock quantity."""
    while True:
        try:
            quantity = int(input("  Quantity: "))
        except ValueError:
            print("    That doesn't look like a number -- digits only, please.")
            continue                     # back to the top -- ask again
        if quantity < 1:
            print("    At least 1, please.")
        elif quantity > available:
            print(f"    Only {available} {product}(s) left.")
        else:
            return quantity


def load_revenue():
    """Read the running revenue, or start at 0.0 -- the Week-3 crash, finally handled."""
    try:
        f = open("revenue.txt")
        amount = float(f.readline())
        f.close()
        return amount
    except (FileNotFoundError, ValueError):
        return 0.0


def save_revenue(revenue):
    f = open("revenue.txt", "w")
    f.write(f"{revenue:.2f}")
    f.close()


def save_receipt(amount):
    log = open("receipts.txt", "a")
    log.write(f"{amount:.2f}\n")
    log.close()


def split_bill(total):
    """Offer to split the bill -- two different disasters, two different catches."""
    guests = input("  Split between how many? (ENTER to skip): ").strip()
    if guests == "":
        return
    try:
        print(f"  That is {total / int(guests):.2f} each.")
    except ZeroDivisionError:
        print("  You cannot split a bill between zero people...")
    except ValueError:
        print("  That does not look like a number of people.")


def take_order(stock, regulars):
    """Sell one customer an order, print the receipt, offer the split; return the bill."""
    name = input("  Customer name (ENTER to skip): ").strip().lower()
    if name != "":
        if name in regulars:
            print(f"    Welcome back, {name}!")
        else:
            regulars.add(name)

    order = []
    still_ordering = True
    while still_ordering:
        product = input("  Product ('menu' or 'done'): ").strip().lower()
        if product == "done":
            still_ordering = False
        elif product == "menu":
            show_menu(stock)
        elif product not in MENU:
            print("    Sorry, we don't sell that.")
        elif stock[product] == 0:               # sold out: asking would loop forever
            print(f"    Sorry, no {product}(s) left.")
        else:
            quantity = ask_quantity(product, stock[product])
            stock[product] = stock[product] - quantity
            assert stock[product] >= 0, "a sale broke the stock invariant"
            order.append((product, quantity))

    order_total = 0.0
    for product, quantity in order:
        order_total = order_total + MENU[product] * quantity
    to_pay = apply_discount(order_total)

    print(f"  {' The Daily Grind ':=^34}")
    for product, quantity in order:
        print("  " + receipt_line(product, MENU[product], quantity))
    print("  " + "=" * 34)
    if to_pay < order_total:
        print("  Happy-hour discount applied!")
    print(f"  {'TOTAL':<12}      {to_pay:>8.2f}   ({sum([q for p, q in order])} items)")
    split_bill(to_pay)
    return to_pay


def day_summary():
    """Read today's receipts back and total them -- safe even when the file is missing."""
    count = 0
    total = 0.0
    try:
        for line in open("receipts.txt"):
            line = line.strip()
            if line != "":
                count = count + 1
                total = total + float(line)
    except FileNotFoundError:
        pass   # no receipts file -- that's fine, the zeros below tell the story
    print(f"  Orders today:  {count}")
    print(f"  Total revenue: {total:.2f}")


def load_lexicon():
    """Read the sentiment lexicon (word,weight per line) into a dict."""
    lexicon = {}
    for line in open(DATA_DIR + "lexicon.txt"):
        parts = line.strip().split(",")
        lexicon[parts[0]] = float(parts[1])
    return lexicon


def review_scores(lexicon):
    """Average weighted sentiment per product from data/reviews.txt."""
    totals = {}
    counts = {}
    is_header = True
    for line in open(DATA_DIR + "reviews.txt"):
        if is_header:
            is_header = False
            continue
        line = line.strip()
        if line == "":
            continue
        product, text = line.split(",", 1)
        score = 0.0
        for word in text.lower().split():
            if word in lexicon:
                score = score + lexicon[word]
        if product in totals:
            totals[product] = totals[product] + score
            counts[product] = counts[product] + 1
        else:
            totals[product] = score
            counts[product] = 1
    averages = {}
    for product in totals:
        averages[product] = round(totals[product] / counts[product], 2)
    return averages


def day_stats(order_totals):
    """Some quick numbers about a day's orders, with numpy."""
    values = np.array(order_totals)
    return {"orders": len(values), "revenue": round(float(values.sum()), 2),
            "biggest": round(float(values.max()), 2), "average": round(float(values.mean()), 2)}


def week_report():
    """Read the week's hourly-items grid and answer the owner's questions."""
    grid = np.genfromtxt(DATA_DIR + "hourly_items.csv", skip_header=1, delimiter=",")
    print(f"  Grid: {grid.shape[0]} days x {grid.shape[1]} hours")
    print(f"  Items sold this week: {grid.sum():.0f}")
    # One COLUMN per hour: grid[:, hour] is that hour across all five days.
    # (grid.T would flip the grid so hours become rows -- same numbers.)
    hour_totals = np.array([grid[:, hour].sum() for hour in range(grid.shape[1])])
    busiest = hour_totals.argmax()
    print(f"  Busiest hour: {OPENING_HOUR + busiest}:00 ({hour_totals[busiest]:.0f} items)")
    # One ROW per day: grid[day] is that whole day.
    day_totals = np.array([grid[day].sum() for day in range(len(grid))])
    print(f"  Biggest day:  {DAYS[day_totals.argmax()]} ({day_totals.max():.0f} items)")


def sales_report(save_path=None):
    """Load the term's transactions with pandas, total revenue per product, plot it."""
    data = pd.read_csv(DATA_DIR + "transactions.csv")
    data["revenue"] = data["qty"] * data["price"]
    by_product = data.groupby("product")["revenue"].sum().sort_index()
    plt.figure()
    by_product.plot(kind="bar")
    plt.title("Revenue by product")
    plt.ylabel("euros")
    plt.tight_layout()                # make the rotated labels fit
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        plt.close()
    return by_product


# --- the midweek tidy-up experiment ----------------------------------------------------
# The sale, extracted into ONE authoritative function: validate everything FIRST, only
# then touch the stock and the money. Wiring this into take_order() means reworking most
# of this file -- the program is fighting its own shape. Week 7 refactors the register into
# classes; complete_sale() is what becomes Register.sell(...), and check_refactor.py
# proves the class version moves the same money and stock as this one.
def order_total(order):
    """Total price of an order. `order` is a list of (product, quantity) tuples."""
    total = 0.0
    for product, quantity in order:
        total = total + MENU[product] * quantity
    return total


def complete_sale(order, stock, cash):
    """Try to complete a sale. This is the AUTHORITATIVE step: it checks stock, and either
    accepts (updating stock and cash) or rejects with a reason.

    Returns (accepted, message, new_cash). (In Week 7 this becomes Register.sell(...).)
    An order with ANY unknown or under-stocked item is rejected whole -- nothing changes.
    One hole, kept on purpose: each line is checked on its own, so one product on two
    lines can slip past. Real registers add the lines up first (Week 7 names it).
    """
    # First, validate: is every item real and in stock? (Week 5: check before you mutate.)
    for product, quantity in order:
        if product not in stock:
            return (False, "we don't sell " + product, cash)
        if stock[product] < quantity:
            return (False, "not enough " + product + " (have " + str(stock[product]) + ")", cash)

    # Accepted: take the stock and the money.
    for product, quantity in order:
        stock[product] = stock[product] - quantity
    paid = apply_discount(order_total(order))
    cash = cash + paid
    return (True, f"paid {paid:.2f}", cash)


# --- 4. main code --------------------------------------------------------------------
def main():
    open("receipts.txt", "w").close()      # start the day with an empty receipts file
    revenue = load_revenue()          # yesterday's money survives -- at last
    stock = {"espresso": 50, "latte": 50, "cappuccino": 40,
             "croissant": 20, "muffin": 15, "tea": 30}
    regulars = set()
    lexicon = load_lexicon()
    order_totals = []                 # this week's new memory: every order of the day
    cashier = input("Cashier name: ")
    print(register_sayings.welcome(cashier))
    print(f"Carried over from yesterday: {revenue:.2f}")
    choice = ""
    while choice != "0":
        print("\n[1] Order  [2] Revenue  [3] Summary  [4] Reviews  [5] Stock" +
              "  [6] Day stats  [7] Week report  [8] Sales report  [0] Close")
        choice = input("Choose: ").strip()
        if choice == "1":
            paid = take_order(stock, regulars)
            revenue = revenue + paid
            order_totals.append(paid)
            save_receipt(paid)
        elif choice == "2":
            print(f"Revenue (all time): {revenue:.2f}")
        elif choice == "3":
            day_summary()
            print(f"  Regulars today: {len(regulars)}")
        elif choice == "4":
            print(f"  Average review score per product: {review_scores(lexicon)}")
        elif choice == "5":
            print(f"  Stock: {stock}")
        elif choice == "6":
            if order_totals == []:
                print("  No orders yet today.")
            else:
                print(f"  Today so far: {day_stats(order_totals)}")
        elif choice == "7":
            week_report()
        elif choice == "8":
            sales_report(save_path="sales_by_product.png")
            print("  Saved the revenue-by-product chart to sales_by_product.png")
        elif choice == "0":
            save_revenue(revenue)
            print(f"Closed. Revenue on file: {revenue:.2f}")
            print(register_sayings.goodbye)
        else:
            print("Please choose 1-8 or 0.")


if __name__ == "__main__":
    main()
