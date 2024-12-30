import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime

# Function Definitions
def fetch_historical_data(symbol, start_date, end_date):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)
        if data.empty:
            raise ValueError("No data fetched for the given date range.")
        return data[['Open', 'Close', 'High', 'Low']]
    except Exception as e:
        st.error(f"Error fetching historical data: {e}")
        raise

def process_monthly_prices_by_year(data):
    try:
        data['Average Price'] = (data['Open'] + data['Close'] + data['High'] + data['Low']) / 4
        data['Month'] = data.index.month
        data['Year'] = data.index.year
        return data.groupby(['Year', 'Month'])['Average Price'].mean().reset_index()
    except Exception as e:
        st.error(f"Error processing monthly prices by year: {e}")
        raise

def process_monthly_prices(data):
    try:
        data['Average Price'] = (data['Open'] + data['Close'] + data['High'] + data['Low']) / 4
        return data['Average Price'].resample('M').mean()
    except Exception as e:
        st.error(f"Error processing monthly prices: {e}")
        raise

def plot_monthly_comparisons(name, monthly_avg):
    try:
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        plt.figure(figsize=(12, 6))
        for year in monthly_avg['Year'].unique():
            yearly_data = monthly_avg[monthly_avg['Year'] == year]
            plt.plot(yearly_data['Month'], yearly_data['Average Price'], label=str(year))

        plt.xticks(range(1, 13), months)
        plt.title(f'Monthly Average Prices for {name} (Jan-Dec, Separated by Year)', fontsize=16)
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Average Price (USD)', fontsize=12)
        plt.legend(title='Year', fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(plt)
    except Exception as e:
        st.error(f"Error plotting monthly comparisons: {e}")

def plot_monthly_prices(name, monthly_prices):
    try:
        plt.figure(figsize=(12, 6))
        monthly_prices.plot(label=name, marker='o', color='teal', linestyle='--')
        plt.title(f'Monthly Average Prices for {name}', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Average Price (USD)', fontsize=12)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(plt)
    except Exception as e:
        st.error(f"Error plotting monthly prices: {e}")

# Streamlit UI
st.set_page_config(page_title="Cryptocurrency Dashboard", layout="wide")
st.title("📊 Cryptocurrency Dashboard")

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
        monthly_avg = process_monthly_prices_by_year(data)
        monthly_prices = process_monthly_prices(data)

        # Create Columns for Visualizations
        col1, col2 = st.columns(2)

        with col1:
            st.header(f"{selected_crypto} Monthly Price Chart")
            plot_monthly_prices(selected_crypto, monthly_prices)

        with col2:
            st.header(f"{selected_crypto} Year-Wise Monthly Comparison")
            plot_monthly_comparisons(selected_crypto, monthly_avg)

    except Exception as e:
        st.error(f"Failed to fetch or process data for {selected_crypto}: {e}")
