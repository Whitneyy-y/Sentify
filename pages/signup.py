import streamlit as st
import pandas as pd
import os
import hashlib

def show_signup_page():
    # Hashing function
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    # Save new user to Excel file
    def save_user(username, password, youtube_channel):
        hashed_password = hash_password(password)
        try:
            df = pd.read_excel("users.xlsx")
        except FileNotFoundError:
            df = pd.DataFrame(columns=["Username", "Password", "YouTube Channel"])
        
        if username in df["Username"].values:
            return False  # User already exists
        
        new_user = pd.DataFrame({
            "Username": [username], 
            "Password": [hashed_password], 
            "YouTube Channel": [youtube_channel]
        })
        df = pd.concat([df, new_user], ignore_index=True)
        print(df)  # This was a step taken to ensure that the data was properly captured.
        df.to_excel("users.xlsx", index=False, engine="openpyxl")

        # os.utime("users.xlsx", None)  # Update file timestamp to ensure it refreshes
        return True

    # Sign Up Page
    st.set_page_config(page_title="Sign Up", page_icon="📝", layout="centered")
    st.title("Sign Up Page")

    new_username = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type="password")
    youtube_channel = st.text_input("Enter your YouTube Channel Name")

    if st.button("Register"):
        if save_user(new_username, new_password, youtube_channel):
            st.session_state.page = "login" 
            st.success("Account created successfully! Redirecting to login...")
            st.rerun() 
            
            
        else:
            st.error("Username already exists. Try another.")

    if st.button("Already Have An Account?"):
        st.session_state.page = "login" 
        st.rerun()