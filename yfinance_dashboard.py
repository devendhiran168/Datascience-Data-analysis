import yfinance as yf
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# Function Definitions
def fetch_historical_data(symbol, start_date, end_date):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)
        if data.empty:
            raise ValueError("No data fetched for the given date range.")
        # Drop rows with NaN values
        data = data.dropna()
        return data[['Open', 'Close', 'High', 'Low']]
    except Exception as e:
        st.error(f"Error fetching historical data: {e}")
        raise

def process_daily_fluctuation(data):
    try:
        data['Fluctuation'] = data['High'] - data['Low']
        return data[['Fluctuation']]
    except Exception as e:
        st.error(f"Error processing daily fluctuations: {e}")
        raise

def process_monthly_avg(data):
    try:
        data['Average Price'] = (data['Open'] + data['Close'] + data['High'] + data['Low']) / 4
        data['Month'] = data.index.month
        data['Year'] = data.index.year
        return data.groupby(['Year', 'Month'])['Average Price'].mean().reset_index()
    except Exception as e:
        st.error(f"Error processing monthly average prices: {e}")
        raise

def filter_month_data(data, month):
    try:
        data['Month'] = data.index.month
        data['Year'] = data.index.year
        return data[data['Month'] == month]
    except Exception as e:
        st.error(f"Error filtering data by month: {e}")
        raise

def best_performing_week(data):
    try:
        data['Week'] = data.index.to_period('W')
        data['Average Price'] = (data['Open'] + data['Close'] + data['High'] + data['Low']) / 4
        weekly_avg = data.groupby('Week')['Average Price'].mean()
        return weekly_avg.idxmax(), weekly_avg.max()
    except Exception as e:
        st.error(f"Error identifying best performing week: {e}")
        raise

def best_performing_week_by_month(data):
    try:
        data['Week'] = data.index.to_period('W')
        data['Month'] = data.index.month
        data['Year'] = data.index.year
        data['Average Price'] = (data['Open'] + data['Close'] + data['High'] + data['Low']) / 4
        weekly_avg = data.groupby(['Year', 'Month', 'Week'])['Average Price'].mean().reset_index()
        best_weeks = weekly_avg.loc[weekly_avg.groupby(['Year', 'Month'])['Average Price'].idxmax()]
        return best_weeks
    except Exception as e:
        st.error(f"Error identifying best performing weeks by month: {e}")
        raise

def plot_live_graph(data, name, y_column, title):
    try:
        fig = px.line(data, x=data.index, y=y_column, title=title, labels={"index": "Date", y_column: "Value"})
        fig.update_traces(line=dict(width=2))
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error plotting live graph: {e}")

def plot_filtered_month(data, name, month):
    try:
        month_name = datetime(2021, month, 1).strftime('%B')
        data['Date'] = data.index
        filtered_data = data[data['Month'] == month]
        fig = px.line(filtered_data, x='Date', y='Average Price', title=f"{name}: Average Price for {month_name}")
        fig.update_layout(xaxis_title='Date', yaxis_title='Average Price (USD)', template="plotly_dark")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error plotting filtered month data: {e}")

# Streamlit UI
st.set_page_config(page_title="Cryptocurrency Dashboard", layout="wide")
st.title("\U0001F4CA Cryptocurrency Dashboard")

crypto_list = {
    'Avalanche': 'AVAX-USD',
    'Chainlink': 'LINK-USD',
    'Toncoin': 'TON-USD',
    'Shiba Inu': 'SHIB-USD',
    'Sui': 'SUI-USD',
    'Stellar': 'XLM-USD',
    'Polkadot': 'DOT-USD',
    'Hedera': 'HBAR-USD',
    'Bitcoin Cash': 'BCH-USD',
    'UNUS SED LEO': 'LEO-USD'
}

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Start Date", value=datetime(2021, 1, 1))
with col2:
    end_date = st.date_input("End Date", value=datetime(2024, 12, 25))

selected_crypto = st.selectbox("Select Cryptocurrency", list(crypto_list.keys()))

if selected_crypto:
    symbol = crypto_list[selected_crypto]
    st.subheader(f"Visualizations for {selected_crypto} ({symbol})")

    try:
        # Fetch and Process Data
        data = fetch_historical_data(symbol, start_date, end_date)
        data.index = pd.to_datetime(data.index)  # Ensure datetime index

        # Daily Fluctuation
        st.header(f"{selected_crypto} Daily Price Fluctuation (Live)")
        daily_fluctuation = process_daily_fluctuation(data)
        plot_live_graph(daily_fluctuation, selected_crypto, 'Fluctuation', f"Daily Price Fluctuation for {selected_crypto}")

        # Monthly Average Prices
        st.header(f"{selected_crypto} Monthly Average Prices (Live)")
        monthly_avg = process_monthly_avg(data)
        monthly_avg['Date'] = monthly_avg.apply(lambda row: datetime(int(row['Year']), int(row['Month']), 1), axis=1)
        plot_live_graph(monthly_avg.set_index('Date'), selected_crypto, 'Average Price', f"Monthly Average Prices for {selected_crypto}")

        # Filter for Specific Month
        st.header(f"{selected_crypto} Filter Data by Month")
        month_filter = st.selectbox("Select Month", range(1, 13), format_func=lambda x: datetime(2021, x, 1).strftime('%B'))
        data['Average Price'] = (data['Open'] + data['Close'] + data['High'] + data['Low']) / 4
        data['Month'] = data.index.month
        plot_filtered_month(data, selected_crypto, month_filter)

        # Best Performing Week
        st.header(f"{selected_crypto} Best Performing Week")
        best_week, best_week_price = best_performing_week(data)
        st.write(f"Best Performing Week Overall: {best_week} with an average price of ${best_week_price:.2f}")

        # Comparing Performing Weeks
        st.header(f"Comparing Best Performing Weeks Across Years")
        best_weeks_by_month = best_performing_week_by_month(data)
        best_weeks_by_month['Month'] = best_weeks_by_month['Week'].apply(lambda x: x.start_time.month)
        plot_live_graph(best_weeks_by_month, selected_crypto, 'Average Price', f"Best Performing Weeks for {selected_crypto}")

    except Exception as e:
        st.error(f"Failed to fetch or process data for {selected_crypto}: {e}")
