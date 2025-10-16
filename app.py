import streamlit as st
st.text("Hello World")

cool_sidebar = st.sidebar

with cool_sidebar:
    st.text("This is a sidebar")

cool_tab, cool_tab2 = st.tabs(["Tab1", "Tab2"])

with cool_tab:
    st.text("This is tab 1")

with cool_tab2:
    st.text("This is tab 2")

st.set_page_config(page_title="Min Streamlit-app", page_icon="#")

knapp = st.button("Tryck på mig")

file = st.file_uploader("Ladda upp fil här")
