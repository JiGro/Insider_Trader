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
urls = ["http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=25&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1",
        "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xs=1&vl=100&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"]

filing_date, trade_date, ticker, stock_name, insider_name, insider_title, buy_sell, quantity, stock_price, percentage_change, trade_volume = [[] for i in range(11)]
for url in urls:
    print("*** Start extraction of {url_string} ***".format(url_string=url))
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    table = soup.find_all("tbody")
    for tr in table[1].find_all("tr"):
        tds = tr.find_all('td')
        filing_date.append(tds[1].get_text())
        trade_date.append(tds[2].get_text())
        ticker.append(tds[3].get_text().replace(" ",""))
        stock_name.append(tds[4].get_text())
        insider_name.append(tds[5].get_text())
        insider_title.append(tds[6].get_text())
        buy_sell.append(tds[7].get_text())
        quantity.append(tds[9].get_text())
        stock_price.append(tds[8].get_text())
        percentage_change.append(tds[11].get_text())
        trade_volume.append(tds[12].get_text())
    print("*** Data extraction finished ***")

insider_stocks_df = pd.DataFrame({"filing_date": filing_date, "trade_date": trade_date, "ticker": ticker,
                                  "stock_name": stock_name, "insider_name": insider_name,
                                  "insider_title": insider_title, "buy_sell": buy_sell,
                                  "quantity": quantity, "stock_price": stock_price,
                                  "percentage_change": percentage_change, "trade_volume": trade_volume})

for index, row in insider_stocks_df.iterrows():
    filing_date = datetime.strptime(row["filing_date"], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    if filing_date != datetime.today().strftime('%Y-%m-%d'):
        print("Starting with calc")
        try:
            stock_history_df = yahoo_historical_data(row["ticker"], filing_date)
            #calc medium stock price
            starting_price = (stock_history_df.at[0, "Open"] +
                              stock_history_df.at[0, "High"] +
                              stock_history_df.at[0, "Low"] +
                              stock_history_df.at[0, "Close"]) / 4
            insider_stocks_df.loc[index, "starting_price"] = starting_price
            if "Purchase" in row["buy_sell"]:
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
        except:
            pass
    else:
        print("Purchased today")
print("Finished calculating time periods")

# sort to differentiate between buy and sell
insider_stocks_df = insider_stocks_df.sort_values(by="buy_sell", ascending=False)

# Split by Kauf / Verkauf
insider_stocks_df_buy = insider_stocks_df[insider_stocks_df["buy_sell"].str.contains("Purchase")]
insider_stocks_df_sell = insider_stocks_df[insider_stocks_df["buy_sell"].str.contains("Sell")]

# prepare df & heatmap
df_buy_hm = pd.concat([insider_stocks_df_buy.iloc[:, 2:3], insider_stocks_df_buy.iloc[:, 12:22]], axis=1)
df_buy_hm = df_buy_hm[df_buy_hm['t_1'].notna()]
df_buy_hm = df_buy_hm.set_index("ticker")
sns.heatmap(df_buy_hm, annot=True)

df_sell_hm = pd.concat([insider_stocks_df_buy.iloc[:, 2:3], insider_stocks_df_buy.iloc[:, 12:22]], axis=1)
df_sell_hm = df_sell_hm[df_sell_hm['t_1'].notna()]
df_sell_hm = df_sell_hm.set_index("ticker")
sns.heatmap(df_sell_hm, annot=True)

