# cafe_w4.py -- "The Daily Grind", the Week 4 version (grown from cafe_w3.py).
#
# Both Week-3 cliffhangers are paid today:
#   - price_of()'s if/elif chain is DEAD: the menu is a DICT (one lookup, grows for free);
#   - the order finally REMEMBERS its items: a LIST of (product, quantity) TUPLES -- so
#     Week 2's aligned receipt_line() is back, and the receipt lists every line again.
# Also new: per-product STOCK (a dict -- the muffin rush, generalized), REGULARS (a set),
# and the sentiment case study: a weighted lexicon (data/lexicon.txt -> dict) scores the
# customer reviews per product.
#
# Still deliberately fragile: type "three" as a quantity and the register DIES (ValueError) --
# and reading a file that might not exist would crash. Week 5 makes it unkillable.
#
# Run it from its own folder, register_sayings.py and data/ beside it:  python3 cafe_w4.py

import register_sayings

DATA_DIR = "data/"

# The menu: last week this was a 15-line if/elif chain. Now it is data.
MENU = {"espresso": 2.50, "latte": 3.20, "cappuccino": 3.00,
        "croissant": 2.80, "muffin": 2.40, "tea": 2.20}

DISCOUNT_THRESHOLD = 10.0
DISCOUNT_RATE = 0.10


def apply_discount(total):
    """Happy-hour rule: a percentage off orders over the threshold."""
    if total > DISCOUNT_THRESHOLD:
        return total * (1.0 - DISCOUNT_RATE)
    else:
        return total


def receipt_line(product, price, quantity):
    """One aligned receipt row (Week 2's function, back in service)."""
    return f"{product:<12} x {quantity:>2} {price * quantity:>8.2f}"


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
    reviews = open(DATA_DIR + "reviews.txt")
    reviews.readline()                   # the header line, read off and ignored
    for line in reviews:
        line = line.strip()
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
    reviews.close()
    averages = {}
    for product in totals:
        averages[product] = round(totals[product] / counts[product], 2)
    return averages


def take_order(stock, regulars):
    """Take one order: a LIST of (product, quantity) tuples -- the bill has a memory now."""
    name = input("  Customer name (ENTER to skip): ").strip().lower()
    if name != "":
        if name in regulars:
            print(f"    Welcome back, {name}!")
        else:
            regulars.add(name)

    order = []
    still_ordering = True
    while still_ordering:
        product = input("  Product (or 'done'): ").strip().lower()
        if product == "done":
            still_ordering = False
        elif product not in MENU:
            print("    Sorry, we don't sell that.")
        else:
            quantity = int(input("  Quantity: "))
            if quantity < 1 or stock[product] < quantity:
                print(f"    You can't buy {quantity} {product}(s): {stock[product]} left.")
            else:
                stock[product] = stock[product] - quantity
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
    return to_pay


def day_summary():
    """Read today's receipts back and total them (Week 3's for-loop)."""
    count = 0
    total = 0.0
    for line in open("receipts.txt"):
        line = line.strip()
        if line != "":
            count = count + 1
            total = total + float(line)
    print(f"  Orders today:  {count}")
    print(f"  Total revenue: {total:.2f}")


def save_receipt(amount):
    log = open("receipts.txt", "a")
    log.write(f"{amount:.2f}\n")
    log.close()


def save_revenue(revenue):
    f = open("revenue.txt", "w")
    f.write(f"{revenue:.2f}")
    f.close()


def main():
    open("receipts.txt", "w").close()      # start the day with an empty receipts file
    revenue = 0.0
    stock = {"espresso": 50, "latte": 50, "cappuccino": 40,
             "croissant": 20, "muffin": 15, "tea": 30}
    regulars = set()
    lexicon = load_lexicon()
    cashier = input("Cashier name: ")
    print(register_sayings.welcome(cashier))
    choice = ""
    while choice != "0":
        print("\n[1] Order  [2] Revenue  [3] Summary  [4] Reviews  [5] Stock  [0] Close")
        choice = input("Choose: ").strip()
        if choice == "1":
            paid = take_order(stock, regulars)
            revenue = revenue + paid
            save_receipt(paid)
        elif choice == "2":
            print(f"Revenue so far: {revenue:.2f}")
        elif choice == "3":
            day_summary()
            print(f"  Regulars today: {len(regulars)}")
        elif choice == "4":
            print(f"  Average review score per product: {review_scores(lexicon)}")
        elif choice == "5":
            print(f"  Stock: {stock}")
        elif choice == "0":
            save_revenue(revenue)
            print(f"Closed. Revenue for the day: {revenue:.2f}")
            print(register_sayings.goodbye)
        else:
            print("Please choose 1-5 or 0.")


if __name__ == "__main__":
    main()
