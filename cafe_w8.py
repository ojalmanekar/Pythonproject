# cafe_w8.py -- "The Daily Grind", the Week 8 version: the register gets a FACE.
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

import tkinter as tk

import cafe_w7


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
class CafeGUI:
    def __init__(self, master):
        self.master = master
        self.cafe = cafe_w7.Cafe(cash=0.0)          # the SAME engine as Week 7
        master.title("The Daily Grind")

        self.readout = tk.StringVar()               # the live label's text lives here
        self.label = tk.Label(master, textvariable=self.readout)
        self.label.pack(side=tk.TOP)

        for name in self.cafe.menu:                 # one sell button per product
            self.make_sell_button(name)
        self.report = tk.Button(master, text="Day report", command=self.day_report)
        self.report.pack()
        self.exit = tk.Button(master, text="Close register", command=self.quit)
        self.exit.pack()

        self.label_update()

    def make_sell_button(self, name):
        """Build one button. A method call gives the lambda its OWN `name` to remember --
        build these in a bare loop and every lambda would share the loop's last value
        (Week 5's aliasing family, GUI edition)."""
        button = tk.Button(self.master, text="Sell 1 " + name,
                           command=lambda: self.sell(name))
        button.pack()

    def sell(self, product):
        """One click = one sale attempt through the authoritative Register."""
        accepted, message = self.cafe.serve([(product, 1)])
        self.label_update()
        self.msg_window(message)

    def day_report(self):
        """The functional helpers, on a button: the menu + the money, in one window."""
        lines = menu_lines(self.cafe.menu)
        lines.append(f"{'CASH':<12} {self.cafe.register.get_cash():>6.2f}")
        self.msg_window("\n".join(lines))

    def label_update(self):
        """Refresh the live readout -- the StringVar's .set() repaints the Label."""
        items_left = sum(self.cafe.register.get_stock(name) for name in self.cafe.menu)
        self.readout.set(f"Cash: {self.cafe.register.get_cash():.2f}   "
                         f"Items in stock: {items_left}")

    def msg_window(self, msg):
        """A small child window for messages (accepts and rejects alike)."""
        child = tk.Toplevel(self.master)
        label = tk.Label(child, text=msg)
        label.pack()

    def quit(self):
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("380x300")
    CafeGUI(root)
    root.mainloop()
