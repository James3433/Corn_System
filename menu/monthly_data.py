import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import httpx

from plotly.subplots import make_subplots
from supabase_connect import get_corn_price

id 

def app():

    user_type = st.session_state.get('user_type', '0')

    # Load custom CSS
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown(f"""
            <style>
                [data-testid="stMain"] {{
                    padding-top: 10%;
                }}

                [data-testid="stAppViewBlockContainer"] {{    
                    border-radius: 10px;
                    background-color: #66CC91;
                    border: 2px solid #389961;
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

    # Mapping full month numbers to their full name
    month_full = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 
                  7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}


    def monthly_plot_view(dataset, selected_region, price_type):
        if dataset is not None:
            grouped = dataset.groupby('year')

            for year, group in reversed(list(grouped)):
                # Create subplots - this is crucial for handling multiple traces cleanly
                fig = make_subplots(specs=[[{"secondary_y": False}]])  # Use secondary_y if needed for different scales

                title = f"{price_type} in the Year {year}"

                # Define price types based on dataset columns
                if 'white_farmgate_corngrains_price' in dataset.columns:
                    price_columns = {
                        'white_farmgate_corngrains_price': 'White Corn', 
                        'yellow_farmgate_corngrains_price': 'Yellow Corn'
                        }

                elif 'white_retail_corngrits_price' in dataset.columns:  
                    price_columns = {
                        'white_retail_corngrits_price': 'White Corn', 
                        'yellow_retail_corngrains_price': 'Yellow Corn'
                        }
                    
                elif 'white_wholesale_corngrits_price' in dataset.columns:  
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
                    if price_types in group.columns:  # Check if the column exists
                        # Replace underscores with spaces and remove '_price'
                        formatted_name = price_types.replace('_price', ' ').title()
                        formatted_name = formatted_name.replace('_', ' ').title()
                        
                        fig.add_trace(go.Scatter(
                                x=group['month'],  # Use month directly
                                y=group[price_types],
                                mode='markers+lines',  # Show both markers and lines
                                name=price_id,
                                marker=dict(size=8), # Adjust marker size
                                hovertemplate= f"Type: {formatted_name}<br>Price: %{{y}}<extra></extra>"  # Custom hover 

                            ),
                            secondary_y=False, #Important
                        )

                # Update layout for better appearance
                fig.update_layout(
                    title=title,
                    title_x=0.05,  # Position title at the far left
                    title_xanchor='left',  # Anchor title to the left
                    template="plotly_dark",  # Or other base template if you prefer
                    hovermode="x unified",
                    plot_bgcolor='#66CC91',  # Yellow-Green for plot area
                    paper_bgcolor='#66CC91',  # Yellow-Green for surrounding paper

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
                        fixedrange=True, # Disable zooming
                        showline=True, linecolor='#389961', linewidth=2
                    ),

                    yaxis=dict(
                        title_font=dict(size=15, color="black"),  # Correct property
                        tickfont=dict(size=12, color="black"), # Y-axis tick labels font
                        fixedrange=True, # Disable zooming
                        showline=True, linecolor='#389961', linewidth=2
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
                        bordercolor='#389961' # Border color of the tooltip
                    )
                )

                # Display the plot in Streamlit
                st.plotly_chart(fig, use_container_width=True)  # Make the plot responsive







    selected_region = st.selectbox("Choose a Region:", ['Davao Region', 'Davao de Oro', 'Davao del Norte', 'Davao del Sur', 'Davao Oriental', 'Davao City'])
    
    # Select dataset based on region
    region_map = {
        'Davao Region': 1,
        'Davao de Oro': 2,
        'Davao del Norte': 3,
        'Davao del Sur': 4,
        'Davao Oriental': 5,
        'Davao City': 6
    }

    
    province_id = region_map.get(selected_region)

    # Group the data by year based on the selected dataset
    try:
        w_df = get_corn_price(1, province_id)
        y_df = get_corn_price(2, province_id)
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

    # Map the month numbers to their full names
    w_df['month'] = w_df['month'].map(month_full).astype(str)
    y_df['month'] = y_df['month'].map(month_full).astype(str)

    # st.dataframe(w_df)
    # st.dataframe(y_df)

# ================================================[ Farmgate Plot View ]=============================================================
    wf_df = w_df.drop(['retail_corngrits_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price'], axis=1)
    yf_df = y_df.drop(['retail_corngrains_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price'], axis=1) 

    wf_df = wf_df.rename(columns={'farmgate_corngrains_price': 'white_farmgate_corngrains_price'}) #Fix naming
    yf_df = yf_df.rename(columns={'farmgate_corngrains_price': 'yellow_farmgate_corngrains_price'}) #Fix naming

    price_type_1 = "Farmgate Price"
    farmgate_df = pd.merge(wf_df, yf_df)

# =================================================[ Retail Plot View ]==============================================================
    wr_df = w_df.drop(['farmgate_corngrains_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price'], axis=1)
    yr_df = y_df.drop(['farmgate_corngrains_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price'], axis=1)

    wr_df = wr_df.rename(columns={'retail_corngrits_price': 'white_retail_corngrits_price'}) #Fix naming
    yr_df = yr_df.rename(columns={'retail_corngrains_price': 'yellow_retail_corngrains_price'}) #Fix naming

    price_type_2 = "Retail Price"
    retail_df = pd.merge(wr_df, yr_df)


# =============================================[ Wholesale Corngrits Plot View ]=====================================================
    ww1_df = w_df.drop(['farmgate_corngrains_price', 'wholesale_corngrains_price', 'retail_corngrits_price'], axis=1)
    yw1_df = y_df.drop(['farmgate_corngrains_price', 'wholesale_corngrains_price', 'retail_corngrains_price'], axis=1)

    ww1_df = ww1_df.rename(columns={'wholesale_corngrits_price': 'white_wholesale_corngrits_price'}) #Fix naming
    yw1_df = yw1_df.rename(columns={'wholesale_corngrits_price': 'yellow_wholesale_corngrits_price'}) #Fix naming

    price_type_3 = "Wholesale Corngrits Price"
    wholasale_df_1 = pd.merge(ww1_df, yw1_df)

# =============================================[ Wholesale Corngrains Plot View ]===================================================
    ww2_df = w_df.drop(['farmgate_corngrains_price', 'wholesale_corngrits_price', 'retail_corngrits_price'], axis=1)
    yw2_df = y_df.drop(['farmgate_corngrains_price', 'wholesale_corngrits_price', 'retail_corngrains_price'], axis=1)

    ww2_df = ww2_df.rename(columns={'wholesale_corngrains_price': 'white_wholesale_corngrains_price'}) #Fix naming
    yw2_df = yw2_df.rename(columns={'wholesale_corngrains_price': 'yellow_wholesale_corngrains_price'}) #Fix naming
    
    price_type_4 = "Wholesale Corngrains Price"
    wholasale_df_2 = pd.merge(ww2_df, yw2_df)


# =======================================[ Farmers Plot View ]====================================================
    if user_type == 1:
        with st.expander("Farmgate Predictions Plots"):
            monthly_plot_view(farmgate_df, selected_region, price_type_1)


# =======================================[ Consumer Plot View ]====================================================
    elif user_type == 3:
        with st.expander("Retail Predictions Plots"):
            monthly_plot_view(retail_df, selected_region, price_type_2)


# =======================================[ Trader Plot View ]====================================================
    elif user_type == 2:
        # Adjust DataFrames based on user type
        col_1, col_2 = st.columns(2)

        with col_1:
            with st.expander("Wholesale Corngrits Monthly Plots"):
                monthly_plot_view(wholasale_df_1, selected_region, price_type_3)
        
        with col_2:
            with st.expander("Wholesale Corngrains Monthly Plots"):
                monthly_plot_view(wholasale_df_2, selected_region, price_type_4)


# =======================================[ Admin Plot View ]====================================================
    elif user_type == 4:
        # Adjust DataFrames based on user type
        col_1, col_2 = st.columns(2)
        col_3, col_4 = st.columns(2)       

        with col_1:
            with st.expander("Farmgate Monthly Plots"):
                monthly_plot_view(farmgate_df, selected_region, price_type_1)
        
        with col_2:
            with st.expander("Retail Monthly Plots"):
                monthly_plot_view(retail_df, selected_region, price_type_2)

        with col_3:
            with st.expander("Wholesale Corngrits Monthly Plots"):
                monthly_plot_view(wholasale_df_1, selected_region, price_type_3)
        
        with col_4:
            with st.expander("Wholesale Corngrains Monthly Plots"):
                monthly_plot_view(wholasale_df_2, selected_region, price_type_4)

