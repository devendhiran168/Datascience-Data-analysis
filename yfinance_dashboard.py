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
        data.index = pd.to_datetime(data.index)  # Ensure datetime index
        return data[['Open', 'Close', 'High', 'Low']]
    except Exception as e:
        st.error(f"Error fetching historical data: {e}")
        raise

def process_daily_fluctuation(data):
    try:
        data['Fluctuation'] = data['High'] - data['Low']
        data['Date'] = data.index  # Add Date column for visualization
        return data[['Date', 'Fluctuation']]
    except Exception as e:
        st.error(f"Error processing daily fluctuations: {e}")
        raise

def process_monthly_avg(data):
    try:
        data['Average Price'] = (data['Open'] + data['Close'] + data['High'] + data['Low']) / 4
        data['Month'] = data.index.month
        data['Year'] = data.index.year
        monthly_avg = data.groupby(['Year', 'Month'])['Average Price'].mean().reset_index()
        monthly_avg['Date'] = monthly_avg.apply(lambda row: datetime(int(row['Year']), int(row['Month']), 1), axis=1)
        return monthly_avg
    except Exception as e:
        st.error(f"Error processing monthly average prices: {e}")
        raise

def best_performing_week(data):
    try:
        data['Week'] = data.index.to_period('W')
        data['Average Price'] = (data['Open'] + data['Close'] + data['High'] + data['Low']) / 4
        weekly_avg = data.groupby('Week')['Average Price'].mean()
        return weekly_avg.idxmax(), weekly_avg.max(), weekly_avg.reset_index()
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

def monthly_comparison(data, selected_months):
    try:
        data['Average Price'] = (data['Open'] + data['Close'] + data['High'] + data['Low']) / 4
        data['Month'] = data.index.month
        data['Year'] = data.index.year
        monthly_comparison = data.groupby(['Year', 'Month'])['Average Price'].mean().reset_index()
        monthly_comparison['Month Name'] = monthly_comparison['Month'].apply(lambda x: datetime(1900, x, 1).strftime('%B'))
        if selected_months:
            monthly_comparison = monthly_comparison[monthly_comparison['Month Name'].isin(selected_months)]
        return monthly_comparison
    except Exception as e:
        st.error(f"Error processing monthly comparisons: {e}")
        raise

def plot_live_graph(data, x_column, y_column, title):
    try:
        fig = px.line(data, x=x_column, y=y_column, title=title, labels={x_column: "Date", y_column: "Value"})
        fig.update_traces(line=dict(width=2))
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error plotting live graph: {e}")

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
selected_months = st.multiselect("Select Months for Comparison",
                                 [datetime(1900, i, 1).strftime('%B') for i in range(1, 13)])

if selected_crypto:
    symbol = crypto_list[selected_crypto]
    st.subheader(f"Visualizations for {selected_crypto} ({symbol})")

    try:
        # Fetch and Process Data
        data = fetch_historical_data(symbol, start_date, end_date)

        # Daily Price Fluctuation
        st.header(f"{selected_crypto} Daily Price Fluctuation (Live)")
        daily_fluctuation = process_daily_fluctuation(data)
        plot_live_graph(daily_fluctuation, 'Date', 'Fluctuation', f"Daily Price Fluctuation for {selected_crypto}")

        # Monthly Average Prices
        st.header(f"{selected_crypto} Monthly Average Prices (Live)")
        monthly_avg = process_monthly_avg(data)
        plot_live_graph(monthly_avg, 'Date', 'Average Price', f"Monthly Average Prices for {selected_crypto}")

        # Best Performing Week
        st.header(f"{selected_crypto} Best Performing Week")
        best_week, best_week_price, weekly_avg_data = best_performing_week(data)
        st.write(f"Best Performing Week Overall: {best_week} with an average price of ${best_week_price:.2f}")

        weekly_avg_data['Week'] = weekly_avg_data['Week'].astype(str)
        fig = px.bar(weekly_avg_data, x='Week', y='Average Price', title=f"{selected_crypto}: Weekly Average Prices")
        fig.update_layout(xaxis_title='Week', yaxis_title='Average Price (USD)', template="plotly_dark")
        st.plotly_chart(fig)

        # Comparing Performing Weeks
        st.header(f"Comparing Best Performing Weeks Across Years")
        best_weeks_by_month = best_performing_week_by_month(data)
        best_weeks_by_month['Week'] = best_weeks_by_month['Week'].astype(str)
        fig = px.bar(best_weeks_by_month, x='Week', y='Average Price', color='Year',
                     title=f"Best Performing Weeks for {selected_crypto}",
                     labels={"Week": "Week", "Average Price": "Average Price (USD)"})
        fig.update_layout(xaxis_title='Week', yaxis_title='Average Price (USD)', template="plotly_dark")
        st.plotly_chart(fig)

        # Monthly Comparisons
        if selected_months:
            st.header(f"{selected_crypto} Monthly Comparisons Across Years")
            monthly_comparison_data = monthly_comparison(data, selected_months)
            for month in monthly_comparison_data['Month Name'].unique():
                st.subheader(f"{month} Comparison Across Years")
                month_data = monthly_comparison_data[monthly_comparison_data['Month Name'] == month]
                fig = px.bar(month_data, x='Year', y='Average Price', color='Year',
                             title=f"{selected_crypto}: {month} Comparison Across Years",
                             labels={"Year": "Year", "Average Price": "Average Price (USD)"})
                fig.update_layout(xaxis_title='Year', yaxis_title='Average Price (USD)', template="plotly_dark")
                st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Failed to fetch or process data for {selected_crypto}: {e}")
