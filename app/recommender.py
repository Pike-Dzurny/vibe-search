import pickle
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SongRecommender:
    def __init__(self, embeddings_path: str = "data/embeddings.pkl"):
        with open(embeddings_path, "rb") as f:
            data = pickle.load(f)
        
        self.song_names: list[str] = data["names"]
        self.embeddings: np.ndarray = data["embeddings"]
        
        # precompute all pairwise similarities (75x75 matrix, tiny)
        self.similarity_matrix = cosine_similarity(self.embeddings)
        
        # create lookup from name to index
        self.name_to_idx = {name.lower(): idx for idx, name in enumerate(self.song_names)}
    
    def list_songs(self) -> list[str]:
        """return all available songs"""
        return self.song_names.copy()
    
    def find_song(self, query: str) -> tuple[int, str] | None:
        """fuzzy match a song name, return (index, actual_name) or None"""
        query_lower = query.lower()
        
        # exact match first
        if query_lower in self.name_to_idx:
            idx = self.name_to_idx[query_lower]
            return idx, self.song_names[idx]
        
        # partial match
        for idx, name in enumerate(self.song_names):
            if query_lower in name.lower():
                return idx, name
        
        return None
    
    def recommend(self, song_query: str, top_k: int = 5) -> dict:
        """
        find similar songs to the given query.
        returns dict with matched song and recommendations.
        """
        match = self.find_song(song_query)
        
        if match is None:
            return {
                "matched": None,
                "recommendations": [],
                "error": f"no song found matching '{song_query}'"
            }
        
        idx, matched_name = match
        
        # get similarity scores for this song
        similarities = self.similarity_matrix[idx]
        
        # get top_k+1 (because the song itself will be #1)
        top_indices = np.argsort(similarities)[::-1][:top_k + 1]
        
        recommendations = []
        for i in top_indices:
            if i == idx:  # skip the query song itself
                continue
            recommendations.append({
                "song": self.song_names[i],
                "similarity": float(similarities[i])
            })
        
        return {
            "matched": matched_name,
            "recommendations": recommendations[:top_k]
        }