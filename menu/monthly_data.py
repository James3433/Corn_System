import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from supabase_connect import get_white_corn_price, get_yellow_corn_price

def app():
    # Load custom CSS
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Mapping full month numbers to their full name
    month_full = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

    corn_price = ""
    # Define the month order
    month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    selected_dataset = st.sidebar.selectbox("Choose an option:", ['White Corn Price', 'Yellow Corn Price'])

    # Group the data by year based on the selected dataset
    if selected_dataset == 'White Corn Price':
        corn_price = "White Corn Price"
        response_1, response_2, response_3, response_4, response_5 = get_white_corn_price()
    else:
        corn_price = "Yellow Corn Price"
        response_1, response_2, response_3, response_4, response_5 = get_yellow_corn_price()

    # Convert the responses to DataFrames
    df1 = pd.DataFrame(response_1)
    df2 = pd.DataFrame(response_2) 
    df3 = pd.DataFrame(response_3)
    df4 = pd.DataFrame(response_4)
    df5 = pd.DataFrame(response_5)

    # Map the month numbers to their full names
    df1['month'] = df1['month'].map(month_full).astype(str)
    df2['month'] = df2['month'].map(month_full).astype(str)
    df3['month'] = df3['month'].map(month_full).astype(str)
    df4['month'] = df4['month'].map(month_full).astype(str)
    df5['month'] = df5['month'].map(month_full).astype(str)

    selected_region = st.selectbox("Choose an Region:", ['Davao Oriental', 'Davao City', 'Davao de Oro', 'Davao del Norte', 'Davao del Sur'])

    if selected_region == 'Davao Oriental':
        selected_dataset = "Davao Oriental"
        dataset = df1
    elif selected_region == 'Davao City':
        selected_dataset = "Davao City"
        dataset = df2
    elif selected_region == 'Davao de Oro':
        selected_dataset = "Davao de Oro"
        dataset = df3
    elif selected_region == 'Davao del Norte':
        selected_dataset = "Davao del Norte"
        dataset = df4
    elif selected_region == 'Davao del Sur':
        selected_dataset = "Davao del Sur"
        dataset = df5

    selected_year1 = int(st.sidebar.selectbox('Select a year', ['2018', '2019', '2020'], key='year_selector_2'))
    dataset_year = dataset[dataset['year'] == selected_year1]

    # Convert the 'Month' column to a categorical type with the specified order
    dataset_year['month'] = pd.Categorical(dataset_year['month'], categories=month_order, ordered=True)

    grouped = dataset_year.groupby('month')

    st.header(f"{selected_dataset}'s {corn_price} in {selected_year1}")
    for month, group in grouped:
        fig, ax = plt.subplots(figsize=(6, 4), facecolor='#B7E505') 
        ax.set_facecolor('#B7E505') 
        ax.plot(group['week'], group['price'], marker='o', markersize=4)
            
        ax.set_xlabel('Month', color='black')
        ax.set_ylabel('Price', color='black')
        ax.set_title(f'{month} of {selected_year1}', color='black')
            
        # Adjust the font size
        for tick in ax.get_xticklabels():
            tick.set_fontsize(8)
            tick.set_color('black')  
        for tick in ax.get_yticklabels():
            tick.set_fontsize(8)
            tick.set_color('black')  
        
        st.pyplot(fig)
