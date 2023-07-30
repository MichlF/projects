from pathlib import Path

import pandas as pd
import streamlit as st
from etl import search

st.set_page_config(
    page_title="About the Data",
    page_icon="🗃",
    layout="wide",
)

# Data load
data = pd.read_csv(Path(__file__).parents[1] / "data/data.csv")
df = pd.DataFrame()

# Header
st.markdown(
    "<h2 style='text-align: center; '>About this data</h2>",
    unsafe_allow_html=True,
)

# Body
st.divider()

st.markdown(
    (
        "<div style='text-align: center;'>The data used here was randomly"
        " created (cudos @Gonçalo Chambel). No identification with actual"
        " persons (living or deceased) is intended or should be"
        " inferred.</div>"
    ),
    unsafe_allow_html=True,
)

# First row
st.divider()

st.markdown(
    "<h3 style='text-align: center; '>Explore the data</h3>",
    unsafe_allow_html=True,
)
st.write("")

(buffer1, col1, col2, buffer2) = st.columns([0.1, 0.20, 0.5, 0.1], gap="large")

with col1:
    key = st.selectbox(
        label="Define a category:",
        options=[
            "All data",
            "Name",
            "Email",
            "Age",
            "Gender",
            "Country",
            "Onboarding Date",
            "Profession",
            "Salary",
        ],
    )

with col2:
    search_term = st.text_input(
        label="Define a search term:",
        value="John Doe",
        help="The search is case-sensitive!",
    )
    if key in ["Age", "Salary"] and search_term != "":
        try:
            int(search_term)
            df = search(data, key, search_term)
        except Exception as e:
            st.error("Wups, this is not a valid number!", icon="🚨")
    elif key not in ["Age", "Salary", ""] and search_term != "":
        df = search(data, key, search_term)

if not df.empty:
    if key == "All data":
        st.write("")
        st.markdown(
            (
                "<div style='text-align: center;'>You choose 'All data' as"
                " category, so we are showing all the data !</div>"
            ),
            unsafe_allow_html=True,
        )
        st.write("")

    st.data_editor(
        df,
        column_config={
            "Salary": st.column_config.ProgressColumn(
                "Salary",
                help="Salary with salary range out of all individuals",
                format="$%f",
                min_value=int(data["Salary"].min()),
                max_value=int(data["Salary"].max()),
            ),
        },
        hide_index=True,
        use_container_width=True,
    )
else:
    st.write("")
    st.write("")
    st.write("")
    st.markdown(
        (
            "<div style='text-align: center;'>Sorry, we couldn't find any data"
            " matching this category and search term....</div>"
        ),
        unsafe_allow_html=True,
    )
