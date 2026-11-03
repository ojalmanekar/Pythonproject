# storage.py -- saving and loading, all in plain text, so it survives a restart.
#
#   session.txt      the desk's state: market, day, cash, shares, starting balances
#                    (one "key=value" per line)
#   results.txt      one line per saved run:        name,final_equity,trades
#   leaderboard.txt  rewritten from every saved run, best final equity first:
#                    rank,name,final_equity
#
# Every function opens its file, reads or writes it, and closes it. A missing file is
# normal on the first run (nothing saved yet) and gives an empty answer; a damaged line is
# skipped rather than crashing the desk.

SESSION_FILE = "session.txt"
RESULTS_FILE = "results.txt"
LEADERBOARD_FILE = "leaderboard.txt"


class StorageError(Exception):
    """A save or load that cannot be done (for example a session file with no market)."""


def save_session(session, path=SESSION_FILE):
    """Write a dict of the desk's state, one key=value per line."""
    handle = open(path, "w", encoding="utf-8")
    for key in sorted(session):
        handle.write(key + "=" + str(session[key]) + "\n")
    handle.close()


def load_session(path=SESSION_FILE):
    """Read session.txt back into a dict with the right types. Raises StorageError."""
    try:
        handle = open(path, encoding="utf-8")
    except FileNotFoundError:
        raise StorageError("no saved session yet (" + path + " not found) -- save one first")
    values = {}
    for line in handle:
        line = line.strip()
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    handle.close()
    try:
        return {
            "ticker": values["ticker"],
            "day": int(values["day"]),
            "cash": float(values["cash"]),
            "shares": float(values["shares"]),
            "start_cash": float(values.get("start_cash", values["cash"])),
            "start_shares": float(values.get("start_shares", values["shares"])),
        }
    except (KeyError, ValueError) as error:
        raise StorageError(path + " is damaged (" + type(error).__name__ + ": " + str(error)
                           + ") -- save the session again")


def append_result(name, final_equity, trades, path=RESULTS_FILE):
    """Add one run to results.txt (mode "a" keeps every earlier run)."""
    handle = open(path, "a", encoding="utf-8")
    handle.write(name.replace(",", " ") + "," + str(round(final_equity, 2)) + ","
                 + str(trades) + "\n")
    handle.close()


def load_results(path=RESULTS_FILE):
    """Every saved run as a list of (name, final_equity, trades); [] if none yet."""
    results = []
    try:
        handle = open(path, encoding="utf-8")
    except FileNotFoundError:
        return results
    for line in handle:
        parts = line.strip().split(",")
        if len(parts) != 3:
            continue                                  # a blank or damaged line
        try:
            results.append((parts[0], float(parts[1]), int(parts[2])))
        except ValueError:
            continue
    handle.close()
    return results


def leaderboard_rows(results):
    """The runs ranked best final equity first: [(rank, name, final_equity), ...].

    The recipe from the time-series supplement: a list of [score, name] pairs sorts by its
    first element, then reverse for best-first."""
    rows = [[final, name] for name, final, trades in results]
    rows.sort()
    rows.reverse()
    ranked = []
    rank = 1
    for final, name in rows:
        ranked.append((rank, name, final))
        rank = rank + 1
    return ranked


def save_leaderboard(results, path=LEADERBOARD_FILE):
    """Rewrite leaderboard.txt from every saved run (mode "w" replaces the old one)."""
    handle = open(path, "w", encoding="utf-8")
    handle.write("rank,name,final_equity\n")
    for rank, name, final in leaderboard_rows(results):
        handle.write(str(rank) + "," + name + "," + str(round(final, 2)) + "\n")
    handle.close()
