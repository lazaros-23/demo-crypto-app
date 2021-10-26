import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import datetime as dt
from get_binance_data import get_bars

st.title('Crypto price-news correlation builder')
symbol = st.text_input("Crypto symbol",value='NMRUSDT')
select_interval = ('1d', '1h')


root_url = 'https://api.binance.com/api/v1/klines'
#symbol = st.selectbox('Select coin:', select_symbol) 
interval = st.selectbox('Select interval', select_interval)
url = root_url + '?symbol=' + symbol + '&interval=' + interval


df = get_bars(symbol,interval)

def draw_candle_sticks(df, intra = False):
    
    if intra:
        df["open_time_date"] = df["open_time"].str.split(" ").apply(lambda x: x[0])

    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric)

    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')


    fig = go.Figure(data=[go.Candlestick(x=df["open_time"],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'])])




    features = ['open_time', 'close_time',
                'open','high','low','close','volume','num_trades']

    df = df[features].copy(deep=True)


    window = 20

    df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
    df[f'MA_{window}'] = df['typical_price'].rolling(window).mean()
    df[f'STD_{window}'] = df['typical_price'].rolling(window).std()


    std_times = 2

    df['bollinger_up'] = df['typical_price'] + std_times * df[f"STD_{window}"] 
    df['bollinger_down'] = df['typical_price'] - std_times * df[f"STD_{window}"] 

    df['above_bound'] = (df['bollinger_up'] < df['high'])
    df['below_bound'] = (df['bollinger_down'] > df['low'])

    def create_cross_bounds(row):
        if row['above_bound'] :
            return 'above'
        elif row['below_bound'] :
            return 'below'
        else:
            return 'neutral'
        
    df["cross_bounds"] = df.apply(lambda row: create_cross_bounds(row), axis=1)

    fig = go.Figure(data=[go.Candlestick(x=df["open_time"],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'])])

    fig.update_layout(
        yaxis_title="USDT",
        title={
            'text': symbol + " Price and cross-points",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    # MA plot
    fig.add_trace(
        go.Scatter(
            x = df["open_time"],
            y = df[f"MA_{window}"],
            name = "Moving average",
            mode="lines",
            line=go.scatter.Line(color="black", dash="dash"),
            showlegend=True)
    )


    # Upper bound
    fig.add_trace(
        go.Scatter(
            x= df["open_time"],
            y= df[f"MA_{window}"] + std_times * df[f"STD_{window}"],
            name = "Upper bound",
            mode="lines",
            line=go.scatter.Line(color="lightgreen"),
            showlegend=True)
    )

    # Lower bound
    fig.add_trace(
        go.Scatter(
            x = df["open_time"],
            y = df[f"MA_{window}"] - std_times * df[f"STD_{window}"],
            name = "Lower bound",
            mode="lines",
            line=go.scatter.Line(color="firebrick"),
            showlegend=True)
    )


    ## Plot crossing points

    low_value = int(df[['open','high','low','close']].min().min() - 10)

    fig.add_trace(go.Scatter(
        x = df.loc[df['above_bound'], "open_time"],
        y = np.repeat(low_value, len(df.loc[df['above_bound'], "open_time"])),
        marker=dict(color="green", size=4),
        mode="markers",
        name = 'above_boundary'
    ))


    fig.add_trace(go.Scatter(
        x = df.loc[df['below_bound'], "open_time"],
        y = np.repeat(low_value, len(df.loc[df['below_bound'], "open_time"])),
        marker=dict(color="crimson", size=4),
        mode="markers",
        name = 'below_boundary'
    ))

    return (st.plotly_chart(fig))

draw_candle_sticks(df,intra = False)

st.subheader('Go intra-day')

interested_day = st.date_input('Select interesting date')

df_intra_day = get_bars(symbol,'1H')

draw_candle_sticks(df_intra_day, intra = True)
