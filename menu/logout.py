import streamlit as st
from streamlit_modal import Modal
from menu import monthly_data, manage_data, manage_predict_1, manage_predict_2, comments

def app():
    feature_app = st.session_state.get('feature_app', 'Comments')  # Get last visited feature

    # Create a modal instance
    modal = Modal("Logout", key="logout-modal", padding=20)

    # Open modal when Logout is clicked
    if st.button('Logout'):
        modal.open()

    # Render modal content
    if modal.is_open():
        with modal.container():
            st.warning("You pressed Logout but are still logged in.")
            st.button("Close", on_click=lambda: st.session_state.update({'show_logout_modal': False}))

    # Show the last visited page
    if feature_app == 'Comments':
        comments.app()
    elif feature_app == 'Monthly Data':
        monthly_data.app()
    elif feature_app == 'Predict Price':
        if st.session_state.get('user_type', 0) == 4:
            manage_predict_2.app()
        else:
            manage_predict_1.app()
    elif feature_app == 'Manage Data':
        manage_data.app()



    # # Set logout state
    # st.session_state['logged_out'] = True
    
    # # Provide feedback to the user
    # st.success("You have successfully logged out.")
    
    # # Optionally redirect to home or login page
    # st.session_state['logged_in'] = False  # Ensure logged in state is updated
    # st.session_state['user_type'] = '0'  # Reset user type if necessary
    # st.rerun()  # Rerun to reflect changes
