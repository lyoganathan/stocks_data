import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import time

sns.set()

headers = {
'authority': 'api.nasdaq.com',
'scheme': 'https',
'accept': 'application/json, text/plain, */*',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'en-US,en;q=0.9',
'origin': 'https://www.nasdaq.com',
'referer': 'https://www.nasdaq.com/',
'sec-ch-ua': "'Google Chrome';v='89', Chromium';v='89', ';Not A Brand';v='99'",
'sec-ch-ua-mobile': '?0',
'sec-fetch-dest': 'empty',
'sec-fetch-mode': 'cors',
'sec-fetch-site': 'same-site',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36'
}

params = {'assetclass': 'etf',
        'fromdate': '2018-01-01',
        'todate': '2021-04-01'
}

etfs = ['SPY','QQQ','XOP', 'XLK', 'XLF', 'XLE', 'SLY', 'MDY', 
        'XLRE', 'RWR', 'SPMB', 'KBE', 'XLV', 'XPH', 'XLP', 'GLD',
        'DIA']

etfsDF = dict()
for etf in etfs:
    url = f'https://api.nasdaq.com/api/quote/{etf}/chart'
    r = requests.get(url, headers=headers, params=params)
    tickerDF = pd.DataFrame(r.json()['data']['chart'])
    tickerDF = tickerDF.drop(columns='z')
    tickerDF['date'] = pd.to_datetime(tickerDF['x'],unit='ms')
    tickerDF['ticker'] = etf
    tickerDF['y_diff'] = tickerDF['y'].diff()
    tickerDF['scaled'] = MinMaxScaler().fit_transform(tickerDF['y'].to_numpy().reshape(-1,1))
    tickerDF['pct_change_daily'] = tickerDF['y'].pct_change()
    tickerDF['pct_change_total'] = (tickerDF['y'] - tickerDF['y'][0])/tickerDF['y'][0] * 100
    
    etfsDF[etf] = tickerDF
    time.sleep(0.5)
    
combinedData = pd.concat([tickerData for tickerData in etfsDF.values()])


ax = sns.lineplot(x="date", y="pct_change_total", hue="ticker", 
                  data=combinedData[combinedData['ticker'].isin(['SPY','QQQ','DIA'])])
ax.set(xlabel='Date', ylabel='% Change since 2018', title='SPY vs QQQ vs DIA')
plt.xticks(rotation=45)
ax.legend(loc='best', bbox_to_anchor=(1, 0.5))
fig = ax.get_figure()
fig.savefig(r"pct_change_total.png",dpi=300,bbox_inches='tight')