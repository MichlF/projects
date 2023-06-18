import datetime as dt

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from etl import get_agg_distribution, get_distribution, get_signups

st.set_page_config(
    page_title="A Simple HR Dashboard",
    page_icon="📈",
    layout="wide",
)

# # Data load
data = pd.read_csv("data/data.csv")
df = pd.DataFrame()

# Header
st.markdown(
    "<h2 style='text-align: center; '>Dashboard</h2>",
    unsafe_allow_html=True,
)

# Second row
st.divider()

st.markdown(
    "<h3 style='text-align: center; '>Distributions</h3>",
    unsafe_allow_html=True,
)
st.write("")

tab1, tab2 = st.tabs(["Gender & Country distribution", "Age distribution"])

with tab1:
    col1, col2 = st.columns(2, gap="large")
    with col1:
        df = get_distribution(data, "Gender", 2)
        fig = go.Figure(
            data=[go.Pie(labels=df.index, values=df.iloc[:, 0].values)]
        )
        st.markdown(
            "<h5 style='text-align: center;'>Gender Distribution</h1>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df = get_distribution(data, "Country", 2)
        fig = go.Figure(
            data=[go.Pie(labels=df.index, values=df.iloc[:, 0].values)]
        )
        st.markdown(
            "<h5 style='text-align: center;'>Country Distribution</h1>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)

with tab2:
    st.markdown(
        "<h5 style='text-align: center;'>Age Distribution</h1>",
        unsafe_allow_html=True,
    )
    st.bar_chart(get_distribution(data, "Age", 2))

# Third row
st.markdown("***")

st.markdown(
    "<h3 style='text-align: center; '>Aggregations</h3>",
    unsafe_allow_html=True,
)
st.write("")

col1, col2 = st.columns([0.6, 0.4], gap="large")
with col1:
    tab1, tab2 = st.tabs(
        ["Average Salary by Profession", "Average Salary by Age"]
    )

    with tab1:
        st.markdown(
            (
                "<h5 style='text-align: center;'>Average salary per"
                " profession</h1>"
            ),
            unsafe_allow_html=True,
        )
        st.bar_chart(get_agg_distribution(data, "Profession", "Salary"))

    with tab2:
        st.markdown(
            (
                "<h5 style='text-align: center;'>Average salary per age"
                " group</h1>"
            ),
            unsafe_allow_html=True,
        )
        st.bar_chart(get_agg_distribution(data, "Age", "Salary"))

with col2:
    tab3, tab4 = st.tabs(["📈 Chart", "🗃 Data"])
    plot_data = get_signups(
        data,
        "Onboarding Date",
        dt.datetime(2020, 1, 1),
        dt.datetime(2022, 1, 1),
    )
    with tab3:
        st.markdown(
            (
                "<h5 style='text-align: center;'>Accumulated onboarded"
                " individuals over time</h1>"
            ),
            unsafe_allow_html=True,
        )
        st.line_chart(plot_data)

    with tab4:
        st.markdown(
            (
                "<h5 style='text-align: center;'>Data: Accumulated onboarded"
                " individuals over time</h1>"
            ),
            unsafe_allow_html=True,
        )
        tab4.write(plot_data)
