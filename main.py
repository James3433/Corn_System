import streamlit as st
from menu import home, monthly_data, yearly_data, predict_price, manage_data, system_description, comments, signup, login
from streamlit_option_menu import option_menu

st.set_page_config(page_title='Corn.com', page_icon='images/corn_logo.png', layout='wide')

user = st.session_state.get('lname', 'Guest')
gender = st.session_state.get('gender', 'Gender')
user_type = st.session_state.get('user_type', '0')

# Check if the user is logged in by checking session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if gender == 1:
    gender = "Mr."
else:
    gender = "Ms."

class MultiApp:
    def __init__(self):
        self.apps = []
    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        }) 
    def run():
        app = None
        with st.sidebar:           
            def show_main_menu_for_user():
                nonlocal app
                app = option_menu(
                    menu_title='Main Menu',
                    options=['About', 'Comments', 'Monthly Data', 'Yearly Data', 'Predict Price'],
                    menu_icon='caht-text-fill',
                    default_index=0,
                    styles={
                        "container": {"background-color": "#a3f841"},
                        "icon": {"color": "black", "font-size": "20px"},
                        "menu-title": {"color": "black", "font-size": "20px", "font-family": "Source Sans Pro, sans-serif"},
                        "nav-link": {"color": "black", "font-size": "13px", "font-family": "Source Sans Pro, sans-serif"},
                        "nav-link-selected": {"background-color": "#eeff00", "font-family": "Source Sans Pro, sans-serif"}
                    }
                )

                st.markdown(f"""
                        <style>
                            [data-testid="stSidebarHeader"]::before {{
                                content: "Welcome {gender} {user}";
                                font-size: 20px;
                                color: black;
                            }}
                        </style>
                """, unsafe_allow_html=True)

            # def show_main_menu_for_admin():
            #     nonlocal app
            #     app = option_menu(
            #         menu_title='Main Menu',
            #         options=['About', 'Comments', 'Monthly Data', 'Yearly Data', 'Predict Price', 'Manage Data'],
            #         menu_icon='caht-text-fill',
            #         default_index=0,
            #         styles={
            #             "container": {"background-color": "#a3f841"},
            #             "icon": {"color": "black", "font-size": "20px"},
            #             "menu-title": {"color": "black", "font-size": "20px", "font-family": "Source Sans Pro, sans-serif"},
            #             "nav-link": {"color": "black", "font-size": "13px", "font-family": "Source Sans Pro, sans-serif"},
            #             "nav-link-selected": {"background-color": "#eeff00", "font-family": "Source Sans Pro, sans-serif"}
            #         }
            #     )

            #     st.markdown(f"""
            #             <style>
            #                 [data-testid="stSidebarHeader"]::before {{
            #                     content: "Welcome {gender} {user}";
            #                     font-size: 20px;
            #                     color: black;
            #                 }}
            #             </style>
            #     """, unsafe_allow_html=True)

            # if st.session_state['logged_in'] and st.session_state['user_type'] == 4:
            #     show_main_menu_for_admin()

            if st.session_state['logged_in'] and st.session_state['user_type'] != 4:
                show_main_menu_for_user()
            else:
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

                
        if app == 'About':
            system_description.app()
        if app == 'Comments':
            comments.app()
        if app == 'Monthly Data':
            monthly_data.app()
        if app == 'Yearly Data':
            yearly_data.app()
        if app == 'Predict Price':
            predict_price.app()
        if app == 'Manage Data':
            manage_data.app()
        if app == 'Home':
            home.app()
        if app == 'Sign-up':
            signup.app()
        if app == 'Log-in':
            login.app()

    run()
