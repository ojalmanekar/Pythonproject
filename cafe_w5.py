# cafe_w5.py -- "The Daily Grind", the Week 5 version (grown from cafe_w4.py).
#
# This week the register becomes UNKILLABLE:
#   - type "three" as a quantity -> caught (try/except ValueError), ask again;
#   - first morning, no revenue.txt -> caught (FileNotFoundError), start at 0.0
#     (the crash we met in Week 3, finally fixed -- revenue now survives BETWEEN days);
#   - split the bill between guests -> ZeroDivisionError AND ValueError, both caught;
#   - an assert guards the invariant a sale must never break (stock >= 0).
#
# The file also SHOWS the canonical program structure from the lecture:
#   1. imports  2. global constants  3. function declarations  4. main code (guarded).
#
# Run it from its own folder, register_sayings.py and data/ beside it:  python3 cafe_w5.py

# --- 1. imports ------------------------------------------------------------------------
import register_sayings

# --- 2. global constants (data structures stay inside main -- avoid globals!) -----------
DATA_DIR = "data/"

MENU = {"espresso": 2.50, "latte": 3.20, "cappuccino": 3.00,
        "croissant": 2.80, "muffin": 2.40, "tea": 2.20}

DISCOUNT_THRESHOLD = 10.0
DISCOUNT_RATE = 0.10


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
    """Read the running revenue, or start at 0.0 -- the Week-3 crash, handled."""
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
        product = input("  Product (or 'done'): ").strip().lower()
        if product == "done":
            still_ordering = False
        elif product not in MENU:
            print("    Sorry, we don't sell that.")
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
    # Week 4 read the header off with readline(); this is the same job done with this
    # week's new word: continue skips straight to the loop's next pass.
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


# --- 4. main code --------------------------------------------------------------------
def main():
    open("receipts.txt", "w").close()      # start the day with an empty receipts file
    revenue = load_revenue()          # yesterday's money survives -- at last
    stock = {"espresso": 50, "latte": 50, "cappuccino": 40,
             "croissant": 20, "muffin": 15, "tea": 30}
    regulars = set()
    lexicon = load_lexicon()
    cashier = input("Cashier name: ")
    print(register_sayings.welcome(cashier))
    print(f"Carried over from yesterday: {revenue:.2f}")
    choice = ""
    while choice != "0":
        print("\n[1] Order  [2] Revenue  [3] Summary  [4] Reviews  [5] Stock  [0] Close")
        choice = input("Choose: ").strip()
        if choice == "1":
            paid = take_order(stock, regulars)
            revenue = revenue + paid
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
        elif choice == "0":
            save_revenue(revenue)
            print(f"Closed. Revenue on file: {revenue:.2f}")
            print(register_sayings.goodbye)
        else:
            print("Please choose 1-5 or 0.")


if __name__ == "__main__":
    main()
