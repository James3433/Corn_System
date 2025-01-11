import pandas as pd
import streamlit as st

from supabase_connect import get_user_name, get_user_by_user_type
from supabase_connect import get_white_corn_fertilizer_data, get_yellow_corn_fertilizer_data, get_white_corn_price_data, get_yellow_corn_price_data, get_white_corn_production_data, get_yellow_corn_production_data, get_white_corn_weather_data, get_yellow_corn_weather_data
from supabase_connect import submit_predictions_fertilizer, submit_predictions_price, submit_predictions_production, submit_predictions_weather

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
    conditions_num = {'Partly Cloudy': 1, 'Rain, Partially Cloudy': 2, 'Rain, Overcas': 2, 'Overcast': 4}



    fertilizer_database= pd.DataFrame(columns=["year", "month", "province_id", "ammophos_price", "ammosul_price", "complete_price", "urea_price"])

    weather_database = pd.DataFrame(columns=["year", "month", "province_id","tempmax", "tempmin", "temp", "dew","humidity", "precip", "precipprob",
                                            "precipcover", "windspeed", "sealevelpressure","visibility", "solarradiation", "uvindex","severerisk", 
                                            "cloudcover", "conditions"])
    
    price_database = pd.DataFrame(columns=["year", "month", "province_id", "farmgate_corngrains_price", "retail_corngrits_price", "wholesale_corngrits_price"])
    
    production_database = pd.DataFrame(columns=["year", "month", "province_id", "corn_production"])



    # def fetch_full_name(user_id):
    #     name = get_user_name(user_id)  # Call your function
    #     if name:  # Check if a name is returned
    #         return f"{name[0]} {name[1]}"  # Return fname lname as a full name
    #     return None



    def clear_text_input():
        # Clear text inputs
        Ammophos, Ammosul, Complete, Urea = "", "", "", ""
        Farmgate_Price, Retail_Price, Wholesale_Price = "", "", ""
        Production = ""
        temp_max, temp_min, temp, dew, humidity, precip, precipprob, precipcover, windspeed = "", "", "", "", "", "", "", "", ""
        sealevelpressure, visibility, solarradiation, uvindex, severerisk, cloudcover, conditions = "", "", "", "", "", "", ""


    def prevent_selection_change(selected_dataset2, previous_selection):
        if selected_dataset2 != previous_selection:
            if 'input_data' in st.session_state and not st.session_state.input_data.empty:
                st.warning("Cannot switch selection. Please clear or submit existing data first.")
                return previous_selection
        return selected_dataset2



    if "selected_dataset2_prev" not in st.session_state:
        st.session_state.selected_dataset2_prev = 'Fertilizer Price'


    selected_dataset1 = st.sidebar.selectbox("Choose an option:", ['White Corn Price', 'Yellow Corn Price'])
    selected_dataset2 = st.selectbox("Choose an option:", ['Fertilizer Price', 'Cron Price', 'Corn Production', 'Weather Info'])


    selected_dataset2 = prevent_selection_change(selected_dataset2, st.session_state.selected_dataset2_prev)

    # Update previous selection
    st.session_state.selected_dataset2_prev = selected_dataset2



    # Group the data by year based on the selected dataset
    if selected_dataset1 == 'White Corn Price':

        corn_type = "White Corn"
        if selected_dataset2 == "Fertilizer Price":
            response = get_white_corn_fertilizer_data()
            
        elif selected_dataset2 == "Cron Price":
            response = get_white_corn_price_data()         

        elif selected_dataset2 == "Corn Production":
            response = get_white_corn_production_data()
            
        elif selected_dataset2 == "Weather Info":
            response = get_white_corn_weather_data()
            

    else:

        corn_type = "Yellow Corn"
        if selected_dataset2 == "Fertilizer Price":
            response = get_yellow_corn_fertilizer_data()
            
        elif selected_dataset2 == "Cron Price":
            response = get_yellow_corn_price_data()         

        elif selected_dataset2 == "Corn Production":
            response = get_yellow_corn_production_data()        
            
        elif selected_dataset2 == "Weather Info":
            response = get_yellow_corn_weather_data()
            

            
    dataset = pd.DataFrame(response)

    # Drop id and province_id
    dataset = dataset.drop(columns=["id"], axis=1)

    # # Apply fetch_full_name to the 'user_id' column
    # dataset['user_id'] = dataset['user_id'].apply(fetch_full_name)

    # Get the current year and month
    last_year = dataset['year'].iloc[-1]
    current_year = last_year
    # Get the last row of the 'month' column
    last_month = dataset['month'].iloc[-1]
    current_month = last_month + 1


    # The get_users_by_user_type function now returns all users with the specified user_type instead of just the first one.
    usernames = get_user_by_user_type(4)


    # Use a unique key for the form by incrementing it each time the form is submitted.
    form_key = st.session_state.get('form_key', 0)


    # Initialize session state for current province index if not already done
    if "current_prov_index" not in st.session_state:
        st.session_state.current_prov_index = 0


    if st.session_state.current_prov_index <= len(provinces) - 1:
        current_prov = provinces[st.session_state.current_prov_index]
    else:
        current_prov = provinces[5]


    if 'input_data' not in st.session_state:
        st.session_state.input_data = pd.DataFrame()  # or some default DataFrame
        if selected_dataset2 == "Fertilizer Price":
            st.session_state.input_data = fertilizer_database
        
        elif selected_dataset2 == "Cron Price":
            st.session_state.input_data = price_database
        
        elif selected_dataset2 == "Corn Production":
            st.session_state.input_data = production_database
            
        elif selected_dataset2 == "Weather Info":
            st.session_state.input_data = weather_database


    if usernames:
        usernames = usernames
    else:
        usernames = "No users found with user_type = 4."


    col1, col2 = st.columns((1.5, 1.5))

    with col1:
        st.header(f"{selected_dataset1} {selected_dataset2}")
        st.dataframe(dataset)
        # st.write("Province = 'Davao Region': 1, 'Davao de Oro': 2, 'Davao del Norte': 3, 'Davao del Sur': 4, 'Davao Oriental': 5, 'Davao City': 6")
        
        st.markdown(f"""
        <div style="background-color: #a3f841; padding: 10px; border-radius: 20px;">
            <h6> Province = 'Davao Region': 1, 'Davao de Oro': 2, 'Davao del Norte': 3, 'Davao del Sur': 4, 'Davao Oriental': 5, 'Davao City': 6 </h6>
            <h6> User Admin = {usernames} </h6>
        </div>
        """, unsafe_allow_html=True)

    with col2: 
        # Create a form for data entry for the current province
        with st.form(key=f'data_entry_form_{form_key}'):
            st.header(f"Data Entry for {current_prov}")
            
            col4, col5 = st.columns(2)

            with col4:
                Month = st.text_input(label="Month", placeholder=f"{current_month}", key=f"month_input", disabled=True)

                # Check if Month input is valid and adjust Year accordingly
                if current_month < last_month:
                    current_year = int(last_year) + 1  # Increment year by 1 if Month is less than last_month

            with col5:
                Year = st.text_input(label="Year", placeholder=f"{current_year}", key=f"year_input", disabled=True)


            if selected_dataset2 == "Fertilizer Price":

                col_1, col_2, col_3, col_4 = st.columns(4)
                with col_1:
                    Ammophos = st.text_input(label="Ammophos Price", placeholder="Ammophos Price", key=f"amp_price_input")
                with col_2:
                    Ammosul = st.text_input(label="Ammosul Price", placeholder="Ammosul Price", key=f"ams_price_input")
                with col_3:
                    Complete = st.text_input(label="Complete Price", placeholder="Complete Price", key=f"com_price_input")
                with col_4:
                    Urea = st.text_input(label="Urea Price", placeholder="Urea Price", key=f"urea_price_input")


            elif selected_dataset2 == "Cron Price":

                col_1, col_2, col_3 = st.columns(3)
                with col_1:
                    Farmgate_Price = st.text_input(label="Farmgate Price", placeholder="Farmgate Price", key=f"f_price_input")
                with col_2:
                    Retail_Price = st.text_input(label="Retail Price", placeholder="Retail Price", key=f"r_price_input")
                with col_3:
                    Wholesale_Price = st.text_input(label="Wholesale Price", placeholder="Wholesale Price", key=f"w_price_input")

            elif selected_dataset2 == "Corn Production":
                Production = st.text_input(label="Production", placeholder="Production", key=f"production_input")

            elif selected_dataset2 == "Weather Info":

                col_1, col_2, col_3 = st.columns(3)
                
                with col_1:
                    temp_min = st.text_input(label="Temperature/Max", placeholder="Temperature/Max", key=f"t_min_input")
                    temp_max = st.text_input(label="Temperature/Max", placeholder="Temperature/Max", key=f"t_max_input")
                    temp = st.text_input(label="Temperature", placeholder="Temperature", key=f"t_input")
                    dew = st.text_input(label="Dew", placeholder="Ammophos Price", key=f"dew_input")
                    humidity = st.text_input(label="Humidity", placeholder="Ammophos Price", key=f"hum_input")
                    
                with col_2:
                    precip = st.text_input(label="Precipitation", placeholder="Precipitation", key=f"precip_input")
                    precipprob = st.text_input(label="Precipitation Probability", placeholder="Precipitation Probability", key=f"preciprob_input")
                    precipcover = st.text_input(label="Precipitation Cover", placeholder="Precipitation Cover", key=f"precov_input")
                    windspeed = st.text_input(label="wind Speed", placeholder="Ammosul Price", key=f"wind_input")
                    sealevelpressure = st.text_input(label="Sea Level Pressure", placeholder="Sea Level Pressure", key=f"sea_input")
                
                with col_3:
                    visibility = st.text_input(label="Visibility", placeholder="Visibility", key=f"vis_price_input")
                    solarradiation = st.text_input(label="Solar Radiation", placeholder="Solar Radiation", key=f"solar_price_input")
                    uvindex = st.text_input(label="Ultraviolet Index", placeholder="Ultraviolet Index", key=f"uv_price_input")
                    severerisk = st.text_input(label="Severe Risk", placeholder="Severe Risk", key=f"sr_price_input")
                    cloudcover = st.text_input(label="Clould Cover", placeholder="Clould Cover", key=f"cloud_price_input")

                conditions = st.selectbox("Condiions:", ['Partly Cloudy', 'Rain, Partially Cloudy', 'Rain, Overcast', 'Overcast'])


            if st.session_state.current_prov_index <= len(provinces) - 1:
                if st.form_submit_button(f'Submit for {current_prov}'):

                    if selected_dataset2 == "Fertilizer Price":
                        fields = [Ammophos, Ammosul, Complete, Urea]
                        field_names = ["ammophos_price", "ammosul_price", "complete_price", "urea_price"]
                        if not all(fields):
                            st.error("Please fill in all fields.")
                            return
                        
                        new_data = {
                            "month": current_month,
                            "year": current_year,
                            "province_id": current_prov,
                            **dict(zip(field_names, fields))
                        }

                    elif selected_dataset2 == "Cron Price":
                        fields = [Farmgate_Price, Retail_Price, Wholesale_Price]
                        field_names = ["farmgate_corngrains_price", "retail_corngrits_price", "wholesale_corngrits_price"]
                        if not all(fields):
                            st.error("Please fill in all fields.")
                            return
                        new_data = {
                            "month": current_month,
                            "year": current_year,
                            "province_id": current_prov,
                            **dict(zip(field_names, fields))
                        }
                        
                    elif selected_dataset2 == "Corn Production":
                        if not Production:
                            st.error("Please fill in all fields.")
                            return
                        new_data = {
                            "month": current_month,
                            "year": current_year,
                            "province_id": current_prov,
                            "corn_production": Production
                        }

                    elif selected_dataset2 == "Weather Info":
                        fields = [temp_max, temp_min, temp, dew, humidity, precip, precipprob, precipcover, windspeed, sealevelpressure, visibility, solarradiation, uvindex, severerisk, cloudcover]
                        field_names = ["tempmax", "tempmin", "temp", "dew", "humidity", "precip", "precipprob", "precipcover", "windspeed", "sealevelpressure", "visibility", "solarradiation", "uvindex", "severerisk", "cloudcover"]
                        if not all(fields):
                            st.error("Please fill in all fields.")
                            return
                        new_data = {
                            "month": current_month,
                            "year": current_year,
                            "province_id": current_prov,
                            **dict(zip(field_names, fields)),
                            "conditions": conditions.map(conditions_num)
                        }

                    new_row_df = pd.DataFrame([new_data])
                    st.session_state.input_data = pd.concat([st.session_state.input_data, new_row_df], ignore_index=True)

                    # Clear text inputs
                    clear_text_input()

                    st.session_state.form_key += 1
                    st.session_state.current_prov_index += 1
                    st.success(f"Data for {current_prov} added successfully!")
                    st.rerun()  # Rerun to reflect changes

            else:

                if st.form_submit_button(f'Submit to the database'):
                    
                    st.session_state.input_data['province_id'] = st.session_state.input_data['province_id'].map(provinces_num)

                    if selected_dataset2 == "Fertilizer Price":
                        submit_predictions_fertilizer(st.session_state.input_data, user_id, corn_type)
                        st.session_state.input_data = fertilizer_database
                    
                    elif selected_dataset2 == "Cron Price":
                        submit_predictions_price(st.session_state.input_data, user_id, corn_type)
                        st.session_state.input_data = price_database
                    
                    elif selected_dataset2 == "Corn Production":
                        submit_predictions_production(st.session_state.input_data, user_id, corn_type)
                        st.session_state.input_data = production_database
                        
                    elif selected_dataset2 == "Weather Info":
                        submit_predictions_weather(st.session_state.input_data, user_id, corn_type)
                        st.session_state.input_data = weather_database

                    st.session_state.current_prov_index = 0

                    # Clear text inputs
                    clear_text_input()

                    st.rerun() # Rerun to reflect changes

            if st.session_state.current_prov_index != 0:

                # Get the current province based on the index
                current_prov = provinces[st.session_state.current_prov_index -1]

                # Remove button logic
                if st.form_submit_button(f'Remove {current_prov} data'):

                    if not st.session_state.input_data[st.session_state.input_data['province_id'] == current_prov].empty:
                        # Remove entries for the current province
                        st.session_state.input_data = st.session_state.input_data[st.session_state.input_data['province_id'] != current_prov]

                        st.session_state.current_prov_index -= 1

                        st.rerun() # Rerun to reflect changes

                        st.success(f"Data for {current_prov} removed successfully!")

                    else:
                        st.warning(f"No data found for {current_prov} to remove.")

            # Display updated DataFrame again after removal
            st.dataframe(st.session_state.input_data)
            