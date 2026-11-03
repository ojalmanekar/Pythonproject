# test_project.py -- quick tests of the pieces, written with plain assert.
#
# Run:  python3 test_project.py      It prints one line per test and "all tests passed".
# Each test feeds a small, hand-worked example to one function and checks the answer, so a
# change that breaks the arithmetic is caught at once.

import numpy as np

import metrics
import storage
from account import Account, OrderError
from agent import TradingAgent


def test_fee_example_from_the_contract():
    # $500 cash, price $25, 0.1% fee: each share costs 25.025, so -1 buys 19, not 20.
    account = Account(500.0, 0.0)
    assert account.execute(("BUY", -1), 25.0) == "ACCEPT"
    assert account.shares == 19
    assert abs(account.cash - (500 - 19 * 25 * 1.001)) < 1e-9


def test_reject_strings():
    account = Account(100.0, 0.0)
    assert account.execute(("BUY", 10), 25.0) == "REJECT currency balance: 100.0"
    assert account.cash == 100.0 and account.shares == 0        # a reject changes nothing
    assert account.execute(("SELL", 3), 25.0) == "REJECT stock owned: 0.0"


def test_sell_pays_the_fee():
    account = Account(0.0, 10.0)
    assert account.execute(("SELL", -1), 100.0) == "ACCEPT"
    assert account.shares == 0
    assert abs(account.cash - 10 * 100 * 0.999) < 1e-9


def test_malformed_orders_are_refused():
    account = Account()
    for bad in [("BUY", float("nan")), ("JUMP", 1), ("BUY", "ten"), "BUY", ("SELL",)]:
        try:
            account.execute(bad, 10.0)
            assert False, "should have refused " + repr(bad)
        except OrderError:
            pass
    assert account.execute(("BUY", np.int64(2)), 10.0) == "ACCEPT"   # numpy counts are fine


def test_daily_returns():
    returns = metrics.daily_returns([100, 110, 99])
    assert len(returns) == 2
    assert abs(returns[0] - 0.10) < 1e-12 and abs(returns[1] - (-0.10)) < 1e-12


def test_moving_average():
    assert list(metrics.moving_average([1, 2, 3, 4, 5], 3)) == [2.0, 3.0, 4.0]
    assert len(metrics.moving_average([1, 2], 3)) == 0


def test_max_drawdown():
    # best 120, then down to 90: (90 - 120) / 120 = -0.25
    assert abs(metrics.max_drawdown([100, 120, 90, 110]) - (-0.25)) < 1e-12
    assert metrics.max_drawdown([100, 101, 102]) == 0.0


def test_sharpe_like():
    assert metrics.sharpe_like([100, 100, 100]) == 0.0              # no movement
    equity = [100, 101, 100, 102]
    returns = np.array([0.01, 100 / 101 - 1, 0.02])
    assert abs(metrics.sharpe_like(equity) - returns.mean() / returns.std()) < 1e-12


def test_agent_news_signal():
    agent = TradingAgent()
    assert agent.news_signal(["QBIT surge as market rally"]) == 1
    assert agent.news_signal(["report token: QBIT set to bearish"]) == -1   # colon handled
    assert agent.news_signal([]) == 0


def test_agent_copes_with_every_regime():
    bar = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1000.0}
    for b, h in [(bar, None), (None, ["X surge"]), (bar, ["X surge"]), (None, None)]:
        order = TradingAgent().decide(b, h, 10000.0, 0.0, None)
        assert order[0] in ("BUY", "SELL", "HOLD")


def test_leaderboard_is_best_first():
    rows = storage.leaderboard_rows([("a", 9000.0, 3), ("b", 12000.0, 5), ("c", 10000.0, 0)])
    assert [name for rank, name, final in rows] == ["b", "c", "a"]
    assert rows[0][0] == 1


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print("  ok  " + test.__name__)
    print("all tests passed (" + str(len(tests)) + ")")
