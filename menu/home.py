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
        <h4> Here are the features of this system</h4>
        <div class="steps_info">
            <h5> Monthly Data </h5>

        </div>

    """, unsafe_allow_html=True)

