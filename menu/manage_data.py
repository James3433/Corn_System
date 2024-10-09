import pandas as pd
import streamlit as st

from supabase_connect import get_white_corn_price, get_yellow_corn_price, get_user_name

def app():

    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Month mapping dictionary
    month_mapping = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }

    selected_dataset = st.sidebar.selectbox("Choose an option:", ['White Corn Price', 'Yellow Corn Price'])

    def fetch_full_name(user_id):
        name = get_user_name(user_id)  # Call your function
        if name:  # Check if a name is returned
            return f"{name[0]} {name[1]}"  # Return fname lname as a full name
        return None

    # Group the data by year based on the selected dataset
    if selected_dataset == 'White Corn Price':
        corn_price = "White Corn Price"
        response_1, response_2, response_3, response_4, response_5 = get_white_corn_price()
    else:
        corn_price = "Yellow Corn Price"
        response_1, response_2, response_3, response_4, response_5 = get_yellow_corn_price()

    # Convert the responses to DataFrames
    dataset1 = pd.DataFrame(response_1)
    dataset2 = pd.DataFrame(response_2) 
    dataset3 = pd.DataFrame(response_3)
    dataset4 = pd.DataFrame(response_4)
    dataset5 = pd.DataFrame(response_5)

    # Apply fetch_full_name to the 'user_id' column

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

    # Drop id and region_id
    grouped = grouped.drop(columns=["id", "region_id"])

    # Apply fetch_full_name to the 'user_id' column
    grouped['user_id'] = grouped['user_id'].apply(fetch_full_name)

    spacer, col1, col2 = st.columns((0.2,1.3,1.5))

    with col1:
        st.header(f"Data about {selected_dataset}")
        st.dataframe(grouped)
    with col2: 
        Month = st.selectbox("Month", list(month_mapping.keys()))
        col4, col5 = st.columns(2)
        with col4:
            Year = st.text_input(label="Year", placeholder="Year", key="year_input")
        with col5:
            Week = st.text_input(label="Week", placeholder="Week", key="week_input")
        Price = st.text_input(label="Price", placeholder="Price", key="price_input")
