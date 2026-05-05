mport streamlit as st
import yfinance as yf
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="Stock & Dividend Tracker", layout="wide")

st.title("📈 Stock Gains vs. Live Market")
st.markdown("Compare your initial investment and dividends against real-time market data.")

# --- SIDEBAR: PORTFOLIO INPUT ---
st.sidebar.header("Add to Portfolio")
with st.sidebar.form("input_form", clear_on_submit=True):
    ticker = st.text_input("Ticker Symbol (e.g., AAPL, TSLA)").upper()
    shares = st.number_input("Number of Shares", min_value=0.0, step=1.0)
    buy_price = st.number_input("Average Buy Price ($)", min_value=0.0, step=0.01)
    total_dividends = st.number_input("Total Dividends Received ($)", min_value=0.0, step=0.01)
    add_data = st.form_submit_button("Add Stock")

# Initialize portfolio in session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []

if add_data and ticker:
    st.session_state.portfolio.append({
        "Ticker": ticker,
        "Shares": shares,
        "Buy Price": buy_price,
        "Dividends": total_dividends
    })

# --- DATA PROCESSING ---
if st.session_state.portfolio:
    df = pd.DataFrame(st.session_state.portfolio)
    
    def get_live_data(symbol):
        try:
            stock = yf.Ticker(symbol)
            # Fetch the most recent closing price
            price = stock.fast_info['last_price']
            return round(price, 2)
        except:
            return 0.0

    with st.spinner('Fetching live market prices...'):
        df['Current Price'] = df['Ticker'].apply(get_live_data)

    # Calculations
    df['Cost Basis'] = df['Shares'] * df['Buy Price']
    df['Current Value'] = df['Shares'] * df['Current Price']
    df['Price Gain/Loss'] = df['Current Value'] - df['Cost Basis']
    df['Total Gain ($)'] = df['Price Gain/Loss'] + df['Dividends']
    df['ROI (%)'] = (df['Total Gain ($)'] / df['Cost Basis']) * 100

    # --- DASHBOARD METRICS ---
    total_invested = df['Cost Basis'].sum()
    total_value = df['Current Value'].sum()
    total_divs = df['Dividends'].sum()
    net_gain = (total_value + total_divs) - total_invested

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Invested", f"${total_invested:,.2f}")
    col2.metric("Portfolio Value", f"${total_value:,.2f}")
    col3.metric("Dividends Collected", f"${total_divs:,.2f}")
    col4.metric("Net Total Gain", f"${net_gain:,.2f}", delta=f"{((net_gain/total_invested)*100):.2f}%" if total_invested > 0 else None)

    st.divider()

    # --- PORTFOLIO TABLE ---
    st.subheader("Your Holdings")
    
    # Styling the dataframe
    def color_gains(val):
        color = 'green' if val > 0 else 'red'
        return f'color: {color}'

    st.dataframe(df.style.map(color_gains, subset=['Price Gain/Loss', 'Total Gain ($)', 'ROI (%)']))

    if st.button("Clear Portfolio"):
        st.session_state.portfolio = []
        st.rerun()
else:
    st.info("Your portfolio is empty. Use the sidebar to add stocks.")

# --- FOOTER ---
st.caption("Data provided by Yahoo Finance via yfinance library. Prices may be delayed.")
