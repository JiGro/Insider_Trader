import requests
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re

def vorstandsdeals_scraper(requests_agent):
    headers = {'User-Agent': requests_agent}
    data = requests.get('https://www.vorstandsdeals.de/', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    stock_price = soup.find("td", attrs={"class": "longprice"}).get_text()
    stock_price = stock_price.replace(' ', '').replace('.', '').replace(',', '.')
    stock_price = float(stock_price.strip())
    return stock_price

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

insider_stocks_df = pd.DataFrame({"stock_name": stock_name, "isin": isin,
                                            "buy_sell": buy_sell, "insiders_involved": insiders_involved,
                                            "trade_volume": trade_volume, "stock_price_avg": stock_price_avg,
                                            "date": date})
