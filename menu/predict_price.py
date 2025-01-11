import pandas as pd
import streamlit as st
import folium
import geopandas as gpd

from branca.colormap import linear
from sklearn.model_selection import train_test_split
from supabase_connect import get_white_davao_region_dataset, get_white_davao_de_oro_dataset, get_white_davao_del_norte_dataset, get_white_davao_del_sur_dataset, get_white_davao_oriental_dataset, get_white_davao_city_dataset
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LassoCV
from datetime import datetime

def app():

    # Load custom CSS
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Get the current year and month
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Generate a list of years from the current year to 5 years in the future
    year_options = [str(current_year + i) for i in range(6)]

    # Month mapping dictionary
    month_mapping = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }

    # def heatmap(dataset, title):
    #     # Load the GeoJSON file
    #     geo_data = gpd.read_file('ph.json')

    #     # Merge dataset with GeoJSON data
    #     geo_data = geo_data.merge(dataset, left_on='name', right_on='province', how='left')

    #     # Create the base map
    #     map = folium.Map(location=[6.8, 125.95], 
    #                     zoom_start=8, 
    #                     scrollWheelZoom=False,
    #                     doubleClickZoom=False,
    #                     dragging=False,
    #                     tiles="cartodbpositron")

    #     # Create a linear colormap
    #     colormap = linear.YlOrRd_09.scale(
    #         dataset['RERF'].min(), 
    #         dataset['RERF'].max()
    #     )

    #     colormap.caption = f'{title} in Davao Region'

    #     # Create the choropleth layer
    #     choropleth = folium.Choropleth(
    #         geo_data=geo_data,
    #         data=dataset,
    #         columns=['province', 'RERF'],
    #         key_on='feature.properties.name',
    #         fill_color='YlOrRd',  # Using the color scale for yellow to red
    #         fill_opacity=0.7,
    #         line_opacity=0.2,
    #         highlight=True,
    #         nan_fill_color='white',  # Color for missing values
    #         legend_name= f'{title} in Davao Region'
    #     ).add_to(map)

    #     # Add tooltips
    #     folium.GeoJson(
    #         geo_data,
    #         style_function=lambda feature: {
    #             'fillColor': colormap(feature['properties']['RERF'])
    #             if feature['properties']['RERF'] is not None
    #             else 'white',
    #             'color': 'black',
    #             'weight': 0.2,
    #             'fillOpacity': 0.7,
    #         },
    #         tooltip=folium.GeoJsonTooltip(
    #             fields=['name', 'RERF'],
    #             aliases=['Province: ', 'Predited Price: '],
    #             localize=True
    #         )
    #     ).add_to(map)

    #     # Save the map as an HTML file
    #     map.save('./map.html')

    #     # Display the map in Streamlit
    #     with open('./map.html', 'r', encoding='utf-8') as f:
    #         html_data = f.read()
    #         st.components.v1.html(html_data, width=500, height=650)

# ===================================================================================================

    # Fetch responses
    white_prod_dr, white_fertil_dr, white_weather_dr, white_price_dr = get_white_davao_region_dataset()

    def train_models(response):
        # Load the dataset
        dataset = pd.DataFrame(response)
        
        # Drop any non-numeric columns or convert them
        x = dataset.drop(['price', 'id', 'region_id', 'user_id'], axis=1)  # Features
        y = dataset['price']  # Target variable

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

        # Train a Random Forest Regressor model
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)

        # Generate predictions from the Random Forest model on the training set
        rf_train_pred = rf_model.predict(X_train)

        # Create a new DataFrame for training the Linear Regression model
        stacked_train_data = pd.DataFrame({
            'RF_Prediction': rf_train_pred,
            'Actual_Price': y_train
        })

        # Train the Linear Regression model using the Random Forest predictions
        lasso_model = LassoCV(cv=5, random_state=42)
        lasso_model.fit(stacked_train_data[['RF_Prediction']], stacked_train_data['Actual_Price'])
        
        return rf_model, lasso_model


    # Train the models with both datasets
    rf_model_1, lasso_model_1 = train_models(response_1)
    rf_model_2, lasso_model_2 = train_models(response_2)
    rf_model_3, lasso_model_3 = train_models(response_3)
    rf_model_4, lasso_model_4 = train_models(response_4)
    rf_model_5, lasso_model_5 = train_models(response_5)

    rf_model_6, lasso_model_6 = train_models(response_6)
    rf_model_7, lasso_model_7 = train_models(response_7)
    rf_model_8, lasso_model_8 = train_models(response_8)
    rf_model_9, lasso_model_9 = train_models(response_9)
    rf_model_10, lasso_model_10 = train_models(response_10)

    davao_regions = ['Davao Oriental', 'Davao City', 'Davao de Oro', 'Davao del Norte', 'Davao del Sur']

    # Streamlit title
    st.title("Predict Corn Price")

    # Collect user inputs
    Month = st.selectbox("Month", list(month_mapping.keys()))

    # Determine the default year based on the selected month
    selected_month_num = month_mapping[Month]

    if selected_month_num < current_month:
        Year = str(current_year + 1)
    else:
        Year = str(current_year)

    Year = st.selectbox("Year", year_options, index=year_options.index(Year))

    if st.button('Predict Corn Price'):
        if Month and Year:
            # Create the input_data DataFrame
            input_data = pd.DataFrame({
                'month': [int(month_mapping[Month])],  # Convert month name to numeric
                'week': [1],  # Assuming Week is always 1 for this example
                'year': [int(Year)]  # Convert year to integer
            })

            # Make predictions using the Random Forest model for both datasets
            rf_pred_1 = rf_model_1.predict(input_data)
            rf_pred_2 = rf_model_2.predict(input_data)
            rf_pred_3 = rf_model_3.predict(input_data)
            rf_pred_4 = rf_model_4.predict(input_data)
            rf_pred_5 = rf_model_5.predict(input_data)

            rf_pred_6 = rf_model_6.predict(input_data)
            rf_pred_7 = rf_model_7.predict(input_data)
            rf_pred_8 = rf_model_8.predict(input_data)
            rf_pred_9 = rf_model_9.predict(input_data)
            rf_pred_10 = rf_model_10.predict(input_data)

            # Use the Random Forest prediction as input to the Linear Regression model for both datasets
            final_prediction_1 = lasso_model_1.predict(rf_pred_1.reshape(-1, 1))
            final_prediction_2 = lasso_model_2.predict(rf_pred_2.reshape(-1, 1))
            final_prediction_3 = lasso_model_3.predict(rf_pred_3.reshape(-1, 1))
            final_prediction_4 = lasso_model_4.predict(rf_pred_4.reshape(-1, 1))
            final_prediction_5 = lasso_model_5.predict(rf_pred_5.reshape(-1, 1))

            final_prediction_6 = lasso_model_6.predict(rf_pred_6.reshape(-1, 1))
            final_prediction_7 = lasso_model_7.predict(rf_pred_7.reshape(-1, 1))
            final_prediction_8 = lasso_model_8.predict(rf_pred_8.reshape(-1, 1))
            final_prediction_9 = lasso_model_9.predict(rf_pred_9.reshape(-1, 1))
            final_prediction_10 = lasso_model_10.predict(rf_pred_10.reshape(-1, 1))

            predict_white_corn = [
                round(final_prediction_1[0], 2),
                round(final_prediction_2[0], 2),
                round(final_prediction_3[0], 2),
                round(final_prediction_4[0], 2),
                round(final_prediction_5[0], 2)
            ]
            predict_yellow_corn = [
                round(final_prediction_6[0], 2),
                round(final_prediction_7[0], 2),
                round(final_prediction_8[0], 2),
                round(final_prediction_9[0], 2),
                round(final_prediction_10[0], 2)
            ]

            title_1 = "White Corn Prices"
            title_2 = "Yellow Corn Prices"
            davao_region_pred_1 = pd.DataFrame({
                'province': davao_regions,
                'RERF': predict_white_corn
            })
            davao_region_pred_2 = pd.DataFrame({
                'province': davao_regions,
                'RERF': predict_yellow_corn
            })

            # Display the results using custom HTML and CSS
            st.markdown(f"""
                <div class="container">
                    <div class="container_1">
                        <h3 class="region_text">Davao City</h3>
                        <div class="message_price">
                            <div>
                                <p>White Corn Price</p>
                                <p>P {predict_white_corn[1]}</p>
                            </div>
                            <div>
                                <p>Yellow Corn Price</h3>
                                <p>P {predict_yellow_corn[1]}</p>
                            </div>
                        </div>
                    </div>
                    <div class="container_2">
                        <h3 class="region_text">Davao de Oro</h3>
                        <div class="message_price">
                            <div>
                                <p>White Corn Price</p>
                                <p>P {predict_white_corn[2]}</p>
                            </div>
                            <div>
                                <p>Yellow Corn Price</h3>
                                <p>P {predict_yellow_corn[2]}</p>
                            </div>
                        </div>
                    </div>
                    <div class="container_3">
                        <h3 class="region_text">Davao del Norte</h3>
                        <div class="message_price">
                            <div>
                                <p>White Corn Price</p>
                                <p>P {predict_white_corn[3]}</p>
                            </div>
                            <div>
                                <p>Yellow Corn Price</h3>
                                <p>P {predict_yellow_corn[3]}</p>
                            </div>
                        </div>
                    </div>
                    <div class="container_4">
                        <h3 class="region_text">Davao del Sur</h3>
                        <div class="message_price">
                            <div>
                                <p>White Corn Price</p>
                                <p>P {predict_white_corn[4]}</p>
                            </div>
                            <div>
                                <p>Yellow Corn Price</h3>
                                <p>P {predict_yellow_corn[4]}</p>
                            </div>
                        </div>
                    </div>
                    <div class="container_5">
                        <h3 class="region_text">Davao Oriental</h3>
                        <div class="message_price">
                            <div>
                                <p>White Corn Price</p>
                                <p>P {predict_white_corn[0]}</p>
                            </div>
                            <div>
                                <p>Yellow Corn Price</h3>
                                <p>P {predict_yellow_corn[0]}</p>
                            </div>
                        </div>
                    </div>
                </div>

            """, unsafe_allow_html=True)

            col_1, col_2 = st.columns(2)
            with col_1:
                heatmap(davao_region_pred_1,title_1)
            with col_2:
                heatmap(davao_region_pred_2,title_2)
                            
        else:
            st.warning("Please fill in all the fields.")



        # # Initialize an empty DataFrame to collect all predictions
        # davao_region = pd.DataFrame()
        # davao_de_oro = pd.DataFrame()
        # davao_del_norte = pd.DataFrame()
        # davao_del_sur = pd.DataFrame()
        # davao_oriental = pd.DataFrame()
        # davao_city = pd.DataFrame()

        # for province_name, config in province_configs.items():
        #     f_star = config['f_star']
        #     r_star = config['r_star']
        #     w_star = config['w_star']
        #     province_id = config['province_id'] # Get the province ID
            
        #     # Call the dataset function for the current province
        #     response_1, response_2, response_3, response_4 = config['get_dataset_func']()
            
        #     # Merge datasets
        #     dataset = merge_dataset(response_1, response_2, response_3, response_4)
            
        #     # Predict dataset using the parameters
        #     predict_df = predict_dataset(dataset,
        #                                 f_star[0], f_star[1], f_star[2], 
        #                                 r_star[0], r_star[1], r_star[2], 
        #                                 w_star[0], w_star[1], w_star[2])
            
        #     # Add province_id to predict_df
        #     predict_df['province_id'] = province_id
            
        #     # Manage plotting for the current province
        #     manage_plot(predict_df, province_name)

        #     if province_id == 1:
        #         davao_region = predict_df
        #     elif province_id == 2:
        #         davao_de_oro = predict_df
        #     elif province_id == 3:
        #         davao_del_norte = predict_df
        #     elif province_id == 4:
        #         davao_del_sur = predict_df
        #     elif province_id == 5:
        #         davao_oriental = predict_df
        #     elif province_id == 6:
        #         davao_city = predict_df

        #     # Append the current predict_df to predictions_df
        #     # predictions_df = pd.concat([predictions_df, predict_df], ignore_index=True)

        # # Mapping from month abbreviations to full month names
        # month_abbr = {'Jan': 'January','Feb': 'February','Mar': 'March','Apr': 'April','May': 'May','Jun': 'June',
        #             'Jul': 'July','Aug': 'August','Sep': 'September','Oct': 'October','Nov': 'November','Dec': 'December'}
        
        # # Month mapping dictionary
        # month_mapping = {
        #     'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 
        #     'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
        # }

        # # List of datasets for iteration
        # datasets = [davao_region, davao_de_oro, davao_del_norte, davao_del_sur, davao_oriental, davao_city]
        # # Mapping full month names to three-letter abbreviations

        # # Create an empty DataFrame for the combined data
        # combined_dataset = pd.DataFrame()

        # # Get the max number of rows from the datasets to iterate over
        # max_rows = max(len(dataset) for dataset in datasets)

        # #  Loop through each row index
        # for i in range(max_rows):
        #     # Loop through each dataset
        #     for dataset in datasets:
        #         if i < len(dataset):
        #             # Get the current row and assign the region
        #             row = dataset.iloc[i].copy()  # Copy the row to avoid SettingWithCopyWarning

        #             # Append the row to the combined dataset
        #             combined_dataset = pd.concat([combined_dataset, row.to_frame().T], ignore_index=True)

        # # Convert conditions column to integers using mapping
        # combined_dataset['month'] = combined_dataset['month'].map(month_abbr)

        # st.dataframe(combined_dataset)
        # last_month = dataset['month'].iloc[-1]
        # last_year = dataset['year'].iloc[-1]

        # # Collect user inputs
        # Month = st.selectbox("Month", list(month_mapping.keys()), index=last_month)

        # # Determine the default year based on the selected month
        # selected_month_num = month_mapping[Month]

        # # Get unique values from the 'year' column and convert to a list
        # year_option_list = predict_df['year'].unique().tolist()

        # # Check if Month input is valid and adjust Year accordingly
        # if int(selected_month_num) < int(last_month):
        #     Year = last_year + 1  # Increment year by 1 if selected month is less than last month
        # else:
        #     Year = last_year       # Default to the last year if not incrementing

        # # Ensure Year is in the list of options for the selectbox
        # if Year not in year_option_list:
        #     year_option_list.append(Year)  # Add Year to options if it's not already present

        # # Select Year with default index based on Year variable
        # Year = st.selectbox("Select Year", sorted(year_option_list), index=year_option_list.index(Year))

        # # Display selected values for debugging
        # st.write(f"Selected Month: {Month}")
        # st.write(f"Selected Year: {Year}")