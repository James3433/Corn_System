import streamlit as st
from menu import home, monthly_data, manage_data, manage_predict_1, manage_predict_2, comments, signup, login
from streamlit_option_menu import option_menu
from streamlit_modal import Modal

st.set_page_config(page_title='DavaoRegionCorn.com', page_icon='images/corn_logo.png', layout='wide')

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_type' not in st.session_state:
    st.session_state['user_type'] = '0'

if 'show_logout_modal' not in st.session_state:
    st.session_state['show_logout_modal'] = False
if 'modal_opened' not in st.session_state:
    st.session_state['modal_opened'] = False

if 'feature_app' not in st.session_state:
    feature_app = st.session_state['feature_app'] = 'Comments'

# Get user details from session state
user = st.session_state.get('lname', 'Guest')
gender = st.session_state.get('gender', 'Gender')
gender = "Mr." if gender == 1 else "Ms."

# Map user type
user_type_map = {1: "Farmer", 2: "Trader", 3: "Consumer", 4: "Admin"}
user_type = user_type_map.get(int(st.session_state.get('user_type', '0')), 'Guest')





# Create a modal instance
modal = Modal("Logout", key="logout-modal", padding=20)

def logout_button():
    if st.button("  Logout  "):
        modal.open()

# Render modal content
if modal.is_open():
    with modal.container():
        st.error("Are you sure you want to log out?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Yes'):
                st.session_state['logged_in'] = False
                st.session_state['user_type'] = '0'  # Reset user type
                modal.close()  # Close modal
                st.rerun()
        with col2:
            if st.button('No'):
                modal.close()  # Close modal
                st.rerun()


# Read CSS file once
with open("styles/style.css") as f:
    css_styles = f.read()

# MultiApp Class
class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({"title": title, "function": func})

    def run(self):
        app = None
        with st.sidebar:
            def show_main_menu_for_user():
                nonlocal app
                app = option_menu(
                    menu_title='Main Menu',
                    options=['Comments', 'Monthly Data', 'Predict Price'],
                    menu_icon='chat-text-fill',
                    default_index=0,
                    styles={
                        "container": {"background-color": "#a3f841"},
                        "icon": {"color": "black", "font-size": "20px"},
                        "menu-title": {"color": "black", "font-size": "20px", "font-family": "Source Sans Pro, sans-serif"},
                        "nav-link": {"color": "black", "font-size": "13px", "font-family": "Source Sans Pro, sans-serif"},
                        "nav-link-selected": {"background-color": "#eeff00", "font-family": "Source Sans Pro, sans-serif"}
                    }
                )

                st.markdown(f"<style>{css_styles}</style>", unsafe_allow_html=True)
                st.markdown(f"""
                    <style>
                        [data-testid="stSidebarHeader"]::before {{
                            background-color: greenyellow;
                            width: 79%;
                            height: 10%;
                            padding: 2% 0% 2% 6%;
                            border-radius: 1.3em;
                            content: "Welcome {gender} {user} ({user_type})";
                            font-size: 20px;
                            color: black;
                        }}

                        .st-emotion-cache-r2l7aq {{
                            gap: 0px;
                        }}
                    </style>
                """, unsafe_allow_html=True)

            def show_main_menu_for_admin():
                nonlocal app
                app = option_menu(
                    menu_title='Main Menu',
                    options=['Comments', 'Monthly Data', 'Predict Price', 'Manage Data'],
                    menu_icon='chat-text-fill',
                    default_index=0,
                    styles={
                        "container": {"background-color": "#a3f841"},
                        "icon": {"color": "black", "font-size": "20px"},
                        "menu-title": {"color": "black", "font-size": "20px", "font-family": "Source Sans Pro, sans-serif"},
                        "nav-link": {"color": "black", "font-size": "13px", "font-family": "Source Sans Pro, sans-serif"},
                        "nav-link-selected": {"background-color": "#eeff00", "font-family": "Source Sans Pro, sans-serif"}
                    }
                )

                st.markdown(f"<style>{css_styles}</style>", unsafe_allow_html=True)
                st.markdown(f"""
                    <style>
                        [data-testid="stSidebarHeader"]::before {{
                            background-color: greenyellow;
                            width: 79%;
                            height: 10%;
                            padding: 2% 0% 2% 6%;
                            border-radius: 1.3em;
                            content: "Welcome {gender} {user} ({user_type})";
                            font-size: 20px;
                            color: black;
                        }}

                        [data-testid="stVerticalBlock"] {{
                            gap: 10px;
                        }}
                    </style>
                """, unsafe_allow_html=True)

            def show_login_and_logout():
                nonlocal app
                app = option_menu(
                    menu_title='Login or Signup',
                    options=['Home', 'Sign-up', 'Log-in'],
                    menu_icon='key-fill',
                    default_index=0,
                    styles={
                        "container": {"background-color": "#a3f841"},
                        "icon": {"color": "black", "font-size": "20px"},
                        "menu-title": {"color": "black", "font-size": "20px", "font-family": "Source Sans Pro, sans-serif"},
                        "menu-icon": {"color": "black", "font-size": "40px"},
                        "nav-link": {"color": "black", "font-size": "13px", "font-family": "Source Sans Pro, sans-serif"},
                        "nav-link-selected": {"background-color": "#eeff00", "font-family": "Source Sans Pro, sans-serif"}
                    }
                )

            # Display appropriate menu based on login state
            if st.session_state['logged_in']:
                if st.session_state['user_type'] == 4:
                    show_main_menu_for_admin()
                    logout_button()
                else:
                    show_main_menu_for_user()
                    logout_button()
            else:
                show_login_and_logout()


        # Store the selected app in session state
        st.session_state['feature_app'] = app


        if app == 'Comments':
            comments.app()
          
        if app == 'Monthly Data':
            monthly_data.app()
         
        if app == 'Predict Price' and st.session_state['user_type'] != 4:
            manage_predict_1.app()

        if app == 'Predict Price' and st.session_state['user_type'] == 4:
            manage_predict_2.app()
          
        if app == 'Manage Data':
            manage_data.app()
  


        if app == 'Home':
            home.app()
        if app == 'Sign-up':
            signup.app()
        if app == 'Log-in':
            login.app()



# Create and run the app
app_instance = MultiApp()

app_instance.run()
