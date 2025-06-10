import bcrypt
import pandas as pd
import streamlit as st

from supabase_connect import insert_user, user_exists

def app():

    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user_type_mapping = {
        'Farmer': 1,
        'Trader': 2,
        'Consumer': 3,
        'Admin': 4
    }
    gender_type_mapping = {
        'Male': 1,
        'Female': 2,
    }

    # Load custom CSS
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    st.markdown(f"""
            <style>
                .st-emotion-cache-bm2z3a {{
                    padding-top: 10%;
                }}

                [data-testid="stAppViewBlockContainer"] {{    
                    border-radius: 10px;
                    background-color: #66CC91;
                    border: 2px solid #389961;
                    width: 90%;
                    padding: 1% 5% 5%;
                }}
            </style>
    """, unsafe_allow_html=True)


    with st.container():
        st.header(" Sign-up Account ")
        col_1, col_2, col_3 = st.columns(3)
        with col_1:
            fname = st.text_input(label="First Name", placeholder="First Name", key="fname_input")
        with col_2:
            mname = st.text_input(label="Middle Name", placeholder="Middle Name", key="mname_input")
        with col_3:
            lname = st.text_input(label="Last Name", placeholder="Last Name", key="lname_input")

        col_4, col_5, col_6 = st.columns((1, 1.5, 2))
        with col_4:
            age = st.text_input(label="Age", max_chars=2, placeholder="Age", key="age_input")
        with col_5:
            gender = st.selectbox('Gender', ['Male', 'Female'], key='gender_selector')
        with col_6:
            # type = st.selectbox('User Type', ['Farmer', 'Trader', 'Consumer', 'Admin'], key='type_selector')
            type = st.selectbox('User Type', ['Farmer', 'Trader', 'Consumer'], key='type_selector')

        password = st.text_input(label="Password", type="password", placeholder="Password",  key="password_input")

        type_numeric = user_type_mapping[type]
        gender_numeric = gender_type_mapping[gender]
        hashed_password = hash_password(password)
        
        if st.button('Submit'):
            if fname and lname and age:  # Ensure essential fields are filled
                if user_exists(fname, mname, lname):
                    st.warning("User with the same name already exists!")
                else:
                    response = insert_user(fname, mname, lname, age, type_numeric, gender_numeric, hashed_password)
                    if response.data:  # Successful insertion
                        st.success(f"User {fname} {mname} {lname} added successfully!")
                    elif response.error:
                        st.error("There was an issue adding the user.")
            else:
                st.warning("Please fill in all required fields.")