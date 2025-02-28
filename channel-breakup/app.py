import streamlit as st
import pandas as pd

@st.cache_data
def load_data(file):
    df = pd.read_excel(file, sheet_name="New Check Out Details ")
    return df

st.title("Automated Pivot Table Report")

uploaded_file = st.file_uploader("Upload your daily Excel report", type=["xlsx"])
if uploaded_file is not None:
    # Load the data
    df = load_data(uploaded_file)
    st.write("### Data Preview", df.head())

    # Cleaning data
    df = df.rename(columns={"category": "Channel", "Company name": "Company", "Bal. Amount/Discount": "Total Bill"})
    df = df[["Channel", "Company", "Total Bill"]].dropna()
    
    # Overall pivot table (sum of Total Bill per Channel)
    pivot_overall = df.groupby("Channel")["Total Bill"].sum().reset_index()
    st.write("### Overall Contribution by Channel", pivot_overall)

    # Drill-down selection
    selected_channel = st.selectbox("Select a Channel to drill down:", pivot_overall["Channel"].unique())
    if selected_channel:
        df_channel = df[df["Channel"] == selected_channel]
        drilldown = df_channel.groupby("Company")["Total Bill"].sum().reset_index()
        st.write(f"### Contribution Breakdown for {selected_channel}", drilldown)
