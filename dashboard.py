import yfinance as yf
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# ---------------------------------------
# Page Config
# ---------------------------------------
st.set_page_config(page_title="Cryptocurrency Dashboard", layout="wide")
st.title("📊 Cryptocurrency Dashboard")

# ---------------------------------------
# Cached Data Fetching
# ---------------------------------------
@st.cache_data
def fetch_historical_data(symbol, start_date, end_date):
    ticker = yf.Ticker(symbol)
    data = ticker.history(start=start_date, end=end_date)

    if data.empty:
        raise ValueError("No data fetched for the given date range.")

    data = data.dropna()
    data.index = pd.to_datetime(data.index)

    return data[['Open', 'Close', 'High', 'Low']]


# ---------------------------------------
# Processing Functions
# ---------------------------------------
def process_daily_fluctuation(data):
    df = data.copy()
    df['Fluctuation'] = df['High'] - df['Low']
    df['Date'] = df.index
    return df[['Date', 'Fluctuation']]


def process_monthly_avg(data):
    df = data.copy()
    df['Average Price'] = (df['Open'] + df['Close'] + df['High'] + df['Low']) / 4
    df['Month'] = df.index.month
    df['Year'] = df.index.year

    monthly_avg = df.groupby(['Year', 'Month'])['Average Price'].mean().reset_index()
    monthly_avg['Date'] = monthly_avg.apply(
        lambda row: datetime(int(row['Year']), int(row['Month']), 1),
        axis=1
    )
    return monthly_avg


def best_performing_week(data):
    df = data.copy()
    df['Week'] = df.index.to_period('W')
    df['Average Price'] = (df['Open'] + df['Close'] + df['High'] + df['Low']) / 4

    weekly_avg = df.groupby('Week')['Average Price'].mean().reset_index()
    best_week = weekly_avg.loc[weekly_avg['Average Price'].idxmax()]

    return best_week['Week'], best_week['Average Price'], weekly_avg


def best_performing_week_by_month(data):
    df = data.copy()
    df['Week'] = df.index.to_period('W')
    df['Month'] = df.index.month
    df['Year'] = df.index.year
    df['Average Price'] = (df['Open'] + df['Close'] + df['High'] + df['Low']) / 4

    weekly_avg = df.groupby(['Year', 'Month', 'Week'])['Average Price'].mean().reset_index()

    best_weeks = weekly_avg.loc[
        weekly_avg.groupby(['Year', 'Month'])['Average Price'].idxmax()
    ]

    return best_weeks


def monthly_comparison(data, selected_months):
    df = data.copy()
    df['Average Price'] = (df['Open'] + df['Close'] + df['High'] + df['Low']) / 4
    df['Month'] = df.index.month
    df['Year'] = df.index.year

    monthly_comp = df.groupby(['Year', 'Month'])['Average Price'].mean().reset_index()
    monthly_comp['Month Name'] = monthly_comp['Month'].apply(
        lambda x: datetime(1900, x, 1).strftime('%B')
    )

    if selected_months:
        monthly_comp = monthly_comp[monthly_comp['Month Name'].isin(selected_months)]

    return monthly_comp


def plot_live_graph(data, x_column, y_column, title):
    fig = px.line(
        data,
        x=x_column,
        y=y_column,
        title=title,
        labels={x_column: "Date", y_column: "Value"}
    )
    fig.update_traces(line=dict(width=2))
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------
# Crypto List
# ---------------------------------------
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

# ---------------------------------------
# User Inputs
# ---------------------------------------
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Start Date", value=datetime(2021, 1, 1))

with col2:
    end_date = st.date_input("End Date", value=datetime(2024, 12, 25))

# Date Validation
if start_date >= end_date:
    st.error("End date must be after start date.")
    st.stop()

selected_crypto = st.selectbox("Select Cryptocurrency", list(crypto_list.keys()))

selected_months = st.multiselect(
    "Select Months for Comparison",
    [datetime(1900, i, 1).strftime('%B') for i in range(1, 13)]
)

# ---------------------------------------
# Main Execution
# ---------------------------------------
if selected_crypto:

    symbol = crypto_list[selected_crypto]
    st.subheader(f"Visualizations for {selected_crypto} ({symbol})")

    try:
        data = fetch_historical_data(symbol, start_date, end_date)

        # Daily Fluctuation
        st.header("Daily Price Fluctuation")
        daily_fluctuation = process_daily_fluctuation(data)
        plot_live_graph(daily_fluctuation, 'Date', 'Fluctuation',
                        f"Daily Price Fluctuation for {selected_crypto}")

        # Monthly Average
        st.header("Monthly Average Prices")
        monthly_avg = process_monthly_avg(data)
        plot_live_graph(monthly_avg, 'Date', 'Average Price',
                        f"Monthly Average Prices for {selected_crypto}")

        # Best Week Overall
        st.header("Best Performing Week")
        best_week, best_week_price, weekly_avg_data = best_performing_week(data)

        st.success(
            f"Best Performing Week Overall: {best_week} "
            f"with an average price of ${best_week_price:.2f}"
        )

        weekly_avg_data['Week'] = weekly_avg_data['Week'].astype(str)

        fig = px.bar(
            weekly_avg_data,
            x='Week',
            y='Average Price',
            title="Weekly Average Prices"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Best Week by Month
        st.header("Best Performing Weeks by Month")
        best_weeks_by_month = best_performing_week_by_month(data)
        best_weeks_by_month['Week'] = best_weeks_by_month['Week'].astype(str)

        fig = px.bar(
            best_weeks_by_month,
            x='Week',
            y='Average Price',
            color='Year',
            title="Best Performing Weeks Across Years"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Monthly Comparison
        if selected_months:
            st.header("Monthly Comparisons Across Years")
            monthly_comp = monthly_comparison(data, selected_months)

            for month in monthly_comp['Month Name'].unique():
                st.subheader(f"{month} Comparison")
                month_data = monthly_comp[
                    monthly_comp['Month Name'] == month
                ]

                fig = px.bar(
                    month_data,
                    x='Year',
                    y='Average Price',
                    color='Year',
                    title=f"{month} Comparison Across Years"
                )

                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
