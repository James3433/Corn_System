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

    # Load custom CSS
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown(f"""
            <style>
                [data-testid="stVerticalBlock"] {{
                    border-radius: 2em;
                    background-color: #8edd27;
                    border: 2px solid green;
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


    def RERF_Model(corn_type, folder_type, province_name, target, price_type):
        RERF_pred = []

        try:
            predictor = pd.read_csv(f'Predictor_Models/{corn_type}/{province_name}/{folder_type}/predictor_dataset.csv')

            # # Polynomial Features (if applicable)
            # if ((province_name == "davao_de_oro" and target == "farmgate_corngrains_price" and corn_type == "White Corn") or
            #     (province_name == "davao_del_sur" and target == "retail_corngrits_price" and corn_type == "White Corn") or
            #     (province_name == "davao_oriental" and target == "retail_corngrits_price" and corn_type == "White Corn") or
            #     (province_name == "davao_city" and target == "retail_corngrits_price" and corn_type == "White Corn") or
            #     (province_name == "davao_city" and target == "farmgate_corngrains_price" and corn_type == "Yellow Corn")):

            #     # Optional: Extend x_train and x_test with polynomial features
            #     poly = PolynomialFeatures(degree=2, include_bias=True)
                
            #     # Get column names before transformation
            #     original_columns = predictor.columns
                
            #     # Transform data
            #     predictor = poly.fit_transform(predictor)
                
            #     # Create new column names (you might need to adjust this based on poly.get_feature_names_out())
            #     new_columns = poly.get_feature_names_out(original_columns)  # Requires scikit-learn >= 1.0

            #     # Convert back to DataFrame
            #     predictor = pd.DataFrame(predictor, columns=new_columns)

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
            RERF_pred_df[price_type] = final_predict

            # st.dataframe(RERF_pred_df)

            return RERF_pred_df  # Return the DataFrame

        except FileNotFoundError as e:
            print(f"Error loading predictor data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return pd.DataFrame()




    def predict_dataset(corn_type, province_name):

        # predict farmgate price for white_davao_region
        f_price_type = "farmgate_corngrains_price"
        f_folder_type = "For Farmgate"
        f_target = "farmgate_corngrains_price"
        f_prediction = RERF_Model(corn_type, f_folder_type, province_name, f_target, f_price_type) 

        if corn_type == "White Corn":
            # predict retail price for white_davao_region
            r_price_type = "retail_corngrits_price"
            r_folder_type = "For Retail"
            r_target = "retail_corngrits_price"
            r_prediction = RERF_Model(corn_type, r_folder_type, province_name, r_target, r_price_type)

        if corn_type == "Yellow Corn":
            # predict retail price for white_davao_region
            r_price_type = "retail_corngrains_price"
            r_folder_type = "For Retail"
            r_target = "retail_corngrains_price"
            r_prediction = RERF_Model(corn_type, r_folder_type, province_name, r_target, r_price_type) 

        # predict wholesale price for white_davao_region
        w_price_type_1 = "wholesale_corngrits_price"
        w_folder_type = "For Wholesale"
        w_target_1 = "wholesale_corngrits_price"
        w_prediction_1 = RERF_Model(corn_type, w_folder_type, province_name, w_target_1, w_price_type_1) 

         # predict wholesale price for white_davao_region
        w_price_type_2 = "wholesale_corngrains_price"
        w_target_2 = "wholesale_corngrains_price"
        w_prediction_2 = RERF_Model(corn_type, w_folder_type, province_name, w_target_2, w_price_type_2) 

        # st.dataframe(f_prediction)
        # st.dataframe(r_prediction)
        # st.dataframe(w_prediction_1)
        # st.dataframe(w_prediction_2)

        predict_dataset = pd.DataFrame()
        r_prediction = r_prediction.drop(['year','month'], axis=1)
        w_prediction_1 = w_prediction_1.drop(['year','month'], axis=1)
        w_prediction_2 = w_prediction_2.drop(['year','month'], axis=1)
        predict_dataset = pd.concat([f_prediction, r_prediction, w_prediction_1, w_prediction_2], axis=1)


        return predict_dataset


    
    def manage_plot(dataset, selected_dataset):

        # Mapping full month names to three-letter abbreviations
        month_abbr = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

        # Map the full month names to their abbreviations
        dataset['month'] = dataset['month'].map(month_abbr).astype(str)
        dataset['Month Year'] = dataset['month'] + ' - ' + dataset['year'].astype(str)

        num_rows = len(dataset)

        # Define price types based on dataset columns
        if 'retail_corngrits_price' in dataset.columns:
            price_columns = ['farmgate_corngrains_price', 'retail_corngrits_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price']
        
        elif 'retail_corngrains_price' in dataset.columns:
            price_columns = ['farmgate_corngrains_price', 'retail_corngrains_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price']

        # Create Plotly figure
        fig = go.Figure()

        # Plot each price type
        for price_type in price_columns:
            if price_type in dataset.columns:
                fig.add_trace(go.Scatter(
                    x=dataset['Month Year'],
                    y=dataset[price_type],
                    mode='markers+lines',
                    name=price_type.replace('_', ' ').title(),
                    hovertemplate=f"Type: {price_type.replace('_', ' ').title()}<br>Price: %{{y}}<extra></extra>"
                ))

        # Update layout
        fig.update_layout(
            title=f'{selected_dataset} Price Data in {num_rows} Months',
            title_x=0.05,  # Position title at the far left
            title_xanchor='left',  # Anchor title to the left
            template="plotly_dark",  # Or other base template if you prefer
            hovermode="x unified",
            plot_bgcolor='#B7E505',  # Yellow-Green for plot area
            paper_bgcolor='#B7E505',  # Yellow-Green for surrounding paper

            font=dict(
                family="Arial",  # Specify font family
                size=15,        # Overall font size
                color="black"    # Overall font color
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

            title_font=dict(size=20, color="black"), # Title font (overrides general font)

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
            predict_df = predict_dataset(corn_type, dataset_name)

            # Add province_id to predict_df
            predict_df['province_id'] = province_id

            # Append the current predict_df to predictions_df
            predictions_df = pd.concat([predictions_df, predict_df], ignore_index=True)

        return predictions_df



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

        with st.expander("White Predictions Plots"):
            predictions_df = prediction_dataset(province_configs, selected_dataset, "White Corn")

            for province_name, config in province_configs.items():
                province_id = config['province_id']
                predictions_df_1 = predictions_df[predictions_df['province_id'] == province_id]
                predictions_df_1 = predictions_df_1.iloc[:year] # Always slice the df, default or button press
                manage_plot(predictions_df_1, province_name)


        
        with st.expander("Yellow Predictions Plots"):
            predictions_df = prediction_dataset(province_configs, selected_dataset, "Yellow Corn")

            for province_name, config in province_configs.items():
                province_id = config['province_id']
                predictions_df_1 = predictions_df[predictions_df['province_id'] == province_id]
                predictions_df_1 = predictions_df_1.iloc[:year] # Always slice the df, default or button press
                manage_plot(predictions_df_1, province_name)




    if selected_dataset == 'Heatmap':

        # Month mapping dictionary
        month_mapping_1 = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 
            'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        # Mapping from month abbreviations to full month names
        province_list = ['Davao Region', 'Davao de Oro', 'Davao del Norte', 'Davao del Sur', 'Davao Oriental', 'Davao City']


        white_prediction_df = prediction_dataset(province_configs, selected_dataset, "White Corn")
        yellow_prediction_df = prediction_dataset(province_configs, selected_dataset, "Yellow Corn")
        

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
        year_option_list = [int(year) for year in white_prediction_df['year'].unique().tolist()]


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

        w_farmgate_df = white_filtered_data[['province', 'farmgate_corngrains_price']]
        w_retail_df = white_filtered_data[['province', 'retail_price']]
        w_wholesale_df_1 = white_filtered_data[['province', 'wholesale_corngrits_price']]
        w_wholesale_df_2 = white_filtered_data[['province', 'wholesale_corngrains_price']]

        y_farmgate_df = yellow_filtered_data[['province', 'farmgate_corngrains_price']]
        y_retail_df = yellow_filtered_data[['province', 'retail_corngrains_price']]
        y_wholesale_df_1 = yellow_filtered_data[['province', 'wholesale_corngrits_price']]
        y_wholesale_df_2 = yellow_filtered_data[['province', 'wholesale_corngrains_price']]



        col1, col2 = st.columns((2))
        with col1:
            st.header("White Corn")
            st.header("Farmgate Price")
            heatmap(w_farmgate_df, 'Farmgate Price', 'White Corn')
            st.header("Retail Price")
            heatmap(w_retail_df, 'Retail Price', 'White Corn')
            st.header("Wholesale Corn Grits Price")
            heatmap(w_wholesale_df_1, 'Wholesale Price', 'White Corn')
            st.header("Wholesale Corn Grains Price")
            heatmap(w_wholesale_df_2, 'Wholesale Price', 'White Corn')

        with col2:
            st.header("Yellow Corn")
            st.header("Farmgate Price")
            heatmap(y_farmgate_df, 'Farmgate Price', 'Yellow Corn')
            st.header("Retail Price")
            heatmap(y_retail_df, 'Retail Price', 'Yellow Corn')
            st.header("Wholesale Corn Grits Price")
            heatmap(y_wholesale_df_1, 'Wholesale Price', 'Yellow Corn')
            st.header("Wholesale Corn Grains Price")
            heatmap(y_wholesale_df_2, 'Wholesale Price', 'Yellow Corn')


        





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

