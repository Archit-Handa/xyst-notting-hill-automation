import streamlit as st
import pandas as pd

@st.cache_data
def load_data(file):
    df = pd.read_excel(file, sheet_name='New Check Out Details ')
    # drop rows with more than 6 missing values
    df = df.dropna(subset=['Checked Out Date', 'Total Bill amount'], how='all')
    return df

def format_indian_number(number):
    number = float(number)
    number = round(number,2)
    is_negative = number < 0
    number = abs(number)
    s, *d = str(number).partition(".")
    r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
    value = "".join([r] + d)
    if is_negative:
       value = '-' + value
    return value


st.title("Automated Pivot Table Report")

uploaded_file = st.file_uploader("Upload your daily Excel report", type=["xlsx"])
if uploaded_file is not None:
    # Load the data
    df = load_data(uploaded_file)
    st.write("### Data Preview", df.head())

    # Cleaning data
    df = df.rename(columns={
            'category': 'Channel',
            'Company name': 'Company',
            'Total Bill amount': 'Total Bill',
            'Checked Out Date': 'Check Out Date'
        })
    df = df[['Channel', 'Company', 'Total Bill', 'Check Out Date']].dropna()
    df['Month'] = pd.to_datetime(df['Check Out Date']).dt.strftime('%b-%y')
    
    pivot_overall = df.pivot_table(index="Channel", columns="Month", values="Total Bill", aggfunc="sum", margins=True, margins_name="Total").reset_index()
    pivot_overall = pivot_overall.applymap(lambda x: format_indian_number(x) if isinstance(x, (int, float)) else x)
    st.write("### Overall Contribution by Channel", pivot_overall)

    # Drill-down selection
    selected_channel = st.selectbox("Select a Channel to drill down:", pivot_overall["Channel"].unique())
    if selected_channel:
        df_channel = df[df["Channel"] == selected_channel]
        drilldown = df_channel.pivot_table(index="Company", columns="Month", values="Total Bill", aggfunc="sum", margins=True, margins_name="Total").reset_index()
        st.write(f"### Contribution Breakdown for {selected_channel}", drilldown)