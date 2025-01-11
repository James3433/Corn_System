import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from supabase_connect import get_white_corn_price, get_yellow_corn_price

def app():

    # Load custom CSS
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Mapping full month names to three-letter abbreviations
    month_abbr = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

    selected_dataset = st.sidebar.selectbox("Choose an option:", ['White Corn Price', 'Yellow Corn Price'])

    # Group the data by year based on the selected dataset
    if selected_dataset == 'White Corn Price':
        corn_price = "White Corn"
        response_1, response_2, response_3, response_4, response_5 = get_white_corn_price()
    else:
        corn_price = "Yellow Corn"
        response_1, response_2, response_3, response_4, response_5 = get_yellow_corn_price()

    # Convert the responses to DataFrames
    dataset1 = pd.DataFrame(response_1)
    dataset2 = pd.DataFrame(response_2)
    dataset3 = pd.DataFrame(response_3)
    dataset4 = pd.DataFrame(response_4)
    dataset5 = pd.DataFrame(response_5)

    # Map the full month names to their abbreviations
    dataset1['month'] = dataset1['month'].map(month_abbr).astype(str)
    dataset2['month'] = dataset2['month'].map(month_abbr).astype(str)
    dataset3['month'] = dataset3['month'].map(month_abbr).astype(str)
    dataset4['month'] = dataset4['month'].map(month_abbr).astype(str)
    dataset5['month'] = dataset5['month'].map(month_abbr).astype(str)

    # Create a new column for 'Month Week'
    dataset1['Month Week'] = dataset1['month'] + ', Wk-' + dataset1['week'].astype(str)
    dataset2['Month Week'] = dataset2['month'] + ', Wk-' + dataset2['week'].astype(str)
    dataset3['Month Week'] = dataset3['month'] + ', Wk-' + dataset3['week'].astype(str)
    dataset4['Month Week'] = dataset4['month'] + ', Wk-' + dataset4['week'].astype(str)
    dataset5['Month Week'] = dataset5['month'] + ', Wk-' + dataset5['week'].astype(str)

    selected_region = st.selectbox("Choose an Region:", ['Davao Oriental', 'Davao City', 'Davao de Oro', 'Davao del Norte', 'Davao del Sur'])

    if selected_region == 'Davao Oriental':
        selected_dataset = "Davao Oriental"
        grouped = dataset1
    elif selected_region == 'Davao City':
        selected_dataset = "Davao City"
        grouped = dataset2
    elif selected_region == 'Davao de Oro':
        selected_dataset = "Davao de Oro"
        grouped = dataset3
    elif selected_region == 'Davao del Norte':
        selected_dataset = "Davao del Norte"
        grouped = dataset4
    elif selected_region == 'Davao del Sur':
        selected_dataset = "Davao del Sur"
        grouped = dataset5

    # Group the data by year
    grouped_by_year = grouped.groupby('year')

    # Plot the data
    for year, group in grouped_by_year:
        fig, ax = plt.subplots(figsize=(14, 6), facecolor='#B7E505')
        ax.set_facecolor('#B7E505')
        ax.plot(group['Month Week'], group['price'], marker='o', markersize=4)  
        ax.set_title(f"{selected_dataset}'s {corn_price} for Year {year}", fontsize=8, color='black')
        ax.set_xlabel('Month', fontsize=8, color='black')  
        ax.set_ylabel('Price', fontsize=8, color='black')  

        # Adjust the font size for the x and y tick labels
        for tick in ax.get_xticklabels():
            tick.set_fontsize(6)
            tick.set_color('black')  
        for tick in ax.get_yticklabels():
            tick.set_fontsize(8)
            tick.set_color('black')  
        
        # Rotate the x-tick labels and adjust alignment
        fig.autofmt_xdate(rotation=45, ha='right')
        
        st.pyplot(fig)  # Use st.pyplot to display the plot in Streamlit

