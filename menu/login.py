import streamlit as st
import bcrypt
from supabase_connect import get_user_by_name
import httpx

def app():

    fname = ''
    lname = ''

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
                    background-color: #8edd27;
                    border: 2px solid green;
                    width: 90%;
                    padding: 1% 5%;
                }}
            </style>
    """, unsafe_allow_html=True)


    with st.container():
        st.header(" Login Account ")
        fname_lname = st.text_input(label="Username", placeholder="(Last Name)+','+(space)+(First Name)", key="fname_input")
        password = st.text_input(label="Password", type="password", placeholder="Password",  key="password_input")
        
        if st.button('Login'):
            if not fname_lname or not password:
                st.error("Please enter both username and password.")
                return

            # Parse the username into first name and last name
            try:
                lname, fname = fname_lname.split(', ', 1) 

            except ValueError:
                st.error("Please enter both Last Name Name and First Name separated by a comma and a space.")
                return

            # Get user by first name and last name
            try:
                user = get_user_by_name(fname, lname)
            except httpx.ConnectError as e:
                st.error(f"Connection error: Unable to connect to the server. Please try again later.")
                return
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                return

            if not user:
                st.error("User not found. Please check your username.")
                return

            # Verify password using bcrypt
            hashed_password = user['password']
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                st.success("Login successful!")
                # Store login status in session state to keep track of the user
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = user.get('id')
                st.session_state['fname'] = fname
                st.session_state['lname'] = lname
                st.session_state['gender'] = user.get('gender')
                st.session_state['user_type'] = user.get('user_type')
                st.rerun()
            else:
                st.error("Invalid password. Please try again.")

