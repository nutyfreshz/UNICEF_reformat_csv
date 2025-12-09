# import streamlit as st
# import pandas as pd
# from io import StringIO

# st.title("CSV Reformatter")

# uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

# if uploaded_file is not None:
#     st.subheader("1. Upload CSV")
#     df = pd.read_csv(uploaded_file)
#     st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
#     st.dataframe(df.head())
    
#     st.subheader("2. Output CSV Re-formatting")
#     df_rev = df.iloc[:, :2]   # first 2 columns only

#     # Convert df_rev to CSV in memory (no temporary files)
#     csv_buffer = StringIO()
#     df_rev.to_csv(csv_buffer, index=False)
#     csv_data = csv_buffer.getvalue()

#     op_names = st.text_input("Enter output file name", placeholder="my_output")
#     st.download_button(
#         label="Download Reformat CSV",
#         data=csv_data,
#         file_name=f"{op_names}.csv",
#         mime="text/csv"
#     )

import streamlit as st
import pandas as pd
from io import StringIO

st.title("CSV Reformatter")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

# initialize session state flag
if "name_entered" not in st.session_state:
    st.session_state.name_entered = False

def enable_download():
    st.session_state.name_entered = True

if uploaded_file is not None:
    st.subheader("1. Upload CSV")
    df = pd.read_csv(uploaded_file)
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    st.dataframe(df.head())
    
    st.subheader("2. Output CSV Re-formatting")
    df_rev = df.iloc[:, :2]

    # Convert to CSV
    csv_buffer = StringIO()
    df_rev.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    # Text input — must press ENTER for on_change to fire
    op_names = st.text_input(
        "Enter output file name",
        placeholder="my_output",
        key="filename_input",
        on_change=enable_download
    )

    # Show button only after pressing Enter
    if st.session_state.name_entered:
        name = op_names.strip() or "my_output"
        st.download_button(
            label="Download Reformatted CSV",
            data=csv_data,
            file_name=f"{name}.csv",
            mime="text/csv"
        )
