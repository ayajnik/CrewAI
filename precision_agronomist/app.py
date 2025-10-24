#!/usr/bin/env python3
"""
FastAPI application for Precision Agronomist
Deploy this to any cloud platform (Railway, Render, Heroku, etc.)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime

# Import your crew functions
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from precision_agronomist.main import detect_diseases_api, chatbot_api, trends_api

app = FastAPI(
    title="Precision Agronomist API",
    description="AI-powered plant disease detection system",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class DetectionRequest(BaseModel):
    num_images: int = 5
    detection_threshold: float = 0.25
    preferred_language: str = "en"

class ChatbotRequest(BaseModel):
    question: str
    language: str = "en"

class TrendsRequest(BaseModel):
    days: int = 30

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Precision Agronomist API",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Disease detection endpoint
@app.post("/detect")
async def detect_diseases(request: DetectionRequest):
    """Detect plant diseases in images"""
    try:
        result = detect_diseases_api(
            num_images=request.num_images,
            detection_threshold=request.detection_threshold,
            preferred_language=request.preferred_language
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chatbot endpoint
@app.post("/chatbot")
async def chatbot(request: ChatbotRequest):
    """Ask the agricultural advisor chatbot"""
    try:
        result = chatbot_api(
            question=request.question,
            language=request.language
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trends analysis endpoint
@app.get("/trends")
async def trends(days: int = 30):
    """Get disease trend analysis"""
    try:
        result = trends_api(days=days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/info")
async def api_info():
    """API information"""
    return {
        "name": "Precision Agronomist API",
        "description": "AI-powered plant disease detection system",
        "endpoints": [
            "POST /detect - Disease detection",
            "POST /chatbot - Agricultural advisor",
            "GET /trends - Trend analysis",
            "GET /health - Health check"
        ],
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
