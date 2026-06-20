import streamlit as st

st.set_page_config(page_title="QueryGenie AI")
st.title("QueryGenie AI")
st.write("Ask your business database a question in plain English.")

question = st.text_input("Your question:")
if question:
    st.info("Backend not connected yet — this will call the /query endpoint.")
