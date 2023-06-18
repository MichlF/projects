import streamlit as st

st.set_page_config(
    page_title="A Simple HR Dashboard",
    page_icon="🧊",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.extremelycoolapp.com/help",
        "Report a bug": "https://www.extremelycoolapp.com/bug",
        "About": "# This is a header. This is an *extremely* cool app!",
    },
)

# Header
st.markdown(
    "<h2 style='text-align: center; '>Welcome, there stranger !</h2>",
    unsafe_allow_html=True,
)

# Body
st.divider()

st.markdown(
    "Thanks for stopping by to this :blue[**very simple HR dashboard**]"
    " realized with :red[_Streamlit_] and :red[_Python_] ! I will continue to"
    " expand this example, so stay tuned if you want to see more!"
)
st.markdown(
    "You'll notice that you will be able to navigate this web app and to go to"
    " the dashboard by using the sidebar. Of course, this is all just for"
    " :green[demonstration purposes]. For a real deployment, you would want"
    " to start directly on the dashboard page."
)
