
import os
import pandas as pd
import requests
stock_symbols = [i for i in os.environ.get("STOCKS").split(" ")]


def get_data(stock: str)->pd.Dataframe:
    r = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=SPY&apikey="+API_KEY)
    data_dict = r.json()['Time Series (Daily)']

    return 0

def calc_rsi(stock: str='JPM', start_date: dt.datetime=dt.datetime(2008,1,1), end_date : dt.datetime = dt.datetime(2009,12,31))->None:

    lookback = 20
    stock_data = get_data([stock], pd.date_range(start_date, end_date), addSPY=True)
    stock_data.drop(['SPY'], axis=1, inplace=True)
    stock_data.loc[1:,'daily_returns'] = stock_data[stock].iloc[1:].values - stock_data[stock].iloc[:-1].values
    stock_data.reset_index(inplace=True)
    stock_data.rename(columns={'index': 'Date'}, inplace=True)

    stock_data['up_gain'] = np.zeros(stock_data.shape[0], dtype=float)
    stock_data['down_loss'] = np.zeros(stock_data.shape[0], dtype=float)
    stock_data['rsi'] = np.zeros(stock_data.shape[0], dtype=float)

    for day in range(lookback, stock_data.shape[0]):

        stock_data['up_gain'] = stock_data.loc[day-lookback+1:day+1,'daily_returns'].where(stock_data['daily_returns']>=0).sum()
        stock_data['down_loss'] = -1*stock_data.loc[day-lookback+1:day+1,'daily_returns'].where(stock_data['daily_returns']<0).sum()

        if stock_data.loc[day, 'down_loss'] == 0:
            stock_data.loc[day, 'rsi'] = 100
        else:
            rs = (stock_data.loc[day, 'up_gain'] / lookback) / (stock_data.loc[day, 'down_loss'] / lookback)
            stock_data.loc[day, 'rsi'] = 100-(100/(1+rs))

    stock_data['rsi'].values[:lookback] = np.nan

    # Plot data
    ax = stock_data.plot(x='Date', y='rsi', title=f'{lookback} Day RSI for {stock}')
    ax.set_xlabel("Date")
    ax.set_ylabel("RSI")
    plt.plot((start_date, end_date), (70, 70), linestyle='-', color='red')
    plt.plot((start_date, end_date), (30, 30), linestyle='-', color='red')
    plt.savefig('./RSI')


def calc_momentum(stock: str='JPM', start_date: dt.datetime=dt.datetime(2008,1,1), end_date : dt.datetime = dt.datetime(2009,12,31)):

    lookback = 20
    stock_data = get_data([stock], pd.date_range(start_date, end_date), addSPY=True)
    stock_data.drop(['SPY'], axis=1, inplace=True)
    stock_data.loc[1:,'daily_returns'] = stock_data[stock].iloc[1:].values - stock_data[stock].iloc[:-1].values
    stock_data.reset_index(inplace=True)
    stock_data.rename(columns={'index': 'Date'}, inplace=True)

    stock_data['momentum'] = np.zeros(stock_data.shape[0], dtype=float)
    stock_data.loc[:lookback-1,'momentum'] = np.nan
    stock_data.loc[lookback:, 'momentum'] = (stock_data.loc[lookback:, stock] - stock_data[stock].values[:-20]) / stock_data[stock].values[:-20]

    # Plot data
    ax = stock_data.plot(x='Date', y='momentum', title=f'{lookback} Day Momentum for Stock {stock}')
    ax.set_xlabel("Date")
    ax.set_ylabel("Momentum")
    ax.axhline(color='black')
    plt.savefig('./Momentum')


def calc_volatility(stock: str='JPM', lookback: int=20, start_date: dt.datetime=dt.datetime(2008,1,1), end_date : dt.datetime = dt.datetime(2009,12,31)):

    stock_data = get_data([stock], pd.date_range(start_date, end_date), addSPY=True)
    stock_data.drop(['SPY'], axis=1, inplace=True)
    stock_data.loc[1:, 'daily_returns'] = stock_data[stock].iloc[1:].values - stock_data[stock].iloc[:-1].values
    stock_data.reset_index(inplace=True)
    stock_data.rename(columns={'index': 'Date'}, inplace=True)

    stock_data.loc[1:,'daily_returns'] = stock_data[stock].iloc[1:].values - stock_data[stock].iloc[:-1].values

    stock_data['volatility'] = np.zeros(stock_data.shape[0], dtype=float)
    stock_data['volatility'] = stock_data['daily_returns'].rolling(lookback).std()

    # Plot data
    ax = stock_data.plot(x='Date', y='volatility', title=f'{lookback} Day Volatility for Stock {stock}')
    ax.set_xlabel("Date")
    ax.set_ylabel("Volatility Index")
    plt.savefig('./Volatility')


def calc_stochastic_oscillator(stock: str='JPM', lookback: int=15, start_date: dt.datetime=dt.datetime(2008,1,1), end_date : dt.datetime = dt.datetime(2008,12,31)):

    stock_data = get_data([stock], pd.date_range(start_date, end_date), addSPY=True)
    stock_data.drop(['SPY'], axis=1, inplace=True)
    stock_data.loc[1:,'daily_returns'] = stock_data[stock].iloc[1:].values - stock_data[stock].iloc[:-1].values
    stock_data.reset_index(inplace=True)
    stock_data.rename(columns={'index': 'Date'}, inplace=True)

    stock_data['max_five_day'] = stock_data[stock].rolling(lookback).max()
    stock_data['min_five_day'] = stock_data[stock].rolling(lookback).min()
    stock_data['pct_k'] = 100 * (stock_data[stock] - stock_data['min_five_day']) / (stock_data['max_five_day'] - stock_data['min_five_day'])
    stock_data['pct_d'] = stock_data['pct_k'].rolling(3).mean()

    # plot k and d, with reference lines at 80 and 20
    ax = stock_data.plot(x='Date', y='pct_k', linestyle='-', title=f'{lookback} Day Stochastic Oscillator for Stock {stock}')
    stock_data.plot(x='Date', y='pct_d', linestyle=':' ,ax=ax)
    plt.plot((start_date, end_date), (80, 80), linestyle='-', color='red')
    plt.plot((start_date, end_date), (20, 20), linestyle='-', color='red')
    xs = np.arange(start_date, end_date, dt.timedelta(1))
    plt.fill_between(xs, 20, 80, color='red', alpha='0.5')
    ax.set_xlabel("Date")
    ax.set_ylabel("Percent")
    plt.savefig('./StochasticOscillator')


def test_code():

    # Call technical indicator functions
    calc_bb()
    calc_rsi()
    calc_momentum()
    calc_volatility()
    calc_stochastic_oscillator()

if __name__ == '__main__':
    test_code()