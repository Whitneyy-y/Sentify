import streamlit as st
import pandas as pd
import subprocess
import sys

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt

from wordcloud import WordCloud
from shared import extract_video_id
from fetchcomments import get_youtube_comments, analyze_sentiment
import os
from dotenv import load_dotenv
import datetime
import time

hour = datetime.datetime.now().hour

def show_dashboard():
    st.set_page_config(page_title="YouTube Sentiment Analyzer", layout="wide")

    # Logout button
    col1, col2 = st.columns([8, 1])  # Create space for alignment
    with col2:
        if st.button("Logout", use_container_width=True):
              st.session_state.clear()  # Clears session state
              st.session_state["logged_out"] = True  
              st.switch_page("landing.py")
    
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

    # if "video_history" not in st.session_state:
    #     st.session_state.video_history = [] 

    # # Sidebar for past analyzed videos
    # st.sidebar.header("Want To Analyze Your Videos?")
    # # if st.session_state.video_history:
    # #     for title, vid in st.session_state.video_history[-5:]:  # Show last 5 analyzed videos
    # #         st.sidebar.markdown(f"▶️ [{title}](https://www.youtube.com/watch?v={vid})")
    # # else:
    # st.sidebar.write("We've got you!!.")

    # Greetings!
    if hour < 12:
        greeting = "Good Morning"
    elif hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    if "user" in st.session_state:
        st.subheader(f"{greeting}, {st.session_state.user} 💚!")
    else:
        st.subheader("Hi there! 👋")
    load_dotenv()
    API_KEY = os.getenv("API_KEY")

    if 'df' not in st.session_state:
        st.session_state.df = None

    st.title("Welcome to Sentify, Your YouTube Comment Sentiment Analyzer 📊 !")
    st.subheader("Understand what people are saying about your content!")

    def show_sentiment_distribution(df):
        st.markdown("### Sentiment Distribution")
        sentiment_counts = df['sentiment'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(
            sentiment_counts,
            labels=sentiment_counts.index,
            autopct='%1.1f%%',
            startangle=140,
            colors=['#4CAF50', '#F44336', '#FFC107']
        )
        ax.axis('equal')
        st.pyplot(fig)

    def show_wordcloud(df):
        st.markdown("### Word Cloud of Comments")
        all_comments = " ".join(df['comment'])
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_comments)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

    def show_top_comments(df):
        st.markdown("### 🌟 Top Comments Summary")

        # Split comments into sentiment categories
        positive_comments = df[df['sentiment'].str.upper() == 'POSITIVE'].head(5)
        neutral_comments = df[df['sentiment'].str.upper() == 'NEUTRAL'].head(5)
        negative_comments = df[df['sentiment'].str.upper() == 'NEGATIVE'].head(5)

        def render_comment_card(comment, sentiment, score, color):
            st.markdown(f"""
            <div style="
                border: 2px solid {color};
                padding: 12px;
                border-radius: 10px;
                background-color: #fff;
                margin-bottom: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            ">
                <strong style="color: {color};">{sentiment} ({score:.2f})</strong><br>
                <span>{comment}</span>
            </div>
            """, unsafe_allow_html=True)

        #Positive Comments
        st.markdown("#### ✅ Top 5 Positive Comments")
        if positive_comments.empty:
            st.write("No positive comments found.")
        else:
            for _, row in positive_comments.iterrows():
                render_comment_card(row['comment'], row['sentiment'], row['score'], "#4CAF50")

        st.markdown("---")

        #Neutral Comments
        st.markdown("#### 😐 Top 5 Neutral Comments")
        if neutral_comments.empty:
            st.write("No neutral comments found.")
        else:
            for _, row in neutral_comments.iterrows():
                render_comment_card(row['comment'], row['sentiment'], row['score'], "#FFC107")

        st.markdown("---")

        #Negative Comments
        st.markdown("#### ❌ Top 5 Negative Comments")
        if negative_comments.empty:
            st.write("No negative comments found.")
        else:
            for _, row in negative_comments.iterrows():
                render_comment_card(row['comment'], row['sentiment'], row['score'], "#F44336")

    video_url = st.text_input("🔗 Paste YouTube Video URL:")

    if video_url:
        video_id = extract_video_id(video_url)
        if not video_id:
            st.error("❌ Invalid YouTube URL. Please try again.")
        else:
            st.success(f"✅ Detected Video ID: `{video_id}`")

            if st.button("🚀 Fetch and Analyze Comments"):
                st.toast("Please wait while we fetch the comments for your video 🚀")

                progress_bar = st.progress(0)
                status_text = st.empty()

                # Pprogress bar
                for percent in range(1, 101):
                    time.sleep(0.04) #Pizzazz
                    progress_bar.progress(percent)
                    status_text.text(f"Fetching and analyzing comments... {percent}%")
                comments, video_title = get_youtube_comments(video_id, API_KEY, max_comments=200)
                if "past_videos" not in st.session_state:
                    st.session_state.past_videos = []  # Initialize list if not present
                st.session_state.past_videos.append((video_title, video_id))
                if not comments:
                    st.error("❌ No comments found for this video.")
                else:
                    sentiments = analyze_sentiment(comments)
                    df = pd.DataFrame(sentiments)
                    st.session_state.df = df  # Store in session state
                    df.to_excel("youtube_comments.xlsx", index=False)
                    st.toast("✅ Analysis complete! Scroll down to see the results!", icon="🎉")

                    st.subheader("📊 Analysis Results")
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        show_sentiment_distribution(df)
                    with col2:
                        show_wordcloud(df)
                    st.markdown("---")
                    show_top_comments(df)
