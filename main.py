import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Title
st.title("30-Day Revenue Visualization")

# --- CONFIGURATION ---

# Replace this with your actual published Google Sheet CSV URL
# Make sure your Google Sheet is published or set to "Anyone with link can view"
# google_sheet_url = "https://docs.google.com/spreadsheets/d/10bdbR_qubL5A6Aq760ufSgPilbx9TEL3bYHlQxzjpCo/export?format=csv"
csv_file = "data/daily-revenue.csv"

# --- LOAD DATA ---
@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    return df

try:
    df = load_data(csv_file)
except Exception as e:
    st.error(f"Failed to load data. Check the file location...\nError details: {e}")
    st.stop()

# --- USER INPUT ---
# multiplier = st.number_input("Enter a multiplier to apply to revenue", min_value=0.0, value=1.0, step=0.1)
with st.form(key='columns_in_form'):
    c1, c2, c3 = st.columns(3)
    with c1:
        close_fee_pct = st.number_input("Close Fee %", value=0.082, format="%.5f")
        commission_rate = st.number_input("Commission Rate", value=0.0469, format="%.5f")
        discount_adjustment_factor = st.number_input("Discount Adjustment Factor", value=0.95, format="%.5f")
    with c2:
        renewal_rate = st.number_input("Renewal Rate", value=1.2175, format="%.5f")
        renewals_bonus = st.number_input("Renewals Bonus %", value=0.002, format="%.5f")
        new_sales_regular_bonus = st.number_input("New Sales Regular Bonus %", value=0.021, format="%.5f")
        new_sales_expansion_bonus = st.number_input("New Sales Expansion Bonus %", value=0.021, format="%.5f")
    with c3:
        renewal_commissions_forecast = st.number_input("Renewal Commissions Forecast", min_value=1, value=1227379)
        current_month_606_release = st.number_input("Current Month 606 Release", min_value=1, value=742730)
        prior_month_606_revised = st.number_input("Prior Month 606 Revised", min_value=1, value=437773)
        unassigned_revenue_estimate = st.number_input("Unassigned Revenue Estimate", min_value=1, value=254406)

    submitButton = st.form_submit_button(label='Calculate')

# plugs
unassigned_revenue_pct = unassigned_revenue_estimate / renewal_commissions_forecast


# --- CALCULATIONS ---
df['vintage_view'] = df['revenue'] / close_fee_pct
df['renewal_estimate'] = df['vintage_view'] * renewal_rate * commission_rate * discount_adjustment_factor
df['new_sales_bonus_estimate'] = df['vintage_view'] * new_sales_regular_bonus
df['renewals_bonus_estimate'] = df['vintage_view'] * renewal_rate * renewals_bonus
df['unassigned_renewals_estimate'] = df['renewal_estimate'] * unassigned_revenue_pct
df['plug_606'] = (prior_month_606_revised + prior_month_606_revised) / df['date'].count()

# df['adjusted_revenue'] = df['revenue'] * multiplier

# --- PLOT STACKED BAR CHART ---
fig = go.Figure()
fig.add_trace(go.Bar(x=df['date'], y=df['revenue'], name='Original Modeled Revenue'))
fig.add_trace(go.Bar(x=df['date'], y=df['renewal_estimate'], name='Renewals Estimate'))
fig.add_trace(go.Bar(x=df['date'], y=df['new_sales_bonus_estimate'], name='New Sales Bonus Estimate'))
fig.add_trace(go.Bar(x=df['date'], y=df['renewals_bonus_estimate'], name='Future Renewals Bonus Estimate'))
fig.add_trace(go.Bar(x=df['date'], y=df['unassigned_renewals_estimate'], name='Future Renewals Bonus Estimate'))
fig.add_trace(go.Bar(x=df['date'], y=df['plug_606'], name='606 Adjustment plug'))

# Set Y-axis to start at 0
max_y = (df['revenue'] + df['renewal_estimate'] + df['new_sales_bonus_estimate'] +
         df['renewals_bonus_estimate'] + df['unassigned_renewals_estimate'] + df['plug_606']).max()

fig.update_layout(
    barmode='stack',
    title="Stacked Revenue Visualization",
    xaxis_title="Date",
    yaxis_title="Total Revenue",
    yaxis=dict(range=[0, max_y * 1.1]),
    hovermode="x unified",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)