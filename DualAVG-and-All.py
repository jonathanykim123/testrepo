import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from pathlib import Path
from datetime import date, datetime, timedelta
payload=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
first_table = payload[0]
# first_table.to_csv(r'first_table from wiki.cvs', sep=',', mode='a')
first_table_dropped = first_table.drop(['Security', 'SEC filings', 'Headquarters Location', 'CIK'], axis=1)
first_table_sorted = first_table_dropped.sort_values(by=['GICS Sector'])
first_column = first_table_sorted.iloc[:,0]
# function to buy and sell
def f_buy_sell(data):
    sigPriceBuy = []
    sigPriceSell = []
    flag = -1
    for i in range(len(data)):
        if data['SMA30'][i] > data['SMA100'][i]:
            if flag != 1:
                sigPriceBuy.append(data[sp_index][i])
                sigPriceSell.append(np.nan)
                flag = 1
            else:
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(np.nan)
        elif data['SMA30'][i] < data['SMA100'][i]:
            if flag != 0:
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(data[sp_index][i])
                flag = 0
            else:
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(np.nan)
        else:
            sigPriceBuy.append(np.nan)
            sigPriceSell.append(np.nan)
    return (sigPriceBuy, sigPriceSell)
#
for i in first_column:
    sp_index = i
    if '.' in sp_index:
        continue
    sp_index_tbl = yf.download(sp_index, start='2015-01-01')
    # create simple moving avg 30
    SMA30 = pd.DataFrame()
    SMA30['Adj Close'] = sp_index_tbl['Adj Close'].rolling(window=30).mean()
    # create simple moving avg 100
    SMA100 = pd.DataFrame()
    SMA100['Adj Close'] = sp_index_tbl['Adj Close'].rolling(window=100).mean()
    # -RSI
    MA200 = pd.DataFrame()
    MA200['Adj Close'] = sp_index_tbl['Adj Close'].rolling(window=200).mean()
    # RSI-
    data = pd.DataFrame()
    data[sp_index] = sp_index_tbl['Adj Close']
    data['SMA30'] = SMA30['Adj Close']
    data['SMA100'] = SMA100['Adj Close']
    # -RSI
    data['MA200'] = MA200['Adj Close']
    #
    data['price change'] = data[sp_index].pct_change()
    print (data)
    print('=== sp_index SMA30 SMA100 MA200 pct_change ===')
    data['Upmove'] = data['price change'].apply(lambda x: x if x > 0 else 0)
    data['Downmove'] = data['price change'].apply(lambda x: abs(x) if x < 0 else 0)
    data['avg Up'] = data['Upmove'].ewm(span=19).mean()
    data['avg Down'] = data['Downmove'].ewm(span=19).mean()
    data['RS'] = data['avg Up'] / data['avg Down']
    data['RSI'] = data['RS'].apply(lambda x: 100 - (100 / (x + 1)))
    data.loc[(data[sp_index] > data['MA200']) & (data['RSI'] < 30), 'Buy'] = data[sp_index]
    data.loc[(data[sp_index] < data['MA200']) | (data['RSI'] > 30), 'Buy'] = None
    print(data)
    print('=== after RSI ===')
    # RSI-
    buy_sell = f_buy_sell(data)
    data['Buy_Signal_Price'] = buy_sell[0]
    data['Sell_Signal_Price'] = buy_sell[1]
    #
    print(data)
    print(data.columns)
    print('=== after buy sell ===')
    # data.to_csv(r'C:/JK-Trade/QuantStart/Output/data_tbl_' + sp_index + '.cvs',sep=',', mode='a')
    # input('=== after buy sell MA ===')
    #
    # buy_sell_rows = data.dropna(thresh=12)
    buy_sell_rows = data.dropna(thresh=12)
    print(buy_sell_rows)
    print(buy_sell_rows.columns)
    print('=== after dropna ===')
    # input('$$$ buy_sell_rows before cvs$$$')
    if buy_sell_rows.empty:
        continue
    curr_date = pd.to_datetime('today').date()
    curr_date_str = curr_date.strftime("%Y-%m-%d")
    data.to_csv(r'C:/JK-Trade/QuantStart/Output/buy_sell_rows_' + sp_index + curr_date_str + '.cvs',sep=',', mode='a')
    # input('$$$ buy_sell_rows $$$')
    ## input('!!! buy_sell_rows with ...')
    #
    #
    #
    #lessthanmonth = True
    #for j in buy_sell_rows.index:
    #    idxtopydate = j.to_pydatetime().date()
    #    monthago = curr_date - timedelta(days = 30)
    #    lessthanmonth = True
    #    #if monthago < idxtopydate or buy_sell_rows[j,'Buy'] == 'Yes':
    #    if monthago < idxtopydate:
    #        lessthanmonth = False
    #        break
    #print('less tahn month',lessthanmonth)
    #if lessthanmonth:
    #    continue
    #input('$$$ out of loop ...')
    #
    #
    #
    # visualize data and strategy to buy and sell
    plt.figure(figsize=(12.5, 4.5))
    plt.plot(data[sp_index], label=sp_index, alpha=0.35)
    plt.plot(data['SMA30'], label='SMA30', alpha=0.35)
    plt.plot(data['SMA100'], label='SMA100', alpha=0.35)
    plt.scatter(data.index, data['Buy_Signal_Price'], label='Buy', marker='^', color='green')
    plt.scatter(data.index, data['Sell_Signal_Price'], label='Sell', marker='v', color='red')
    plt.scatter(data.index, data['Buy'], label='RSI Buy', marker='*', color='purple')
    plt.title('Adj Close Price History Buy and Sell Sig')
    plt.xlabel('2015-01-01 - ')
    plt.ylabel('Adj Closed Price USD ($)')
    plt.legend(loc='upper left')
    plt.savefig("C:/JK-Trade/QuantStart/Output/"+sp_index+"_"+curr_date_str+".JPG")
    #
# df_out = df_out.sort_values(by=['Pct Change'])
# result = pd.merge(left, right, on="key")
# df_out_merge = pd.merge(first_table_sorted, df_out, on="Symbol")
# df_out_merge = df_out_merge.sort_values(by=['Pct Change'])
# C:\JK-Trade\QuantStart\Output\VWILX.JPG')
# df_out_merge.to_csv(r'C:\JK-Trade\QuantStart\Output\sorted_tbl_'+d4+'.cvs', header=None, sep=',', mode='a')
# print(len(first_column))
# print(df_out)