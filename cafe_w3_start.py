# cafe_w3.py -- "The Daily Grind", the Week 3 version (grown from cafe_w2.py).
#
# Tools we have so far:
#   Weeks 1-2: variables and math, printing, f-strings, keyboard input, writing/reading
#              files, functions, boolean logic, modules (register_sayings is still with us).
#   Week 3 (NEW): flow control -- if/elif/else, while loops, for loops.
#
# Last week the register could COMPUTE "big_order -> True" but could not act on it. This week
# the if statement cashes that cliffhanger: apply_discount() finally DECIDES.
#
# We do NOT have lists or dictionaries yet (that is Week 4). So we look prices up with an
# if/elif chain and sum an order into a single running total. Notice how clumsy that is --
# we cannot even remember the individual items on the bill. Feeling that pain is the point:
# next week's data structures will fix it. Reading a saved total back *safely* needs
# exception handling (Week 5); until then we clear the receipts file when we open up, so the
# file always exists.

import register_sayings

DISCOUNT_THRESHOLD = 10.0     # orders over this get a discount
DISCOUNT_RATE = 0.10          # 10% off

def price_of(product):
    """Return the price of a product, or 0.0 if we don't sell it.

    An if/elif chain for now. In Week 4 this whole function becomes a single dictionary
    lookup -- a good example of choosing the right data structure.
    """
    if product == "espresso":
        return 2.50
    elif product == "latte":
        return 3.20
    elif product == "cappuccino":
        return 3.00
    elif product == "croissant":
        return 2.80
    elif product == "muffin":
        return 2.40
    elif product == "tea":
        return 2.20
    else:
        return 0.0

def save_receipt(amount):
    """Append the paid amount to today's receipts log (demonstrates writing to a file)."""
    log = open("receipts.txt", "a")
    log.write(f"{amount:.2f}\n")
    log.close()

def day_summary():
    """Read today's receipts back and total them -- our first `for` loop.

    A `for` loop visits each line in turn. This is the natural shape for "do something with
    every item in a collection", and it is why we opened the file fresh at the start of the
    day: the file always exists, so we never crash on a missing file (safe reading of a file
    that might NOT exist waits for Week 5's exceptions).
    """
    count = 0
    total = 0.0
    for line in open("receipts.txt"):
        line = line.strip()
        if line != "":
            count = count + 1
            total = total + float(line)
    print(f"  Orders today:  {count}")
    print(f"  Total revenue: {total:.2f}")

def save_revenue(revenue):
    """Write the day's total revenue to a file."""
    f = open("revenue.txt", "w")
    f.write(f"{revenue:.2f}")
    f.close()

def main():
    """The main menu loop -- a shape you will reuse all term (and in your project)."""
    open("receipts.txt", "w").close()      # start the day with an empty receipts file
    revenue = 0.0
    cashier = input("Cashier name: ")
    print(register_sayings.welcome(cashier))
    choice = ""
    while choice != "0":
        print("\n[1] New order   [2] Today's revenue   [3] Day summary   [0] Close up")
        choice = input("Choose: ").strip()
        if choice == "1":
            paid = take_order()
            revenue = revenue + paid
            save_receipt(paid)
        elif choice == "2":
            print(f"Revenue so far: {revenue:.2f}")
        elif choice == "3":
            day_summary()
        elif choice == "0":
            save_revenue(revenue)
            print(f"Closed. Revenue for the day: {revenue:.2f}")
            print(register_sayings.goodbye)
        else:
            print("Please choose 1, 2, 3 or 0.")

if __name__ == "__main__":
    main()
