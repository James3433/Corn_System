import streamlit as st
from menu import home, monthly_data, yearly_data, predict_price, system_description, signup, login
from streamlit_option_menu import option_menu

st.set_page_config(page_title='Corn.com', page_icon='images/corn_logo.png', layout='wide')

user = st.session_state.get('user', 'Guest')
gender = st.session_state.get('gender', 'Gender')

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
            def show_main_menu():
                nonlocal app
                app = option_menu(
                    menu_title='Main Menu',
                    options=['About', 'Monthly Data', 'Yearly Data', 'Predict Price'],
                    menu_icon='caht-text-fill',
                    default_index=0,
                    styles={
                        "container": {"background-color": "#a3f841"},
                        "icon": {"color": "black", "font-size": "5px"},
                        "nav-link": {"color": "black", "font-size": "13px", "font-family": "Source Sans Pro, sans-serif"},
                        "nav-link-selected": {"background-color": "#eeff00", "font-family": "Source Sans Pro, sans-serif"}
                    }
                )
            #     st.markdown(f"""
            #             <style>
            #                 [data-testid="stSidebarHeader"]::before {{
            #                     content: "Welcome {gender} {user}";
            #                     font-size: 20px;
            #                     color: black;
            #                 }}
            #             </style>
            #     """, unsafe_allow_html=True)

            # if st.session_state['logged_in']:
            #     show_main_menu()  # Show the main menu if the user is logged in
            # else:
            #     app = option_menu(
            #         menu_title='  ',
            #         options=['Home', 'Sign-up', 'Log-in'],
            #         menu_icon='key-fill',
            #         default_index=0,
            #         styles={
            #             "container": {"background-color": "#a3f841"},
            #             "icon": {"color": "black", "font-size": "5px"},
            #             "nav-link": {"color": "black", "font-size": "13px", "font-family": "Source Sans Pro, sans-serif"},
            #             "nav-link-selected": {"background-color": "#eeff00", "font-family": "Source Sans Pro, sans-serif"}
            #         }
            #     )
            
            show_main_menu()

                
        if app == 'About':
            system_description.app()
        if app == 'Monthly Data':
            monthly_data.app()
        if app == 'Yearly Data':
            yearly_data.app()
        if app == 'Predict Price':
            predict_price.app()
        if app == 'Home':
            home.app()
        if app == 'Sign-up':
            signup.app()
        if app == 'Log-in':
            login.app()

    run()
