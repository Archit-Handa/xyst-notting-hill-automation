import streamlit as st
import pandas as pd
import re
from difflib import get_close_matches

@st.cache_data
def load_data(file):
    df = pd.read_excel(file, sheet_name='New Check Out Details ')
    df = df.dropna(subset=['Checked Out Date', 'Total Bill amount'])
    df['category'] = df['category'].apply(format_category)
    return df

def format_category(x):
    x = re.sub(r'\s+', ' ', x)
    return x.strip()

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
    
    df["Company"] = df["Company"].str.strip().str.lower()
    
    # Merge similar company names
    unique_companies = df["Company"].unique().tolist()
    merged_names = {}
    
    for company in unique_companies:
        matches = get_close_matches(company, unique_companies, cutoff=0.8)
        if len(matches) > 1:
            main_name = matches[0]
            if main_name != company:
                user_choice = st.radio(f"Merge '{company}' with '{main_name}'?", ("Yes", "No"), key=company)
                if user_choice == "Yes":
                    merged_names[company] = main_name
    
    df["Company"] = df["Company"].replace(merged_names)
    
    pivot_overall = df.pivot_table(index="Channel", columns="Month", values="Total Bill", aggfunc="sum", margins=True, margins_name="Total").reset_index()
    
    st.write("### Overall Contribution by Channel", pivot_overall)

    # Drill-down selection
    selected_channel = st.selectbox("Select a Channel to drill down:", pivot_overall["Channel"].unique())
    if selected_channel:
        df_channel = df[df["Channel"] == selected_channel]
        drilldown = df_channel.pivot_table(index="Company", columns="Month", values="Total Bill", aggfunc="sum", margins=True, margins_name="Total").reset_index()
        st.write(f"### Contribution Breakdown for {selected_channel}", drilldown)