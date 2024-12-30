import streamlit as st
import pandas as pd
import requests
import plotly.graph_objs as go

st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon="🌍",
    layout="wide",
)

# UI
st.markdown(
    """
    <style>
        /* Background */
        .stApp {
            background-color: #121212;
            color: white;
        }
        /* Headers */
        h1, h2, h3 {
            color: #FFD700;
            text-align: center;
        }
        /* Chart Containers */
        .chart-box {
            border: 2px solid #FFD700;
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
            background-color: #222222;
        }
        /* Buttons */
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 10px;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        /* Footer */
        footer {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def fetch_real_time_data():
    url = "https://api.thingspeak.com/channels/1596152/feeds.json?results=5"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["feeds"]
        df = pd.DataFrame(data)
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        df["PM2.5"] = pd.to_numeric(df["field1"], errors="coerce")
        df["PM10"] = pd.to_numeric(df["field2"], errors="coerce")
        df["Ozone"] = pd.to_numeric(df["field3"], errors="coerce")
        df["Humidity"] = pd.to_numeric(df["field4"], errors="coerce")
        df["Temperature"] = pd.to_numeric(df["field5"], errors="coerce")
        df["CO"] = pd.to_numeric(df["field6"], errors="coerce")

        # Drop rows with NaN values
        df = df.dropna(subset=["PM2.5", "PM10", "Ozone", "Humidity", "Temperature", "CO", "created_at"])

        return df
    else:
        st.error("Failed to fetch data. Please check the API.")
        return pd.DataFrame()



def create_chart(df, field, color):# for chart creation
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["created_at"],
        y=df[field],
        mode="lines+markers",
        name=field,
        line=dict(color=color),
    ))
    fig.update_layout(
        title=dict(text=field, x=0.5, font=dict(size=20, color=color)),
        xaxis_title="Time",
        yaxis_title="Value",
        yaxis=dict(range=[0, max(df[field].max() + 10, 70)]),
        template="plotly_dark",
        margin=dict(l=20, r=20, t=30, b=20),
    )
    return fig

st.markdown("<h1>🌍 Real-Time Air Quality Monitoring Dashboard 🌍</h1>", unsafe_allow_html=True)# title


st.markdown("## Refresh Data")# refresh button
if st.button("🔄 Refresh"):
    st.session_state["data"] = fetch_real_time_data()


if "data" not in st.session_state:# Initialize session state for the data
    st.session_state["data"] = fetch_real_time_data()

data = st.session_state["data"]

# Display charts
if not data.empty:
    with st.container():
        st.markdown("<h2>📊 Air Quality Metrics</h2>", unsafe_allow_html=True)
        for field, color in zip(["PM2.5", "PM10", "Ozone", "Humidity", "Temperature", "CO"], 
                                ["blue", "green", "yellow", "cyan", "orange", "red"]):
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.plotly_chart(create_chart(data, field, color), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("No data available. Please refresh.")

# footer
st.markdown(
    """
    <hr>
    <div style="text-align: center;">
        <p style="color: #FFD700;">Built By Yash Choudhary</p>
    </div>
    """,
    unsafe_allow_html=True,
)
