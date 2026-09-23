from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

from backend.recommender import RecommenderSystem

app = FastAPI(title="Intelligent Product Recommendation API")

# Initialize the recommender system
# Adjust path to models if running from root directory
models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
recommender = RecommenderSystem(models_dir=models_dir)

class RecommendRequest(BaseModel):
    products: List[str]
    min_confidence: Optional[float] = 0.0
    min_lift: Optional[float] = 0.0

@app.get("/health")
def health_check():
    return {"status": "healthy", "models_loaded": recommender.rules is not None}

@app.get("/products")
def get_products():
    return {"products": recommender.get_products()}

@app.post("/recommend")
def recommend(req: RecommendRequest):
    if not req.products:
        raise HTTPException(status_code=400, detail="Must provide at least one product")
        
    # We use the same method for single and multiple products
    recs = recommender.recommend(
        selected_products=req.products,
        min_confidence=req.min_confidence,
        min_lift=req.min_lift
    )
    return {"recommendations": recs}

@app.post("/recommend-multiple")
def recommend_multiple(req: RecommendRequest):
    if not req.products:
        raise HTTPException(status_code=400, detail="Must provide at least one product")
        
    recs = recommender.recommend(
        selected_products=req.products,
        min_confidence=req.min_confidence,
        min_lift=req.min_lift
    )
    return {"recommendations": recs}

@app.get("/rules")
def get_rules():
    return {"rules": recommender.get_all_rules()}

@app.get("/analytics")
def get_analytics():
    return recommender.get_analytics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
