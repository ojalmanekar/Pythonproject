# desk_gui.py -- OPTIONAL: the desk with a window (week 8's tkinter, cafe_w8.py's shape).
#
# The rubric says a text menu earns full marks and a GUI changes nothing in the grade, so
# desk.py is the program to demonstrate. This file shows week 8's idea: a face put on THE
# SAME ENGINE. It imports desk (week 2's modules; week 5's __name__ guard is why desk's
# text menu does not start on import) and drives the very same Desk methods with buttons.
#
# Run it on your own computer, not over a bare SSH session:   python3 desk_gui.py
# Charts are saved as PNG files (not opened from inside the window); the message window
# names the files.

# --- 1. imports --------------------------------------------------------------------------
import tkinter as tk

import desk

# --- 2. global constants ------------------------------------------------------------------
WINDOW_SIZE = "520x430"


# --- 3. class declaration: the desk's face --------------------------------------------------
class DeskGUI:
    def __init__(self, master):
        self.master = master
        self.desk = desk.Desk()                      # the SAME engine as the text menu
        master.title(desk.DESK_NAME)

        self.readout = tk.StringVar()                # the live status line lives here
        tk.Label(master, textvariable=self.readout).pack(side=tk.TOP)

        tk.Label(master, text=f"Ticker ({desk.TICKER_HINT}):").pack()
        self.ticker_entry = tk.Entry(master)
        self.ticker_entry.insert(0, "NOVA")
        self.ticker_entry.pack()

        # One button per action. make_button gives each lambda its OWN action to remember
        # (cafe_w8's make_sell_button lesson: lambdas built in a bare loop share one value).
        self.make_button("Load dataset", self.load)
        self.make_button("Step one day", self.step)
        self.make_button("Buy 10 shares at today's close", lambda: self.trade("BUY", 10))
        self.make_button("Sell all shares at today's close", lambda: self.trade("SELL", -1))
        self.make_button("Run our agent (price + news)", self.run_agent)
        self.make_button("Save charts as PNG files", self.charts)
        self.make_button("Save session and results", self.save)
        self.make_button("Load saved session", self.load_saved)
        self.make_button("Close desk", self.quit)
        self.label_update()

    def make_button(self, text, command):
        button = tk.Button(self.master, text=text, command=command)
        button.pack()

    # ---- each button: call the engine, refresh the readout, show the reply ------------
    def load(self):
        self.show(self.desk.load(self.ticker_entry.get()))

    def step(self):
        self.show(self.desk.step())

    def trade(self, action, amount):
        self.show(self.desk.manual_trade(action, amount))

    def run_agent(self):
        self.show(self.desk.run_agent("1", "1"))

    def charts(self):
        first = self.desk.price_chart(show=False)
        second = self.desk.equity_charts(show=False)
        self.show(first + "\n" + second)

    def save(self):
        self.show(self.desk.save())

    def load_saved(self):
        self.show(self.desk.load_saved())

    def show(self, message):
        """Refresh the readout, then a small child window with the reply (cafe_w8)."""
        self.label_update()
        if message == "":
            message = "done"
        child = tk.Toplevel(self.master)
        tk.Label(child, text=message, justify=tk.LEFT, font=("Courier", 11)).pack()

    def label_update(self):
        """The StringVar's .set() repaints the Label."""
        self.readout.set(self.desk.status())

    def quit(self):
        self.master.destroy()


# --- 4. main code ---------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(WINDOW_SIZE)
    DeskGUI(root)
    root.mainloop()
