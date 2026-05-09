import requests
import logging

logger = logging.getLogger(__name__)

def get_tweet_text(tweet_url: str) -> str:
    """
    Fetch a single tweet's text using vxtwitter (Free Webhook version).
    """
    if "x.com" in tweet_url:
        api_url = tweet_url.replace("x.com", "api.vxtwitter.com")
    elif "twitter.com" in tweet_url:
        api_url = tweet_url.replace("twitter.com", "api.vxtwitter.com")
    else:
        # If it's just an ID
        api_url = f"https://api.vxtwitter.com/status/{tweet_url}"

    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            tweet_data = response.json()
            tweet_text = tweet_data.get("text")
            author_handle = tweet_data.get("user_screen_name")

            if tweet_text and author_handle:
                return f"@{author_handle} | {tweet_text}"
        
        return f"Error: Scraping failed ({response.status_code})"
    except Exception as e:
        return f"Error: Request failed: {e}"
