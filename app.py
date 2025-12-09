import streamlit as st
import pandas as pd
from io import StringIO

st.title("CSV Reformatter")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is not None:
    st.subheader("1. Upload CSV")
    df = pd.read_csv(uploaded_file)
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    st.dataframe(df.head())
    
    st.subheader("2. Output CSV Re-formatting")
    df_rev = df.iloc[:, :2]   # first 2 columns only

    # Convert df_rev to CSV in memory (no temporary files)
    csv_buffer = StringIO()
    df_rev.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    op_names = st.text_input("Enter output file name", value="")
    st.download_button(
        label="Download Reformat CSV",
        data=csv_data,
        file_name=f"{op_names}.csv",
        mime="text/csv"
    )
