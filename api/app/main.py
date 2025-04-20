import base64
import io
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import numpy as np
from PIL import Image

from models.image_processor import WhiskyBottleProcessor
from utils.database import BottleDatabase

app = FastAPI(
    title="Whisky Bottle Recognition API",
    description="API for identifying whisky bottles using computer vision",
    version="1.0.0"
)

# Configure CORS for mobile app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models on startup
bottle_processor = None
bottle_db = None

@app.on_event("startup")
async def startup_event():
    global bottle_processor, bottle_db
    # Initialize image processor with CLIP model
    bottle_processor = WhiskyBottleProcessor()
    # Initialize vector database
    bottle_db = BottleDatabase()
    # Load precomputed bottle embeddings
    bottle_db.load_embeddings()

class BottleMatch(BaseModel):
    id: str
    name: str
    confidence: float
    image_url: Optional[str] = None

class BottleResponse(BaseModel):
    matches: List[BottleMatch]
    processing_time_ms: float

@app.get("/")
async def root():
    return {"message": "Whisky Bottle Recognition API"}

@app.post("/api/identify", response_model=BottleResponse)
async def identify_bottle(file: UploadFile = File(...)):
    """
    Identify a whisky bottle from an uploaded image.
    Returns top matches with confidence scores.
    """
    start_time = datetime.now()
    
    try:
        # Read and validate image file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Extract features using CLIP model
        features = bottle_processor.extract_features(image)
        
        # Find matching bottles in the database
        matches = bottle_db.find_matches(features, top_k=3)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return BottleResponse(
            matches=matches,
            processing_time_ms=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/identify_base64")
async def identify_bottle_base64(base64_image: str = Body(..., embed=True)):
    """
    Identify a whisky bottle from a base64-encoded image.
    Useful for direct integration with React Native.
    """
    start_time = datetime.now()
    
    try:
        # Decode base64 image
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))
        
        # Extract features using CLIP model
        features = bottle_processor.extract_features(image)
        
        # Find matching bottles in the database
        matches = bottle_db.find_matches(features, top_k=3)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return BottleResponse(
            matches=matches,
            processing_time_ms=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bottles", response_model=List[BottleMatch])
async def list_bottles():
    """List all bottles in the database."""
    try:
        return bottle_db.list_all_bottles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 