from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict
import ai_agent
import uvicorn
import os

# Path to the frontend folder (one level up from backend/)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TweetItem(BaseModel):
    id: str # This is the URL or ID
    text: str # Scraped text

class GenerationRequest(BaseModel):
    tweets: List[TweetItem]
    tone: str = "professional"

# Serve static assets (style.css, script.js, etc.)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.post("/api/generate-replies")
async def generate_replies(req: GenerationRequest):
    if not req.tweets:
        return {"results": []}

    results = []
    
    # Map for AI agent
    ai_input = [{"id": t.id, "text": t.text} for t in req.tweets]

    try:
        replies = ai_agent.generate_batch_replies(ai_input, tone=req.tone)
        
        # Map replies back
        reply_map = {r['id']: r['reply'] for r in replies if 'id' in r and 'reply' in r}
        
        for tweet in req.tweets:
            reply = reply_map.get(tweet.id, "Error generating reply")
            results.append({
                "id": tweet.id,
                "reply": reply,
                "status": "success"
            })
    except Exception as e:
        for tweet in req.tweets:
            results.append({
                "id": tweet.id,
                "reply": f"Error: {e}",
                "status": "error"
            })

    return {"results": results}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
