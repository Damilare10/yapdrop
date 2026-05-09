import os
import re
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def generate_reply(tweet_text, tone="professional"):
    """
    Generates a reply to a tweet using Groq.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY not found in environment"

    try:
        client = Groq(api_key=api_key)
        
        prompt = f"""
        You are replying to this tweet: "{tweet_text}"

        Rules:
        - ONE sentence only. Max 100 characters.
        - Sound like a real person texting, not writing an essay.
        - No hashtags, no quotes, no markdown, no emojis unless natural.
        - Be casual, witty, or punchy. No generic fillers.

        OUTPUT ONLY THE REPLY. NOTHING ELSE.
        """
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
        )

        reply = completion.choices[0].message.content.strip()
        
        # Clean up
        reply = re.sub(r'<[^>]+>', '', reply)
        reply = re.sub(r'\*\*.*?\*\*', '', reply)
        reply = re.sub(r'\*.*?\*', '', reply)
        
        return reply
    except Exception as e:
        return f"Error: {e}"

def generate_batch_replies(tweets_data: list[dict], tone="professional") -> list[dict]:
    """
    Generates replies for a batch of tweets.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return [{"id": t['id'], "reply": "Error: GROQ_API_KEY missing"} for t in tweets_data]

    try:
        client = Groq(api_key=api_key)
        tweets_json_str = json.dumps(tweets_data, indent=2)
        
        prompt = f"""
        Reply to each of these {len(tweets_data)} tweets.

        {tweets_json_str}

        Rules:
        - ONE sentence per reply. Max 100 characters.
        - Sound like a real person, casual and direct.
        - No hashtags, no quotes, no markdown.
        - Return ONLY a JSON array: [ {{"id": "...", "reply": "..."}} ]
        - NO extra text, NO explanation.
        """

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        response_text = completion.choices[0].message.content.strip()
        
        # Extract JSON
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            response_text = json_match.group(0)
        
        replies_data = json.loads(response_text)
        return replies_data
    except Exception as e:
        # Fallback to individual generation
        results = []
        for tweet in tweets_data:
            reply = generate_reply(tweet['text'], tone)
            results.append({"id": tweet['id'], "reply": reply})
        return results
