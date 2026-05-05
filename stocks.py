import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Pro Stock Tracker", layout="wide")

# --- INITIALIZE PORTFOLIO ---
# We store the portfolio as a dictionary { Ticker: {Shares, Buy Price, Dividends} }
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

st.title("📈 Pro Stock & Dividend Tracker")

# --- SIDEBAR: ADD NEW STOCK ---
st.sidebar.header("Add New Holding")
with st.sidebar.form("input_form", clear_on_submit=True):
    new_ticker = st.text_input("Ticker Symbol").upper().strip()
    new_shares = st.number_input("Shares", min_value=0.0, step=0.1)
    new_buy_price = st.number_input("Avg Buy Price ($)", min_value=0.0, step=0.01)
    new_divs = st.number_input("Total Divs Received ($)", min_value=0.0, step=0.01)
    if st.form_submit_button("Add to Portfolio"):
        if new_ticker:
            st.session_state.portfolio[new_ticker] = {
                "Shares": new_shares,
                "Buy Price": new_buy_price,
                "Dividends": new_divs
            }
            st.rerun()

# --- MAIN LOGIC ---
if st.session_state.portfolio:
    # Convert dict to DataFrame for processing
    df = pd.DataFrame.from_dict(st.session_state.portfolio, orient='index').reset_index()
    df.columns = ['Ticker', 'Shares', 'Buy Price', 'Dividends']

    # Fetch Live Prices
    with st.spinner('Updating Market Prices...'):
        def fetch_price(t):
            try: return round(yf.Ticker(t).fast_info['last_price'], 2)
            except: return 0.0
        df['Current Price'] = df['Ticker'].apply(fetch_price)

    # Calculations
    df['Cost Basis'] = df['Shares'] * df['Buy Price']
    df['Current Value'] = df['Shares'] * df['Current Price']
    df['Gain/Loss'] = (df['Current Value'] - df['Cost Basis']) + df['Dividends']
    
    # Display Metrics
    total_cost = df['Cost Basis'].sum()
    total_val = df['Current Value'].sum()
    total_div = df['Dividends'].sum()
    net = (total_val + total_div) - total_cost
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Invested", f"${total_cost:,.2f}")
    m2.metric("Market Value", f"${total_val:,.2f}")
    m3.metric("Dividends", f"${total_div:,.2f}")
    m4.metric("Total Return", f"${net:,.2f}", delta=f"{(net/total_cost*100 if total_cost>0 else 0):.2f}%")

    st.divider()

    # --- EDIT / DELETE SECTION ---
    st.subheader("📋 Manage Your Portfolio")
    st.write("Edit values directly in the table or select a row to delete.")

    # 1. Edit Logic using st.data_editor
    # num_rows="dynamic" allows deleting rows by selecting them and pressing 'Delete'
    edited_df = st.data_editor(
        df[['Ticker', 'Shares', 'Buy Price', 'Dividends']], 
        num_rows="dynamic",
        key="portfolio_editor",
        use_container_width=True
    )

    # 2. Sync changes back to Session State
    if st.button("Save Changes"):
        # Rebuild the dictionary from the edited dataframe
        new_portfolio = {}
        for _, row in edited_df.iterrows():
            if pd.notnull(row['Ticker']) and row['Ticker'] != "":
                new_portfolio[row['Ticker']] = {
                    "Shares": row['Shares'],
                    "Buy Price": row['Buy Price'],
                    "Dividends": row['Dividends']
                }
        st.session_state.portfolio = new_portfolio
        st.success("Portfolio updated successfully!")
        st.rerun()

    # Display Gain/Loss Table (Read Only)
    st.subheader("📊 Performance Analysis")
    st.dataframe(df[['Ticker', 'Current Price', 'Cost Basis', 'Gain/Loss']].style.highlight_max(axis=0))

else:
    st.info("Start by adding a ticker symbol in the sidebar.")
