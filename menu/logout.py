import streamlit as st

def app():
    # Set logout state
    st.session_state['logged_out'] = True
    
    # Provide feedback to the user
    st.success("You have successfully logged out.")
    
    # Optionally redirect to home or login page
    st.session_state['logged_in'] = False  # Ensure logged in state is updated
    st.session_state['user_type'] = '0'  # Reset user type if necessary
    st.rerun()  # Rerun to reflect changes
