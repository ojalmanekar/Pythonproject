# check_project.py -- plain-assert checks of the project's arithmetic and rules.
#
# The week-5 idea (check_discount.py) and week 7's check_refactor.py at project scale: feed
# each piece a small, hand-worked example and assert the answer. The notes say the
# project's tests stay plain asserts (unittest and pytest are not on the library list).
# The first assert that fails stops the file and names the promise it broke.
#
# Run it from the project folder:   python3 check_project.py

# --- 1. imports --------------------------------------------------------------------------
import account
import agent
import benchmarks
import market_data
import metrics
import storage

# --- 2. global constants ------------------------------------------------------------------
CLOSE = 1e-9                   # never compare floats with == (week 1): ask "close enough?"


# --- 3. function declarations ---------------------------------------------------------------
def check_fee_example_from_the_contract():
    # 500 cash, price 25, 0.1% fee: each share costs 25.025, so -1 buys 19, not 20.
    acct = account.Account(500.0, 0.0)
    assert acct.execute(("BUY", -1), 25.0) == "ACCEPT"
    assert acct.get_shares() == 19
    assert abs(acct.get_cash() - (500 - 19 * 25 * 1.001)) < CLOSE


def check_reject_strings_change_nothing():
    acct = account.Account(100.0, 0.0)
    assert acct.execute(("BUY", 10), 25.0) == "REJECT currency balance: 100.0"
    assert acct.get_cash() == 100.0 and acct.get_shares() == 0
    assert acct.execute(("SELL", 3), 25.0) == "REJECT stock owned: 0.0"


def check_sell_pays_the_fee():
    acct = account.Account(0.0, 10.0)
    assert acct.execute(("SELL", -1), 100.0) == "ACCEPT"
    assert acct.get_shares() == 0
    assert abs(acct.get_cash() - 10 * 100 * 0.999) < CLOSE


def check_bad_orders_are_refused():
    acct = account.Account()
    for bad in [("BUY", float("nan")), ("JUMP", 1), ("BUY", "ten"), "BUY", ("SELL",)]:
        assert acct.execute(bad, 10.0).startswith("REJECT bad order"), bad
    assert acct.get_cash() == 10000.0                # none of them moved the money


def check_money_is_private():
    acct = account.Account(50.0)
    acct.__cash = 1000000                            # writing from outside: a NEW attribute
    assert acct.get_cash() == 50.0                   # the real money never moved (week 7)


def check_daily_returns():
    returns = metrics.daily_returns([100, 110, 99])
    assert len(returns) == 2
    assert abs(returns[0] - 0.10) < CLOSE and abs(returns[1] + 0.10) < CLOSE


def check_moving_average_matches_the_supplement():
    values = [3.0, 1.0, 4.0, 1.0, 5.0, 9.0, 2.0, 6.0]
    ours = metrics.moving_average(values, 3)
    # the supplement's slow version, computed here to compare: same numbers
    slow = [sum(values[i - 3:i]) / 3 for i in range(3, len(values) + 1)]
    assert len(ours) == len(slow)
    for a, b in zip(ours, slow):
        assert abs(a - b) < CLOSE


def check_max_drawdown():
    # best 120, then down to 90: (90 - 120) / 120 = -0.25
    assert abs(metrics.max_drawdown([100, 120, 90, 110]) + 0.25) < CLOSE
    assert metrics.max_drawdown([100, 101, 102]) == 0.0


def check_sharpe_like():
    assert metrics.sharpe_like([100, 100, 100]) == 0.0      # no movement, no division
    returns = metrics.daily_returns([100, 101, 100, 102])
    assert abs(metrics.sharpe_like([100, 101, 100, 102])
               - returns.mean() / returns.std()) < CLOSE


def check_agent_reads_the_news():
    trader = agent.TradingAgent()
    assert trader.news_signal(["QBIT surge as market rally"]) == 1
    assert trader.news_signal(["report token: QBIT set to bearish"]) == -1  # colon handled
    assert trader.news_signal([]) == 0


def check_agent_copes_with_every_regime():
    bar = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1000.0}
    for b, h in [(bar, None), (None, ["X surge"]), (bar, ["X surge"]), (None, None)]:
        action, amount = agent.TradingAgent().decide(b, h, 10000.0, 0.0, None)
        assert action in account.ACTIONS


def check_base_agent_is_abstract():
    try:
        benchmarks.BaseAgent("bare").decide(None, None, 0.0, 0.0, None)
        assert False, "BaseAgent.decide should have raised"
    except NotImplementedError:
        pass
    assert str(benchmarks.HoldAgent()) == "HoldAgent (benchmark)"


def check_market_loads_and_misses_cleanly():
    market, message = market_data.load_market("nova")       # lower case is fine
    assert market is not None, message
    assert market.days() == 750 and market.news_found
    assert market.headlines_on(0)[0] == "NOVA selloff in late session investors"
    missing, message = market_data.load_market("NOPE")
    assert missing is None and "no price file NOPE.csv" in message


def check_leaderboard_is_best_first():
    rows = storage.leaderboard_rows([("a", 9000.0, 3), ("b", 12000.0, 5), ("c", 10000.0, 0)])
    assert [name for rank, name, final in rows] == ["b", "c", "a"]
    assert rows[0][0] == 1


# --- 4. main code ---------------------------------------------------------------------------
def main():
    checks = [check_fee_example_from_the_contract, check_reject_strings_change_nothing,
              check_sell_pays_the_fee, check_bad_orders_are_refused, check_money_is_private,
              check_daily_returns, check_moving_average_matches_the_supplement,
              check_max_drawdown, check_sharpe_like, check_agent_reads_the_news,
              check_agent_copes_with_every_regime, check_base_agent_is_abstract,
              check_market_loads_and_misses_cleanly, check_leaderboard_is_best_first]
    for check in checks:
        check()                                      # a broken promise stops here
        print(f"  ok  {check.__name__}")
    print(f"All {len(checks)} checks passed.")


if __name__ == "__main__":
    main()
