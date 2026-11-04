# storage.py -- saving and loading in plain text, so the work survives a restart.
#
#   session.txt      the desk's state, one key=value per line        (written with "w")
#   results.txt      one line per saved run: name,final_equity,trades  (written with "a")
#   leaderboard.txt  every saved run, best first: rank,name,final_equity (rebuilt, "w")
#
# Week 2's file I/O: open, write or read, close; "w" replaces a file, "a" adds to it.
# Week 5's safety net: a file that is not there yet (the very first run) is normal, so
# reading catches FileNotFoundError and answers with an empty value instead of crashing.

# --- 1. imports --------------------------------------------------------------------------
# (none needed)

# --- 2. global constants ------------------------------------------------------------------
SESSION_FILE = "session.txt"
RESULTS_FILE = "results.txt"
LEADERBOARD_FILE = "leaderboard.txt"


# --- 3. function declarations ---------------------------------------------------------------
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
        return {"ticker": values["ticker"],
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
