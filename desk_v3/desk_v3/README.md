# MIS41110 trading desk and agent (version 3: six files, one per piece of the brief)

## Start it
```
python3 desk.py            the desk: a text menu (Windows: python desk.py)
python3 desk.py 5000 10    optional: start with cash 5000 and 10 shares
python3 storage.py         our 14 plain-assert checks (week 5 style)
python3 selfcheck.py       the course's full check (runs agent_unittest.py first);
                           its three "ran end-to-end" lines go in the report
```
Run them from THIS folder (in PyCharm: right-click the file, Run), with the nine
data files in `data/training/` beside the code.

## The six files = the brief's six pieces (one reference member each)
| File | Brief's piece | Job |
|---|---|---|
| `market_data.py` | Data | loads prices, news and the word list; survives missing cells and a missing news file |
| `engine.py` | Account and engine | `Account` (cash, shares, 0.1% fee, ACCEPT/REJECT), `run_backtest` (the day loop, next-open fills), the benchmark agents |
| `agent.py` | The agent | our competition entry: `TradingAgent.decide()` |
| `desk.py` | The desk | the text menu; manual trades at today's close; bad input handled |
| `analytics.py` | Analytics and charts | returns, moving average, total return, drawdown, sharpe-like; the three charts |
| `storage.py` | Saving and tests | session, results and leaderboard in plain text; the 14 asserts (`python3 storage.py`) |

Put each reference member's full name on the `# Reference:` line at the top of their file,
and the group code plus every member's name at the top of `agent.py`.

Submit the 6 `.py` files above. The program runs in the terminal only. Do not submit the
data, `agent_unittest.py`, `selfcheck.py`, or the generated `.txt` and `.png` files.
