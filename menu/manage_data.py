import pandas as pd
import numpy as np
import streamlit as st
import httpx

from streamlit_modal import Modal

from supabase_connect import get_user_name, get_user_by_user_type, get_unique_years
from supabase_connect import get_fertilizer_data, get_weather_data, get_white_corn_price_data, get_yellow_corn_price_data, get_white_corn_production_data, get_yellow_corn_production_data
from supabase_connect import submit_predictions_fertilizer, submit_predictions_price, submit_predictions_production, submit_predictions_weather
from supabase_connect import update_predictions_fertilizer, update_predictions_price, update_predictions_production, update_predictions_weather

from supabase_connect import upload_model_to_supabase, upload_csv_to_supabase

from supabase_connect import get_production_dataset_for_edit, get_fertilizer_dataset_for_edit, get_weather_dataset_for_edit, get_price_dataset_for_edit

from supabase_connect import get_white_davao_region_dataset, get_yellow_davao_region_dataset
from sklearn.preprocessing import PolynomialFeatures
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Lasso
from sklearn.linear_model import LassoCV
from sklearn.model_selection import GridSearchCV

def app():

    user_id = st.session_state.get('user_id', '0')

    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


    # Month mapping dictionary
    month_mapping = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,'May': 5, 'June': 6, 'July': 7,
        'August': 8,'September': 9, 'October': 10, 'November': 11, 'December': 12
    }

    provinces = ['Davao Region', 'Davao de Oro', 'Davao del Norte', 'Davao del Sur', 'Davao Oriental', 'Davao City']
    provinces_num = {'Davao Region': 1, 'Davao de Oro': 2, 'Davao del Norte': 3, 'Davao del Sur': 4, 'Davao Oriental': 5, 'Davao City': 6}
    conditions_num = {'Partly Cloudy': 1, 'Rain, Partially Cloudy': 2, 'Rain, Overcast': 3, 'Overcast': 4}
    corn_type = {'White Corn': 1, 'Yellow Corn': 2}


    fertilizer_database= pd.DataFrame(columns=["year", "month", "province_id", "corn_type", "ammophos_price", "ammosul_price", "complete_price", "urea_price"])

    # weather_database = pd.DataFrame(columns=["year", "month", "province_id", "corn_type", "temp", "feelslike", "dew", "humidity", "precip", "precipprob","precipcover", 'windgust', 
    #                                 "windspeed", "winddir", "sealevelpressure","visibility", "solarradiation", "solarenergy", "uvindex", "severerisk", "cloudcover", "conditions"])
    
    weather_database = pd.DataFrame(columns=["year", "month", "province_id", "corn_type", "feelslike", "dew", "humidity", "precip", "precipcover", 
                                    'windgust', "windspeed", "winddir", "sealevelpressure", "visibility", "severerisk", "conditions"])
    

    price_database = pd.DataFrame(columns=["year", "month", "province_id", "corn_type", "farmgate_corngrains_price", "retail_corngrits_price", "retail_corngrains_price", "wholesale_corngrits_price", "wholesale_corngrains_price"])
    
    production_database = pd.DataFrame(columns=["year", "month", "province_id", "corn_type", "corn_production"])





    def clear_text_input():
        # Clear text inputs
        Ammophos, Ammosul, Complete, Urea = "", "", "", ""
        Farmgate_Price, Retail_Price, Wholesale_Price = "", "", ""
        Production = ""
        feelslike, dew, humidity, precip, precipcover, windspeed = "", "", "", "", "", ""
        sealevelpressure, visibility, severerisk, conditions = "", "", "", ""



    if "selected_dataset2_num" not in st.session_state:
        st.session_state.selected_dataset2_num = 1


    
    dataset2 = ['Manage Data', 'Train Data']


    selected_dataset2 = dataset2[st.session_state.selected_dataset2_num]

    # Update previous selection
    st.session_state.selected_dataset2_prev = selected_dataset2





            
    # For Adding Data to Database
    if 'production_input_data' not in st.session_state:
        st.session_state.production_input_data = pd.DataFrame()  # or some default DataFrame
        st.session_state.production_input_data = production_database

    if 'fertilizer_input_data' not in st.session_state:
        st.session_state.fertilizer_input_data = pd.DataFrame()  # or some default DataFrame
        st.session_state.fertilizer_input_data = fertilizer_database

    if 'weather_input_data' not in st.session_state:
        st.session_state.weather_input_data = pd.DataFrame()  # or some default DataFrame
        st.session_state.weather_input_data = weather_database

    if 'price_input_data' not in st.session_state:
        st.session_state.price_input_data = pd.DataFrame()  # or some default DataFrame
        st.session_state.price_input_data = price_database

    # Use a unique key for the form by incrementing it each time the form is submitted.
    if "add_form_key" not in st.session_state:
        st.session_state.add_form_key = 0  
    add_form_key = st.session_state.get('add_form_key')

    # Initialize session state for current province index if not already done
    if "add_current_prov_index" not in st.session_state:
        st.session_state.add_current_prov_index = 0

    if st.session_state.add_current_prov_index <= len(provinces) - 1:
        current_prov_1 = provinces[st.session_state.add_current_prov_index]
    else:
        current_prov_1 = provinces[2]





    # For Editing Data to Database
    if 'production_edit_data' not in st.session_state:
        st.session_state.production_edit_data = pd.DataFrame()  # or some default DataFrame
        st.session_state.production_edit_data = production_database

    if 'fertilizer_edit_data' not in st.session_state:
        st.session_state.fertilizer_edit_data = pd.DataFrame()  # or some default DataFrame
        st.session_state.fertilizer_edit_data = fertilizer_database

    if 'weather_edit_data' not in st.session_state:
        st.session_state.weather_edit_data = pd.DataFrame()  # or some default DataFrame
        st.session_state.weather_edit_data = weather_database

    if 'price_edit_data' not in st.session_state:
        st.session_state.price_edit_data = pd.DataFrame()  # or some default DataFrame
        st.session_state.price_edit_data = price_database


    # Use a unique key for the form by incrementing it each time the form is submitted.
    if "edit_form_key" not in st.session_state:
        st.session_state.edit_form_key = 0
    edit_form_key = st.session_state.get('edit_form_key')


    # Initialize session state for current province index if not already done
    if "edit_current_prov_index" not in st.session_state:
        st.session_state.edit_current_prov_index = 0


    if st.session_state.edit_current_prov_index <= len(provinces) - 1:
        current_prov_2 = provinces[st.session_state.edit_current_prov_index]
    else:
        current_prov_2 = provinces[2]





    try:
        response_1 = get_fertilizer_data()

        dataset = pd.DataFrame(response_1)

        # Drop id and province_id
        dataset = dataset.drop(columns=["id"], axis=1)

        # # Apply fetch_full_name to the 'user_id' column
        # dataset['user_id'] = dataset['user_id'].apply(fetch_full_name)

        # Get the current year and month
        last_year = dataset['year'].iloc[-1]

        # Get the last row of the 'month' column
        last_month = dataset['month'].iloc[-1]

    except (httpx.RequestError, httpx.WriteTimeout) as e:  # Catch connection & request-related errors
        st.error("Connection error: Unable to connect to the server. Please try again later.")
        if st.button("Reload"):
            st.rerun()
        st.stop()  # Prevents further execution


    # Initialize session state for current province index if not already done
    if "ready_edit" not in st.session_state:
        st.session_state.ready_edit = False
    
    # Reverse the dictionary
    month_mapping_num = {v: k for k, v in month_mapping.items()}            

    # Initialize session state defaults if not set
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = last_year

    if "selected_month" not in st.session_state:
        st.session_state.selected_month = month_mapping_num[last_month]





    # Create a modal instance
    modal_1 = Modal("Submit Data", key="submit-data-modal", padding=20)

    # Render modal content for submiting data to the database
    if modal_1.is_open():
        with modal_1.container():
            st.error("Are you sure you want to submit this data?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Yes'):

                    # Fertilizer
                    st.session_state.fertilizer_input_data['month'] = st.session_state.fertilizer_input_data['month'].map(month_mapping)                                       
                    st.session_state.fertilizer_input_data['province_id'] = st.session_state.fertilizer_input_data['province_id'].map(provinces_num)
                    st.session_state.fertilizer_input_data['corn_type'] = st.session_state.fertilizer_input_data['corn_type'].map(corn_type)
                    submit_predictions_fertilizer(st.session_state.fertilizer_input_data, user_id)

                    del st.session_state.fertilizer_input_data # Remove flag

                    # Price
                    st.session_state.price_input_data['month'] = st.session_state.price_input_data['month'].map(month_mapping)                                       
                    st.session_state.price_input_data['province_id'] = st.session_state.price_input_data['province_id'].map(provinces_num)
                    st.session_state.price_input_data['corn_type'] = st.session_state.price_input_data['corn_type'].map(corn_type)
                    submit_predictions_price(st.session_state.price_input_data, user_id)

                    del st.session_state.price_input_data # Remove flag

                    # Production
                    st.session_state.production_input_data['month'] = st.session_state.production_input_data['month'].map(month_mapping)                                       
                    st.session_state.production_input_data['province_id'] = st.session_state.production_input_data['province_id'].map(provinces_num)
                    st.session_state.production_input_data['corn_type'] = st.session_state.production_input_data['corn_type'].map(corn_type)
                    submit_predictions_production(st.session_state.production_input_data, user_id)

                    del st.session_state.production_input_data # Remove flag
                        
                    # Weather
                    st.session_state.weather_input_data['month'] = st.session_state.weather_input_data['month'].map(month_mapping)                                       
                    st.session_state.weather_input_data['province_id'] = st.session_state.weather_input_data['province_id'].map(provinces_num)
                    st.session_state.weather_input_data['corn_type'] = st.session_state.weather_input_data['corn_type'].map(corn_type)
                    st.session_state.weather_input_data['conditions'] = st.session_state.weather_input_data['conditions'].map(conditions_num)
                    submit_predictions_weather(st.session_state.weather_input_data, user_id)

                    del st.session_state.weather_input_data # Remove flag


                    st.session_state.add_form_key = 0
                    st.session_state.add_current_prov_index = 0
                    st.session_state.selected_dataset2_num += 1

                    # Clear text inputs
                    clear_text_input()

                    modal_1.close()  # Close modal
                    st.rerun() # Rerun to reflect changes

                with col2:
                    if st.button('No'):
                        
                        # Clear text inputs
                        clear_text_input()

                        modal_1.close()  # Close modal
                        st.rerun()



    # Create a modal instance
    modal_2 = Modal("Submit Edited Data", key="submit-edited-data-modal", padding=20)

    # Render modal content for submiting data to the database
    if modal_2.is_open():
        with modal_2.container():
            st.error("Are you sure you want to submit this edited data?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Yes'):

                    # Fertilizer
                    st.session_state.fertilizer_edit_data['month'] = st.session_state.fertilizer_edit_data['month'].map(month_mapping)                                       
                    st.session_state.fertilizer_edit_data['province_id'] = st.session_state.fertilizer_edit_data['province_id'].map(provinces_num)
                    st.session_state.fertilizer_edit_data['corn_type'] = st.session_state.fertilizer_edit_data['corn_type'].map(corn_type)
                    update_predictions_fertilizer(st.session_state.fertilizer_edit_data, user_id)

                    del st.session_state.fertilizer_edit_data # Remove flag

                    # Price
                    st.session_state.price_edit_data['month'] = st.session_state.price_edit_data['month'].map(month_mapping)                                       
                    st.session_state.price_edit_data['province_id'] = st.session_state.price_edit_data['province_id'].map(provinces_num)
                    st.session_state.price_edit_data['corn_type'] = st.session_state.price_edit_data['corn_type'].map(corn_type)
                    update_predictions_price(st.session_state.price_edit_data, user_id)

                    del st.session_state.price_edit_data # Remove flag

                    # Production
                    st.session_state.production_edit_data['month'] = st.session_state.production_edit_data['month'].map(month_mapping)                                       
                    st.session_state.production_edit_data['province_id'] = st.session_state.production_edit_data['province_id'].map(provinces_num)
                    st.session_state.production_edit_data['corn_type'] = st.session_state.production_edit_data['corn_type'].map(corn_type)
                    update_predictions_production(st.session_state.production_edit_data, user_id)

                    del st.session_state.production_edit_data # Remove flag
                        
                    # Weather
                    st.session_state.weather_edit_data['month'] = st.session_state.weather_edit_data['month'].map(month_mapping)                                       
                    st.session_state.weather_edit_data['province_id'] = st.session_state.weather_edit_data['province_id'].map(provinces_num)
                    st.session_state.weather_edit_data['corn_type'] = st.session_state.weather_edit_data['corn_type'].map(corn_type)
                    st.session_state.weather_edit_data['conditions'] = st.session_state.weather_edit_data['conditions'].map(conditions_num)
                    update_predictions_weather(st.session_state.weather_edit_data, user_id)

                    del st.session_state.weather_edit_data # Remove flag


                    st.session_state.edit_form_key = 0
                    st.session_state.edit_current_prov_index = 0
                    st.session_state.selected_dataset2_num += 1

                    # Clear text inputs
                    clear_text_input()

                    modal_1.close()  # Close modal
                    st.rerun() # Rerun to reflect changes

                with col2:
                    if st.button('No'):
                        
                        # Clear text inputs
                        clear_text_input()

                        modal_2.close()  # Close modal
                        st.rerun()




    if selected_dataset2 != "Train Data":
        
        selected_feature = st.sidebar.selectbox("Choose an option:", ['Add Data', 'Edit Data'])

        if selected_feature == 'Add Data':

            current_month = (last_month) % 12 + 1  # Wrap around using modulo
            current_year = last_year + (last_month) // 12  # Increment year if month exceeds December
        
            # Reverse the month mapping dictionary
            month_to_string = {v: k for k, v in month_mapping.items()}

            # Convert current month to string
            current_month = month_to_string[current_month]

            # Create a form for data entry for the current province
            with st.form(key=f'data_entry_form_{add_form_key}'):

                if st.session_state.add_current_prov_index <= len(provinces) - 1:
                    st.header(f"Data Entry for {current_prov_1}")

                    col1, col2 = st.columns((1.5, 1.5))

                    with col1:
                        Month = st.text_input(label="Month", placeholder=f"{current_month}", key=f"month_input", disabled=True)
                    with col2: 
                        Year = st.text_input(label="Year", placeholder=f"{current_year}", key=f"year_input", disabled=True)

                    col4, col5, col6, col7 = st.columns((0.5, 0.5, 1.5, 1.5))

                    with col4:
                        st.write("Corn Productions")
                        W_Production = st.text_input(label="White Corn Production", placeholder="Production", key=f"production_input1")
                        Y_Production = st.text_input(label="Yellow Corn Production", placeholder="Production", key=f"production_input2")

                    with col5:
                        st.write("Fertilizers Prices")
                        Ammophos = st.text_input(label="Ammophos Price", placeholder="Ammophos Price", key=f"amp_price_input")
                        Ammosul = st.text_input(label="Ammosul Price", placeholder="Ammosul Price", key=f"ams_price_input")
                        Complete = st.text_input(label="Complete Price", placeholder="Complete Price", key=f"com_price_input")
                        Urea = st.text_input(label="Urea Price", placeholder="Urea Price", key=f"urea_price_input")
                        
                    with col6:
                        st.write("Weather Data")
                        col_1, col_2, col_3 = st.columns(3)
                                
                        with col_1:
                            Feelslike = st.text_input(label="Feels Like Temp.", placeholder="Feels Like Temp.", key=f"feelslike_input")
                            Dew = st.text_input(label="Dew", placeholder="Dew", key=f"dew_input")
                            Humidity = st.text_input(label="Humidity", placeholder="Humidity", key=f"humidity_input")
                            Precip = st.text_input(label="Precipitation", placeholder="Precipitation", key=f"precip_input")
                            
                        with col_2:
                            Precipcover = st.text_input(label="Precipitation Cover", placeholder="Precipitation Cover", key=f"precov_input")
                            Windgust = st.text_input(label="Wind Gust", placeholder="Wind Gust", key=f"windgust_input")
                            Windspeed = st.text_input(label="Wind Speed", placeholder="Wind Speed", key=f"windspeed_input")
                            Winddir = st.text_input(label="Wind Direction", placeholder="Wind Direction", key=f"winddir_input")
                        
                        with col_3:
                            Sealevelpressure = st.text_input(label="Sea Level Pressure", placeholder="Sea Level Pressure", key=f"sea_level_input")
                            Visibility = st.text_input(label="Visibility", placeholder="Visibility", key=f"visibility_input")
                            Severerisk = st.text_input(label="Severe Risk", placeholder="Severe Risk", key=f"severerisk_input")
                            Conditions = st.selectbox("Condiions:", ['Partly Cloudy', 'Rain, Partially Cloudy', 'Rain, Overcast', 'Overcast'], key=f"conditions_input")

                    with col7:
                        col_1, col_2 = st.columns(2)
                        with col_1:
                            st.write("White Corn Prices")
                            W_Farmgate_Price = st.text_input(label="Farmgate Corngrains Price", placeholder="Farmgate Price", key=f"f_price_input1")
                            W_Retail_Price = st.text_input(label="Retail Corngrits Price", placeholder="Retail Price", key=f"r_price_input1")
                            W_Wholesale_Price_1 = st.text_input(label="Wholesale Corngrits Price", placeholder="Wholesale Price", key=f"w_price_input11")
                            W_Wholesale_Price_2 = st.text_input(label="Wholesale Corngrains Price", placeholder="Wholesale Price", key=f"w_price_input12")

                        with col_2:
                            st.write("Yellow Corn Prices")
                            Y_Farmgate_Price = st.text_input(label="Farmgate Corngrains Price", placeholder="Farmgate Price", key=f"f_price_input2")
                            Y_Retail_Price = st.text_input(label="Retail Corngrains Price", placeholder="Retail Price", key=f"r_price_input2")
                            Y_Wholesale_Price_1 = st.text_input(label="Wholesale Corngrits Price", placeholder="Wholesale Price", key=f"w_price_input21")
                            Y_Wholesale_Price_2 = st.text_input(label="Wholesale Corngrains Price", placeholder="Wholesale Price", key=f"w_price_input22")

                # spacer
                st.write(".       ")

                col8, col9 = st.columns(2)

                with col8:
                    if st.session_state.add_current_prov_index <= len(provinces) - 1:
                        # Submit button logic (into temprary dataset)
                        submit_data = st.form_submit_button(f'Submit for {current_prov_1}')
                    else:
                        # Submit button logic (into Database)
                        sent_data_to_database = st.form_submit_button('Submit to the database')
                with col9:
                    if st.session_state.add_current_prov_index != 0:
                        # Get the current province based on the index
                        remove_current_prov = provinces[st.session_state.add_current_prov_index - 1]

                        # Remove button logic
                        remove_data = st.form_submit_button(f'Remove {remove_current_prov} data')

                # Display updated DataFrame
                col8, col9 = st.columns(2)
                with col8:
                    st.write("Production Dataset")
                    st.dataframe(st.session_state.production_input_data)
                with col9:
                    st.write("Fertilizer Dataset")
                    st.dataframe(st.session_state.fertilizer_input_data)

                col10, col11 = st.columns(2)
                with col10:
                    st.write("Weather Dataset")
                    st.dataframe(st.session_state.weather_input_data)
                with col11:
                    st.write("Price Dataset")
                    st.dataframe(st.session_state.price_input_data)




                if st.session_state.add_current_prov_index <= len(provinces) - 1:

                    def validate_and_convert(fields):
                        try:
                            return [float(f) for f in fields]
                        except ValueError:
                            st.error("Please enter valid numeric values for all data.")
                            return None

                    def append_corn_data(df, data, corn_types):
                        for corn_type in corn_types:
                            row = data.copy()
                            row["corn_type"] = corn_type
                            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                        return df



                    if submit_data:
                        corn_types = ["White Corn", "Yellow Corn"]

                        # Fertilizer
                        f_fields = validate_and_convert([Ammophos, Ammosul, Complete, Urea])
                        if not f_fields or not all(f_fields):
                            st.error("Please fill in all fields.")
                            return
                        f_data = {
                            "month": current_month,
                            "year": current_year,
                            "province_id": current_prov_1,
                            **dict(zip(["ammophos_price", "ammosul_price", "complete_price", "urea_price"], f_fields))
                        }
                        st.session_state.fertilizer_input_data = append_corn_data(st.session_state.fertilizer_input_data, f_data, corn_types)



                        # Prices
                        r1 = validate_and_convert([W_Farmgate_Price, W_Retail_Price, 0.00, W_Wholesale_Price_1, W_Wholesale_Price_2])
                        r2 = validate_and_convert([Y_Farmgate_Price, 0.00, Y_Retail_Price, Y_Wholesale_Price_1, Y_Wholesale_Price_2])
                        if not r1 or not r2:
                            return
                        r_field_names = ["farmgate_corngrains_price", "retail_corngrits_price", "retail_corngrains_price", "wholesale_corngrits_price", "wholesale_corngrains_price"]
                        price_data = [
                            dict(month=current_month, year=current_year, province_id=current_prov_1, **dict(zip(r_field_names, r1))),
                            dict(month=current_month, year=current_year, province_id=current_prov_1, **dict(zip(r_field_names, r2)))
                        ]
                        for corn_type, data in zip(corn_types, price_data):
                            data["corn_type"] = corn_type
                            st.session_state.price_input_data = pd.concat([st.session_state.price_input_data, pd.DataFrame([data])], ignore_index=True)



                        # Production
                        prod_fields = validate_and_convert([W_Production, Y_Production])
                        if not prod_fields or not all(prod_fields):
                            st.error("Please fill in the production field.")
                            return
                        prod_data = [
                            dict(month=current_month, year=current_year, province_id=current_prov_1, corn_type="White Corn", corn_production=W_Production),
                            dict(month=current_month, year=current_year, province_id=current_prov_1, corn_type="Yellow Corn", corn_production=Y_Production)
                        ]
                        for data in prod_data:
                            st.session_state.production_input_data = pd.concat([st.session_state.production_input_data, pd.DataFrame([data])], ignore_index=True)



                        # Weather
                        w_fields = validate_and_convert([Feelslike, Dew, Humidity, Precip, Precipcover, Windgust, Windspeed, Winddir, Sealevelpressure, Visibility, Severerisk])
                        if not w_fields or not all(w_fields):
                            st.error("Please fill in all fields.")
                            return
                        w_field_names = ["feelslike", "dew", "humidity", "precip", "precipcover", "windgust", "windspeed", "winddir", "sealevelpressure", "visibility", "severerisk"]
                        w_data = {
                            "month": current_month,
                            "year": current_year,
                            "province_id": current_prov_1,
                            **dict(zip(w_field_names, w_fields)),
                            "conditions": Conditions
                        }
                        st.session_state.weather_input_data = append_corn_data(st.session_state.weather_input_data, w_data, corn_types)


                        clear_text_input()
                        st.session_state.add_form_key += 1
                        st.session_state.add_current_prov_index += 1
                        st.success(f"Data for {current_prov_1} added successfully!")
                        st.rerun()



                else:
                    if sent_data_to_database:
                        # Opening modal abut choosing to countinue to submit data or cancel it out
                        modal_1.open()



                if st.session_state.add_current_prov_index != 0 and remove_data:
                    remove_current_prov = provinces[st.session_state.add_current_prov_index - 1]
                    mask = st.session_state.production_input_data['province_id'] == remove_current_prov
                    if not st.session_state.production_input_data[mask].empty:
                        for key in ['production_input_data', 'price_input_data', 'weather_input_data', 'fertilizer_input_data']:
                            st.session_state[key] = st.session_state[key][st.session_state[key]['province_id'] != remove_current_prov]
                        st.session_state.add_current_prov_index -= 1
                        st.rerun()
                        st.success(f"Data for {remove_current_prov} removed successfully!")
                    else:
                        st.warning(f"No data found for {remove_current_prov} to remove.")


        if selected_feature == 'Edit Data':

            if not st.session_state["ready_edit"]:
                st.header("Select Year and Month")

                month_names = list(month_mapping.keys())

                # st.write(st.session_state.selected_month)
                # st.write(st.session_state.selected_year)

                def update_year():
                    selected_month_num = month_mapping[st.session_state.selected_month]
                    if selected_month_num > last_month and st.session_state.selected_year == last_year:
                        st.session_state.selected_year = last_year - 1
                        st.rerun()
                def update_month():
                    selected_month_num = month_mapping[st.session_state.selected_month]
                    if selected_month_num > last_month and st.session_state.selected_year == last_year:
                        st.session_state.selected_month = month_mapping_num[last_month]
                        st.rerun()
                

                col_1, col_2 = st.columns(2)

                with col_1:
                    Month = st.selectbox(
                        "Month",
                        month_names,
                        index=month_names.index(st.session_state.selected_month),
                    )

                with col_2:
                    # Get unique years dynamically
                    year_option_list = get_unique_years()

                    Year = st.selectbox(
                        "Select Year",
                        year_option_list,
                        index=year_option_list.index(st.session_state.selected_year),
                    )

                # Update session state manually if changed
                if Month != st.session_state.selected_month:
                    st.session_state.selected_month = Month
                    st.session_state.selected_year = Year
                    update_year()
                    st.rerun()

                if Year != st.session_state.selected_year:
                    st.session_state.selected_month = Month
                    st.session_state.selected_year = Year
                    update_month()
                    st.rerun()

                # st.write(f"Selected Month Number: {month_mapping[st.session_state.selected_month]}")
                # st.write(f"Selected Year: {st.session_state.selected_year}")


                if st.button("Edit data", key="ready_for_edit_button"):
                    st.session_state.ready_edit = True    
                    st.rerun()        


            if st.session_state["ready_edit"]:

                # st.write(st.session_state.selected_month)
                # st.write(st.session_state.selected_year)

                current_month = st.session_state.selected_month
                current_year = st.session_state.selected_year

                # Create a form for data entry for the current province
                if st.button("Back to Choose Month and Year", key="go_back_button"):
                    st.session_state.ready_edit = False    
                    st.rerun()  

                with st.form(key=f'data_edit_form_{edit_form_key}'):

                    try:
                        if st.session_state.edit_current_prov_index <= len(provinces) - 1:
                            w_production, y_production = get_production_dataset_for_edit(month_mapping[current_month], current_year, st.session_state.edit_current_prov_index + 1)
                            ammophos, ammosul, complete, urea =  get_fertilizer_dataset_for_edit(month_mapping[current_month], current_year, st.session_state.edit_current_prov_index + 1)
                            feelslike, dew, humidity, precip, precipcover, windgust, windspeed, winddir, sealevelpressure, visibility, severerisk, conditions =  get_weather_dataset_for_edit(month_mapping[current_month], current_year, st.session_state.edit_current_prov_index + 1)
                            w_farmgate, w_retail, w_wholesale_1, w_wholesale_2, y_farmgate, y_retail, y_wholesale_1, y_wholesale_2  =  get_price_dataset_for_edit(month_mapping[current_month], current_year, st.session_state.edit_current_prov_index + 1)


                            st.header(f"Data Edit for {current_prov_2}")
                            col1, col2 = st.columns((1.5, 1.5))

                            with col1:
                                Month = st.text_input(label="Month", placeholder=f"{current_month}", key=f"month_input", disabled=True)
                            with col2: 
                                Year = st.text_input(label="Year", placeholder=f"{current_year}", key=f"year_input", disabled=True)

                            col4, col5, col6, col7 = st.columns((0.5, 0.5, 1.5, 1.5))

                            with col4:
                                st.write("Corn Productions")
                                W_Production = st.text_input(label="White Corn Production", placeholder=f"Production", value=str(w_production), key=f"production_input1")
                                Y_Production = st.text_input(label="Yellow Corn Production", placeholder=f"Production", value=str(y_production), key=f"production_input2")

                            with col5:
                                st.write("Fertilizers Prices")
                                Ammophos = st.text_input(label="Ammophos Price", placeholder="Ammophos Price", value=str(ammophos), key=f"amp_price_input")
                                Ammosul = st.text_input(label="Ammosul Price", placeholder="Ammosul Price", value=str(ammosul), key=f"ams_price_input")
                                Complete = st.text_input(label="Complete Price", placeholder="Complete Price", value=str(complete), key=f"com_price_input")
                                Urea = st.text_input(label="Urea Price", placeholder="Urea Price", value=str(urea), key=f"urea_price_input")
                                
                            with col6:
                                st.write("Weather Data")
                                col_1, col_2, col_3 = st.columns(3)
                                    
                                with col_1:
                                    Feelslike = st.text_input(label="Feels Like Temp.", placeholder="Feels Like Temp.", value=str(feelslike), key=f"feelslike_input")
                                    Dew = st.text_input(label="Dew", placeholder="Dew", value=str(dew), key=f"dew_input")
                                    Humidity = st.text_input(label="Humidity", placeholder="Humidity", value=str(humidity), key=f"humidity_input")
                                    Precip = st.text_input(label="Precipitation", placeholder="Precipitation", value=str(precip), key=f"precip_input")
                                    
                                with col_2:
                                    Precipcover = st.text_input(label="Precipitation Cover", placeholder="Precipitation Cover", value=str(precipcover), key=f"precov_input")
                                    Windgust = st.text_input(label="Wind Gust", placeholder="Wind Gust", value=str(windgust), key=f"windgust_input")
                                    Windspeed = st.text_input(label="Wind Speed", placeholder="Wind Speed", value=str(windspeed), key=f"windspeed_input")
                                    Winddir = st.text_input(label="Wind Direction", placeholder="Wind Direction", value=str(winddir), key=f"winddir_input")
                                
                                with col_3:
                                    Sealevelpressure = st.text_input(label="Sea Level Pressure", placeholder="Sea Level Pressure", value=str(sealevelpressure), key=f"sea_level_input")
                                    Visibility = st.text_input(label="Visibility", placeholder="Visibility", value=str(visibility), key=f"visibility_input")
                                    Severerisk = st.text_input(label="Severe Risk", placeholder="Severe Risk", value=str(severerisk), key=f"severerisk_input")
                                    Conditions = st.selectbox("Condiions:", ['Partly Cloudy', 'Rain, Partially Cloudy', 'Rain, Overcast', 'Overcast'], index=int(conditions - 1), key=f"conditions_input")

                            with col7:
                                col_1, col_2 = st.columns(2)
                                with col_1:
                                    st.write("White Corn Prices")
                                    W_Farmgate_Price = st.text_input(label="Farmgate Corngrains Price", placeholder="Farmgate Price", value=str(w_farmgate), key=f"f_price_input1")
                                    W_Retail_Price = st.text_input(label="Retail Corngrits Price", placeholder="Retail Price", value=str(w_retail), key=f"r_price_input1")
                                    W_Wholesale_Price_1 = st.text_input(label="Wholesale Corngrits Price", placeholder="Wholesale Price", value=str(w_wholesale_1), key=f"w_price_input11")
                                    W_Wholesale_Price_2 = st.text_input(label="Wholesale Corngrains Price", placeholder="Wholesale Price", value=str(w_wholesale_2), key=f"w_price_input12")

                                with col_2:
                                    st.write("Yellow Corn Prices")
                                    Y_Farmgate_Price = st.text_input(label="Farmgate Corngrains Price", placeholder="Farmgate Price", value=str(y_farmgate), key=f"f_price_input2")
                                    Y_Retail_Price = st.text_input(label="Retail Corngrains Price", placeholder="Retail Price", value=str(y_retail), key=f"r_price_input2")
                                    Y_Wholesale_Price_1 = st.text_input(label="Wholesale Corngrits Price", placeholder="Wholesale Price", value=str(y_wholesale_1), key=f"w_price_input21")
                                    Y_Wholesale_Price_2 = st.text_input(label="Wholesale Corngrains Price", placeholder="Wholesale Price", value=str(y_wholesale_2), key=f"w_price_input22")

                    except httpx.RequestError as e:  # Catch connection & request-related errors
                        st.error("Connection error: Unable to connect to the server. Please try again later.")
                        if st.button("Reload"):
                            st.rerun()
                        st.stop()  # Prevents further execution

                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")
                        st.error("Connection error: Unable to connect to the server. Please try again later.")
                        if st.button("Reload"):
                            st.rerun()
                        st.stop()  # Prevents further execution  


                    # spacer
                    st.write(".       ")

                    col8, col9 = st.columns(2)

                    with col8:
                        if st.session_state.edit_current_prov_index <= len(provinces) - 1:
                            # Submit button logic (into temprary dataset)
                            submit_data = st.form_submit_button(f'Submit for {current_prov_2}')
                        else:
                            # Submit button logic (into Database)
                            sent_edited_data_to_database = st.form_submit_button('Submit to the database')
                    with col9:
                        if st.session_state.edit_current_prov_index != 0:
                            # Get the current province based on the index
                            remove_current_prov = provinces[st.session_state.edit_current_prov_index - 1]

                            # Remove button logic
                            remove_data = st.form_submit_button(f'Remove {remove_current_prov} data')

                    # Display updated DataFrame
                    col8, col9 = st.columns(2)
                    with col8:
                        st.write("Production Dataset")
                        st.dataframe(st.session_state.production_edit_data)
                    with col9:
                        st.write("Fertilizer Dataset")
                        st.dataframe(st.session_state.fertilizer_edit_data)

                    col10, col11 = st.columns(2)
                    with col10:
                        st.write("Weather Dataset")
                        st.dataframe(st.session_state.weather_edit_data)
                    with col11:
                        st.write("Price Dataset")
                        st.dataframe(st.session_state.price_edit_data)




                    if st.session_state.edit_current_prov_index <= len(provinces) - 1:

                        def validate_and_convert(fields):
                            try:
                                return [float(f) for f in fields]
                            except ValueError:
                                st.error("Please enter valid numeric values for all data.")
                                return None

                        def append_corn_data(df, data, corn_types):
                            for corn_type in corn_types:
                                row = data.copy()
                                row["corn_type"] = corn_type
                                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                            return df



                        if submit_data:
                            corn_types = ["White Corn", "Yellow Corn"]

                            # Fertilizer
                            f_fields = validate_and_convert([Ammophos, Ammosul, Complete, Urea])
                            if not f_fields or not all(f_fields):
                                st.error("Please fill in all fields.")
                                return
                            f_data = {
                                "month": current_month,
                                "year": current_year,
                                "province_id": current_prov_2,
                                **dict(zip(["ammophos_price", "ammosul_price", "complete_price", "urea_price"], f_fields))
                            }
                            st.session_state.fertilizer_edit_data = append_corn_data(st.session_state.fertilizer_edit_data, f_data, corn_types)



                            # Prices
                            r1 = validate_and_convert([W_Farmgate_Price, W_Retail_Price, 0.00, W_Wholesale_Price_1, W_Wholesale_Price_2])
                            r2 = validate_and_convert([Y_Farmgate_Price, 0.00, Y_Retail_Price, Y_Wholesale_Price_1, Y_Wholesale_Price_2])
                            if not r1 or not r2:
                                return
                            r_field_names = ["farmgate_corngrains_price", "retail_corngrits_price", "retail_corngrains_price", "wholesale_corngrits_price", "wholesale_corngrains_price"]
                            price_data = [
                                dict(month=current_month, year=current_year, province_id=current_prov_2, **dict(zip(r_field_names, r1))),
                                dict(month=current_month, year=current_year, province_id=current_prov_2, **dict(zip(r_field_names, r2)))
                            ]
                            for corn_type, data in zip(corn_types, price_data):
                                data["corn_type"] = corn_type
                                st.session_state.price_edit_data = pd.concat([st.session_state.price_edit_data, pd.DataFrame([data])], ignore_index=True)



                            # Production
                            prod_fields = validate_and_convert([W_Production, Y_Production])
                            if not prod_fields or not all(prod_fields):
                                st.error("Please fill in the production field.")
                                return
                            prod_data = [
                                dict(month=current_month, year=current_year, province_id=current_prov_2, corn_type="White Corn", corn_production=W_Production),
                                dict(month=current_month, year=current_year, province_id=current_prov_2, corn_type="Yellow Corn", corn_production=Y_Production)
                            ]
                            for data in prod_data:
                                st.session_state.production_edit_data = pd.concat([st.session_state.production_edit_data, pd.DataFrame([data])], ignore_index=True)



                            # Weather
                            w_fields = validate_and_convert([Feelslike, Dew, Humidity, Precip, Precipcover, Windgust, Windspeed, Winddir, Sealevelpressure, Visibility, Severerisk])
                            if not w_fields or not all(w_fields):
                                st.error("Please fill in all fields.")
                                return
                            w_field_names = ["feelslike", "dew", "humidity", "precip", "precipcover", "windgust", "windspeed", "winddir", "sealevelpressure", "visibility", "severerisk"]
                            w_data = {
                                "month": current_month,
                                "year": current_year,
                                "province_id": current_prov_2,
                                **dict(zip(w_field_names, w_fields)),
                                "conditions": Conditions
                            }
                            st.session_state.weather_edit_data = append_corn_data(st.session_state.weather_edit_data, w_data, corn_types)


                            clear_text_input()
                            st.session_state.edit_form_key += 1
                            st.session_state.edit_current_prov_index += 1
                            st.success(f"Data for {current_prov_2} added successfully!")
                            st.rerun()



                    else:
                        if sent_edited_data_to_database:
                            # Opening modal abut choosing to countinue to submit data or cancel it out
                            modal_2.open()



                    if st.session_state.edit_current_prov_index != 0 and remove_data:
                        remove_current_prov = provinces[st.session_state.edit_current_prov_index - 1]
                        mask = st.session_state.production_edit_data['province_id'] == remove_current_prov
                        if not st.session_state.production_edit_data[mask].empty:
                            for key in ['production_edit_data', 'price_edit_data', 'weather_edit_data', 'fertilizer_edit_data']:
                                st.session_state[key] = st.session_state[key][st.session_state[key]['province_id'] != remove_current_prov]
                            st.session_state.edit_current_prov_index -= 1
                            st.rerun()
                            st.success(f"Data for {remove_current_prov} removed successfully!")
                        else:
                            st.warning(f"No data found for {remove_current_prov} to remove.")

                
    else:  

         # Function to hide/show sidebar
        def toggle_sidebar(state):
            if state:
                hide_sidebar = """
                    <style>
                        [data-testid="stSidebar"] {display: none;}
                    </style>
                """
                st.markdown(hide_sidebar, unsafe_allow_html=True)

        # Initialize session state for sidebar control
        if "training" not in st.session_state:
            st.session_state["training"] = False

        # Initialize session state for refresh control
        if "refresh_control" not in st.session_state:
            st.session_state["refresh_control"] = False

        


        toggle_sidebar(st.session_state["training"])

        # Only show buttons when training is NOT in progress
        if not st.session_state["training"] and not st.session_state["refresh_control"]:
            st.success("Your System is Ready to be train")     
            st.write("Do you want train the model with the new data or add another?") 

            col_1, col_2 = st.columns(2)

            with col_1:
                train_data = st.button("Train Data", key="train_data_button")

            with col_2:
                add_data = st.button("Add More Data", key="add_data_button_1")

            # Handle training button
            if train_data:
                st.session_state["training"] = True
                st.rerun()

            # Handle add data button
            if add_data:
                st.session_state.form_key = 0
                st.session_state.current_prov_index = 0
                st.session_state.selected_dataset2_num = 0
                st.session_state.input_data = production_database
                st.rerun()  # Rerun to reflect changes


        if st.session_state["refresh_control"]:
            st.success("The Model is Fully Trained, Ready to Add More Data!")
            if st.button("Add More Data", key="add_data_button_2"):
                st.session_state.form_key = 0
                st.session_state.current_prov_index = 0
                st.session_state.selected_dataset2_num = 0
                st.session_state.input_data = production_database
                st.session_state["refresh_control"] = False
                st.rerun()  # Rerun to reflect changes


        # Simulated training process
        if st.session_state["training"]:
            st.success("Training model...")

# # ==============================================[PREDICTS X TEST]=================================================================================   

            def predict_predictor(dataset, predictor_set, corn_type, folder_type, province_name, main_target):
                # Create datetime index from year and month
                new_dataset = dataset

                new_dataset['ds'] = pd.to_datetime(new_dataset['year'].astype(str) + '-' + new_dataset['month'].astype(str), format='%Y-%m')
                
                # Initialize dictionary to store models
                models = {}
                predictions_df = pd.DataFrame()
                
                # Remove Main Target
                predictor_set = [x for x in predictor_set if x != f"{main_target}"]

                for target in predictor_set:
                    # Prepare Prophet-compatible dataframe
                    prophet_df = new_dataset[['ds', target]].rename(columns={target: 'y'})
                    

                    # Create and fit Prophet model
                    fr_model = Prophet(yearly_seasonality = True, seasonality_prior_scale=0.1)

                    fr_model.fit(prophet_df)

                    # Create future dataframe
                    future = fr_model.make_future_dataframe(periods=25, freq='M')
                    
                    # Generate predictions
                    forecast = fr_model.predict(future)

                    # Filter forecast to include only future predictions (last 25 rows)
                    forecast = forecast.tail(25)

                    # Remove the first row of the forcast because it tried to predict the last row of the dataset
                    forecast.drop(forecast.index[0], inplace=True)

                    
                    # Store model and predictions
                    models[target] = fr_model
                    predictions = forecast[['ds', 'yhat']].rename(columns={'yhat': target}).round(2)
                    
                    # Merge predictions into main DataFrame
                    if predictions_df.empty:
                        predictions_df = predictions
                    else:
                        predictions_df = pd.merge(predictions_df, predictions, on='ds', how='outer')
                
                # Extract year and month from the 'ds' column (datetime)
                predictions_df['year'] = predictions_df['ds'].dt.year
                predictions_df['month'] = predictions_df['ds'].dt.month
                
                # Drop the datetime column and reorder
                predictions_df = predictions_df.drop('ds', axis=1)
                col_order = ['year', 'month'] + predictor_set
                predictions_df = predictions_df[col_order].reset_index(drop=True)
                
                # st.dataframe(predictions_df)

                # Save results
                upload_csv_to_supabase(predictions_df, f"{corn_type}/{province_name}/{folder_type}/predictor_dataset_for_{main_target}.csv")


                print('Cleaned dataset saved')
                
                return predictions_df



            # # ==============================================[RERF PREDICTS]=================================================================================   

            def RERF_Model(X, Y, corn_type, folder_type, province_name, target):
                # Step 1: Remove the 'ds' column (likely a date or timestamp) from the feature matrix X
                X = X.drop('ds', axis=1)

                # Step 2: Perform k-fold cross-validation to find the optimal Lasso regularization parameter (lambda)
                # LassoCV automatically selects the best alpha (lambda) from the specified range using 5-fold CV
                lasso_cv = LassoCV(alphas=np.logspace(-6, 2, 100), cv=5, random_state=0)
                lasso_cv.fit(X, Y)

                # Extract the best alpha (lambda) value found by cross-validation
                lambda_star = lasso_cv.alpha_

                # Step 3: Fit the Lasso model on the full training data using the optimal lambda
                lasso_optimal = Lasso(alpha=lambda_star)
                lasso_optimal.fit(X, Y)

                # Step 4: Calculate residuals from the Lasso model predictions on training data
                # These residuals represent the part of Y not explained by the Lasso model
                residuals_train = Y - lasso_optimal.predict(X)

                # Step 5: Define hyperparameter grid for Random Forest to model the residuals
                param_grid_rf = {
                    'max_features': ["sqrt", "log2", None],  # Number of features to consider at each split
                    'min_samples_leaf': [1, 3, 5]            # Minimum samples required at a leaf node
                }

                # Step 6: Use GridSearchCV with 5-fold cross-validation to find the best RF hyperparameters
                grid_search_rf = GridSearchCV(
                    estimator=RandomForestRegressor(random_state=42),
                    param_grid=param_grid_rf,
                    cv=5,
                    scoring='r2',    # Use R² as the evaluation metric
                    verbose=2,
                    n_jobs=-1 
                )

                # Fit grid search on features X and residuals from Lasso
                grid_search_rf.fit(X, residuals_train)

                # Step 7: Extract the best hyperparameters found for Random Forest
                best_params_rf = grid_search_rf.best_params_
                s_star = best_params_rf['min_samples_leaf']
                m_star = best_params_rf['max_features']

                # Step 8: Fit the final Random Forest model on residuals using the best hyperparameters
                rf_optimal = RandomForestRegressor(min_samples_leaf=s_star, max_features=m_star, random_state=42)
                rf_optimal.fit(X, residuals_train)

                # Step 9: Save the trained Lasso and Random Forest models to Supabase storage for later use
                upload_model_to_supabase(lasso_optimal, f"{corn_type}/{province_name}/{folder_type}/RERF_Model/Lasso_models_for_{target}.joblib")
                upload_model_to_supabase(rf_optimal, f"{corn_type}/{province_name}/{folder_type}/RERF_Model/RF_models_for_{target}.joblib")






            dataset_features = ['corn_production', 'ammophos_price', 'ammosul_price', 'complete_price', 'urea_price', 'feelslike', 'dew', 
                        'humidity', 'precip', 'precipcover', 'windgust', 'windspeed', 'winddir','sealevelpressure', 'visibility', 
                        'severerisk', 'conditions', 'farmgate_corngrains_price', 'retail_corngrits_price', 'retail_corngrains_price',
                        'wholesale_corngrits_price', 'wholesale_corngrains_price']

            # Load datasets
            white_province_mapping = {
                "davao_region": 1,
                "davao_de_oro": 2,
                "davao_del_norte": 3,
                "davao_del_sur": 4,
                "davao_oriental": 5,
                "davao_city": 6,
            }

            # Load datasets
            yellow_province_mapping = {
                "davao_region": 1,
                "davao_de_oro": 2,
                "davao_del_norte": 3,
                "davao_del_sur": 4,
                "davao_oriental": 5,
                "davao_city": 6,
            }

            # # ==============================================[WHITE CORN PRICE PREDICTS]=================================================================================   

            col_1, col_2 = st.columns(2)

            w_dataset_features = [x for x in dataset_features if x != "retail_corngrains_price"]
            y_dataset_features = [x for x in dataset_features if x != "retail_corngrits_price"]

            try:
                with col_1:
                    st.write("White Corn Price Train")
                    for dataset_name, dataset_id in white_province_mapping.items():

                        # White Corn Datasets
                        dataset = get_white_davao_region_dataset(dataset_id)

                        # predict farmgate price for white_davao_region
                        f_future_pred = predict_predictor(dataset, w_dataset_features, "white_corn", "farmgate", f"{dataset_name}", "farmgate_corngrains_price")

                    
                        f_X = dataset.drop(['farmgate_corngrains_price'], axis=1)
                        f_Y = dataset['farmgate_corngrains_price']
                        RERF_Model(f_X, f_Y, "white_corn", "farmgate", f"{dataset_name}", "farmgate_corngrains_price") 



                        
                        # predict retail price for white_davao_region
                        r_future_pred = predict_predictor(dataset, w_dataset_features, "white_corn", "retail",  f"{dataset_name}", "retail_corngrits_price")
                    
                        r_X = dataset.drop(['retail_corngrits_price'], axis=1)
                        r_Y = dataset['retail_corngrits_price']
                        RERF_Model(r_X, r_Y, "white_corn", "retail",  f"{dataset_name}", "retail_corngrits_price") 




                        # predict wholesale corn grits price for white_davao_region
                        w_future_pred_1 = predict_predictor(dataset, w_dataset_features, "white_corn", "wholesale",  f"{dataset_name}", "wholesale_corngrits_price")
                        print()
                    
                        w_X_1 = dataset.drop(['wholesale_corngrits_price'], axis=1)
                        w_Y_1 = dataset['wholesale_corngrits_price']
                        RERF_Model(w_X_1, w_Y_1, "white_corn", "wholesale",  f"{dataset_name}", "wholesale_corngrits_price") 





                        # predict wholesale corn grains price for white_davao_region
                        w_future_pred_2 = predict_predictor(dataset, w_dataset_features, "white_corn", "wholesale",  f"{dataset_name}", "wholesale_corngrains_price")
                        print()
                    
                        w_X_2 = dataset.drop(['wholesale_corngrains_price'], axis=1)
                        w_Y_2 = dataset['wholesale_corngrains_price']
                        RERF_Model(w_X_2, w_Y_2, "white_corn", "wholesale",  f"{dataset_name}", "wholesale_corngrains_price") 



                        st.success(f'White Corn {dataset_name} trained successfully!')
                        # # st.write(f'Farmgate: {f_r2} || Retail: {r_r2}')
                        # # st.write(f'Wholesale Corngrits: {w_r2_1} || Wholesale Corngrains: {w_r2_2}')


                # # # ==============================================[YELLOW CORN PRICE PREDICTS]=================================================================================   
                with col_2:
                    st.write("Yellow Corn Price Train")
                    for dataset_name, dataset_id in yellow_province_mapping.items():

                        # Yellow Corn Datasets
                        dataset = get_yellow_davao_region_dataset(dataset_id)

                        # st.dataframe(yellow_corn_davao_region)

                        # predict farmgate price for white_davao_region
                        f_future_pred = predict_predictor(dataset, y_dataset_features, "yellow_corn", "farmgate", f"{dataset_name}", "farmgate_corngrains_price")
                    
                        f_X = dataset.drop(['farmgate_corngrains_price'], axis=1)
                        f_Y = dataset['farmgate_corngrains_price']
                        RERF_Model(f_X, f_Y, "yellow_corn", "farmgate", f"{dataset_name}", "farmgate_corngrains_price") 



                        
                        # predict retail price for white_davao_region
                        r_future_pred = predict_predictor(dataset, y_dataset_features, "yellow_corn", "retail",  f"{dataset_name}", "retail_corngrains_price")

                        r_X = dataset.drop(['retail_corngrains_price'], axis=1)
                        r_Y = dataset['retail_corngrains_price']
                        RERF_Model(r_X, r_Y, "yellow_corn", "retail",  f"{dataset_name}", "retail_corngrains_price") 



                        # predict wholesale corn grits price for white_davao_region
                        w_future_pred_1 = predict_predictor(dataset, y_dataset_features, "yellow_corn", "wholesale",  f"{dataset_name}", "wholesale_corngrits_price")
                        print()
                    
                        w_X_1 = dataset.drop(['wholesale_corngrits_price'], axis=1)
                        w_Y_1 = dataset['wholesale_corngrits_price']
                        RERF_Model(w_X_1, w_Y_1, "yellow_corn", "wholesale",  f"{dataset_name}", "wholesale_corngrits_price") 
                    




                        # predict wholesale corn grains price for white_davao_region
                        w_future_pred_2 = predict_predictor(dataset, y_dataset_features, "yellow_corn", "wholesale",  f"{dataset_name}", "wholesale_corngrains_price")
                        print()
                    
                        w_X_2 = dataset.drop(['wholesale_corngrains_price'], axis=1)
                        w_Y_2 = dataset['wholesale_corngrains_price']
                        RERF_Model(w_X_2, w_Y_2, "yellow_corn", "wholesale",  f"{dataset_name}", "wholesale_corngrains_price") 



                        st.success(f'Yellow Corn {dataset_name} trained successfully!')
                        # st.write(f'Farmgate: {f_r2} || Retail: {r_r2}')
                        # st.write(f'Wholesale Corngrits: {w_r2_1} || Wholesale Corngrains: {w_r2_2}')


                        if dataset_name == "davao_city":
                            st.session_state["training"] = False  # Re-enable sidebar
                    
                            st.session_state["refresh_control"] = True # Endable Add More Data Button  
                            st.rerun() 
                    
            except (httpx.RequestError, httpx.WriteTimeout) as e:  # Catch connection & request-related errors
                st.error("Connection error: Unable to connect to the server. Please try again later.")
                if st.button("Reload"):
                    st.rerun()
                st.stop()  # Prevents further execution

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.error("Connection error: Unable to connect to the server. Please try again later.")
                if st.button("Reload"):
                    st.rerun()
                st.stop()  # Prevents further execution                    
            
