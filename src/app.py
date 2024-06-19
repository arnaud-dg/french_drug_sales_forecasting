import pandas as pd
import numpy as np
import boto3
from io import BytesIO
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go

from credentials import aws_access_key_id, aws_secret_access_key

# Layout of the main page
st.set_page_config(layout="wide")

color_map = {
    'Actual': '#0D2C54', 
    'Forecast': '#352D5E',
    'Forecast_IC': '#615889',
    'Forecast_area': '#BDB6DE' 
}

# Initializing s3 client
s3 = boto3.client('s3',
                  aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key,
                  region_name='us-east-1'
                  )

def load_data_from_s3(bucket_name, file_key):
    """Get a .csv file from a S3 bucket and transform it as a dataframe"""
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    content = response['Body'].read()
    df = pd.read_csv(BytesIO(content))
    return df

# Import the csv files from S3 bucket - CIP product table
df_product = load_data_from_s3("french-drug-sales-forecasting", "data/FRENCH_DRUG_SALES_F.csv")

# Extract the list of unique product
product_list = list(df_product['ATC_Class'].unique())
product_list.sort()
product_list = product_list[:5] + ["METFORMINE", "VITAMINES"]
family_list = list(df_product['ATC_Class2'].unique())
family_list.sort()
family_list = family_list[:5]

# Interface Streamlit
st.title("📈 Drugs Sales Forecasting - French Market :flag-fr:")

st.sidebar.write("""This web application, made with Streamlit, is a personal project I undertook to practice with Time-series Forecasting. 
                 The technical stack used implies AWS, Snowflake, SQL, and Python. 
                 The aim of this application is to provide a trend analysis and a forecast of the drug consumption in France.
                 In order to reduce computation costs, a sample of 10 CIP Code only is available.""")

tab1, tab2, tab3 = st.tabs(["ATC Classification - Level 1", "ATC Classification - Level", "Forecast by CIP13 code"])
with tab1:
    st.header("An owl")
    st.image("https://static.streamlit.io/examples/owl.jpg", width=200)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        selection = st.selectbox('Product to forecast:', product_list, key=5)
        chart_title = "Sales Forecasting" + " - " + selection   
    with col2:
        scope = st.selectbox('Forecasting scope:', ['Both','Community pharmacy', 'Hospital'], key=6)
    
    with col1:
        prediction_timeframe = st.slider('Forecasting horizon (in months):', min_value=3, value=6, max_value=12, step=1, key=7)
    with col2:
        confidence_interval = st.selectbox('Forecast Confidence Interval:', ['95%','90%', '80%'], key=8)
    
    # Filter the dataframe
    if scope == 'Both':
        df = df_prod[df_prod['PRODUCT'] == selection]
    else:
        df = df_prod_scope[(df_prod_scope['PRODUCT'] == selection) & (df_prod_scope['SCOPE'] == scope)]

    # Chart
    fig = px.line(predictions, x="DATE", y="VALUE", color="TYPE", color_discrete_map=color_map)
    if method == 'Linear Regression':
        new_trace = go.Scatter(x=curve['DATE'], y=curve['VALUE'], mode='lines', name='Regression line', line=dict(color='black', dash='dot'), opacity=0.5)
        fig.add_trace(new_trace)
    fig.update_layout(legend=dict(yanchor="top",y=1.0,xanchor="right",x=1.0,bgcolor="rgba(255, 255, 255, 0.5)", borderwidth=1), 
                      xaxis_title="", yaxis_title="Sales reimbursed (M€)", title=chart_title)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    # Raw data
    with st.expander("Forecasting raw data"):
        st.dataframe(predictions[predictions['TYPE']=='Forecast'][['DATE', 'VALUE']])

    # Explanations
    with st.expander(expander_title):
        st.write(expander_text)

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