import subprocess
import streamlit as st
import pandas as pd

st.title("CSV Splitter")
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

df = pd.read_csv(uploaded_file)
print(f'rows: {df.shape[0]} columns: {df.shape[1]}')
df.head()
