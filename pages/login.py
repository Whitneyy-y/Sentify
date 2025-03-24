import streamlit as st
import pandas as pd
import hashlib

def show_login_page():
    # Hashing function for the password for better safety
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    # Load user data from Excel
    def load_users():
        try:
            df = pd.read_excel("users.xlsx")
            return df.set_index("Username")['Password'].to_dict()
        except FileNotFoundError:
            return {}

    # Authenticate user
    def authenticate(username, password, users):
        hashed_password = hash_password(password)
        return users.get(username) == hashed_password

    #Establishing user sessions
    if "user" not in st.session_state:
        st.session_state["user"] = None

    #Checks if already logged in
    if st.session_state["user"]:
        st.success(f"You are already logged in as {st.session_state['user']}!")
        if st.button("Go to Dashboard"):
            st.switch_page("pages/main.py") 
        st.stop()

    # Login Page
    st.set_page_config(page_title="Login", page_icon="🔑", layout="centered")
    st.title("Login Page")

    # Load users
    users = load_users()

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):
        if authenticate(username, password, users):
            st.session_state.page = "dashboard"
            st.success("Logged in successfully!")
            st.session_state["user"] = username  # Store login session
            st.rerun() 
        else:
            st.error("Invalid username or password!")
    
    if st.button("Don't Have An Account?"):
        st.session_state.page = "signup" 
        st.rerun()
