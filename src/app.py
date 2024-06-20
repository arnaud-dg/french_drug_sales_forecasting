import pandas as pd
import numpy as np
import boto3
from io import BytesIO
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
import requests

# Layout of the main page
st.set_page_config(layout="wide")

color_map = {
    'Actual': '#0D2C54', 
    'Forecast': '#352D5E',
    'Forecast_IC': '#615889',
    'Forecast_area': '#BDB6DE' 
}

# Import the csv files from S3 bucket
df_product = pd.read_csv("https://french-drug-sales-forecasting.s3.amazonaws.com/data/FRENCH_DRUG_SALES_F.csv", sep=",")
df_atc1 = pd.read_csv("https://french-drug-sales-forecasting.s3.amazonaws.com/data/FRENCH_DRUG_SALES_F.csv", sep=",")
df_atc2 = pd.read_csv("https://french-drug-sales-forecasting.s3.amazonaws.com/data/FRENCH_DRUG_SALES_F.csv", sep=",")
# df_product['MARKET'] = df_product['MARKET'].str.replace("Community", "Community pharmacy")
# df_atc1['MARKET'] = df_atc1['MARKET'].str.replace("Community", "Community pharmacy")
df_atc2['MARKET'] = df_atc2['MARKET'].str.replace("Community", "Community pharmacy")

# Add the Both category to the dataframe

# Extract the list of unique items for the dropdown list
# product_list = list(df_product['PRODUCT'].unique())
# product_list.sort()
# atc1_list = list(df_product['ATC1_DESCRIPTION'].unique())
# atc1_list.sort()
atc2_list = list(df_product['ATC2_DESCRIPTION'].unique())
atc2_list.sort()

# Interface Streamlit
st.title("📈 Drugs Sales Forecasting - French Market")

st.sidebar.write("""This web application, made with Streamlit, is a personal project I undertook to practice with Time-series Forecasting. 
                 The technical stack used implies AWS, Snowflake, SQL, and Python. 
                 The aim of this application is to provide a trend analysis and a forecast of the drug consumption in France.
                 In order to reduce computation costs, a sample of 10 CIP Code only is available.""")

tab1, tab2, tab3 = st.tabs(["Forecast by ATC Classif. - Level 1", "Forecast by ATC Classif. - Leve 2", "Forecast by CIP13 code"])
with tab1:
    st.header("An owl")
    st.image("https://static.streamlit.io/examples/owl.jpg", width=200)

with tab2:
    # Selection panels
    col1, col2 = st.columns(2)
    with col1:
        selection = st.selectbox('Products to forecast:', atc2_list, key=5)  
    with col2:
        scope = st.selectbox('Market to forecast:', ['Community pharmacy', 'Hospital', 'Both'], key=6)
        if scope == "Both":
            scope_title = "Community & Hospital"
        elif scope == "Community pharmacy":
            scope_title = "Community pharmacy"
        elif scope == "Hospital":
            scope_title = "Hospital"
    chart_title = "Sales Forecasting" + " - " + selection + " - " + scope_title + " market"

    #  Customize the chart
    with st.expander("Access to configuration panel"): 
        col3, col4 = st.columns(2)  
        with col3:
            prediction_timeframe = st.slider('Forecasting horizon (in months):', min_value=3, value=6, max_value=12, step=1, key=7)
        with col4:
            confidence_interval = st.selectbox('Forecast Confidence Interval:', ['95%','90%', '80%'], key=8)
            if confidence_interval == '95%':
                IC_LW = 'LW_095'
                IC_UP = 'UP_095'
            elif confidence_interval == '90%':
                IC_LW = 'LW_090'
                IC_UP = 'UP_090'
            elif confidence_interval == '80%':
                IC_LW = 'LW_080'
                IC_UP = 'UP_080'
    
    # Filter the dataframe
    df_atc2 = df_atc2[df_atc2['ATC2_DESCRIPTION'] == selection]
    df_atc2 = df_atc2[df_atc2['MARKET'] == scope]

    # Draw Chart
    # Creating the plot
    fig = go.Figure()
    # Add actual sales line
    fig.add_trace(go.Scatter(x=df_atc2['TS'], y=df_atc2['ACTUAL'], mode='lines', name='Actual Sales', line=dict(color=color_map['Actual'])))
    # Add confidence interval
    fig.add_trace(go.Scatter(x=list(df_atc2['TS']) + list(df_atc2['TS'][::-1]), y=list(df_atc2[IC_UP]) + list(df_atc2[IC_LW][::-1]), fill='toself', fillcolor=color_map['Forecast_area'],
        line=dict(color=color_map['Forecast_IC']), hoverinfo="skip", showlegend=False))
    # Add forecast line
    fig.add_trace(go.Scatter(x=df_atc2['TS'], y=df_atc2['FORECAST'], mode='lines', name='Forecast', line=dict(color=color_map['Forecast'])))
    # Update layout
    fig.update_layout(title=chart_title, xaxis_title='Date', yaxis_title='Sales', template='plotly_white')
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    

    # Raw data
    with st.expander("Access to raw data"):
        st.dataframe(df_atc2)

with tab3:
   st.header("An owl")
   st.image("https://static.streamlit.io/examples/owl.jpg", width=200)

# Get the data from snowflake
# query = "SELECT * FROM ATC1 WHERE ATC_Class = '" + selected_product + "'"
# df_chart = fetch_data(query)
# df_chart['SALESDATE'] = pd.to_datetime(df_chart['SALESDATE'])

# query = "SELECT * FROM ATC2 WHERE ATC_Class2 = 'VITAMINES'"
# df_chart = fetch_data(query)
# df_chart['SALESDATE'] = pd.to_datetime(df_chart['SALESDATE'])

# # Affichage du graphique altair
# st.line_chart(data=df_chart, x='SALESDATE', y='NB_UNITS')
# st.dataframe(df_chart)