import pandas as pd
import numpy as np
import streamlit as st
import joblib
import httpx

from streamlit_modal import Modal

from supabase_connect import get_user_name, get_user_by_user_type
from supabase_connect import get_fertilizer_data, get_weather_data, get_white_corn_price_data, get_yellow_corn_price_data, get_white_corn_production_data, get_yellow_corn_production_data
from supabase_connect import submit_predictions_fertilizer, submit_predictions_price, submit_predictions_production, submit_predictions_weather

from supabase_connect import get_corn_production_dataset, get_fertilizer_dataset, get_weather_dataset, get_corn_price_dataset

from supabase_connect import get_white_davao_region_dataset, get_white_davao_de_oro_dataset, get_white_davao_del_norte_dataset, get_white_davao_del_sur_dataset, get_white_davao_oriental_dataset, get_white_davao_city_dataset
from supabase_connect import get_yellow_davao_region_dataset, get_yellow_davao_de_oro_dataset, get_yellow_davao_del_norte_dataset, get_yellow_davao_del_sur_dataset, get_yellow_davao_oriental_dataset, get_yellow_davao_city_dataset
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
    conditions_num = {'Partly Cloudy': 1, 'Rain, Partially Cloudy': 2, 'Rain, Overcas': 2, 'Overcast': 4}
    corn_type = {'White Corn': 1, 'Yellow Corn': 2}



    fertilizer_database= pd.DataFrame(columns=["year", "month", "province_id", "corn_type", "ammophos_price", "ammosul_price", "complete_price", "urea_price"])

    # weather_database = pd.DataFrame(columns=["year", "month", "province_id", "corn_type", "temp", "feelslike", "dew", "humidity", "precip", "precipprob","precipcover", 'windgust', 
    #                                 "windspeed", "winddir", "sealevelpressure","visibility", "solarradiation", "solarenergy", "uvindex", "severerisk", "cloudcover", "conditions"])
    
    weather_database = pd.DataFrame(columns=["year", "month", "province_id", "corn_type", "feelslike", "dew", "humidity", "precip", "precipcover", 
                                    'windgust', "windspeed", "winddir", "sealevelpressure", "visibility", "severerisk", "conditions"])
    

    price_database = pd.DataFrame(columns=["year", "month", "province_id", "corn_type", "farmgate_corngrains_price", "retail_corngrits_price", "wholesale_corngrits_price"])
    
    production_database = pd.DataFrame(columns=["year", "month", "province_id", "corn_type", "corn_production"])



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
        feelslike, dew, humidity, precip, precipcover, windspeed = "", "", "", "", "", ""
        sealevelpressure, visibility, severerisk, conditions = "", "", "", ""



    if "selected_dataset2_num" not in st.session_state:
        st.session_state.selected_dataset2_num = 0


    
    dataset2 = ['Corn Production', 'Fertilizer Price', 'Weather Info', 'Corn Price', 'Train Data']


    selected_dataset2 = dataset2[st.session_state.selected_dataset2_num]

    # Update previous selection
    st.session_state.selected_dataset2_prev = selected_dataset2


    # Get dataset from Supabase
    try:
        if selected_dataset2 == "Fertilizer Price":
            response_1 = get_fertilizer_data()
            
        elif selected_dataset2 == "Corn Price":
            response_1 = get_white_corn_price_data()
            response_2 = get_yellow_corn_price_data()      
        
        elif selected_dataset2 == "Corn Production":
            response_1 = get_white_corn_production_data()
            response_2 = get_yellow_corn_production_data()
            
        elif selected_dataset2 == "Weather Info":
            response_1 = get_weather_data()


        # The get_users_by_user_type function now returns all users with the specified user_type instead of just the first one.
        usernames = get_user_by_user_type(4)

    except httpx.RequestError as e:  # Catch connection & request-related errors
        st.error("Connection error: Unable to connect to the server. Please try again later.")
        if st.button("Reload"):
            st.rerun()
        st.stop()  # Prevents further execution

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        if st.button("Reload"):
            st.rerun()
        st.stop()  # Prevents further execution
            


    if 'input_data' not in st.session_state:
        st.session_state.input_data = pd.DataFrame()  # or some default DataFrame

        if selected_dataset2 == "Fertilizer Price":
            st.session_state.input_data = fertilizer_database

        elif selected_dataset2 == "Corn Price":
            st.session_state.input_data = price_database

        elif selected_dataset2 == "Corn Production":
            st.session_state.input_data = production_database
            
        elif selected_dataset2 == "Weather Info":
            st.session_state.input_data = weather_database



    # Use a unique key for the form by incrementing it each time the form is submitted.
    if "form_key" not in st.session_state:
        st.session_state.form_key = 0


    # Initialize session state for current province index if not already done
    if "current_prov_index" not in st.session_state:
        st.session_state.current_prov_index = 0


    form_key = st.session_state.get('form_key')


    if st.session_state.current_prov_index <= len(provinces) - 1:
        current_prov = provinces[st.session_state.current_prov_index]
    else:
        current_prov = provinces[5]



    if usernames:
        usernames = usernames
    else:
        usernames = "No users found with user_type = 4."



    # Create a modal instance
    modal = Modal("Submit Data", key="submit-data-modal", padding=20)

    # Render modal content for submiting data to the database
    if modal.is_open():
        with modal.container():
            st.error("Are you sure you want to submit this data?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Yes'):
                    st.session_state.input_data['month'] = st.session_state.input_data['month'].map(month_mapping)                                       
                    st.session_state.input_data['province_id'] = st.session_state.input_data['province_id'].map(provinces_num)
                    st.session_state.input_data['corn_type'] = st.session_state.input_data['corn_type'].map(corn_type)

                    if selected_dataset2 == "Fertilizer Price":
                        submit_predictions_fertilizer(st.session_state.input_data, user_id)
                        st.session_state.input_data = fertilizer_database

                    elif selected_dataset2 == "Corn Price":
                        submit_predictions_price(st.session_state.input_data, user_id)
                        st.session_state.input_data = price_database

                    elif selected_dataset2 == "Corn Production":
                        submit_predictions_production(st.session_state.input_data, user_id)
                        st.session_state.input_data = production_database
                        
                    elif selected_dataset2 == "Weather Info":
                        st.session_state.input_data['conditions'] = st.session_state.input_data['conditions'].map(conditions_num)
                        submit_predictions_weather(st.session_state.input_data, user_id)
                        st.session_state.input_data = weather_database


                    st.session_state.form_key = 0
                    st.session_state.current_prov_index = 0
                    st.session_state.selected_dataset2_num += 1

                    # Clear text inputs
                    clear_text_input()

                    modal.close()  # Close modal
                    st.rerun() # Rerun to reflect changes

                with col2:
                    if st.button('No'):
                        st.session_state.form_key = 0
                        st.session_state.current_prov_index = 0

                        # Clear text inputs
                        clear_text_input()

                        modal.close()  # Close modal
                        st.rerun() # Rerun to reflect changes




    if selected_dataset2 != "Train Data":


        dataset = pd.DataFrame(response_1)

        # Drop id and province_id
        dataset = dataset.drop(columns=["id"], axis=1)

        # # Apply fetch_full_name to the 'user_id' column
        # dataset['user_id'] = dataset['user_id'].apply(fetch_full_name)

        # Get the current year and month
        last_year = dataset['year'].iloc[-1]

        # Get the last row of the 'month' column
        last_month = dataset['month'].iloc[-1]

        current_month = (last_month) % 12 + 1  # Wrap around using modulo
        current_year = last_year + (last_month) // 12  # Increment year if month exceeds December
    
        # Reverse the month mapping dictionary
        month_to_string = {v: k for k, v in month_mapping.items()}

        # Convert current month to string
        current_month = month_to_string[current_month]

        col1, col2 = st.columns((1.5, 1.5))

        with col1:
            st.header(f"{selected_dataset2}")
            if selected_dataset2 == "Corn Production" or selected_dataset2 == "Corn Price":
                dataset_1 = pd.DataFrame(response_1)
                dataset_2 = pd.DataFrame(response_2)

                select_database = st.selectbox("Choose an corn type:", ['White Corn', 'Yellow Corn'])
                if select_database == "White Corn":
                    st.dataframe(dataset_1)
                elif select_database == "Yellow Corn":  
                    st.dataframe(dataset_2)
            else:
                dataset_1 = pd.DataFrame(response_1)
                st.dataframe(dataset_1)
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


                elif selected_dataset2 == "Corn Price":
                    st.write("White Corn")
                    col_1, col_2, col_3 = st.columns(3)
                    with col_1:
                        W_Farmgate_Price = st.text_input(label="Farmgate Price", placeholder="Farmgate Price", key=f"f_price_input1")
                    with col_2:
                        W_Retail_Price = st.text_input(label="Retail Price", placeholder="Retail Price", key=f"r_price_input1")
                    with col_3:
                        W_Wholesale_Price = st.text_input(label="Wholesale Price", placeholder="Wholesale Price", key=f"w_price_input1")

                    st.write("Yellow Corn")
                    col_4, col_5, col_6 = st.columns(3)
                    with col_4:
                        Y_Farmgate_Price = st.text_input(label="Farmgate Price", placeholder="Farmgate Price", key=f"f_price_input2")
                    with col_5:
                        Y_Retail_Price = st.text_input(label="Retail Price", placeholder="Retail Price", key=f"r_price_input2")
                    with col_6:
                        Y_Wholesale_Price = st.text_input(label="Wholesale Price", placeholder="Wholesale Price", key=f"w_price_input2")


                elif selected_dataset2 == "Corn Production":
                    st.write("White Corn")
                    W_Production = st.text_input(label="Production", placeholder="Production", key=f"production_input1")

                    st.write("Yellow Corn")
                    Y_Production = st.text_input(label="Production", placeholder="Production", key=f"production_input2")



                elif selected_dataset2 == "Weather Info":

                    col_1, col_2, col_3 = st.columns(3)
                    
                    with col_1:
                        feelslike = st.text_input(label="Feels Like Temp.", placeholder="Feels Like Temp.", key=f"feelslike_input")
                        dew = st.text_input(label="Dew", placeholder="Dew", key=f"dew_input")
                        humidity = st.text_input(label="Humidity", placeholder="Humidity", key=f"humidity_input")
                        precip = st.text_input(label="Precipitation", placeholder="Precipitation", key=f"precip_input")
                        
                    with col_2:
                        precipcover = st.text_input(label="Precipitation Cover", placeholder="Precipitation Cover", key=f"precov_input")
                        windgust = st.text_input(label="Wind Gust", placeholder="Wind Gust", key=f"windgust_input")
                        windspeed = st.text_input(label="Wind Speed", placeholder="Wind Speed", key=f"windspeed_input")
                        winddir = st.text_input(label="Wind Direction", placeholder="Wind Direction", key=f"winddir_input")
                    
                    with col_3:
                        sealevelpressure = st.text_input(label="Sea Level Pressure", placeholder="Sea Level Pressure", key=f"sea_level_input")
                        visibility = st.text_input(label="Visibility", placeholder="Visibility", key=f"visibility_input")
                        severerisk = st.text_input(label="Severe Risk", placeholder="Severe Risk", key=f"severerisk_input")
                        conditions = st.selectbox("Condiions:", ['Partly Cloudy', 'Rain, Partially Cloudy', 'Rain, Overcast', 'Overcast'])

                


                col_1, col_2 = st.columns(2)

                with col_1:
                    if st.session_state.current_prov_index <= len(provinces) - 1:
                        # Submit button logic (into temprary dataset)
                        submit_data = st.form_submit_button(f'Submit for {current_prov}')
                    else:
                        # Submit button logic (into Database)
                        sent_data_to_database = st.form_submit_button('Submit to the database')
                with col_2:
                    if st.session_state.current_prov_index != 0:
                        # Get the current province based on the index
                        remove_current_prov = provinces[st.session_state.current_prov_index - 1]

                        # Remove button logic
                        remove_data = st.form_submit_button(f'Remove {remove_current_prov} data')




                if st.session_state.current_prov_index <= len(provinces) - 1:
                    if submit_data:

                        if selected_dataset2 == "Fertilizer Price":
                            fields = [Ammophos, Ammosul, Complete, Urea]
                            field_names = ["ammophos_price", "ammosul_price", "complete_price", "urea_price"]
                            
                            # Attempt to convert all fields to float
                            try:
                                fields = [float(field) for field in fields]
                                
                            except ValueError:
                                st.error("Please enter valid numeric values for all corn prices.")
                                return
                            
                            if not all(fields):
                                st.error("Please fill in all fields.")
                                return

                            new_data_white = {
                                "month": current_month,
                                "year": current_year,
                                "province_id": current_prov,
                                **dict(zip(field_names, fields))
                            }
                            new_data_yellow = {
                                "month": current_month,
                                "year": current_year,
                                "province_id": current_prov,
                                **dict(zip(field_names, fields))
                            }


                        elif selected_dataset2 == "Corn Price":
                            fields1 = [W_Farmgate_Price, W_Retail_Price, W_Wholesale_Price]
                            fields2 = [Y_Farmgate_Price, Y_Retail_Price, Y_Wholesale_Price]
                            field_names = ["farmgate_corngrains_price", "retail_corngrits_price", "wholesale_corngrits_price"]
                            
                            # Attempt to convert all fields to float
                            try:
                                fields1 = [float(field1) for field1 in fields1]
                                fields2 = [float(field2) for field2 in fields2]
                                
                            except ValueError:
                                st.error("Please enter valid numeric values for all corn prices.")
                                return
                            
                            if not all(fields1) or not all(fields2):
                                st.error("Please fill in all fields.")
                                return

                            new_data_white = {
                                "month": current_month,
                                "year": current_year,
                                "province_id": current_prov,
                                "corn_type": "White Corn",
                                **dict(zip(field_names, fields1))
                            }
                            new_data_yellow = {
                                "month": current_month,
                                "year": current_year,
                                "province_id": current_prov,
                                "corn_type": "Yellow Corn",
                                **dict(zip(field_names, fields2))
                            }
                            
                        elif selected_dataset2 == "Corn Production":

                            # Attempt to convert Production to a float
                            try:
                                W_Production = float(W_Production)
                                Y_Production = float(Y_Production)
                                
                            except ValueError:
                                st.error("Please enter a valid numeric value for corn production.")
                                return
                            
                            if not W_Production or not Y_Production:
                                st.error("Please fill in the production field.")
                                return
                            
                            new_data_white = {
                                "month": current_month,
                                "year": current_year,
                                "province_id": current_prov,
                                "corn_type": "White Corn",
                                "corn_production": W_Production
                            }
                            new_data_yellow = {
                                "month": current_month,
                                "year": current_year,
                                "province_id": current_prov,
                                "corn_type": "Yellow Corn",
                                "corn_production": Y_Production
                            }

                        elif selected_dataset2 == "Weather Info":
                            fields = [feelslike, dew, humidity, precip, precipcover, windgust, windspeed, winddir, sealevelpressure, visibility, severerisk]
                            field_names = ["feelslike", "dew", "humidity", "precip", "precipcover", "windgust", "windspeed", "winddir", "sealevelpressure", "visibility", "severerisk"]
                            
                            # Attempt to convert all fields to float
                            try:
                                fields = [float(field) for field in fields]
                                
                            except ValueError:
                                st.error("Please enter valid numeric values for all corn prices.")
                                return
                            
                            if not all(fields):
                                st.error("Please fill in all fields.")
                                return

                            new_data_white = {
                                "month": current_month,
                                "year": current_year,
                                "province_id": current_prov,
                                "corn_type": "White Corn",
                                **dict(zip(field_names, fields)),
                                "conditions": conditions
                            }
                            new_data_yellow = {
                                "month": current_month,
                                "year": current_year,
                                "province_id": current_prov,
                                "corn_type": "Yellow Corn",
                                **dict(zip(field_names, fields)),
                                "conditions": conditions
                            }


                        new_row_df = pd.DataFrame([new_data_white])
                        st.session_state.input_data = pd.concat([st.session_state.input_data, new_row_df], ignore_index=True)
                        
                        new_row_df = pd.DataFrame([new_data_yellow])
                        st.session_state.input_data = pd.concat([st.session_state.input_data, new_row_df], ignore_index=True)

                        # Clear text inputs
                        clear_text_input()

                        st.session_state.form_key += 1
                        st.session_state.current_prov_index += 1
                        st.success(f"Data for {current_prov} added successfully!")
                        st.rerun()  # Rerun to reflect changes

                else:
                    if sent_data_to_database:

                        # Opening modal abut choosing to countinue to submit data or cancel it out
                        modal.open()
 

                if st.session_state.current_prov_index != 0:
                    # Remove button logic
                    if remove_data:

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

            def predict_predictor(dataset, predictor_set, corn_type, folder_type, province_name):
                # Create datetime index from year and month
                new_dataset = dataset
                new_dataset['ds'] = pd.to_datetime(new_dataset['year'].astype(str) + '-' + new_dataset['month'].astype(str), format='%Y-%m')
                
                # Initialize dictionary to store models
                models = {}
                predictions_df = pd.DataFrame()
                
                # st.dataframe(dataset)

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
                predictions_df.to_csv(
                    f'Predictor_Models/{corn_type}/{province_name}/{folder_type}/predictor_dataset.csv', 
                    index=False
                )
                print('Cleaned dataset saved')
                
                return predictions_df



            # # ==============================================[RERF PREDICTS]=================================================================================   

            def extend_predictors(x_train, x_test):

                poly = PolynomialFeatures(degree=2, include_bias=True)
                x_train = poly.fit_transform(x_train)
                x_test = poly.transform(x_test)
                
                return x_train, x_test

            def RERF_Model(X, Y, corn_type, folder_type, province_name, target):

                X = X.drop('ds', axis=1)
                
                # Step 2: Perform k-fold cross-validation for Lasso to find optimal λ 
                lasso_cv = LassoCV(alphas=np.logspace(-6, 2, 100), cv=5, random_state=0)
                lasso_cv.fit(X, Y)

                # Get the best alpha (λ)
                lambda_star = lasso_cv.alpha_
                
                # Fit Lasso with optimal λ on training data
                lasso_optimal = Lasso(alpha=lambda_star)
                lasso_optimal.fit(X, Y)
                
                # Calculate residuals for training data
                residuals_train = Y - lasso_optimal.predict(X)
                
                # Step 3: Fit Random Forest on residuals from Lasso
                param_grid_rf = {
                    'max_features': ["sqrt", "log2", None],
                    'min_samples_leaf': [1, 3, 5]
                    }
                
                grid_search_rf = GridSearchCV(estimator=RandomForestRegressor(random_state=42), 
                                            param_grid=param_grid_rf,   
                                            cv=5, 
                                            scoring='r2', 
                                            verbose=2, 
                                            n_jobs=-1)
                
                grid_search_rf.fit(X, residuals_train)
                
                # Get best parameters for Random Forest
                best_params_rf = grid_search_rf.best_params_


                s_star = best_params_rf['min_samples_leaf']
                m_star = best_params_rf['max_features']
                
                # Fit Random Forest with optimal parameters on training data
                rf_optimal = RandomForestRegressor(min_samples_leaf=s_star, max_features=m_star, random_state=42)
                rf_optimal.fit(X, residuals_train)
                
                
                with open(f'Predictor_Models/{corn_type}/{province_name}/{folder_type}/RERF_Model/Lasso_models_for_{target}.joblib', 'wb') as f:
                    joblib.dump(lasso_optimal, f)
                    
                with open(f'Predictor_Models/{corn_type}/{province_name}/{folder_type}/RERF_Model/RF_models_for_{target}.joblib', 'wb') as f:
                    joblib.dump(rf_optimal, f)


            try:
                # White Corn Datasets
                white_corn_davao_region = get_white_davao_region_dataset()
                white_corn_davao_de_oro = get_white_davao_de_oro_dataset()
                white_corn_davao_del_norte = get_white_davao_del_norte_dataset()
                white_corn_davao_del_sur = get_white_davao_del_sur_dataset()
                white_corn_davao_oriental = get_white_davao_oriental_dataset()
                white_corn_davao_city = get_white_davao_city_dataset()

                # Yellow Corn Datasets
                yellow_corn_davao_region = get_yellow_davao_region_dataset()
                yellow_corn_davao_de_oro = get_yellow_davao_de_oro_dataset()
                yellow_corn_davao_del_norte = get_yellow_davao_del_norte_dataset()
                yellow_corn_davao_del_sur = get_yellow_davao_del_sur_dataset()
                yellow_corn_davao_oriental = get_yellow_davao_oriental_dataset()
                yellow_corn_davao_city = get_yellow_davao_city_dataset()

            except httpx.RequestError as e:  # Catch connection & request-related errors
                st.error("Connection error: Unable to connect to the server. Please try again later.")
                if st.button("Reload"):
                    st.rerun()
                st.stop()  # Prevents further execution

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                if st.button("Reload"):
                    st.rerun()
                st.stop()  # Prevents further execution

            # st.dataframe(white_corn_davao_region)
            # st.dataframe(white_corn_davao_region_dataset)

            w_f_predictor = ['corn_production', 'ammophos_price', 'ammosul_price', 'complete_price', 'urea_price', 'feelslike', 'dew', 
                        'humidity', 'precip', 'precipcover', 'windgust', 'windspeed', 'winddir','sealevelpressure', 'visibility', 
                        'severerisk', 'conditions', 'retail_corngrits_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price']

            w_r_predictor = ['corn_production', 'ammophos_price', 'ammosul_price', 'complete_price', 'urea_price', 'feelslike', 'dew', 
                        'humidity', 'precip', 'precipcover', 'windgust', 'windspeed', 'winddir','sealevelpressure', 'visibility', 
                        'severerisk', 'conditions', 'farmgate_corngrains_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price']

            w_w_predictor_1 = ['corn_production', 'ammophos_price', 'ammosul_price', 'complete_price', 'urea_price', 'feelslike', 'dew', 
                        'humidity', 'precip', 'precipcover', 'windgust', 'windspeed', 'winddir','sealevelpressure', 'visibility', 
                        'severerisk', 'conditions', 'farmgate_corngrains_price', 'retail_corngrits_price', 'wholesale_corngrains_price']

            w_w_predictor_2 = ['corn_production', 'ammophos_price', 'ammosul_price', 'complete_price', 'urea_price', 'feelslike', 'dew', 
                        'humidity', 'precip', 'precipcover', 'windgust', 'windspeed', 'winddir','sealevelpressure', 'visibility', 
                        'severerisk', 'conditions', 'farmgate_corngrains_price', 'retail_corngrits_price', 'wholesale_corngrits_price']




            y_f_predictor = ['corn_production', 'ammophos_price', 'ammosul_price', 'complete_price', 'urea_price', 'feelslike', 'dew', 
                        'humidity', 'precip', 'precipcover', 'windgust', 'windspeed', 'winddir','sealevelpressure', 'visibility', 
                        'severerisk', 'conditions', 'retail_corngrains_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price']

            y_r_predictor = ['corn_production', 'ammophos_price', 'ammosul_price', 'complete_price', 'urea_price', 'feelslike', 'dew', 
                        'humidity', 'precip', 'precipcover', 'windgust', 'windspeed', 'winddir','sealevelpressure', 'visibility', 
                        'severerisk', 'conditions', 'farmgate_corngrains_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price']

            y_w_predictor_1 = ['corn_production', 'ammophos_price', 'ammosul_price', 'complete_price', 'urea_price', 'feelslike', 'dew', 
                        'humidity', 'precip', 'precipcover', 'windgust', 'windspeed', 'winddir','sealevelpressure', 'visibility', 
                        'severerisk', 'conditions', 'farmgate_corngrains_price', 'retail_corngrains_price', 'wholesale_corngrains_price']

            y_w_predictor_2 = ['corn_production', 'ammophos_price', 'ammosul_price', 'complete_price', 'urea_price', 'feelslike', 'dew', 
                        'humidity', 'precip', 'precipcover', 'windgust', 'windspeed', 'winddir','sealevelpressure', 'visibility', 
                        'severerisk', 'conditions', 'farmgate_corngrains_price', 'retail_corngrains_price', 'wholesale_corngrits_price']




            # Load datasets
            white_province_mapping = {
                "davao_region": white_corn_davao_region,
                "davao_de_oro": white_corn_davao_de_oro,
                "davao_del_norte": white_corn_davao_del_norte,
                "davao_del_sur": white_corn_davao_del_sur,
                "davao_oriental": white_corn_davao_oriental,
                "davao_city": white_corn_davao_city,
            }

            # Load datasets
            yellow_province_mapping = {
                "davao_region": yellow_corn_davao_region,
                "davao_de_oro": yellow_corn_davao_de_oro,
                "davao_del_norte": yellow_corn_davao_del_norte,
                "davao_del_sur": yellow_corn_davao_del_sur,
                "davao_oriental": yellow_corn_davao_oriental,
                "davao_city": yellow_corn_davao_city,
            }

            # # ==============================================[WHITE CORN PRICE PREDICTS]=================================================================================   

            col_1, col_2 = st.columns(2)

            with col_1:
                st.write("White Corn Price Train")
                for dataset_name, dataset in white_province_mapping.items():

                    dataset = dataset.drop(["retail_corngrains_price"], axis=1)

                    # predict farmgate price for white_davao_region
                    f_future_pred = predict_predictor(dataset, w_f_predictor, "White Corn", "For Farmgate", f"{dataset_name}")

                
                    f_X = dataset.drop(['farmgate_corngrains_price'], axis=1)
                    f_Y = dataset['farmgate_corngrains_price']
                    RERF_Model(f_X, f_Y, "White Corn", "For Farmgate", f"{dataset_name}", "farmgate_corngrains_price") 



                    
                    # predict retail price for white_davao_region
                    r_future_pred = predict_predictor(dataset, w_r_predictor, "White Corn", "For Retail",  f"{dataset_name}")
                
                    r_X = dataset.drop(['retail_corngrits_price'], axis=1)
                    r_Y = dataset['retail_corngrits_price']
                    RERF_Model(r_X, r_Y, "White Corn", "For Retail",  f"{dataset_name}", "retail_corngrits_price") 




                    # predict wholesale corn grits price for white_davao_region
                    w_future_pred_1 = predict_predictor(dataset, w_w_predictor_1, "White Corn", "For Wholesale",  f"{dataset_name}")
                    print()
                
                    w_X_1 = dataset.drop(['wholesale_corngrits_price'], axis=1)
                    w_Y_1 = dataset['wholesale_corngrits_price']
                    RERF_Model(w_X_1, w_Y_1, "White Corn", "For Wholesale",  f"{dataset_name}", "wholesale_corngrits_price") 





                    # predict wholesale corn grains price for white_davao_region
                    w_future_pred_2 = predict_predictor(dataset, w_w_predictor_2, "White Corn", "For Wholesale",  f"{dataset_name}")
                    print()
                
                    w_X_2 = dataset.drop(['wholesale_corngrains_price'], axis=1)
                    w_Y_2 = dataset['wholesale_corngrains_price']
                    RERF_Model(w_X_2, w_Y_2, "White Corn", "For Wholesale",  f"{dataset_name}", "wholesale_corngrains_price") 



                    st.success(f'White Corn {dataset_name} trained successfully!')
                    # st.write(f'Farmgate: {f_r2} || Retail: {r_r2}')
                    # st.write(f'Wholesale Corngrits: {w_r2_1} || Wholesale Corngrains: {w_r2_2}')


            # # # ==============================================[YELLOW CORN PRICE PREDICTS]=================================================================================   
            with col_2:
                st.write("Yellow Corn Price Train")
                for dataset_name, dataset in yellow_province_mapping.items():

                    dataset = dataset.drop(["retail_corngrits_price"], axis=1)

                    # predict farmgate price for white_davao_region
                    f_future_pred = predict_predictor(dataset, y_f_predictor, "Yellow Corn", "For Farmgate", f"{dataset_name}")
                
                    f_X = dataset.drop(['farmgate_corngrains_price'], axis=1)
                    f_Y = dataset['farmgate_corngrains_price']
                    RERF_Model(f_X, f_Y, "Yellow Corn", "For Farmgate", f"{dataset_name}", "farmgate_corngrains_price") 



                    
                    # predict retail price for white_davao_region
                    r_future_pred = predict_predictor(dataset, y_r_predictor, "Yellow Corn", "For Retail",  f"{dataset_name}")

                    r_X = dataset.drop(['retail_corngrains_price'], axis=1)
                    r_Y = dataset['retail_corngrains_price']
                    RERF_Model(r_X, r_Y, "Yellow Corn", "For Retail",  f"{dataset_name}", "retail_corngrains_price") 



                    # predict wholesale corn grits price for white_davao_region
                    w_future_pred_1 = predict_predictor(dataset, y_w_predictor_1, "Yellow Corn", "For Wholesale",  f"{dataset_name}")
                    print()
                
                    w_X_1 = dataset.drop(['wholesale_corngrits_price'], axis=1)
                    w_Y_1 = dataset['wholesale_corngrits_price']
                    RERF_Model(w_X_1, w_Y_1, "Yellow Corn", "For Wholesale",  f"{dataset_name}", "wholesale_corngrits_price") 
                




                    # predict wholesale corn grains price for white_davao_region
                    w_future_pred_2 = predict_predictor(dataset, y_w_predictor_2, "Yellow Corn", "For Wholesale",  f"{dataset_name}")
                    print()
                
                    w_X_2 = dataset.drop(['wholesale_corngrains_price'], axis=1)
                    w_Y_2 = dataset['wholesale_corngrains_price']
                    RERF_Model(w_X_2, w_Y_2, "Yellow Corn", "For Wholesale",  f"{dataset_name}", "wholesale_corngrains_price") 



                    st.success(f'Yellow Corn {dataset_name} trained successfully!')
                    # st.write(f'Farmgate: {f_r2} || Retail: {r_r2}')
                    # st.write(f'Wholesale Corngrits: {w_r2_1} || Wholesale Corngrains: {w_r2_2}')


                    if dataset_name == "davao_city":
                        st.session_state["training"] = False  # Re-enable sidebar
                
                        st.session_state["refresh_control"] = True # Endable Add More Data Button  
                        st.rerun() 
                                
            
