# cafe_w2.py -- "The Daily Grind", the Week 2 version.
#
# New tools this week: f-strings + str.format() (the receipt finally prints money
# properly), input() (the cafe can listen), file I/O (the revenue survives closing time),
# program arguments (see w02_argv_start.py), our own FUNCTIONS, boolean comparisons,
# and modules (register_sayings.py -- our first two-file program).
#
# Still deliberately missing: if/elif and loops (Week 3). So the order form is FIXED (one
# question per product), and the cafe can COMPUTE decisions (big_order -> True) but cannot
# ACT on them yet. Feel that itch -- next week's flow control scratches it.
#
# Run it from its own folder, with register_sayings.py beside it:  python3 cafe_w2.py

import register_sayings

espresso_price = 2.50
latte_price = 3.20
muffin_price = 2.40


def line_total(price, quantity):
    return price * quantity


def receipt_line(product, price, quantity):
    """One aligned receipt row -- the format specs do the layout work."""
    return f"{product:<12} x {quantity:>2} {line_total(price, quantity):>8.2f}"


def euros_and_cents(amount):
    """Split an amount into whole euros and the cent fraction (two return values)."""
    whole = amount // 1.0
    return whole, amount - whole


# --- the cafe listens (input() ALWAYS returns a string -> convert!) ---
cashier = input("Cashier name: ")
print(register_sayings.welcome(cashier))

espresso_qty = int(input("How many espressos? "))
latte_qty = int(input("How many lattes? "))
muffin_qty = int(input("How many muffins? "))

total = line_total(espresso_price, espresso_qty) \
    + line_total(latte_price, latte_qty) \
    + line_total(muffin_price, muffin_qty)

# --- the receipt: aligned columns, honest money ---
print(f"{' The Daily Grind ':=^34}")
print(receipt_line("espresso", espresso_price, espresso_qty))
print(receipt_line("latte", latte_price, latte_qty))
print(receipt_line("muffin", muffin_price, muffin_qty))
print("=" * 34)
print(f"{'TOTAL':<12}      {total:>8.2f}")    # three lattes now print 9.60 -- the wall is dead

euros, cents = euros_and_cents(total)
print(f"That is {euros:.0f} euro(s) and {cents * 100:.0f} cent(s).")

# --- booleans: the register can now ANSWER questions... ---
big_order = total > 10.0
busy_start = espresso_qty + latte_qty + muffin_qty >= 5
print(f"Big order (over 10.00)?  {big_order}")
print(f"Busy start (5+ items)?   {busy_start}")
# ...but it cannot ACT on the answers -- "IF it is a big order, apply a discount" needs
# next week's if statement. For now the register just states facts.

# --- persistence: the day survives closing time ---
revenue_file = open("revenue.txt", "w")       # "w": start the file fresh
revenue_file.write(f"{total:.2f}")            # write() wants a string -- f-strings deliver
revenue_file.close()

log = open("receipts.txt", "a")               # "a": append to the running log
log.write(f"{total:.2f}\n")
log.close()

revenue_file = open("revenue.txt", "r")       # read it back: proof it survived
saved = revenue_file.readline()
revenue_file.close()
print(f"Revenue on file: {saved}")

print(register_sayings.goodbye)
