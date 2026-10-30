# cafe_w8.py -- "The Daily Grind", the Week 8 version: the register gets a FACE.
#
# THIS IS THE START FILE (cafe_w8_start.py, saved as cafe_w8.py). It holds the four report
# helpers and opens no window, so running it prints nothing. Friday's lecture types the
# rest live: the two imports, the CafeGUI class and the launcher (slides 33 to 36).
#
# Two things happen this week, and both build on Week 7's refactor:
#   - FUNCTIONAL report helpers: pure functions that rewrite loops we wrote by hand in
#     Weeks 2-7 as comprehensions / map / lambda / zip one-liners;
#   - a tkinter GUI (class CafeGUI) that drives THE SAME Register as ever -- we import
#     cafe_w7 (Week 2's module lesson, structural edition) and put buttons on it.
#     Week 5's __name__ guard is why the import is clean: cafe_w7's demo main() does
#     not run when imported.
#
# The GUI needs a display: run  python3 cafe_w8.py  locally (not over a bare SSH pipe).

# --- functional report helpers (pure: inputs in, result out, nothing touched) -----------
def price_list(menu):
    """Product -> price, as a plain dict (a dict comprehension over the menu)."""
    return {name: menu[name].price for name in menu}

def menu_lines(menu):
    """The menu as aligned receipt-style lines -- Week 2's formatting, one comprehension."""
    return [f"{name:<12} {menu[name].price:>6.2f}" for name in menu]

def preview_rise(prices, rate):
    """What every price becomes after a rise -- map + lambda, no loop in sight."""
    return list(map(lambda p: round(p * (1.0 + rate), 2), prices))

def basket_total(quantities, prices):
    """The bill, one more time: quantities x prices, paired by zip, summed lazily."""
    return sum(q * p for q, p in zip(quantities, prices))

# --- the register's face ---------------------------------------------------------------------
