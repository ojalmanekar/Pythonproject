# Reference : Ojal Manekar



import sys


import agent
import analytics
import engine
import market_data
import storage


DESK_NAME = "Group- 19 Trading Desk"
ticker_HINT = "VOLT, ZNTH ,NOVA,QBIT"
MAX_AMOUNT= 1e7

MENU_TEXT= f"""{' ' +DESK_NAME + ' ':=^62}
 [1] Load dataset              [2] Set starting cash/shares
 [3] Step one day              [4] Manual buy
 [5] Manual sell               [6] Run agent to end
 [7] Show price chart          [8] Show equity + drawdown
 [9] Save / load               [0] Quit
{'=' * 62}"""

AGENT_CHOICES = { "1" : "TradingAgent", "2": "BuyAndHolgAgent", "3":"Hold_agent"}


class Desk:
    def __init__(self, cash=engine.DEFAULT_CASH, shares=engine.DEFAULT_SHARES):
        self.start_cash= float(cash)
        self.start_shares = float(shares)
        self.market = None
        self.day = 0
        self.account= engine.Account(cash,shares)
        self.manual_trades=[]
        self.last_result = None
        self.word_list= market_data.load_word_list()
        self.last_event= "-"

    def __str__(self):
        return self.status()

    def status(self):
        if self.market is None:
            return f"no market is loaded | {self.account}"
        price= self.market.close_on(self.day)
        return (f"{self.market.ticker} day {self.day}/{self.market.days() - 1} | "
                f"price {price:.2f} | {self.account} | "
                f"equity {self.account.get_equity(price):.2f}")

    def headlines_text(self):
        if self.market is None or not self.market.news_found:
            return ""
        headlines = self.market.headlines_on(self.day)
        if headlines == []:
            return " no news for today"
        score = market_data.headline_score(headlines, self.word_list)
        mood = "neutral"
        if score> 0:
            mood ="good"
        elif score <0:
            mood="bad"
        lines = [f" news today (score: {score:+.0f}, {mood}):"]
        lines = lines + [f"  - {headline}" for headline in headlines]
        return "\n".join(lines)


    def load(self,ticker):
        market, message = market_data.load_market(ticker)
        if market is None:
            return "could not load it: "+ message
        self.market= market
        self.day = 0
        self.account=engine.Account(self.start_cash, self.start_shares)
        self.manual_traders =[]
        self.last_result=None
        lines = [message]
        if not market.news_found:
            lines.append(f" notes: no news file for {market.ticker}: the agent sees no headlines")
        for note in market.notes[:5]:
            lines.append(" warning: " + note)
        news= self.headlines_text()
        if news != "":
            lines.append(news)
        self.last_event= "loaded" + market.ticker
        return "\n".join(lines)

    def set_balances(self,cash,shares):
        self.start_cash = cash
        self.start_shares = shares
        self.account = engine.Account(cash, shares)
        self.day=0
        self.manual_trades=[]
        self.last_event= f" balances set : {self.account}"

    def step(self):
        if self.market is None:
            return "load dataset first(option 1)"
        if self.day>= self.market.days()-1:
            return "this is the last day of the data: there is no next day"
        self.day = self.day+1
        self.last_event = f"stepped to day{self.day}"
        return self.headlines_text()

    def manual_trade(self,action,amount):
        if self.market is None:
            return "load dataset first(option 1)"
        price= self.market.close_on(self.day)
        shares_before= self.account.get_shares()
        reply = self.account.execute((action,amount),price)
        moved= abs(self.account.get_shares()-shares_before)
        if moved > 0:
            self.manual_trades.append(engine.Trade(self.day, action,moved,price))
        self.last_event= f"{action} {amount} -> {reply}"
        return "-->"+reply

    def run_agent(self, agent_choice, regime_choice):
        if self.market is None:
            return "oad dataset first(option 1)"
        if agent_choice not in AGENT_CHOICES or regime_choice not in engine.REGIMES:
            return " choose 1,2, or 3 for each question"
        name = AGENT_CHOICES[agent_choice]
        if name == "Trading_Agent":
            chosen= agent.TradingAgent()
        elif name == "BuyAndHoldAgent":
            chosen = engine.BuyAndHoldAgent()
        else:
            chosen = engine.HoldAgent()
        label, use_prices , use_news = engine.REGIMES[regime_choice]
        result= engine.run_backtest(chosen, self.market, self.start_cash, self.start_shares, use_prices, use_news, name)
        self.last_result=result
        self.last_event=f"ran {result.label()}: {result.equity[-1]:.2f}"
        return str(result)

    def price_chart(self, show=True):
        if self.market is None:
            return "load dataset first(option 1)"
        if self.last_result is not None:
            trades= self.last_result.trades
            extra = f'(trades of {self.last_result.agent_name})'
        else:
            trades = self.manual_trades
            extra ="(your manual trades)"
        return " saved" + analytics.price_with_trades(self.market, trades , extra , show)

    def equity_charts(self, show=True):
        if self.last_result is None:
            return "run an agent (option 6): these charts show its run"
        first = analytics.equity_curve(self.last_result,show)
        second= analytics.drawdown(self.last_result,show)
        return f"saved {first} and {second}"

    def save(self):
        if self.market is None:
            return "load a datset first: there is no session to save"
        storage.save_session({"ticker": self.market.ticker, "day":self.day,
                              "cash": self.account.get_cash(),
                              "shares":self.account.get_shares(),
                              "start_cash": self.start_cash,
                              "start_shares": self.start_shares})
        lines=[f'Saved the session to { storage.SESSION_FILE}.']
        if self.last_result is not None:
            numbers = self.last_result.numbers()
            storage.append_result(self.last_result.label(), numbers["final_equity"],
                                  len(self.last_result.trades))
            storage.save_leaderboard((storage.load_results()))
            lines.append(f"Save the run to {storage.RESULTS_FILE} and the leaderboard"
                         f"to{storage.LEADERBOARD_FILE}")

            self.last_event="saved"
            return "\n".join(lines)

        def load_saved(self):
            saved= storage.load_session()
            if saved is None :
                return f"no usable saved session({storage.SESSION_FILE} is missing or damaged)"
            market,message = market_data.load_market(saved["ticker"])
            if market is None:
                return " could not reload the saved market:"+message
            if saved["day"] <0 or saved["day"]>= market.days():
                return f"the saved day {saved['day']} is outside the data"

            self.market = market
            self.day = saved["day"]
            self.start_cash= saved["start_cash"]
            self.start_shares=saved["start_shares"]
            self.account= engine.Account(saved["cash"],saved["shares"])
            self.manual_trades = []
            self.last_result = None
            self.last_event= "loaded the saved session"
            return f'loaded session: {market.ticker} day {self.day}.\n' + self.leaderboard_text()

        def leaderboard_text(self):
            rows= storage.leaderboard_rows(storage.load_results())
            if rows==[]:
                return "leaderboard: no saved runs yet"
            lines= [" leaderboard, best final equity first:"]
            lines= lines + [f"{rank:>2} , {name:<45} {final:>10.2f}"
                            for rank,name,final in rows[:10]]
            return "\n".join(lines)

def ask(prompt,default=""):
    answer = input(prompt).strip()
    if answer == "":
        return default
    return answer

def ask_number(prompt, default, allow_all = False):
    while True:
        text= ask(prompt,str(default))
        try:
            value= float(text)
        except ValueError:
            print(f"  '{text}' is not a number -- digits only , please")
            continue
        if value != value or abs(value) == float("inf"):
            print(" That is not a real amount")
        elif allow_all and value ==-1:
            return value
        elif value < 0:
            if allow_all:
                print("   It cannot be negative(or type -1 for all)")
            else:
                print(" It cannot be negative.")

        elif value> MAX_AMOUNT:
            print(' the amount is too large')
        else:
            return value

def starting_balance(arguments):
    cash= engine.DEFAULT_CASH
    shares= engine.DEFAULT_SHARES
    try:
        if len(arguments)>1:
            cash= float(arguments[1])
        if len(arguments)>2:
            shares= float(arguments[2])
        assert 0 <= cash <= MAX_AMOUNT and 0 <= shares <= MAX_AMOUNT, \
            "cash and shares must be between 0 and 1e7"
    except (ValueError, AssertionError) as error:
        print(f" Ignoring the command line ({error}) : using cash{engine.DEFAULT_CASH}")
        cash= engine.DEFAULT_CASH
        shares= engine.DEFAULT_SHARES
    return  cash, shares

def manual_trade_menu(desk, action):
    word="sell"
    if action == "BUY":
        word= "buy"
    amount= ask_number(f" How many shares to {word}? ", -1,
                        allow_all=True)
    if amount != int(amount):
        return " Shares are bought and sold whole : try a whole number"
    return desk.manual_trade(action, int(amount))


def run_agent_menu(desk):
    print( " Select an Agent [1] TradingAgent  [2] BuyandHoldAgent  [3] HoldAgent ")
    agent_choice= ask("Which agent [1]: ", "1")
    print("   It sees: [1] price + news  [2] price only  [3] news only")
    regime_choice = ask(" Which [1]: " , "1")
    return desk.run_agent(agent_choice, regime_choice)

def saveorload(desk):
    choice=ask(" [s]save or [l]load ").lower()
    if choice.startswith("s"):
        return desk.save()
    elif choice.startswith("l"):
        return desk.load_saved()
    return "Type s to save or l to load"


def main():
    cash , shares = starting_balance(sys.argv)
    desk = Desk(cash, shares)
    print(f'Welcome. Starting cash {cash:.2f}, shares { shares:g}')
    choice = ""
    while choice != "0":
        print(MENU_TEXT)
        choice = ask("Choose: ")
        if choice == "1":
            message = desk.load(ask(f"ticker (e.g. {ticker_HINT}): "))
        elif choice == "2":
            new_cash = ask_number(f"Starting cash  [{desk.start_cash:g}]: ", desk.start_cash)
            new_shares = ask_number(f"Starting shares [{desk.start_shares:g}]: ", desk.start_shares)
            message = desk.set_balances(new_cash, new_shares)
        elif choice == "3":
            message = desk.step()
        elif choice == "4":
            message = manual_trade_menu(desk, "BUY")
        elif choice == "5":
            message = manual_trade_menu(desk, "SELL")
        elif choice == "6":
            message = run_agent_menu(desk)
        elif choice == "7":
            message = desk.price_chart()
        elif choice=="8":
            message = desk.equity_charts()
        elif choice == "9":
            message = saveorload(desk)
        elif choice == "0":
            message = "Goodbye"
        else:
            message = f" '{choice}' is not on the menu :type a number from 0 to 9."

        if message != "":
            print(message)
        if choice != "0":
            print(desk.status())
            print(f"  latest event: {desk.last_event}")


if __name__=="__main__":
    try:
        main()
    except( KeyboardInterrupt, EOFError):
        print("\nGoodbye.")

















            



















