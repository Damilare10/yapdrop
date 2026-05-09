import re

def extract_tweet_id(url: str) -> str:
    """
    Extract tweet ID from various input formats.
    """
    # 1. Check for standard status URL
    status_match = re.search(r'/status/(\d+)', url)
    if status_match:
        return status_match.group(1)
        
    # 2. Check for intent URL (in_reply_to parameter)
    intent_match = re.search(r'in_reply_to=(\d+)', url)
    if intent_match:
        return intent_match.group(1)

    # 3. Check for intent URL (tweet_id parameter)
    tweet_id_match = re.search(r'tweet_id=(\d+)', url)
    if tweet_id_match:
        return tweet_id_match.group(1)
        
    # 4. Check if the input is just a raw ID
    if re.match(r'^\d{15,20}$', url.strip()):
        return url.strip()
        
    raise ValueError(f"Could not extract Tweet ID from: {url}")
