import json
import requests
import datetime as dt
import pandas as pd 
def get_bars(symbol, interval):
    """
    Collect data from Binance API
    """
    root_url = 'https://api.binance.com/api/v1/klines'
    url = root_url + '?symbol=' + symbol + '&interval=' + interval
    data = dict()
    data['limit'] = 1_000 # 290
    data = json.loads(requests.get(url, params=data).text)
    df = pd.DataFrame(data)
    df.columns = ['open_time',
                  'open', 'high', 'low', 'close', 'volume',
                  'close_time', 'qav', 'num_trades',
                  'taker_base_vol', 'taker_quote_vol', 'ignore']
    df.index = [dt.datetime.fromtimestamp(x/1000.0) for x in df.close_time]
    return df