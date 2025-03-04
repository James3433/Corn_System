import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from supabase_connect import get_corn_price

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
        if dataset is not None:
            grouped = dataset.groupby('year')

            for year, group in reversed(list(grouped)):
                # Create subplots - this is crucial for handling multiple traces cleanly
                fig = make_subplots(specs=[[{"secondary_y": False}]])  # Use secondary_y if needed for different scales

                # Define price types based on dataset columns
                if 'retail_corngrits_price' in dataset.columns:
                    price_types = {
                        'farmgate_corngrains_price': 'Farmgate Corn Grains Price',
                        'retail_corngrits_price': 'Retail Corn Grits Price',
                        'wholesale_corngrits_price': 'Wholesale Corn Grits Price',
                        'wholesale_corngrains_price': 'Wholesale Corn Grains Price'
                    }
                elif 'retail_corngrains_price' in dataset.columns:
                    price_types = {
                        'farmgate_corngrains_price': 'Farmgate Corn Grains Price',
                        'retail_corngrains_price': 'Retail Corn Grains Price',
                        'wholesale_corngrits_price': 'Wholesale Corn Grits Price',
                        'wholesale_corngrains_price': 'Wholesale Corn Grains Price'
                    }
                else:
                    price_types = { # Default if none exists
                        'wholesale_corngrits_price': 'Wholesale Price',
                        'wholesale_corngrains_price': 'Wholesale Price'
                    }

                # Plot each price type
                for price_col, label in price_types.items():
                    if price_col in group.columns:  # Check if the column exists
                        fig.add_trace(
                            go.Scatter(
                                x=group['month'],  # Use month directly
                                y=group[price_col],
                                mode='markers+lines',  # Show both markers and lines
                                name=label,
                                marker=dict(size=8), # Adjust marker size
                                hovertemplate=f"Type: {label}<br>Price: %{{y}}<extra></extra>" # Custom hover
                            ),
                            secondary_y=False, #Important
                        )

                # Update layout for better appearance
                fig.update_layout(
                    title=f"Corn Prices in the Year {year}",
                    xaxis_title="Month",
                    yaxis_title="Price",
                    template="plotly_dark",  # Or other base template if you prefer
                    hovermode="x unified",
                    title_x=0.5,  # Center title
                    plot_bgcolor='#B7E505',  # Yellow-Green for plot area
                    paper_bgcolor='#B7E505',  # Yellow-Green for surrounding paper

                    font=dict(
                        family="Arial",  # Specify font family
                        size=15,        # Overall font size
                        color="black"    # Overall font color
                    ),

                    xaxis=dict(
                        tickangle=-45,
                        titlefont=dict(size=15, color="black"),  # X-axis title font
                        tickfont=dict(size=12, color="black")    # X-axis tick labels font
                    ),

                    yaxis=dict(
                        titlefont=dict(size=15, color="black"),  # Y-axis title font
                        tickfont=dict(size=12, color="black")    # Y-axis tick labels font
                    ),

                    title_font=dict(size=20, color="black"),  # Title font (overrides general font)

                                        # Customize hover label appearance
                    hoverlabel=dict(
                            bgcolor="rgba(0, 0, 0, 0.8)",  # Background color (semi-transparent black)
                            font=dict(
                                size=14,                  # Font size
                                family="Arial",           # Font family
                                color="white"             # Font color
                            ),
                            bordercolor="yellow"          # Border color of the tooltip
                        )
                    )

                # # Rotate x-axis labels for readability
                # fig.update_xaxes(tickangle=-45)

                st.plotly_chart(fig, use_container_width=True)



    def user_plot_view(dataset, price_data):
        if dataset is not None:
            # Rename price columns
            dataset = dataset.rename(columns=lambda x: 'price' if '_price' in x else x)

            grouped = dataset.groupby('year')

            for year, group in reversed(list(grouped)):
                # Create the Plotly Express line plot
                fig = px.line(group,
                            x="month",
                            y="price",
                            mode='markers+lines',  # Show both markers and lines
                            marker=dict(size=8), # Adjust marker size
                            hovertemplate=f"Price: %{{y}}<extra></extra>" # Custom hover
                        )
                
                # Update layout for better appearance
                fig.update_layout(
                    title=f"Corn Prices in the Year {year}",
                    xaxis_title="Month",
                    yaxis_title="Price",
                    template="plotly_dark",  # Or other base template if you prefer
                    hovermode="x unified",
                    title_x=0.5,  # Center title
                    plot_bgcolor='#B7E505',  # Yellow-Green for plot area
                    paper_bgcolor='#B7E505',  # Yellow-Green for surrounding paper

                    font=dict(
                        family="Arial",  # Specify font family
                        size=15,        # Overall font size
                        color="black"    # Overall font color
                    ),

                    xaxis=dict(
                        tickangle=-45,
                        titlefont=dict(size=15, color="black"),  # X-axis title font
                        tickfont=dict(size=12, color="black")    # X-axis tick labels font
                    ),

                    yaxis=dict(
                        titlefont=dict(size=15, color="black"),  # Y-axis title font
                        tickfont=dict(size=12, color="black")    # Y-axis tick labels font
                    ),

                    title_font=dict(size=20, color="black"),  # Title font (overrides general font)

                    # Customize hover label appearance
                    hoverlabel=dict(
                            bgcolor="rgba(0, 0, 0, 0.8)",  # Background color (semi-transparent black)
                            font=dict(
                                size=14,                  # Font size
                                family="Arial",           # Font family
                                color="white"             # Font color
                            ),
                            bordercolor="yellow"          # Border color of the tooltip
                        )
                    )

                # Rotate x-axis labels for readability
                fig.update_xaxes(tickangle=-45)

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
    w_df = get_corn_price(1, province_id)
    y_df = get_corn_price(2, province_id)


    w_df.drop(['retail_corngrains_price'], axis=1, inplace=True)
    y_df.drop(['retail_corngrits_price'], axis=1, inplace=True)


    # Map the month numbers to their full names
    w_df['month'] = w_df['month'].map(month_full).astype(str)
    y_df['month'] = y_df['month'].map(month_full).astype(str)

    # Adjust DataFrames based on user type
    price_data = ""
    if user_type == 1:
        price_data = "Farmgate Price"
        w_df.drop(['retail_corngrits_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price'], axis=1, inplace=True)
        y_df.drop(['retail_corngrains_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price'], axis=1, inplace=True)

    elif user_type == 3:
        price_data = "Retail Price"
        w_df.drop(['farmgate_corngrains_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price'], axis=1, inplace=True)
        y_df.drop(['farmgate_corngrains_price', 'wholesale_corngrits_price', 'wholesale_corngrains_price'], axis=1, inplace=True)
        

    elif user_type == 2:
        price_data = "Wholesale Price"
        w_df.drop(['farmgate_corngrains_price', 'retail_corngrits_price'], axis=1, inplace=True)
        y_df.drop(['farmgate_corngrains_price', 'retail_corngrains_price'], axis=1, inplace=True)


    if user_type == 2 or user_type == 4:
        
        with st.expander("White Predictions Plots"):
            admin_plot_view(w_df, selected_region)
        
        with st.expander("Yellow Predictions Plots"):
            admin_plot_view(y_df, selected_region)
    else:
        
        with st.expander("White Predictions Plots"):
            user_plot_view(w_df, price_data)
    
        with st.expander("Yellow Predictions Plots"):
            user_plot_view(y_df, price_data)



    # if user_type == 4 or user_type == 3:
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         st.header("White Corn")
    #         with st.expander("White Predictions Plots"):
    #             admin_plot_view(white_dataset, selected_region)
    #     with col2:
    #         st.header("Yellow Corn")
    #         with st.expander("Yellow Predictions Plots"):
    #             admin_plot_view(yellow_dataset, selected_region)
    # else:
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         st.header("White Corn")
    #         with st.expander("White Predictions Plots"):
    #             user_plot_view(white_dataset, price_data)
    #     with col2:
    #         st.header("Yellow Corn")
    #         with st.expander("Yellow Predictions Plots"):
    #             user_plot_view(yellow_dataset, price_data)