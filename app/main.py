from fastapi import FastAPI
from pydantic import BaseModel
from app.recommender import SongRecommender

app = FastAPI(
    title="vibe-search",
    description="song recommendation via clap embeddings"
)

# load once at startup
recommender = SongRecommender()

class RecommendRequest(BaseModel):
    song: str
    top_k: int = 5

class SongResult(BaseModel):
    song: str
    similarity: float

class RecommendResponse(BaseModel):
    matched: str | None
    recommendations: list[SongResult]
    error: str | None = None

@app.get("/health")
def health():
    return {
        "status": "ok",
        "songs_loaded": len(recommender.song_names)
    }

@app.get("/songs")
def list_songs():
    """list all available songs in the corpus"""
    return {"songs": recommender.list_songs()}

@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    """get song recommendations based on a query song"""
    result = recommender.recommend(req.song, req.top_k)
    return result