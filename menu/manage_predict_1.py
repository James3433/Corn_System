import os
import base64
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import folium
import geopandas as gpd
import joblib

from branca.colormap import linear
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from plotly.subplots import make_subplots

def app():

    @st.cache_data
    def get_img_as_base64(file):
        with open (file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    

    user_type = st.session_state.get('user_type', '0')

    # Load custom CSS
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown(f"""
            <style>
                .st-emotion-cache-bm2z3a {{
                    padding-top: 10%;
                }}

                .st-emotion-cache-vdokb0.e1nzilvr4 img{{
                    margin-left: 20em;
                    margin-top: -43em;
                }}

                [data-testid="stAppViewBlockContainer"] {{    
                    border-radius: 10px;
                    background-color: #8edd27;
                    border: 2px solid green;
                    width: 90%;
                    padding: 1% 5% 5%;
                }}

                @media (max-width: 768px) {{
                    [data-testid="stAppViewBlockContainer"] {{    
                        padding: 1em;
                    }}
                }}
            </style>
    """, unsafe_allow_html=True)

    def heatmap(dataset, price_type, title):
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


        # Define the colorbar image filename
        colorbar_filename = f'{title} {price_type} Colorbar.png'

        # Check if the colorbar image exists and delete it
        if os.path.exists(colorbar_filename):
            os.remove(colorbar_filename)


        # Create a vertical colormap image
        fig, ax = plt.subplots(figsize=(0.5, 8))
        fig.subplots_adjust(left=0.5)
        cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), 
                        cax=ax, orientation='vertical')
        cb.set_label(f'{title} in Davao Region')
        plt.savefig(colorbar_filename, bbox_inches='tight', dpi=100)


        # Display the map and colorbar in Streamlit
        img_1 = get_img_as_base64(colorbar_filename)

        with open('./map.html', 'r', encoding='utf-8') as f:
            html_data = f.read()
            st.components.v1.html(html_data, width=380, height=540)

        st.markdown(f"""
                    
            <img src="data:image/png;base64,{img_1}" alt="A beautiful landscape" width="70px" height="450px">
            
    """, unsafe_allow_html=True)


# ===================================================================================================

    def RERF_Model(corn_type, folder_type, province_name, target):
        RERF_pred = []

        try:
            predictor = pd.read_csv(f'Predictor_Models/{corn_type}/{province_name}/{folder_type}/predictor_dataset.csv')

            # Load the models
            try:
                lasso_optimal = joblib.load(f'Predictor_Models/{corn_type}/{province_name}/{folder_type}/RERF_Model/Lasso_models_for_{target}.joblib')
                rf_optimal = joblib.load(f'Predictor_Models/{corn_type}/{province_name}/{folder_type}/RERF_Model/RF_models_for_{target}.joblib')
            except FileNotFoundError as e:
                print(f"Error loading models: {e}")
                return pd.DataFrame()  # Return an empty DataFrame

            for index, row in predictor.iterrows():
                input_pred = row.values.reshape(1, -1)  # Reshape for single prediction

                # Predictions using Lasso
                y_pred_lasso_test = lasso_optimal.predict(input_pred)

                # Final predictions from Random Forest on test set residuals
                y_pred_rf_test = rf_optimal.predict(input_pred)

                # Combine predictions from Lasso and Random Forest for final prediction
                final_prediction = y_pred_lasso_test + y_pred_rf_test

                RERF_pred.append(final_prediction[0])  # Append the single prediction

            final_predict = pd.Series([round(pred, 2) for pred in RERF_pred])
            RERF_pred_df = predictor[['year','month']].copy() # Prevent SettingWithCopyWarning
            RERF_pred_df['price'] = final_predict

            return RERF_pred_df  # Return the DataFrame

        except FileNotFoundError as e:
            print(f"Error loading predictor data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return pd.DataFrame()





    def predict_dataset(corn_type, province_name):

        if user_type == 1: 
            # predict farmgate price for white_davao_region
            price_type = "Farmgate Price"
            folder_type = "For Farmgate"
            target = "farmgate_corngrains_price"
            prediction = RERF_Model(corn_type, folder_type, province_name, target) 

        elif user_type == 3:
            # predict retail price for white_davao_region
            price_type = "Retail Price"
            if corn_type == "White Corn":
                # Target 1: Corn Grits
                folder_type = "For Retail"
                target = "retail_corngrits_price"
                prediction = RERF_Model(corn_type, folder_type, province_name, target)

            if corn_type == "Yellow Corn":
                # Target 2: Corn Grains
                folder_type = "For Retail"
                target = "retail_corngrains_price"
                prediction = RERF_Model(corn_type, folder_type, province_name, target) 

        elif user_type == 2:
            # predict wholesale price for white_davao_region
            # Target 1: Corn Grits
            price_type = "Wholesale Price"
            folder_type = "For Wholesale"
            target_1 = "wholesale_corngrits_price"
            prediction_1 = RERF_Model(corn_type, folder_type, province_name, target_1)
            prediction_1 = prediction_1.rename(columns={'price': 'wholesale_corngrits_price'}) #Fix naming

            # Target 2: Corn Grains
            target_2 = "wholesale_corngrains_price"
            prediction_2 = RERF_Model(corn_type, folder_type, province_name, target_2)
            prediction_2 = prediction_2.rename(columns={'price': 'wholesale_corngrains_price'}) #Fix naming

            #Concatenate the 2 dataframes
            prediction = pd.merge(prediction_1, prediction_2)

            target = target_1



        return prediction, price_type, target

    
    def manage_plot(dataset, selected_dataset, price_type):
        # Mapping full month names to three-letter abbreviations
        month_abbr = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

        # Map the full month names to their abbreviations
        dataset['month'] = dataset['month'].map(month_abbr).astype(str)
        dataset['Month Year'] = dataset['month'] + ' - ' + dataset['year'].astype(str)

        num_rows = len(dataset)

        # Create Plotly figure
        fig = go.Figure()

        # Add trace
        if user_type == 1:  
            price_columns = {
                'white_farmgate_corngrains_price': 'White Corn', 
                'yellow_farmgate_corngrains_price': 'Yellow Corn'
                }

        elif user_type == 3:
            price_columns = {
                'white_retail_corngrits_price': 'White Corn', 
                'yellow_retail_corngrains_price': 'Yellow Corn'
                }
        
        elif user_type == 2:  
            if 'white_wholesale_corngrits_price' in dataset.columns:
                price_columns = {
                    'white_wholesale_corngrits_price': 'White Corn', 
                    'yellow_wholesale_corngrits_price': 'Yellow Corn'
                    }

            elif 'white_wholesale_corngrains_price' in dataset.columns:  
                price_columns = {
                    'white_wholesale_corngrains_price': 'White Corn', 
                    'yellow_wholesale_corngrains_price': 'Yellow Corn'
                    }


        # Plot each price type
        for price_types, price_id in price_columns.items():
            if price_types in dataset.columns:
                # Replace underscores with spaces and remove '_price'
                formatted_name = price_types.replace('_price', ' ').title()
                formatted_name = formatted_name.replace('_', ' ').title()

                fig.add_trace(go.Scatter(
                    x=dataset['Month Year'],
                    y=dataset[price_types],
                    mode='markers+lines',
                    name=price_id,
                    hovertemplate=f"Type: {formatted_name}<br>Price: %{{y}}<extra></extra>",

                    )
                )

        # Update layout
        fig.update_layout(
            title=f'{selected_dataset} {price_type} Data in {num_rows} Months',
            title_x=0.05,  # Position title at the far left
            title_xanchor='left',  # Anchor title to the left
            template="plotly_dark",  # Or other base template if you prefer
            hovermode="x unified",
            plot_bgcolor='#B7E505',  # Yellow-Green for plot area
            paper_bgcolor='#B7E505',  # Yellow-Green for surrounding paper

            legend=dict(
                font=dict(
                    family="Arial",  # Specify font family
                    color="black"    # Overall font color
                )
            ),

            xaxis=dict(
                tickangle=-45,
                title_font=dict(size=15, color="black"),  # Correct property
                tickfont=dict(size=12, color="black"), # X-axis tick labels font
                fixedrange=True # Disable zooming
            ),

            yaxis=dict(
                title_font=dict(size=15, color="black"),  # Correct property
                tickfont=dict(size=12, color="black"), # Y-axis tick labels font
                fixedrange=True # Disable zooming
            ),

            title_font=dict(color="black"), # Title font (overrides general font)

            # Customize hover label appearance
                hoverlabel=dict(
                    bgcolor="rgba(0, 0, 0, 0.8)", # Background color (semi-transparent black)
                    font=dict(
                    size=14, # Font size
                    family="Arial", # Font family
                    color="white" # Font color
                ),
                bordercolor="yellow" # Border color of the tooltip
            )
        )

        st.plotly_chart(fig, use_container_width=True)





    def prediction_dataset(province_configs, selected_dataset, corn_type):

        # Initialize an empty DataFrame to collect all predictions
        predictions_df = pd.DataFrame()

        # Loop through each province in the dictionary
        for province_name, config in province_configs.items():
            dataset_name = config['get_dataset_func']
            province_id = config['province_id'] # Get the province ID

            # Predict dataset using the parameters
            predict_df, price_type, target = predict_dataset(corn_type, dataset_name)

            # Add province_id to predict_df
            predict_df['province_id'] = province_id

            # Append the current predict_df to predictions_df
            predictions_df = pd.concat([predictions_df, predict_df], ignore_index=True)
        
        return predictions_df, price_type, target




    # white corn province configurations
    province_configs = {
        'Davao Region': {
            'get_dataset_func': 'davao_region',
            'province_id': 1
        },
        'Davao de Oro': {
            'get_dataset_func': 'davao_de_oro',
            'province_id': 2
        },
        'Davao del Norte': {
            'get_dataset_func': 'davao_del_norte',
            'province_id': 3
        },
        'Davao del Sur': {
            'get_dataset_func': 'davao_del_sur',
            'province_id': 4
        },
        'Davao Oriental': {
            'get_dataset_func': 'davao_oriental',
            'province_id': 5
        },
        'Davao City': {
            'get_dataset_func': 'davao_city',
            'province_id': 6
        }
    }



    selected_dataset = st.sidebar.selectbox("Choose an option:", ['Graph Plots', 'Heatmap'])


    if selected_dataset == 'Graph Plots':
        year = 12  # Default value is 11

        selected_year = st.selectbox("Choose an year:", ['1 Year', '2 Year'])

        if selected_year == "1 Year":
            year = 12 # Overwrite default only if button is pressed

        if selected_year == "2 Year":
            year = 24  # Overwrite default only if button is pressed

        w_predictions_df, price_type, target_1 = prediction_dataset(province_configs, selected_dataset, "White Corn")
        y_predictions_df, price_type, target_2 = prediction_dataset(province_configs, selected_dataset, "Yellow Corn")


        # st.dataframe(w_predictions_df)
        # st.dataframe(y_predictions_df)

        if user_type == 2:
            w_predictions_df_1 = w_predictions_df.drop(["wholesale_corngrains_price"], axis=1)
            y_predictions_df_1 = y_predictions_df.drop(["wholesale_corngrains_price"], axis=1)

            w_predictions_df_2 = w_predictions_df.drop(["wholesale_corngrits_price"], axis=1)
            y_predictions_df_2 = y_predictions_df.drop(["wholesale_corngrits_price"], axis=1)

            with st.expander("Corn Grits Predictions Plots"):
                for province_name, config in province_configs.items():
                    province_id = config['province_id']

                    predictions_df_1 = w_predictions_df_1[w_predictions_df_1['province_id'] == province_id]
                    predictions_df_1 = predictions_df_1.rename(columns={"wholesale_corngrits_price": 'white_wholesale_corngrits_price'})
                    predictions_df_1 = predictions_df_1.iloc[:year] # Always slice the df, default or button press

                    predictions_df_2 = y_predictions_df_1[y_predictions_df_1['province_id'] == province_id]
                    predictions_df_2 = predictions_df_2.rename(columns={"wholesale_corngrits_price": 'yellow_wholesale_corngrits_price'})
                    predictions_df_2 = predictions_df_2.iloc[:year] # Always slice the df, default or button press
         
                    merged_predictions_df = pd.merge(predictions_df_1, predictions_df_2)

                    manage_plot(merged_predictions_df, province_name, price_type)


            with st.expander("Corn Grains Predictions Plots"):
                for province_name, config in province_configs.items():
                    province_id = config['province_id']

                    predictions_df_1 = w_predictions_df_2[w_predictions_df_2['province_id'] == province_id]
                    predictions_df_1 = predictions_df_1.rename(columns={"wholesale_corngrains_price": 'white_wholesale_corngrains_price'})
                    predictions_df_1 = predictions_df_1.iloc[:year] # Always slice the df, default or button press

                    predictions_df_2 = y_predictions_df_2[y_predictions_df_2['province_id'] == province_id]
                    predictions_df_2 = predictions_df_2.rename(columns={"wholesale_corngrains_price": 'yellow_wholesale_corngrains_price'})
                    predictions_df_2 = predictions_df_2.iloc[:year] # Always slice the df, default or button press
                    
                    merged_predictions_df = pd.merge(predictions_df_1, predictions_df_2)

                    manage_plot(merged_predictions_df, province_name, price_type)




        else:
            with st.expander("Predictions Plots"):
                for province_name, config in province_configs.items():
                    province_id = config['province_id']

                    predictions_df_1 = w_predictions_df[w_predictions_df['province_id'] == province_id]
                    predictions_df_1 = predictions_df_1.rename(columns={"price": f'white_{target_1}'})
                    predictions_df_1 = predictions_df_1.iloc[:year] # Always slice the df, default or button press

                    predictions_df_2 = y_predictions_df[y_predictions_df['province_id'] == province_id]
                    predictions_df_2 = predictions_df_2.rename(columns={"price": f'yellow_{target_2}'})
                    predictions_df_2 = predictions_df_2.iloc[:year] # Always slice the df, default or button press
                    
                    merged_predictions_df = pd.merge(predictions_df_1, predictions_df_2)

                    # st.dataframe(predictions_df_1)
                    # st.dataframe(predictions_df_2)
                    # st.dataframe(merged_predictions_df)

                    manage_plot(merged_predictions_df, province_name, price_type)


    if selected_dataset == 'Heatmap':

        # Month mapping dictionary
        month_mapping_1 = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 
            'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        # Mapping from month abbreviations to full month names
        province_list = ['Davao Region', 'Davao de Oro', 'Davao del Norte', 'Davao del Sur', 'Davao Oriental', 'Davao City']


        white_prediction_df, price_type, target = prediction_dataset(province_configs, selected_dataset, "White Corn")
        yellow_prediction_df, price_type, target = prediction_dataset(province_configs, selected_dataset, "Yellow Corn")
        

        # st.dataframe(white_prediction_df)
        # st.dataframe(yellow_prediction_df)


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



        col_1, col_2 = st.columns(2)

        with col_1:
            # Collect user inputs
            Month = st.selectbox("Month", month_names, index=default_index)



        # Determine the default year based on the selected month
        selected_month_num = month_mapping_1[Month]


        # Get unique values from the 'year' column and convert to a list
        year_option_list = [int(year) for year in white_prediction_df['year'].unique().tolist()]


        # Check if Month input is valid and adjust Year accordingly
        if int(selected_month_num) < int(last_month):
            Year = last_year + 1  # Increment year by 1 if selected month is less than last month
        else:
            Year = last_year       # Default to the last year if not incrementing

        # Ensure Year is in the list of options for the selectbox
        if Year not in year_option_list:
            year_option_list.append(Year)  # Add Year to options if it's not already present


        with col_2:
            # Select Year with default index based on Year variable
            Year = st.selectbox("Select Year", sorted(year_option_list), index=year_option_list.index(Year))


        # Filter predictions_df based on user inputs
        white_filtered_data = white_prediction_df[(white_prediction_df['month'] == selected_month_num) & (white_prediction_df['year'] == Year)]
        yellow_filtered_data = yellow_prediction_df[(yellow_prediction_df['month'] == selected_month_num) & (yellow_prediction_df['year'] == Year)]

        # Map province IDs to province names
        white_filtered_data['province'] = white_filtered_data['province_id'].map(lambda x: province_list[x - 1] if x - 1 < len(province_list) else None)        
        yellow_filtered_data['province'] = yellow_filtered_data['province_id'].map(lambda x: province_list[x - 1] if x - 1 < len(province_list) else None) 

        # st.dataframe(white_filtered_data)
        # st.dataframe(yellow_filtered_data)

        if user_type == 1: 
            price_type = "Farmgate Price"
        if user_type == 3: 
            price_type = "Retail Price"
        if user_type == 2: 
            white_filtered_data_1 = white_filtered_data.drop(["wholesale_corngrains_price"], axis=1)
            white_filtered_data_2 = white_filtered_data.drop(["wholesale_corngrits_price"], axis=1)

            yellow_filtered_data_1 = yellow_filtered_data.drop(["wholesale_corngrains_price"], axis=1)
            yellow_filtered_data_2 = yellow_filtered_data.drop(["wholesale_corngrits_price"], axis=1)

            price_type_1 = "Wholesale Corn Grits Price"
            price_type_2 = "Wholesale Corn Grains Price"



        col1, col2 = st.columns(2)
        with col1:
            if user_type == 2: 
                with st.expander("White Predictions Heat Map"):
                    st.subheader(f"{price_type_1}")
                    heatmap(white_filtered_data_1, price_type_1, "White Corn")

                    st.subheader(f"{price_type_2}")
                    heatmap(white_filtered_data_2, price_type_2, "White Corn")
            else:
                st.header(f"White Corn {price_type}")
                heatmap(white_filtered_data, price_type, "White Corn")

        with col2:
            if user_type == 2: 
                with st.expander("Yellow Predictions Heat Map"):
                    st.subheader(f"{price_type_1}")
                    heatmap(yellow_filtered_data_1, price_type_1, "Yellow Corn")

                    st.subheader(f"{price_type_2}")
                    heatmap(yellow_filtered_data_2, price_type_2, "Yellow Corn")
            else:
                st.header(f"Yellow Corn {price_type}")
                heatmap(yellow_filtered_data, price_type, "Yellow Corn")


