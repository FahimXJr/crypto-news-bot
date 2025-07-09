import requests
import feedparser
import os
import time
from transformers import pipeline

BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHANNEL = os.environ["CHANNEL_NAME"]

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
posted_links = set()

def get_news():
    feed = feedparser.parse("https://cointelegraph.com/rss")
    return feed.entries[:1]

def summarize(text):
    if len(text) > 1000:
        text = text[:1000]
    summary = summarizer(text, max_length=80, min_length=25, do_sample=False)
    return summary[0]['summary_text']

def post_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHANNEL, "text": message, "parse_mode": "Markdown"}
    return requests.post(url, data=data).status_code == 200

def run_bot():
    while True:
        news = get_news()
        for item in news:
            if item.link not in posted_links:
                summary = summarize(item.summary)
                message = f"*{item.title}*\n\n{summary}\n\n[Read More]({item.link})"
                if post_to_telegram(message):
                    posted_links.add(item.link)
        time.sleep(60 * 60 * 3)

run_bot()
