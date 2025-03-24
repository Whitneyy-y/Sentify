# .\venv\Scripts\activate

import requests #Used for sending HTTP requests which will be used for fetching the comments.
import pandas as pd #Used in handling data in a tabular form
import re #Used in removing the punctuations in comments.
import nltk #Used for natural language processing
from nltk.corpus import stopwords #Removes words that do not add extra meaning
from nltk.tokenize import word_tokenize #Used for splitting words into individual words.
from nltk.stem import WordNetLemmatizer #Reduces words to their root form.
from transformers import pipeline
from dotenv import load_dotenv
import os
import time  # For adding delays in progress messages
import streamlit as st

load_dotenv()  # Load environment variables from .env file
API_KEY = st.secret["API_KEY"]
if API_KEY is None:
    raise ValueError("API Key not found! Make sure it's set in the .env file.")


# Set up Hugging Face DistilBERT for sentiment analysis
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# NLTK resources needed for cleaning comments
nltk.download("stopwords") # Downloads a list of stopwords.
nltk.download("punkt") #Downloads the tokenizer for breaking text into words.
nltk.download("wordnet") #Downloads the WordNet dataset for lemmatization. Wordnet is a database that is used for understanding words better.

# Initialize stopwords and lemmatizer
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

# Function to clean comments
def clean_comment(comment):
    comment = re.sub(r"[^\w\s]", "", comment)  # Remove punctuation
    comment = comment.lower()  # Convert to lowercase
    words = word_tokenize(comment)  # Tokenize
    words = [word for word in words if word not in stop_words]  # Remove stopwords
    words = [lemmatizer.lemmatize(word) for word in words]  # Lemmatize words
    return " ".join(words)  # Join words back into a sentence


def get_youtube_comments(video_id, api_key, max_comments=200):
    #Fetch Video Title
    video_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}"
    response = requests.get(video_url).json()
    
    if "items" in response and response["items"]:
        video_title = response["items"][0]["snippet"]["title"]
    else:
        video_title = "Unknown Title"

    #Fetch Comments
    comments = []
    next_page_token = None
    url = "https://www.googleapis.com/youtube/v3/commentThreads"  # YouTube API URL

    while len(comments) < max_comments:
        # Prepare API request
        params = {
            "part": "snippet",
            "videoId": video_id,
            "key": api_key,
            "maxResults": min(100, max_comments - len(comments)),  # Fetch up to 100 per request
            "pageToken": next_page_token,  # Handle pagination
        }

        response = requests.get(url, params=params)  # Send request

        if response.status_code != 200:
            error_data = response.json()
            if "error" in error_data and error_data["error"]["code"] == 403:
                st.error("❌ Number of comments acceptable has been exceeded. Please try again later.")
            else:
                st.error(f"❌ An error occurred: {error_data['error']['message']}")
            return []  # Return an empty list so Streamlit doesn't break
        data = response.json()

        # Extract and clean comments
        for item in data.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            cleaned_comment = clean_comment(comment)  # Clean the comment
            comments.append(cleaned_comment)
            if len(comments) >= max_comments:
                break  # Stop when max comments are reached

        # Check for nextPageToken (pagination)
        next_page_token = data.get("nextPageToken", None)
        if not next_page_token:
            break  # Stop if no more comments

    return comments, video_title  # Return both comments and video title


# Function for analyzing sentiment
def analyze_sentiment(comments):
    print("\n🔍 Analyzing sentiment... (this may take a few seconds)")
    time.sleep(1)  # Small delay for better UX
    results = []

    for comment in comments:
        result = sentiment_analyzer(comment)[0]  # Get sentiment result
        label = result["label"]
        score = result["score"]

        # If confidence is below 0.8, classify as neutral
        if score < 0.80:
            label = "Neutral"

        results.append({"comment": comment, "sentiment": label, "score": score})

    print("✅ Sentiment analysis completed!")
    return results


def excel_comments(comments, sentiments, filename="youtube_comments.xlsx"):
    df = pd.DataFrame({
        "Comment": comments,
        "Sentiment": [s["sentiment"] for s in sentiments],  # Fix KeyError
        "Confidence Score": [s["score"] for s in sentiments]
    })
    df.to_excel(filename, index=False, engine="openpyxl")