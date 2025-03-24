import streamlit as st
from pages.login import show_login_page
from pages.signup import show_signup_page
from pages.dashboard import show_dashboard

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "landing"  # lowercase "landing" to match the logic below

def show_landing_page():
    # Page Configurations
    st.set_page_config(page_title="Welcome To Sentify", page_icon="🚀", layout="centered")

    # Stylings for the body.
    st.markdown(
        """
        <style>
            .stApp {
                background-color: white;  
                 color: #333333;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Welcome/Introduction
    st.subheader(" ")
    st.title("Welcome to Sentify! 🔍📊")
    st.subheader("Want to Understand What Your YouTube Audience Thinks Of You? ")
    st.subheader("Sentify's Got You!")
    st.toast("Hi there 😊! I'm Sentify and I'm here to help you analyse YouTube comments. Let's go!")


    # Styling the buttons
    button_style = """
        <style>
            .stButton>button {
                width: 200px;
                height: 60px;
                border-radius: 30px;
                font-size: 18px;
                font-weight: bold;
                margin: 10px;
                color: black;
            }
            body {
                background-color: #F0F8EA;  
            }
        </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)

    # Buttons
    col1, col2 = st.columns([1, 1]) 
    with col1:
        if st.button("Log In"):
            st.session_state.page = "login"  # This is how we switch to login page
    with col2:
        if st.button("Sign Up"):
            st.session_state.page = "signup"  # This switches to signup page

# This is where we actually "route" to the right page
if st.session_state.page == "landing":
    show_landing_page()
elif st.session_state.page == "login":
    show_login_page()
elif st.session_state.page == "signup":
    show_signup_page()
elif st.session_state.page == "dashboard":
    show_dashboard()
