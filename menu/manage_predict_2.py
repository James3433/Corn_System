import base64
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import folium
import geopandas as gpd


from branca.colormap import linear
from sklearn.model_selection import train_test_split
from supabase_connect import get_white_davao_region_dataset, get_white_davao_de_oro_dataset, get_white_davao_del_norte_dataset, get_white_davao_del_sur_dataset, get_white_davao_oriental_dataset, get_white_davao_city_dataset
from supabase_connect import get_yellow_davao_region_dataset, get_yellow_davao_de_oro_dataset, get_yellow_davao_del_norte_dataset, get_yellow_davao_del_sur_dataset, get_yellow_davao_oriental_dataset, get_yellow_davao_city_dataset
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso

def app():
    @st.cache_data
    def get_img_as_base64(file):
        with open (file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    # Load custom CSS
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown(f"""
            <style>
                [data-testid="stVerticalBlock"] {{
                    border-radius: 2em;
                    background-color: #8edd27;
                }}

                [data-testid="stHorizontalBlock"] {{
                    margin: 0em 2em;
                }}

                [data-testid="stMarkdown"] {{
                    margin-top: -35em;
                    margin-left: 20em;
                }}

                @media (max-width: 768px) {{
                    .section.main.st-emotion-cache-bm2z3a.ea3mdgi8 {{
                        padding: 0px;
                    }}

                    [data-testid="stHorizontalBlock"] {{
                        margin: 0em;
                    }}
            
                }}

            </style>
    """, unsafe_allow_html=True)

    def heatmap(dataset, title):
        # Rename columns that contain "_price" to "price"
        dataset.rename(columns=lambda x: 'price' if '_price' in x else x, inplace=True)

        # Load the GeoJSON file
        geo_data = gpd.read_file('ph.json')

        # Merge dataset with GeoJSON data
        geo_data = geo_data.merge(dataset, left_on='name', right_on='province', how='left')

        # Create the base map
        map = folium.Map(location=[6.8, 125.95], 
                        zoom_start=8, 
                        scrollWheelZoom=False,
                        doubleClickZoom=False,
                        dragging=False,
                        tiles="cartodbpositron")

        # Create a linear colormap
        cmap = plt.get_cmap('YlOrRd')

        # Normalize the price values
        norm = plt.Normalize(vmin=dataset['price'].min(), vmax=dataset['price'].max())

        # Create the choropleth layer without a built-in colorbar
        folium.GeoJson(
            geo_data,
            style_function=lambda feature: {
                'fillColor': '#{:02x}{:02x}{:02x}'.format(*[int(x * 255) for x in cmap(norm(feature['properties']['price']))])
                if feature['properties']['price'] is not None
                else 'white',
                'color': 'black',
                'weight': 0.2,
                'fillOpacity': 0.7,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['name', 'price'],
                aliases=['Province: ', 'Predicted Price: '],
                localize=True
            )
        ).add_to(map)

        # Save the map as an HTML file
        map.save('./map.html')

        # Create a vertical colormap image
        fig, ax = plt.subplots(figsize=(0.5, 8))
        fig.subplots_adjust(left=0.5)
        cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), 
                        cax=ax, orientation='vertical')
        cb.set_label(f'{title} in Davao Region')
        plt.savefig('colorbar.png', bbox_inches='tight', dpi=100)

        # Display the map and colorbar in Streamlit

        img_1 = get_img_as_base64("colorbar.png")

        with open('./map.html', 'r', encoding='utf-8') as f:
            html_data = f.read()
            st.components.v1.html(html_data, width=380, height=540)

        st.markdown(f"""
                    
            <img src="data:image/png;base64,{img_1}" alt="A beautiful landscape" width="70px" height="450px">
            
    """, unsafe_allow_html=True)



# ===================================================================================================


    def predict_predictor(dataset, predictor_set):
        # Initialize a dictionary to store models and predictions
        models = {}
        
        # Create an empty DataFrame to hold all predictions
        predictions_df = pd.DataFrame()
        
        # Define features (X) - all columns except those in f_predictor
        feature_columns = [col for col in dataset.columns if col not in predictor_set]
        
        for target in predictor_set:
            # Define features (X) and target (y)
            X = dataset[feature_columns]
            y = dataset[target]
        
            # Split the data into training and testing sets
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
            # Create a Linear Regression model
            model = LinearRegression()
            
            # Fit the model on the training data
            model.fit(X_train, y_train)
            
            # Make predictions on the test set
            y_pred = model.predict(X_test)
            
            # Store the model and predictions
            models[target] = model
            # Add predictions to the predictions_df DataFrame
            predictions_df[target] = pd.Series(y_pred, index=X_test.index)  # Aligning with the index of X_test
            
            predictions_df = predictions_df.iloc[:24]

        return predictions_df



    def RERF_Model(X, Y, predictor, lambda_star, m_star, s_star, name):
        
        RERF_pred = []
        
        # Define predictors and target variable
        
        # Step 2: Split the data into training and testing sets
        x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
        
        
        # Fit Lasso with optimal λ on training data
        lasso_optimal = Lasso(alpha=lambda_star)
        lasso_optimal.fit(x_train, y_train)
        
        # Calculate residuals for training data
        residuals_train = y_train - lasso_optimal.predict(x_train)
    
        # Fit Random Forest with optimal parameters on training data
        rf_optimal = RandomForestRegressor(n_estimators=m_star, max_depth=s_star, random_state=42)
        rf_optimal.fit(x_train, residuals_train)
        
        for index, row in predictor.iterrows():
            input_pred = row.values.reshape(1, -1)  # Reshape for single prediction
            
            # Predictions using Lasso
            y_pred_lasso_test = lasso_optimal.predict(input_pred)
            
            # Final predictions from Random Forest on test set residuals
            y_pred_rf_test = rf_optimal.predict(input_pred)
            
            # Combine predictions from Lasso and Random Forest for final prediction
            final_prediction = y_pred_lasso_test + y_pred_rf_test
            
            RERF_pred.append(final_prediction[0])  # Append the single prediction
        
        return pd.Series([round(pred, 2) for pred in RERF_pred])  # Return as a Series or DataFrame if needed



    def add_month_and_year(dataset, dataset_1):
        # Set the index to start from 1
        dataset.index = range(0, len(dataset))
        
        # Assuming white_davao_region is your existing DataFrame
        # Initialize last_year and last_month
        last_year = dataset_1['year'].iloc[-1]
        last_month = dataset_1['month'].iloc[-1]
        last_month = last_month + 1

        # Create an empty list to hold new year and month pairs
        year_month_pairs = []
        
        num_rows = len(dataset)
        
        # Generate year and month pairs starting from last_year and last_month
        for i in range(num_rows):  # Generate 12 months
            # Calculate the month
            current_month = (last_month + i - 1) % 12 + 1  # Wrap around using modulo
            current_year = last_year + (last_month + i - 1) // 12  # Increment year if month exceeds December
            
            year_month_pairs.append((current_year, current_month))
        
        # Create a DataFrame from the year-month pairs
        year_month_df = pd.DataFrame(year_month_pairs, columns=['year', 'month'])
        
        final_dataset = pd.concat([year_month_df, dataset], axis=1)

        return final_dataset




    def predict_dataset(dataset, f_star_1, f_star_2, f_star_3, r_star_1, r_star_2, r_star_3, w_star_1, w_star_2, w_star_3):
        f_predictor = ['corn_production', 'ammophos_price', 'ammosul_price', 'complete_price', 'urea_price', 
                    'tempmax', 'tempmin', 'temp', 'dew', 'humidity', 'precip', 'precipprob', 'precipcover',	
                    'windspeed', 'sealevelpressure', 'visibility', 'solarradiation', 'uvindex', 'severerisk',	
                    'cloudcover', 'conditions', 'retail_corngrits_price', 'wholesale_corngrits_price']

        r_predictor = ['corn_production', 'ammophos_price', 'ammosul_price', 'complete_price', 'urea_price', 
                    'tempmax', 'tempmin', 'temp', 'dew', 'humidity', 'precip', 'precipprob', 'precipcover',	
                    'windspeed', 'sealevelpressure', 'visibility', 'solarradiation', 'uvindex', 'severerisk',	
                    'cloudcover', 'conditions', 'farmgate_corngrains_price', 'wholesale_corngrits_price']

        w_predictor = ['corn_production', 'ammophos_price', 'ammosul_price', 'complete_price', 'urea_price', 
                    'tempmax', 'tempmin', 'temp', 'dew', 'humidity', 'precip', 'precipprob', 'precipcover',	
                    'windspeed', 'sealevelpressure', 'visibility', 'solarradiation', 'uvindex', 'severerisk',	
                    'cloudcover', 'conditions', 'farmgate_corngrains_price', 'retail_corngrits_price']


        # predict farmgate price for white_davao_region
        f_predictors_df = predict_predictor(dataset, f_predictor)
        f_predictors_df = add_month_and_year(f_predictors_df, dataset)
        f_X = dataset.drop(['farmgate_corngrains_price'], axis=1)
        f_Y = dataset['farmgate_corngrains_price']
        f_prediction = RERF_Model(f_X, f_Y, f_predictors_df, f_star_1, f_star_2, f_star_3, 'white_davao_region') 


        # predict retail price for white_davao_region
        r_predictors_df = predict_predictor(dataset, r_predictor)
        r_predictors_df = add_month_and_year(r_predictors_df, dataset)
        r_X = dataset.drop(['retail_corngrits_price'], axis=1)
        r_Y = dataset['retail_corngrits_price']
        r_prediction = RERF_Model(r_X, r_Y, r_predictors_df, r_star_1, r_star_2, r_star_3, 'white_davao_region') 


        # predict wholesale price for white_davao_region
        w_predictors_df = predict_predictor(dataset, w_predictor)
        w_predictors_df = add_month_and_year(w_predictors_df, dataset)
        w_X = dataset.drop(['wholesale_corngrits_price'], axis=1)
        w_Y = dataset['wholesale_corngrits_price']
        w_prediction = RERF_Model(w_X, w_Y, w_predictors_df, w_star_1, w_star_2, w_star_3, 'white_davao_region') 


        predict_dataset = pd.DataFrame()
        predict_dataset['year'] = f_predictors_df['year']
        predict_dataset['month'] = f_predictors_df['month']
        predict_dataset['farmgate_price'] = f_prediction
        predict_dataset['retail_price'] = r_prediction
        predict_dataset['wholesale_price'] = w_prediction

        return predict_dataset


    def merge_dataset(dataset1, dataset2, dataset3, dataset4):
        # Merge datasets on 'user_id' (or another common key)
        merged_dataset = pd.merge(dataset1, dataset2)
        merged_dataset = pd.merge(merged_dataset, dataset3)
        merged_dataset = pd.merge(merged_dataset, dataset4)
        merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id'], axis=1)

        return merged_dataset
    
    def manage_plot(dataset, selected_dataset):
        # Mapping full month names to three-letter abbreviations
        month_abbr = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

        # Map the full month names to their abbreviations
        dataset['month'] = dataset['month'].map(month_abbr).astype(str)
        dataset['Month Year'] = dataset['month'] + ' - ' + dataset['year'].astype(str)

        num_rows = len(dataset)

        # Rename columns that contain "_price" to "price"
        # Assuming the dataset has specific columns for each price type
        price_columns = ['farmgate_price', 'retail_price', 'wholesale_price']
        
        # Create a figure and axis for the plot
        fig, ax = plt.subplots(figsize=(14, 6), facecolor='#B7E505')
        ax.set_facecolor('#B7E505') 

        # Plot each price type with different styles
        for price_type in price_columns:
            if price_type in dataset.columns:
                ax.plot(dataset['Month Year'], dataset[price_type], marker='o', markersize=4, label=price_type.replace('_', ' ').title())

        ax.set_xlabel('Month', color='black')
        ax.set_ylabel('Price', color='black')
        ax.set_title(f'{selected_dataset} Price Data in {num_rows} Months', color='black')

        # Set x-tick labels with rotation for better readability
        ax.set_xticklabels(dataset['Month Year'], rotation=45, ha='right')  # Rotate labels 45 degrees

        # Adjust the font size
        for tick in ax.get_xticklabels():
            tick.set_fontsize(6)
            tick.set_color('black')  
        for tick in ax.get_yticklabels():
            tick.set_fontsize(8)
            tick.set_color('black')  

        # Add a legend to identify each line
        ax.legend(title='Price Type')

        st.pyplot(fig)


    def prediction_dataset(province_configs, selected_dataset):

        # Initialize an empty DataFrame to collect all predictions
        predictions_df = pd.DataFrame()

        # Loop through each province in the dictionary
        for province_name, config in province_configs.items():
            f_star = config['f_star']
            r_star = config['r_star']
            w_star = config['w_star']
            province_id = config['province_id'] # Get the province ID
            
            # Call the dataset function for the current province
            response_1, response_2, response_3, response_4 = config['get_dataset_func']()
            
            # Merge datasets
            dataset = merge_dataset(response_1, response_2, response_3, response_4)
            
            # Predict dataset using the parameters
            predict_df = predict_dataset(dataset,
                                        f_star[0], f_star[1], f_star[2], 
                                        r_star[0], r_star[1], r_star[2], 
                                        w_star[0], w_star[1], w_star[2])
            
            # Add province_id to predict_df
            predict_df['province_id'] = province_id

            # Append the current predict_df to predictions_df
            predictions_df = pd.concat([predictions_df, predict_df], ignore_index=True)

            if selected_dataset == 'Graph Plots':
                # Manage plotting for the current province
                manage_plot(predict_df, province_name)

        if selected_dataset == 'Heatmap':

            return predictions_df



    province = ""
    f_star = [0] * 3  # Initialize with zeros or appropriate values
    r_star = [0] * 3
    w_star = [0] * 3 

    # white corn province configurations
    province_configs_1 = {
        'Davao Region': {
            'f_star': [0.01, 100, 20],
            'r_star': [0.1, 200, 25],
            'w_star': [0.1, 150, 15],
            'get_dataset_func': get_white_davao_region_dataset,
            'province_id': 1
        },
        'Davao de Oro': {
            'f_star': [0.01, 150, 15],
            'r_star': [0.1, 200, 30],
            'w_star': [0.1, 200, 20],
            'get_dataset_func': get_white_davao_de_oro_dataset,
            'province_id': 2
        },
        'Davao del Norte': {
            'f_star': [0.01, 250, 15],
            'r_star': [0.1, 250, 15],
            'w_star': [0.1, 50, 5],
            'get_dataset_func': get_white_davao_del_norte_dataset,
            'province_id': 3
        },
        'Davao del Sur': {
            'f_star': [0.01, 50, 5],
            'r_star': [1.0, 100, 10],
            'w_star': [0.1, 100, 15],
            'get_dataset_func': get_white_davao_del_sur_dataset,
            'province_id': 4
        },
        'Davao Oriental': {
            'f_star': [0.1, 250, 20],
            'r_star': [0.1, 50, None],
            'w_star': [0.1, 150, 10],
            'get_dataset_func': get_white_davao_oriental_dataset,
            'province_id': 5
        },
        'Davao City': {
            'f_star': [0.01, 50, 20],
            'r_star': [0.01, 100, 10],
            'w_star': [0.1, 250, 15],
            'get_dataset_func': get_white_davao_city_dataset,
            'province_id': 6
        }
    }

    # yellow corn province configurations
    province_configs_2 = {
        'Davao Region': {
            'f_star': [0.1, 250, 15],
            'r_star': [0.1, 250, 15],
            'w_star': [0.1, 300, 20],
            'get_dataset_func': get_yellow_davao_region_dataset,
            'province_id': 1
        },
        'Davao de Oro': {
            'f_star': [0.1, 150, 20],
            'r_star': [0.01, 200, 20],
            'w_star': [0.01, 50, 20],
            'get_dataset_func': get_yellow_davao_de_oro_dataset,
            'province_id': 2
        },
        'Davao del Norte': {
            'f_star': [1.0, 300, 15],
            'r_star': [0.1, 300, 10],
            'w_star': [0.1, 250, 15],
            'get_dataset_func': get_yellow_davao_del_norte_dataset,
            'province_id': 3
        },
        'Davao del Sur': {
            'f_star': [0.01, 300, 15],
            'r_star': [0.01, 150, 25],
            'w_star': [1.0, 300, 20],
            'get_dataset_func': get_yellow_davao_del_sur_dataset,
            'province_id': 4
        },
        'Davao Oriental': {
            'f_star': [0.01, 250, 25],
            'r_star': [0.01, 250, 10],
            'w_star': [0.01, 300, 20],
            'get_dataset_func': get_yellow_davao_oriental_dataset,
            'province_id': 5
        },
        'Davao City': {
            'f_star': [0.1, 250, 30],
            'r_star': [0.01, 150, None],
            'w_star': [0.01, 300, 20],
            'get_dataset_func': get_yellow_davao_city_dataset,
            'province_id': 6
        }
    }


    selected_dataset = st.sidebar.selectbox("Choose an option:", ['Graph Plots', 'Heatmap'])


    if selected_dataset == 'Graph Plots':

        with st.expander("White Predictions Plots"):
            prediction_dataset(province_configs_1, selected_dataset)
        
        with st.expander("Yellow Predictions Plots"):
            prediction_dataset(province_configs_2, selected_dataset)



    if selected_dataset == 'Heatmap':

        # Month mapping dictionary
        month_mapping_1 = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 
            'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        # Mapping from month abbreviations to full month names
        province_list = ['Davao Region', 'Davao de Oro', 'Davao del Norte', 'Davao del Sur', 'Davao Oriental', 'Davao City']


        white_prediction_df = prediction_dataset(province_configs_1, selected_dataset)
        yellow_prediction_df = prediction_dataset(province_configs_2, selected_dataset)
        

        # Reverse the dictionary
        month_mapping_2 = {v: k for k, v in month_mapping_1.items()}

        last_month = white_prediction_df['month'].iloc[1]
        last_year = white_prediction_df['year'].iloc[1]

        # Collect user inputs for Month selection
        month_names = list(month_mapping_1.keys())

        # Ensure last_month is converted correctly for indexing
        if last_month in month_mapping_2:
            default_index = month_names.index(month_mapping_2[last_month])
        else:
            default_index = 0  # Fallback to first month if last_month is invalid

        # Collect user inputs
        Month = st.selectbox("Month", month_names, index=default_index)

        # Determine the default year based on the selected month
        selected_month_num = month_mapping_1[Month]


        # Get unique values from the 'year' column and convert to a list
        year_option_list = white_prediction_df['year'].unique().tolist()


        # Check if Month input is valid and adjust Year accordingly
        if int(selected_month_num) < int(last_month):
            Year = last_year + 1  # Increment year by 1 if selected month is less than last month
        else:
            Year = last_year       # Default to the last year if not incrementing

        # Ensure Year is in the list of options for the selectbox
        if Year not in year_option_list:
            year_option_list.append(Year)  # Add Year to options if it's not already present

        # Select Year with default index based on Year variable
        Year = st.selectbox("Select Year", sorted(year_option_list), index=year_option_list.index(Year))

        # Filter predictions_df based on user inputs
        white_filtered_data = white_prediction_df[(white_prediction_df['month'] == selected_month_num) & (white_prediction_df['year'] == Year)]
        yellow_filtered_data = yellow_prediction_df[(yellow_prediction_df['month'] == selected_month_num) & (yellow_prediction_df['year'] == Year)]

        # Map province IDs to province names
        white_filtered_data['province'] = white_filtered_data['province_id'].map(lambda x: province_list[x - 1] if x - 1 < len(province_list) else None)        
        yellow_filtered_data['province'] = yellow_filtered_data['province_id'].map(lambda x: province_list[x - 1] if x - 1 < len(province_list) else None) 

        w_farmgate_df = white_filtered_data[['province', 'farmgate_price']]
        w_retail_df = white_filtered_data[['province', 'retail_price']]
        w_wholesale_df = white_filtered_data[['province', 'wholesale_price']]

        y_farmgate_df = yellow_filtered_data[['province', 'farmgate_price']]
        y_retail_df = yellow_filtered_data[['province', 'retail_price']]
        y_wholesale_df = yellow_filtered_data[['province', 'wholesale_price']]


        title_1 = "White Corn Price"
        title_2 = "Yellow Corn Price"


        col1, col2 = st.columns((2))
        with col1:
            st.header("White Corn")
            st.header("Farmgate Price")
            heatmap(w_farmgate_df,title_1)
            st.header("Retail Price")
            heatmap(w_retail_df,title_1)
            st.header("Wholesale Price")
            heatmap(w_wholesale_df,title_1)

        with col2:
            st.header("Yellow Corn")
            st.header("Farmgate Price")
            heatmap(y_farmgate_df,title_2)
            st.header("Retail Price")
            heatmap(y_retail_df,title_2)
            st.header("Wholesale Price")
            heatmap(y_wholesale_df,title_2)


        





    # # Streamlit UI for submission
    # if st.button("Submit Predicted Prices"):
    #     user_id = st.session_state.get('user_id')  # Get user ID from session state or define it as needed
    #     submit_predictions(combined_dataset, user_id)

    # # Fetch responses
    # white_prod_dr, white_fertil_dr, white_weather_dr, white_price_dr = get_white_davao_region_dataset()
    # white_prod_ddo, white_fertil_ddo, white_weather_ddo, white_price_ddo = get_white_davao_de_oro_dataset()
    # white_prod_ddn, white_fertil_ddn, white_weather_ddn, white_price_ddn = get_white_davao_del_norte_dataset()
    # white_prod_dds, white_fertil_dds, white_weather_dds, white_price_dds = get_white_davao_del_sur_dataset()
    # white_prod_do, white_fertil_do, white_weather_do, white_price_do = get_white_davao_oriental_dataset()
    # white_prod_dc, white_fertil_dc, white_weather_dc, white_price_dc = get_white_davao_city_dataset()


    # f_predict_df = predict_df.drop(['retail_price', 'wholesale_price'], axis=1)
    # r_predict_df = predict_df.drop(['farmgate_price', 'wholesale_price'], axis=1)
    # w_predict_df = predict_df.drop(['farmgate_price', 'retail_price' ], axis=1)
    
    # f_predict_df["price"] = predict_df['farmgate_price']
    # r_predict_df["price"] = predict_df['retail_price']
    # w_predict_df["price"] = predict_df['wholesale_price']

    # manage_plot(f_predict_df, province, "Farmgate Price")
    # manage_plot(r_predict_df, province, "Retail Price")
    # manage_plot(w_predict_df, province, "Wholesale Price")

