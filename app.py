import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.title("e-Donation CSV Reformatter")
st.badge("PLEASE DON'T OPEN CSV FILE WITH EXCEL FROM DATA WAREHOUSE", icon=":material/check:", color="red")
st.markdown("""
SQL: For query input data in Data Warehouse
```sql
WITH prep as
(SELECT 
    CASE WHEN o.[On Behalf Of] is null then o.[CRM Contact ID]
         WHEN o.[On Behalf Of] is not null then o.[On Behalf Of]
		 ELSE o.[CRM Contact ID] END as contact_key, /*DOBO rules can't use contact_id directly*/
    FORMAT(o.[Close Date],'dd/MM/yyyy') AS CloseDate, 
    o.[Donation ID],
	o.Stage,
	o.[Payment Method],
	o.[Payment Gateway],
	o.[Close Date] AS date_retro,
    SUM(o.Amount) AS total_donation_amount
FROM sfs.vw_opportunity o
WHERE 1=1
	AND o.[Close Date] BETWEEN DATEFROMPARTS(YEAR(GETDATE()), 1, 1) AND DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 16)
    AND o.[Payment Method] <> 'QR code'
    AND (LOWER(o.Stage) = 'closed won'
		OR LOWER(o.Stage) like '%refund%')
GROUP BY 
	CASE WHEN o.[On Behalf Of] is null then o.[CRM Contact ID]
         WHEN o.[On Behalf Of] is not null then o.[On Behalf Of]
		 ELSE o.[CRM Contact ID] END,
    o.[Close Date], 
    o.[Donation ID],
	o.Stage,
	o.[Payment Method],
	o.[Payment Gateway]
)	

select c.[CRM Contact ID], c.[Supporter ID], c.Title
    , c.[First Name], c.[Last Name]
	, COALESCE(c.[Tax ID],'xx') as "Tax ID"
	, p.CloseDate, p.[Donation ID]
	, c.[Type of Account], p.Stage
	, CASE WHEN LEFT(c.[Tax ID], 1) = '0' AND c.[First Name] is null THEN '2'
		WHEN lower(c.[Type of Account]) = 'individual' THEN '1'
        WHEN lower(c.[Type of Account]) = 'organization' THEN '2'
        ELSE 'ERROR' END AS type_acc_id
	, p.total_donation_amount
	, c.[Supporter ID]
	, p.[Payment Method]
	, p.[Payment Gateway]
	, CASE
		WHEN LEN(c.[Tax ID]) <> 13
		OR c.[Tax ID] LIKE '%[^0-9]%' OR (LEFT(c.[Tax ID], 1) = '0' AND c.[First Name] is not null)
		THEN 'INVALID'
		WHEN
		(
		(
		11 - (
			(
			SUBSTRING(c.[Tax ID],1,1) * 13 +
			SUBSTRING(c.[Tax ID],2,1) * 12 +
			SUBSTRING(c.[Tax ID],3,1) * 11 +
			SUBSTRING(c.[Tax ID],4,1) * 10 +
			SUBSTRING(c.[Tax ID],5,1) * 9  +
			SUBSTRING(c.[Tax ID],6,1) * 8  +
			SUBSTRING(c.[Tax ID],7,1) * 7  +
			SUBSTRING(c.[Tax ID],8,1) * 6  +
			SUBSTRING(c.[Tax ID],9,1) * 5  +
			SUBSTRING(c.[Tax ID],10,1) * 4 +
			SUBSTRING(c.[Tax ID],11,1) * 3 +
			SUBSTRING(c.[Tax ID],12,1) * 2
			) % 11
			)
		) % 10
		) = CAST(SUBSTRING(c.[Tax ID],13,1) AS INT)
		THEN 'VALID'
		ELSE 'INVALID'
		END AS id_validate
		, CASE WHEN MONTH(p.date_retro) = MONTH(GETDATE()) THEN 'CURRENT'
			WHEN MONTH(p.date_retro) <> MONTH(GETDATE()) THEN 'RETRO'
			ELSE 'ERROR' END AS retro
from prep p
LEFT JOIN sfs.vw_contact c
    ON p.contact_key = c.[CRM Contact ID]
	;
""")

# st.markdown("""
# SQL: For exclude donation_id which "REFUND"
# ```sql
# SELECT 
#     c.[CRM Contact ID], 
#     c.[Supporter ID], 
#     c.Title, 
#     c.[First Name], 
#     c.[Last Name], 
#     COALESCE(c.[Tax ID],'xx') as "Tax ID", 
#     FORMAT(o.[Close Date],'dd/MM/yyyy') AS CloseDate, 
#     o.[Donation ID],
#     o.stage,
#     SUM(o.Amount) AS total_donation_amount
# FROM sfs.vw_contact c
# LEFT JOIN sfs.vw_opportunity o
#     ON c.[CRM Contact ID] = o.[CRM Contact ID]
# WHERE YEAR(o.[Close Date]) >= YEAR(GETDATE())
#     AND LOWER(o.Stage) like '%refund%'
# GROUP BY 
#     c.[CRM Contact ID], 
#     c.[Supporter ID], 
#     c.Title, 
#     c.[First Name], 
#     c.[Last Name], 
#     c.[Tax ID], 
#     o.[Close Date], 
#     o.[Donation ID],
#     o.Stage;
# """)

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
    # df['CloseDate'] = pd.to_datetime(df['CloseDate'], errors='coerce')
    df['CloseDate'] = pd.to_datetime(
        df['CloseDate'],
        errors='coerce',
        infer_datetime_format=True,
        dayfirst=True
        )

    df['วันที่รับบริจาค'] = df['CloseDate'].apply(
        lambda x: f"{x.day:02d}{x.month:02d}{x.year + 543}" if pd.notnull(x) else None
        )

    df['รายการทรัพย์สิน'] = np.nan
    df['มูลค่าทรัพย์สิน'] = np.nan

    df['ประเภทผู้บริจาค'] = df['type_acc_id']
    df['ชื่อนิติบุคคล'] = np.where(
							df['type_acc_id'] == 2,
							df['Last Name'],
							np.nan
							)
    df['Tax ID'] = df['Tax ID'].astype(str)
    
    df = df.rename(columns={'Tax ID': 'เลขประจำตัวผู้เสียภาษีอากร'
						,'Title': 'คำนำหน้าชื่อ'
						, 'First Name': 'ชื่อ'
						, 'Last Name': 'นามสกุล'
						, 'total_donation_amount': 'มูลค่าเงินสด'
						, 'Donation ID': 'DONATION_ID'
				})
    
    df_rev = df[['วันที่รับบริจาค','ประเภทผู้บริจาค','เลขประจำตัวผู้เสียภาษีอากร','คำนำหน้าชื่อ','ชื่อ','นามสกุล','ชื่อนิติบุคคล','มูลค่าเงินสด','รายการทรัพย์สิน','มูลค่าทรัพย์สิน','DONATION_ID','Stage','Supporter ID','Pledge ID','Payment Method','Payment Gateway','id_validate','retro']]

    mask = (
    df_rev['เลขประจำตัวผู้เสียภาษีอากร'].isna() |
    df_rev['เลขประจำตัวผู้เสียภาษีอากร'].astype(str).str.contains('xx', case=False, na=False)
            )
    df_rev_tax_incom = df_rev[mask]
    df_rev_tax_com = df_rev[~mask]

    # tax_col = 'เลขประจำตัวผู้เสียภาษีอากร'
    # df_rev_tax_com[tax_col] = (
    #     df_rev_tax_com[tax_col]
    #     .astype(str)
    #     .apply(lambda x: f"'{x}" if x != 'nan' else x)
    # )

    # st.write(f"Total Rows: {df_rev.shape[0]}, Columns: {df_rev.shape[1]}")
    st.write(f"Incomplete TaxID - Rows: {df_rev_tax_incom.shape[0]}, Columns: {df_rev_tax_incom.shape[1]}")
    st.write(f"Complete TaxID - Rows: {df_rev_tax_com.shape[0]}, Columns: {df_rev_tax_com.shape[1]}")
    # st.dataframe(df_rev.head())

    # Create separate buffers
    buffer_incomplete = BytesIO()
    buffer_complete = BytesIO()

    df_rev_tax_incom.to_csv(buffer_incomplete, index=False, encoding="utf-8-sig")
    df_rev_tax_com.to_csv(buffer_complete, index=False, encoding="utf-8-sig")

    buffer_incomplete.seek(0)
    buffer_complete.seek(0)

    # Text box (Enter needed to activate)
    st.badge("Example file naming")
    st.code("InputDonateFile-yyyymmdd")
    st.badge("InputDonateFile-25681204", icon=":material/check:", color="green")
    op_names = st.text_input(
        "Enter output file name",
        placeholder="my_output",
        key="filename_input",
        on_change=lambda: setattr(st.session_state, "name_entered", True)
    )
    
    # Show download button only after Enter
    if st.session_state.name_entered:
        name = op_names.strip() or "my_output"

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="⬇️ Download Incomplete TaxID",
                data=buffer_incomplete,
                file_name=f"{name}_incomplete_taxid.csv",
                mime="text/csv",
            )

        with col2:
            st.download_button(
                label="⬇️ Download Complete TaxID",
                data=buffer_complete,
                file_name=f"{name}_complete_taxid.csv",
                mime="text/csv",
            )
else:
    st.info("Please upload a CSV file to continue.")
