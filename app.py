import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.title("e-Donation CSV Reformatter")
st.markdown("""
SQL for query this input data in Data Warehouse
```sql
SELECT 
    c.[CRM Contact ID], 
    c.[Supporter ID], 
    c.Title, 
    c.[First Name], 
    c.[Last Name], 
    c.[Tax ID], 
    FORMAT(o.[Close Date],'dd/MM/yyyy') AS CloseDate, 
    o.[Donation ID], 
    SUM(o.Amount) AS total_donation_amount
FROM sfs.vw_contact c
LEFT JOIN sfs.vw_opportunity o
    ON c.[CRM Contact ID] = o.[CRM Contact ID]
WHERE o.[Close Date] >= '2025-01-01'
GROUP BY 
    c.[CRM Contact ID], 
    c.[Supporter ID], 
    c.Title, 
    c.[First Name], 
    c.[Last Name], 
    c.[Tax ID], 
    o.[Close Date], 
    o.[Donation ID];
""")

# Track last uploaded file name
if "last_file" not in st.session_state:
    st.session_state.last_file = None
if "name_entered" not in st.session_state:
    st.session_state.name_entered = False

def reset_state():
    st.session_state.name_entered = False

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

# Detect file change or removal → reset
current_file_name = uploaded_file.name if uploaded_file is not None else None
if current_file_name != st.session_state.last_file:
    reset_state()
    st.session_state.last_file = current_file_name

if uploaded_file is not None:
    st.subheader("1. Upload CSV Example")
    df = pd.read_csv(uploaded_file)
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    st.dataframe(df.head())
    
    st.subheader("2. Output CSV Re-formatting")

    # Manipulate output here
    df['CloseDate'] = pd.to_datetime(df['CloseDate'], errors='coerce')
    df['วันที่รับบริจาค'] = df['CloseDate'].apply(
        lambda x: f"{x.day:02d}{x.month:02d}{x.year + 543}" if pd.notnull(x) else None)
    df = df.rename(columns={'Tax ID': 'เลขประจำตัวผู้เสียภาษีอากร'
                            ,'Title': 'คำนำหน้าชื่อ'
                            , 'First Name': 'ชื่อ'
                            , 'Last Name': 'นามสกุล'
                            , 'total_donation_amount': 'มูลค่าเงินสด'
                    })
    df['รายการทรัพย์สิน'] = np.nan
    df['มูลค่าทรัพย์สิน'] = np.nan
    
    df['ประเภทผู้บริจาค'] = 'waiting dev'
    df['ชื่อนิติบุคคล'] = 'waiting dev'
    df_rev = df[['วันที่รับบริจาค','ประเภทผู้บริจาค','เลขประจำตัวผู้เสียภาษีอากร','คำนำหน้าชื่อ','ชื่อ','นามสกุล','ชื่อนิติบุคคล','มูลค่าเงินสด','รายการทรัพย์สิน','มูลค่าทรัพย์สิน']]
    st.dataframe(df_rev.head())

    # Convert to UTF-8-SIG using BytesIO (CRITICAL FIX)
    csv_buffer = BytesIO()
    df_rev.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    csv_buffer.seek(0)  # reset pointer

    # Text box (Enter needed to activate)
    op_names = st.text_input(
        "Enter output file name: e.g. inputDonatefile-25681204",
        placeholder="my_output",
        key="filename_input",
        on_change=lambda: setattr(st.session_state, "name_entered", True)
    )

    # Show download button only after Enter
    if st.session_state.name_entered:
        name = op_names.strip() or "my_output"
        st.download_button(
            label="Download Reformatted CSV",
            data=csv_buffer,           # BytesIO works 100%
            file_name=f"{name}.csv",
            mime="text/csv",
        )
else:
    st.info("Please upload a CSV file to continue.")
