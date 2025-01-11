import streamlit as st
import bcrypt
from supabase_connect import get_user_by_name

def app():

    fname = ''
    lname = ''

    # Load custom CSS
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown(f"""
            <style>
                [data-testid="stVerticalBlockBorderWrapper"] {{
                    background-color: #a3f841;
                    width: 100%;
                    height: 110%; 
                    border-radius: 10px;
                    padding: 1% 5%;
                }}
            </style>
    """, unsafe_allow_html=True)


    with st.container():
        st.header(" Login Account ")
        fname_lname = st.text_input(label="Username", placeholder="Enter your First Name, space and then Last Name", key="fname_input")
        password = st.text_input(label="Password", type="password", placeholder="Password",  key="password_input")
        
        if st.button('Login'):
            if not fname_lname or not password:
                st.error("Please enter both username and password.")
                return

            # Parse the username into first name and last name
            try:
                fname, lname = fname_lname.split(' ', 1) 

            except ValueError:
                st.error("Please enter both First Name and Last Name separated by a space.")
                return

            # Get user by first name and last name
            user = get_user_by_name(fname, lname)
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
