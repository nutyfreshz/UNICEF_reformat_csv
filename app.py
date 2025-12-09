import streamlit as st
import pandas as pd
from io import StringIO

st.title("CSV Reformatter")

# Track last uploaded file name
if "last_file" not in st.session_state:
    st.session_state.last_file = None
if "name_entered" not in st.session_state:
    st.session_state.name_entered = False

def reset_state():
    st.session_state.name_entered = False

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

# ❗ Detect file change or file removed → reset
current_file_name = uploaded_file.name if uploaded_file is not None else None
if current_file_name != st.session_state.last_file:
    reset_state()
    st.session_state.last_file = current_file_name

if uploaded_file is not None:
    st.subheader("1. Upload CSV")
    df = pd.read_csv(uploaded_file)
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    st.dataframe(df.head())
    
    st.subheader("2. Output CSV Re-formatting")
    #######################
    ## Manipulate data here - Use df_rev as output ##
    df_rev = df.iloc[:, :2]
    #######################

    # Convert to CSV
    csv_buffer = StringIO()
    df_rev.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    csv_data = csv_buffer.getvalue()

    # Text input — must press ENTER for on_change to fire
    op_names = st.text_input(
        "Enter output file name",
        placeholder="my_output",
        key="filename_input",
        on_change=lambda: setattr(st.session_state, "name_entered", True)
    )

    # Show button only after ENTER is pressed
    if st.session_state.name_entered:
        name = op_names.strip() or "my_output"
        st.download_button(
            label="Download Reformatted CSV",
            data=df_rev.encode("utf-8-sig"),
            file_name=f"{name}.csv",
            mime="text/csv"
        )
else:
    st.info("Please upload a CSV file to continue.")
