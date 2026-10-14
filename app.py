import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

DATA_FILE = "311_2025_dashboard.csv"

st.set_page_config(page_title="311 Dashboard", layout="wide")
st.title("2025 311 Requests Dashboard")


# 1. Read the data (cached, so the file is only read once)
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    # Same conversion as the notebook; normalize() drops any time of day
    df["request_date"] = pd.to_datetime(df["request_date"], errors="coerce").dt.normalize()
    return df


df = load_data()

# 2. Date controls: these replace START_DATE and END_DATE
min_date = df["request_date"].min().date()
max_date = df["request_date"].max().date()

st.sidebar.header("Choose a date range")
start_date = st.sidebar.date_input(
    "Start date", value=min_date, min_value=min_date, max_value=max_date
)
end_date = st.sidebar.date_input(
    "End date", value=max_date, min_value=min_date, max_value=max_date
)

# Same check as the notebook, but shown as a message instead of an error
if start_date > end_date:
    st.sidebar.error("Start date must be on or before end date.")
    st.stop()

# 3. Filter the DataFrame (same logic as the notebook)
filtered_df = df[
    (df["request_date"] >= pd.to_datetime(start_date))
    & (df["request_date"] <= pd.to_datetime(end_date))
].copy()

st.write(f"Selected period: {start_date} through {end_date}")
st.write(f"Requests in selected period: {len(filtered_df):,}")

if filtered_df.empty:
    st.warning("No requests in this date range.")
    st.stop()

# 4. Charts: same code as the notebook, with st.pyplot instead of plt.show
col1, col2 = st.columns(2)

with col1:
    top_requests = filtered_df["service_name"].value_counts().head(10).sort_values()
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    top_requests.plot(kind="barh", ax=ax1, title="Top 10 Types of 311 Requests")
    ax1.set_xlabel("Number of Requests")
    ax1.set_ylabel("Service Type")
    fig1.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

with col2:
    requests_by_day = filtered_df.groupby("request_date").size()
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    requests_by_day.plot(kind="line", ax=ax2, title="311 Requests Over Time")
    ax2.set_xlabel("Request Date")
    ax2.set_ylabel("Number of Requests")
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)
