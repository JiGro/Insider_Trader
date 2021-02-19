import requests
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import Yahoo_Ticker_search
import yfinance as yf
from datetime import datetime
import seaborn as sns

# use yahoo api to get historical data
def yahoo_historical_data(ticker_str, start_date):
    data = yf.Ticker(ticker_str)
    ticker_history = data.history(start=start_date)
    ticker_history.reset_index(inplace=True, drop=False)
    return ticker_history


agent = UserAgent()
user_agent = agent.random
headers = {'User-Agent': user_agent}
data = requests.get('https://www.vorstandsdeals.de/', headers=headers)
soup = BeautifulSoup(data.text, 'html.parser')
table = soup.find("tbody")
stock_name, isin, buy_sell, insiders_involved, trade_volume, stock_price_avg, date = [[] for i in range(7)]
for tr in table.find_all("tr"):
    tds = tr.find_all('td')
    stock_name.append(tds[0].get_text())
    isin.append(tds[1].get_text())
    buy_sell.append(tds[3].get_text())
    insiders_involved.append(tds[4].get_text())
    trade_volume.append(tds[5].get_text())
    stock_price_avg.append(tds[6].get_text())
    date.append(tds[7].get_text())

insider_stocks_df = pd.DataFrame({"stock_name": stock_name, "isin": isin, "buy_sell": buy_sell,
                                  "insiders_involved": insiders_involved, "trade_volume": trade_volume,
                                  "stock_price_avg": stock_price_avg, "date": date})

for index, row in insider_stocks_df.iterrows():
    result = Yahoo_Ticker_search.search(row["isin"])
    if len(result) == 0:
        result = Yahoo_Ticker_search.search(row["stock_name"])
    insider_stocks_df.loc[index, "ticker"] = result[0]["symbol"]

for index, row in insider_stocks_df.iterrows():
    purchase_date = datetime.strptime(row["date"], '%d.%m.%Y').strftime('%Y-%m-%d')
    if purchase_date != datetime.today().strftime('%Y-%m-%d'):
        print("Starting with calc")
        stock_history_df = yahoo_historical_data(row["ticker"], purchase_date)
        #calc medium stock price
        starting_price = (stock_history_df.at[0, "Open"] +
                          stock_history_df.at[0, "High"] +
                          stock_history_df.at[0, "Low"] +
                          stock_history_df.at[0, "Close"]) / 4
        insider_stocks_df.loc[index, "starting_price"] = starting_price
        if row["buy_sell"] == "Kauf":
            for index2, row2 in stock_history_df.iterrows():
                if index2 >= 1:
                    daily_high_low = row2["High"]
                    diff = daily_high_low / starting_price
                    help_str = "t_" + str(index2)
                    insider_stocks_df.loc[index, help_str] = diff
        else:
            for index2, row2 in stock_history_df.iterrows():
                if index2 >= 1:
                    daily_high_low = row2["Low"]
                    diff = daily_high_low / starting_price
                    help_str = "t_" + str(index2)
                    insider_stocks_df.loc[index, help_str] = diff
    else:
        print("Purchased today")
print("Finished calculating time periods")

# sort to differentiate between buy and sell
insider_stocks_df = insider_stocks_df.sort_values(by="buy_sell", ascending=False)

# Split by Kauf / Verkauf
insider_stocks_df_buy = insider_stocks_df[insider_stocks_df["buy_sell"] == "Kauf"]
insider_stocks_df_sell = insider_stocks_df[insider_stocks_df["buy_sell"] == "Verkauf"]

# prepare df & heatmap
df_buy_hm = pd.concat([insider_stocks_df_buy.iloc[:, :1], insider_stocks_df_buy.iloc[:, 9:19]], axis=1)
df_buy_hm = df_buy_hm[df_buy_hm['t_1'].notna()]
df_buy_hm = df_buy_hm.set_index("stock_name")
sns.heatmap(df_buy_hm, annot=True)

df_sell_hm = pd.concat([insider_stocks_df_sell.iloc[:, :1], insider_stocks_df_sell.iloc[:, 9:19]], axis=1)
df_sell_hm = df_sell_hm[df_sell_hm['t_1'].notna()]
df_sell_hm = df_sell_hm.set_index("stock_name")
sns.heatmap(df_sell_hm, annot=True)
