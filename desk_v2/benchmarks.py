# benchmarks.py -- two simple agents to compare ours against on the desk's leaderboard.
#
# Week 7's inheritance and abstraction, the MenuItem shape:
#   - BaseAgent is the abstract base: it stores a name, prints itself with __str__, and its
#     decide() raises NotImplementedError ("every subclass must define decide()");
#   - HoldAgent and BuyAndHoldAgent are subclasses: each calls the base constructor BY
#     NAME, BaseAgent.__init__(self, ...), the course's form (not super()), and each
#     overrides decide().
# The simulator calls decide() on whichever agent it is given and never asks which class
# it holds: polymorphism.
#
# These are NOT our competition entry. agent.py must stand alone (it may import nothing of
# ours), so TradingAgent does not inherit from BaseAgent; it simply has the same decide().

# --- 1. imports --------------------------------------------------------------------------
# (none needed)

# --- 2. global constants ------------------------------------------------------------------
# (none)


# --- 3. class declarations ----------------------------------------------------------------
class BaseAgent:
    def __init__(self, name):
        self.name = name

    def decide(self, bar, headlines, cash, shares, last_response):
        raise NotImplementedError("every BaseAgent subclass must define decide()")

    def __str__(self):
        return f"{self.name} (benchmark)"


class HoldAgent(BaseAgent):
    """Never trades: the stub agent. Shows what doing nothing earns, exactly 0%."""

    def __init__(self):
        BaseAgent.__init__(self, "HoldAgent")

    def decide(self, bar, headlines, cash, shares, last_response):
        return ("HOLD", 0)


class BuyAndHoldAgent(BaseAgent):
    """Spends all its cash on day 0 and holds to the end: the market's own return."""

    def __init__(self):
        BaseAgent.__init__(self, "BuyAndHoldAgent")

    def decide(self, bar, headlines, cash, shares, last_response):
        if shares == 0 and cash > 0:
            return ("BUY", -1)
        return ("HOLD", 0)
