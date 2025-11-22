from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from textblob import TextBlob
import re

app = Flask(__name__)

API_KEY = "YOUR_YOUTUBE_API_KEY"

# Extract video ID from URL
def extract_video_id(url):
    match = re.search(r"v=([^&]+)", url)
    return match.group(1) if match else None

# Fetch comments
def get_comments(video_id):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    comments = []

    result = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=20
    ).execute()

    for item in result["items"]:
        text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(text)

    return comments

# Sentiment Logic
def analyze_sentiment(comments):
    positive = 0
    negative = 0
    neutral = 0

    for c in comments:
        analysis = TextBlob(c)
        if analysis.sentiment.polarity > 0:
            positive += 1
        elif analysis.sentiment.polarity < 0:
            negative += 1
        else:
            neutral += 1

    # Final result
    if positive > negative:
        return "Positive"
    elif negative > positive:
        return "Negative"
    else:
        return "Neutral"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    url = data["url"]

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube link"}), 400

    comments = get_comments(video_id)
    sentiment = analyze_sentiment(comments)

    return jsonify({"sentiment": sentiment})

if __name__ == "__main__":
    app.run(debug=True)