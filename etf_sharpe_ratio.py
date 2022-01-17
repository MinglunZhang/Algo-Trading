import sys
from pip._vendor import requests
import numpy as np
import pandas as pd
from datetime import datetime
import yfinance as yf


def getSymbolList():
    etf_list = pd.DataFrame(None)
    urls = ['https://etfdb.com/compare/highest-52-week-returns/',
            'https://etfdb.com/compare/highest-13-week-returns/',
            'https://etfdb.com/compare/highest-weekly-returns/',
            'https://etfdb.com/compare/highest-monthly-returns/',
            'https://etfdb.com/compare/highest-3-year-returns/',
            'https://etfdb.com/compare/highest-5-year-returns/',
            'https://etfdb.com/compare/highest-ytd-returns/']
    for url in urls:
        html = requests.get(url).content
        df = pd.read_html(html)[0]
        etf_list = pd.concat([etf_list, df], ignore_index=True)
    etf_list = etf_list.drop_duplicates(subset=['Symbol'], keep="first", inplace=False)
    etf_list = etf_list[['Symbol']].reset_index(drop=True)
    etf_list[['1ySharpe', '6mSharpe', '3mSharpe', '1mSharpe', '1yReturn', '6mReturn', '3mReturn', '1mReturn']] = ['', '', '', '', '', '', '', '']
    return etf_list


def sharpe_ratio(sym, start, end):
    sharpe12, sharpe6, sharpe3, sharpe1 = np.NaN, np.NaN, np.NaN, np.NaN
    rtn12, rtn6, rtn3, rtn1 = np.NaN, np.NaN, np.NaN, np.NaN
    try:
        df = yf.Ticker(sym).history(start=start, end=end)
        df['Daily Return'] = df['Close'].pct_change(1)
        size = len(df)
        sharpe12 = df['Daily Return'].mean() / df['Daily Return'].std()
        sharpe6 = df['Daily Return'][size // 2:].mean() / df['Daily Return'][size // 2:].std()
        sharpe3 = df['Daily Return'][3 * size // 4:].mean() / df['Daily Return'][3 * size // 4:].std()
        sharpe1 = df['Daily Return'][11 * size // 12:].mean() / df['Daily Return'][11 * size // 12:].std()
        df = df.reset_index(drop=True)
        rtn12 = df.iloc[-1]['Close'] / df.loc[0]['Close'] - 1
        rtn6 = df.iloc[-1]['Close'] / df.loc[size // 2]['Close'] - 1
        rtn3 = df.iloc[-1]['Close'] / df.loc[3 * size // 4]['Close'] - 1
        rtn1 = df.iloc[-1]['Close'] / df.loc[11 * size // 12]['Close'] - 1
    except:
        print("error: " + sym)
    return sharpe12, sharpe6, sharpe3, sharpe1, rtn12, rtn6, rtn3, rtn1


def main():
    etf_list = getSymbolList()
    start = str(datetime.now().year - 1) + "-" + str(datetime.now().month) + "-" + str(datetime.now().day)
    end = str(datetime.now().year) + "-" + str(datetime.now().month) + "-" + str(datetime.now().day)
    for index, sym in enumerate(etf_list['Symbol']):
        print(index)
        etf_list.loc[index][['1ySharpe', '6mSharpe', '3mSharpe', '1mSharpe', '1yReturn', '6mReturn', '3mReturn', '1mReturn']] = sharpe_ratio(sym, start, end)
    etf_list = etf_list.dropna()
    etf_list.to_excel("ETF_list.xlsx", index=False)
    return 0


if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
