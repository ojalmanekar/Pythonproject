# MIS41110 trading desk and agent (version 2: built with the lecture notes' tools)

## Start it
```
python3 desk.py            the desk: a text menu (Windows: python desk.py)
python3 desk.py 5000 10    optional: start with cash 5000 and 10 shares
python3 check_project.py   our plain-assert checks (week 5 style)
python3 agent_unittest.py  the course's protocol check (needs your GROUP_CODE in agent.py)
python3 selfcheck.py       the course's full check: its three "ran end-to-end" lines go in the report
```
Run them from THIS folder (in PyCharm: right-click desk.py, Run 'desk'), with the nine
data files in `data/training/` beside the code.

## Files
| File | Job | Lecture notes it follows |
|---|---|---|
| `desk.py` | Desk engine + text menu | week 3 menu loop, week 2 argv, week 5 try/except, week 7 composition |
| `agent.py` | Our competition entry: `TradingAgent.decide()` | week 4 lexicon dict, week 7 class |
| `account.py` | The authoritative account: cash, shares, fee, ACCEPT/REJECT | week 7 Register (`__cash`, `get_cash`, validate then mutate) |
| `market_data.py` | Loads prices, news and the word list | week 2/3 file reading, week 6 `read_csv`, week 5 `FileNotFoundError` |
| `simulator.py` | The back-test loop, next-open fills | week 3 loops, week 5 copies, week 7 polymorphism |
| `metrics.py` | Returns, moving average, drawdown, sharpe-like | week 6 numpy, time-series supplement, week 8 map/lambda |
| `charts.py` | The three charts | week 6 matplotlib, supplement's scatter recipe |
| `storage.py` | session.txt, results.txt, leaderboard.txt | week 2 "w"/"a", week 5 try/except, supplement leaderboard recipe |
| `benchmarks.py` | BaseAgent, HoldAgent, BuyAndHoldAgent | week 7 inheritance + abstraction (`raise NotImplementedError`) |
| `check_project.py` | 14 assert checks | week 5 check_discount.py, week 7 check_refactor.py |

Submit the 10 `.py` files above. The program runs in the terminal only. Do not submit the data,
`agent_unittest.py`, `selfcheck.py`, or the generated `.txt` and `.png` files.
