#Credit to MARC
import requests
from lxml import html
from html import unescape
import pprint

headers = {'Accept': 'application/json',
  'X-Requested-With': 'XMLHttpRequest',
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
}

def search(query):
  res = requests.get('https://query2.finance.yahoo.com/v1/finance/search', headers=headers, timeout=20, params={
    'q': query,
    'quotesCount': 6,
    'newsCount': 0,
    'enableFuzzyQuery': True,
    'quotesQueryId': 'tss_match_phrase_query',
    'multiQuoteQueryId': 'multi_quote_single_token_query',
    'newsQueryId': 'news_cie_vespa',
    'enableCb': True,
    'enableNavLinks': True,
    'enableEnhancedTrivialQuery': True
    # lang=en-US&region=US
  })
  jd = res.json()
  return jd['quotes']

def readPageTree(url, headers={}):
  return html.fromstring(requests.get(url, headers=headers.update(headers)).content)

def xpath(pt, xp):
  try:
    return ''.join(map(lambda x: unescape(str(x).strip()), pt.xpath(xp)))
  except Exception:
    return None

def toNum(s):
  return float(str(s).replace(',',''))

