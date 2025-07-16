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
multiplier = st.number_input("Enter a multiplier to apply to revenue", min_value=0.0, value=1.0, step=0.1)

# --- CALCULATE ADJUSTED REVENUE ---
df['adjusted_revenue'] = df['revenue'] * multiplier

# --- PLOT STACKED BAR CHART ---
fig = go.Figure()
fig.add_trace(go.Bar(x=df['date'], y=df['revenue'], name='Original Revenue'))
fig.add_trace(go.Bar(x=df['date'], y=df['adjusted_revenue'], name=f'Adjusted Revenue (x{multiplier})'))

# Set Y-axis to start at 0
max_y = (df['revenue'] + df['adjusted_revenue']).max()

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