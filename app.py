import streamlit as st
import pandas as pd

st.title("CSV Splitter")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

def split_csv_by_group_name(df, group_column, output_prefix):
    output_files = []
    for group_name in df[group_column].unique():
        group_data = df[df[group_column] == group_name]
        output_file = f"{output_prefix}_{group_name}.csv"
        group_data.to_csv(output_file, index=False)
        output_files.append(output_file)
    return output_files

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    st.dataframe(df.head())
    
    st.subheader("2. Split by Group Name")
    group_column = st.selectbox("Select column to split by group name:", df.columns)
    prefix_group = st.text_input("Enter file prefix for split by group name:", value="output")
    
    if st.button("Split by Group Name"):
        output_files = split_csv_by_group_name(df, group_column, prefix_group)
        st.success("Files created:")
        for file in output_files:
            st.write(file)
            st.download_button(
                label=f"Download {file}",
                data=open(file, "rb").read(),
                file_name=file,
                mime="text/csv"
            )
        for file in output_files:
            os.remove(file)
# else:
#     st.info("Please upload a CSV file to continue.")
