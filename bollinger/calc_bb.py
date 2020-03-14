import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from airflow.operators.email_operator import EmailOperator
from airflow.hooks.base_hook import BaseHook

connection = BaseHook.get_connection("alphavantage")
API_KEY = connection.password


def plot():
    '''

    :return:
    '''

    # Read data
    df = pd.read_csv('./spy_data.csv')

    # Plot and save
    try:
        plt.ioff()
        ax = df.plot(x='Date', y='AdjClose', title='Bollinger Bands')
        df.plot(x='Date', y='roll_mean', label='rolling mean', ax=ax)
        df.plot(x='Date', y='ubb', ax=ax)
        df.plot(x='Date', y='lbb', ax=ax)
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.get_figure().savefig('./BollingerBands')

    except Exception as e:
        print(e)


def work_up_data(d: dict)-> pd.DataFrame:

    # Create the dataframe
    df = pd.DataFrame.from_dict(d)
    df = df.sort_values(by=['Date'])
    df = df.reset_index(drop=True)

    # Work-up the data
    df['AdjClose'] = df['AdjClose'].astype(float)
    df['Date'] = pd.to_datetime(df['Date'])
    df['roll_mean'] = df['AdjClose'].rolling(20).mean()
    df['roll_sd'] = df['AdjClose'].rolling(20).std()
    df['ubb'] = df['roll_mean'] + 2 * df['roll_sd']
    df['lbb'] = df['roll_mean'] - 2 * df['roll_sd']

    # Check Bollinger bands for action
    df['buy'] = np.where((df['AdjClose'] > df['lbb']) & (df['AdjClose'].shift() < df['lbb'].shift()), 1, 0)
    df['sell'] = np.where((df['AdjClose'] < df['ubb']) & (df['AdjClose'].shift() > df['ubb'].shift()), 1, 0)

    return df


def get_spy_data(**context):

    dates = []
    closings = []
    print('hello bollinger bands')
    r = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=SPY&apikey="+API_KEY)
    data_dict = r.json()['Time Series (Daily)']

    # Parse dict to capture desired info into lists
    for k,v in data_dict.items():
        dates.append(k)
        closings.append(v['5. adjusted close'])

    d = {'Date': dates, 'AdjClose': closings}

    stock_data = work_up_data(d)

    # Send email based on conditions
    if stock_data.iloc[-1]['buy'] == 1:
        print("BUY!!!!")
        email = EmailOperator(task_id="email_task",
                              to="seanmsolberg@gmail.com",
                              subject="BUT SOME SPY STOCK!",
                              html_content="Bollinger bands say to buy some SPY",
                              dag=context.get("dag"))

        email.execute(context=context)

    if stock_data.iloc[-1]['sell'] == 1:
        print("SELL!!!!")
        email = EmailOperator(task_id="email_task",
                              to="seanmsolberg@gmail.com",
                              subject="SELL SOME SPY STOCK!",
                              html_content="Bollinger bands say to sell SPY",
                              dag=context.get("dag"))

    # Populate db
    stock_data.to_csv('./spy_data.csv')



if __name__ == '__main__':
    get_spy_data()



