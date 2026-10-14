import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# --- Page setup ---
st.set_page_config(page_title="311 Request Dashboard", layout="wide")
st.title("2025 311 Request Dashboard")
st.write("Choose a date range to explore 311 requests.")

# Keep the CSV in the same folder as this app.py file.
DATA_FILE = "311_2025_dashboard.csv"

@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data["request_date"] = pd.to_datetime(data["request_date"], errors="coerce")
    data = data.dropna(subset=["request_date"])
    return data

try:
    df = load_data(DATA_FILE)
except FileNotFoundError:
    st.error(
        f"Could not find {DATA_FILE}. Put the CSV file in the same folder as app.py."
    )
    st.stop()

if df.empty:
    st.warning("The CSV has no rows with a valid request_date.")
    st.stop()

# Set the date controls to the earliest and latest dates in the dataset.
min_date = df["request_date"].min().date()
max_date = df["request_date"].max().date()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        "Start date",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
    )
with col2:
    end_date = st.date_input(
        "End date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
    )

if start_date > end_date:
    st.error("Start date must be on or before end date.")
    st.stop()

# Use an exclusive next-day boundary so requests on the end date are included,
# even if request_date contains a time of day.
start_timestamp = pd.Timestamp(start_date)
end_timestamp_exclusive = pd.Timestamp(end_date) + pd.Timedelta(days=1)

filtered_df = df[
    (df["request_date"] >= start_timestamp)
    & (df["request_date"] < end_timestamp_exclusive)
].copy()

st.subheader(f"Requests from {start_date:%b %d, %Y} through {end_date:%b %d, %Y}")
st.metric("Requests in selected period", f"{len(filtered_df):,}")

if filtered_df.empty:
    st.info("No requests were found in this date range.")
    st.stop()

# Chart 1: Top 10 service types (same analysis as the notebook).
st.subheader("Top 10 Types of 311 Requests")
top_requests = (
    filtered_df["service_name"]
    .value_counts()
    .head(10)
    .sort_values()
)

fig1, ax1 = plt.subplots(figsize=(8, 5))
top_requests.plot(kind="barh", ax=ax1)
ax1.set_xlabel("Number of Requests")
ax1.set_ylabel("Service Type")
fig1.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

# Chart 2: Number of requests per date (same analysis as the notebook).
st.subheader("311 Requests Over Time")
requests_by_day = filtered_df.groupby(filtered_df["request_date"].dt.date).size()

fig2, ax2 = plt.subplots(figsize=(9, 4))
requests_by_day.plot(kind="line", ax=ax2)
ax2.set_xlabel("Request Date")
ax2.set_ylabel("Number of Requests")
fig2.tight_layout()
st.pyplot(fig2)
plt.close(fig2)
