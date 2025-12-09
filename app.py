import streamlit as st
import pandas as pd

st.title("CSV Reformatter")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is not None:
    st.subheader("1. Upload CSV")
    df = pd.read_csv(uploaded_file)
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    st.dataframe(df.head())
    
    st.subheader("2. Output CSV Re-formatting")
    df_rev = df.iloc[:,:2]

    output_files = df_rev
    st.write(file)
        st.download_button(
            label=f"Download {file}",
            data=open(file, "rb").read(),
            file_name=file,
            mime="text/csv"
        )

# else:
#     st.info("Please upload a CSV file to continue.")
