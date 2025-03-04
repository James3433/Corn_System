import base64
import pandas as pd
import streamlit as st

def app():

    @st.cache_data
    def get_img_as_base64(file):
        with open (file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    
    img_1 = get_img_as_base64("images/Philippine_Statistics_Authority.svg.png")
    img_2 = get_img_as_base64("images/trade.png")
    img_3 = get_img_as_base64("images/trader.png")
    img_4 = get_img_as_base64("images/farmers.png")

    with st.sidebar:
        st.success("Select a page above.") 
    # Load custom CSS
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="intro">
            <h3> Welcome to Corn.com</h3>
            <p> Here in Corn.com we help you with your problems</p>
        </div>
        <div class="info">
            <div class="info_1">
                <img src="data:image/png;base64,{img_1}" alt="A beautiful landscape" width="100px" height="100px">
                <p>This website helps the PSa to record futuristic data in a short period of time.</p>
            </div>
            <div class="info_2">
                <img src="data:image/png;base64,{img_2}" alt="A beautiful landscape" width="100px" height="100px">
                <p>This website helps the consumers to prepare changes of corn price in a short period of time.</p>
            </div>
            <div class="info_3">
                <img src="data:image/png;base64,{img_3}" alt="A beautiful landscape" width="100px" height="100px">
                <p>This website helps the traders to make early decision planning using predicted corn price in a short period of time.</p>
            </div>
            <div class="info_4">
                <img src="data:image/png;base64,{img_4}" alt="A beautiful landscape" width="100px" height="100px">
                <p>This website helps the farmers to early decision planning using predicted corn price in a short period of time.</p>
            </div>
        </div>

    """, unsafe_allow_html=True)


    st.markdown(f"""
        <h4>Here are the features of this system for farmers, traders and consumers</h4>

        <div class="step_info">
            <div class="step_info_box_1">
                <h5>Monthly Data</h5>
                <p>This feature of the app will show the previous data from 1990 to the present year in graph plots.</p>
            </div>
            <div class="step_info_box_2">
                <h5>Predicted Data (Graph Plots)</h5>
                <p>This feature of the app will show the predicted data from one year or two years in graph plots.</p>
            </div>
            <div class="step_info_box_3">
                <h5>Predicted Data (Choropleth Plots)</h5>
                <p>This feature of the app will show the predicted data from one year or two years in choropleth plots.</p>
            </div>
            <div class="step_info_box_4">
                <h5>Manage Data</h5>
                <p>This feature of the app allows users to add new data into the database, ensuring that the application remains dynamic and responsive to user needs.</p>
            </div>
        </div>  <!-- Closing the step_info div -->
    """, unsafe_allow_html=True)



    st.markdown(f"""
        <h4>Here are the features of this system for the admin</h4>

        <div class="step_info">
            <div class="step_info_box_1">
                <h5>Monthly Data</h5>
                <p>This feature of the app will show the previous data from 1990 to the present year in graph plots.</p>
            </div>
            <div class="step_info_box_2">
                <h5>Predicted Data (Graph Plots)</h5>
                <p>This feature of the app will show the predicted data from one year or two years in graph plots.</p>
            </div>
            <div class="step_info_box_3">
                <h5>Predicted Data (Choropleth Plots)</h5>
                <p>This feature of the app will show the predicted data from one year or two years in choropleth plots.</p>
            </div>
            <div class="step_info_box_4">
                <h5>Comments</h5>
                <p>This feature of the app will allow the users to provide advice or complaints to the system.</p>
            </div>
            <div class="step_info_box_5">
                <h5>Comments</h5>
                <p>This feature of the app will allow the users to provide advice or complaints to the system.</p>
            </div>
        </div>  <!-- Closing the step_info div -->

    """, unsafe_allow_html=True)