import streamlit as st
import pandas as pd

st.title("CSV Splitter")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    st.dataframe(df.head())
else:
    st.info("Please upload a CSV file to continue.")
