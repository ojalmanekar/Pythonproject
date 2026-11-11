# storage.py -- the SAVING AND TESTS piece: plain-text files, and the asserts that prove
# the rules.
# Reference: Pooja Pansare
#
# Part A, saving: plain text, so the work survives a restart.
#   session.txt      the desk's state, one key=value per line        (written with "w")
#   results.txt      one line per saved run: name,final_equity,trades  (written with "a")
#   leaderboard.txt  every saved run, best first: rank,name,final_equity (rebuilt, "w")
# Week 2's file I/O; week 5's safety net: a file that is not there yet (the very first run)
# is normal, so reading catches FileNotFoundError and answers with an empty value.
#
# Part B, the tests: the week-5 idea (check_discount.py) and week 7's check_refactor.py at
# project scale. Each check feeds one piece a small, hand-worked example and asserts the
# answer; the notes say the project's tests stay plain asserts (unittest and pytest are not
# on the library list). The first assert that fails stops the run and names the promise it
# broke. Run them with:   python3 storage.py
# The desk imports this file only for part A; the checks run only when it is started.

# --- 1. imports --------------------------------------------------------------------------
import agent
import analytics
import engine
import market_data

# --- 2. global constants ------------------------------------------------------------------
SESSION_FILE = "session.txt"
RESULTS_FILE = "results.txt"
LEADERBOARD_FILE = "leaderboard.txt"

CLOSE = 1e-9                   # never compaare floats with == (week 1): ask "close enough?"


# --- 3. function declarations ---------------------------------------------------------------
# ---- part A: saving and loading -------------------------------------------------------------
def save_session(session, path=SESSION_FILE):
    """Write the desk's state (a dict) as key=value lines."""
    f = open(path, "w")
    for key in session:
        f.write(f"{key}={session[key]}\n")
    f.close()


def load_session(path=SESSION_FILE):
    """Read session.txt back into a dict with the right types; None if missing or damaged."""
    values = {}
    try:
        for line in open(path):
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                values[key] = value
        return {"checker": values["checker"],
                "day": int(values["day"]),
                "cash": float(values["cash"]),
                "shares": float(values["shares"]),
                "start_cash": float(values["start_cash"]),
                "start_shares": float(values["start_shares"])}
    except (FileNotFoundError, KeyError, ValueError):
        return None


def append_result(name, final_equity, trades, path=RESULTS_FILE):
    """Add one run to results.txt; "a" keeps every earlier run."""
    f = open(path, "a")
    f.write(f"{name.replace(',', ' ')},{final_equity:.2f},{trades}\n")
    f.close()


def load_results(path=RESULTS_FILE):
    """Every saved run as a list of (name, final_equity, trades) tuples; [] if none yet."""
    results = []
    try:
        for line in open(path):
            parts = line.strip().split(",")
            if len(parts) != 3:
                continue                             # a blank or damaged line
            try:
                results.append((parts[0], float(parts[1]), int(parts[2])))
            except ValueError:
                continue
    except FileNotFoundError:
        pass                                         # nothing saved yet: that is fine
    return results


def leaderboard_rows(results):
    """The runs ranked best final equity first: [(rank, name, final_equity), ...].

    The supplement's recipe: [score, name] pairs sort by their first element with .sort(),
    then .reverse() for best-first; enumerate numbers them (from 0, so we add 1)."""
    rows = [[final, name] for name, final, trades in results]
    rows.sort()
    rows.reverse()
    ranked = []
    for index, pair in enumerate(rows):
        final, name = pair
        ranked.append((index + 1, name, final))
    return ranked


def save_leaderboard(results, path=LEADERBOARD_FILE):
    """Rewrite leaderboard.txt from every saved run ("w" replaces the old one)."""
    f = open(path, "w")
    f.write("rank,name,final_equity\n")
    for rank, name, final in leaderboard_rows(results):
        f.write(f"{rank},{name},{final:.2f}\n")
    f.close()


# ---- part B: the checks ----------------------------------------------------------------------
def check_fee_example_from_the_contract():
    # 500 cash, price 25, 0.1% fee: each share costs 25.025, so -1 buys 19, not 20.
    acct = engine.Account(500.0, 0.0)
    assert acct.execute(("BUY", -1), 25.0) == "ACCEPT"
    assert acct.get_shares() == 19
    assert abs(acct.get_cash() - (500 - 19 * 25 * 1.001)) < CLOSE


def check_reject_strings_change_nothing():
    acct = engine.Account(100.0, 0.0)
    assert acct.execute(("BUY", 10), 25.0) == "REJECT currency balance: 100.0"
    assert acct.get_cash() == 100.0 and acct.get_shares() == 0
    assert acct.execute(("SELL", 3), 25.0) == "REJECT stock owned: 0.0"


def check_sell_pays_the_fee():
    acct = engine.Account(0.0, 10.0)
    assert acct.execute(("SELL", -1), 100.0) == "ACCEPT"
    assert acct.get_shares() == 0
    assert abs(acct.get_cash() - 10 * 100 * 0.999) < CLOSE


def check_bad_orders_are_refused():
    acct = engine.Account()
    for bad in [("BUY", float("nan")), ("JUMP", 1), ("BUY", "ten"), "BUY", ("SELL",)]:
        assert acct.execute(bad, 10.0).startswith("REJECT bad order"), bad
    assert acct.get_cash() == 10000.0                # none of them moved the money


def check_money_is_private():
    acct = engine.Account(50.0)
    acct.__cash = 1000000                            # writing from outside: a NEW attribute
    assert acct.get_cash() == 50.0


def check_daily_returns():
    returns = analytics.daily_returns([100, 110, 99])
    assert len(returns) == 2
    assert abs(returns[0] - 0.10) < CLOSE and abs(returns[1] + 0.10) < CLOSE


def check_moving_average_matches_the_supplement():
    values = [3.0, 1.0, 4.0, 1.0, 5.0, 9.0, 2.0, 6.0]
    ours = analytics.moving_average(values, 3)
    # the supplement's slow version, computed here to compare: same numbers
    slow = [sum(values[i - 3:i]) / 3 for i in range(3, len(values) + 1)]
    assert len(ours) == len(slow)
    for a, b in zip(ours, slow):
        assert abs(a - b) < CLOSE


def check_max_drawdown():
    # best 120, then down to 90: (90 - 120) / 120 = -0.25
    assert abs(analytics.max_drawdown([100, 120, 90, 110]) + 0.25) < CLOSE
    assert analytics.max_drawdown([100, 101, 102]) == 0.0
    assert analytics.max_drawdown([0.0, 0.0, 0.0]) == 0.0     # an empty account: no crash
    assert analytics.sharpe_like([0.0, 0.0, 0.0]) == 0.0


def check_sharpe_like():
    assert analytics.sharpe_like([100, 100, 100]) == 0.0      # no movement, no division
    returns = analytics.daily_returns([100, 101, 100, 102])
    assert abs(analytics.sharpe_like([100, 101, 100, 102])
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
        assert action in engine.ACTIONS


def check_base_agent_is_abstract():
    try:
        engine.BaseAgent("bare").decide(None, None, 0.0, 0.0, None)
        assert False, "BaseAgent.decide should have raised"
    except NotImplementedError:
        pass
    assert str(engine.HoldAgent()) == "HoldAgent (benchmark)"


def check_market_loads_and_misses_cleanly():
    market, message = market_data.load_market("nova")
    assert market is not None, message
    assert market.days() == 750 and market.news_found
    assert market.headlines_on(0)[0] == "NOVA selloff in late session investors"
    missing, message = market_data.load_market("NOPE")
    assert missing is None and "no price file NOPE.csv" in message


def check_leaderboard_is_best_first():
    rows = leaderboard_rows([("a", 9000.0, 3), ("b", 12000.0, 5), ("c", 10000.0, 0)])
    assert [name for rank, name, final in rows] == ["b", "c", "a"]
    assert rows[0][0] == 1


def run_all_checks():
    checks = [check_fee_example_from_the_contract, check_reject_strings_change_nothing,
              check_sell_pays_the_fee, check_bad_orders_are_refused, check_money_is_private,
              check_daily_returns, check_moving_average_matches_the_supplement,
              check_max_drawdown, check_sharpe_like, check_agent_reads_the_news,
              check_agent_copes_with_every_regime, check_base_agent_is_abstract,
              check_market_loads_and_misses_cleanly, check_leaderboard_is_best_first]
    for check in checks:
        check()
        print(f"  ok  {check.__name__}")
    print(f"All {len(checks)} checks passed.")



# --- 4. main code: the checks run only when this file is started ---------------------------
if __name__ == "__main__":
    run_all_checks()
