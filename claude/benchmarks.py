# benchmarks.py -- two simple agents to compare ours against, on the desk's leaderboard.
#
# These are NOT our competition entry (that is agent.py, which must stand alone). They are
# here so the desk can show whether TradingAgent beats doing nothing or buying and holding,
# and they are where inheritance earns its place: both share one base class.


class BenchmarkAgent:
    """The base class: holds a name and refuses to trade until a subclass says how."""

    name = "BenchmarkAgent"

    def decide(self, bar, headlines, cash, shares, last_response):
        raise NotImplementedError("a benchmark must define decide()")

    def __str__(self):
        return self.name


class HoldAgent(BenchmarkAgent):
    """Never trades: the stub agent. Shows what doing nothing earns (exactly 0%)."""

    name = "HoldAgent"

    def decide(self, bar, headlines, cash, shares, last_response):
        return ("HOLD", 0)


class BuyAndHoldAgent(BenchmarkAgent):
    """Buys everything on the first day and holds to the end: the market's own return."""

    name = "BuyAndHoldAgent"

    def decide(self, bar, headlines, cash, shares, last_response):
        if shares == 0 and cash > 0:
            return ("BUY", -1)
        return ("HOLD", 0)
