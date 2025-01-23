import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import time

from supabase_connect import get_white_corn_price, get_yellow_corn_price

def app():

    user_type = st.session_state.get('user_type', '0')

    # Load custom CSS
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown(f"""
            <style>
                [data-testid="stHorizontalBlock"] {{
                    padding: 2em;
                    border-radius: 2em;
                    background-color: #8edd27;
                }}
                @media (max-width: 768px) {{
                    [data-testid="stHorizontalBlock"] {{
                        padding: 1em 0em 1em 1em;
                }}
                }}
            </style>
    """, unsafe_allow_html=True)

    # Mapping full month numbers to their full name
    month_full = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 
                  7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}


    def admin_plot_view(dataset, selected_region):
        # Ensure that price_data and year are defined before this point
        if dataset is not None:
            grouped = dataset.groupby('year')

            for year, group in reversed(list(grouped)): 

                fig, ax = plt.subplots(figsize=(6, 4), facecolor='#B7E505') 
                ax.set_facecolor('#B7E505') 
                # Define price columns and their labels
                
                price_types = {
                    'farmgate_corngrains_price': 'Farmgate Price',
                    'retail_corngrits_price': 'Retail Price',
                    'wholesale_corngrits_price': 'Wholesale Price'
                }

                # Plot each price type if it exists in the dataset
                for price_col, label in price_types.items():
                    ax.plot(group['month'], group[price_col], marker='o', markersize=4, label=label)

                ax.set_xlabel('Month', color='black')
                ax.set_ylabel('Price', color='black')
                ax.set_title(f'{selected_region} Price Data in the Year {year}', color='black')

                # Set x-tick positions and labels for better readability
                x_ticks = range(len(group['month']))  # Assuming month is a categorical variable
                ax.set_xticks(x_ticks)  # Set positions for ticks
                ax.set_xticklabels(group['month'], rotation=45, ha='right')  # Set labels

                # Adjust the font size
                for tick in ax.get_xticklabels() + ax.get_yticklabels():
                    tick.set_fontsize(8)
                    tick.set_color('black')

                # Add a legend to identify each line
                ax.legend(title='Price Type')

                st.pyplot(fig)  # Display the plot using Streamlit


    def user_plot_view(dataset, selected_region):
        if dataset is not None:
            # Rename columns that contain "_price" to "price"
            dataset.rename(columns=lambda x: 'price' if '_price' in x else x, inplace=True)

            grouped = dataset.groupby('year')

            for year, group in reversed(list(grouped)): 

                fig, ax = plt.subplots(figsize=(6, 4), facecolor='#B7E505') 
                ax.set_facecolor('#B7E505') 
                # Define price columns and their labels
                
                # Plot each price type if it exists in the dataset
                ax.plot(group['month'], group['price'], marker='o', markersize=4)

                ax.set_xlabel('Month', color='black')
                ax.set_ylabel('Price', color='black')
                ax.set_title(f'{selected_region} {price_data} Data in the Year {year}', color='black')

                # Set x-tick positions and labels for better readability
                x_ticks = range(len(group['month']))  # Assuming month is a categorical variable
                ax.set_xticks(x_ticks)  # Set positions for ticks
                ax.set_xticklabels(group['month'], rotation=45, ha='right')  # Set labels

                # Adjust the font size
                for tick in ax.get_xticklabels() + ax.get_yticklabels():
                    tick.set_fontsize(8)
                    tick.set_color('black')

                st.pyplot(fig)  # Display the plot using Streamlit




    # Group the data by year based on the selected dataset
    df1, df2, df3, df4, df5, df6 = get_white_corn_price()

    df7, df8, df9, df10, df11, df12 = get_yellow_corn_price()

    # Map the month numbers to their full names
    for df in [df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12]:
        df['month'] = df['month'].map(month_full).astype(str)

    # Adjust DataFrames based on user type
    price_data = ""
    if user_type == 1:
        price_data = "Farmgate Price"
        for df in [df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12]:
            df.drop(['retail_corngrits_price', 'wholesale_corngrits_price'], axis=1, inplace=True)
    elif user_type == 2:
        price_data = "Retail Price"
        for df in [df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12]:
            df.drop(['farmgate_corngrains_price', 'wholesale_corngrits_price'], axis=1, inplace=True)
    elif user_type == 3:
        price_data = "Wholesale Price"
        for df in [df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12]:
            df.drop(['farmgate_corngrains_price', 'retail_corngrits_price'], axis=1, inplace=True)
    

    selected_region = st.selectbox("Choose a Region:", ['Davao Region', 'Davao de Oro', 'Davao del Norte', 'Davao del Sur', 'Davao Oriental', 'Davao City'])
    
    # Select dataset based on region
    region_map_1 = {
        'Davao Region': df1,
        'Davao de Oro': df2,
        'Davao del Norte': df3,
        'Davao del Sur': df4,
        'Davao Oriental': df5,
        'Davao City': df6
    }
    region_map_2 = {
        'Davao Region': df7,
        'Davao de Oro': df8,
        'Davao del Norte': df9,
        'Davao del Sur': df10,
        'Davao Oriental': df11,
        'Davao City': df12
    }
    
    white_dataset = region_map_1.get(selected_region)
    yellow_dataset = region_map_2.get(selected_region)

    if user_type == 4:
        col1, col2 = st.columns(2)
        with col1:
            st.header("White Corn")
            with st.expander("White Predictions Plots"):
                admin_plot_view(white_dataset, selected_region)
        with col2:
            st.header("Yellow Corn")
            with st.expander("Yellow Predictions Plots"):
                admin_plot_view(yellow_dataset, selected_region)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.header("White Corn")
            with st.expander("White Predictions Plots"):
                user_plot_view(white_dataset, selected_region)
        with col2:
            st.header("Yellow Corn")
            with st.expander("Yellow Predictions Plots"):
                user_plot_view(yellow_dataset, selected_region)