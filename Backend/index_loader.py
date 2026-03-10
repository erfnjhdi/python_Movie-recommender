import os
import pickle
import logging
import numpy as np
from annoy import AnnoyIndex

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IndexLoader:
    def __init__(self, index_dir="precomputed"):
        self.index_dir = index_dir
        self.annoy_index = None
        self.vectorizer = None
        self.movie_index = None
        self.embeddings = None
        self.is_loaded = False
        self._load_index()

    def _load_index(self):
        try:
            vectorizer_path = os.path.join(self.index_dir, "vectorizer.pkl")
            if os.path.exists(vectorizer_path):
                with open(vectorizer_path, "rb") as f:
                    self.vectorizer = pickle.load(f)

            movie_index_path = os.path.join(self.index_dir, "movie_index.pkl")
            if os.path.exists(movie_index_path):
                with open(movie_index_path, "rb") as f:
                    self.movie_index = pickle.load(f)

            annoy_path = os.path.join(self.index_dir, "movies.annoy")
            embeddings_path = os.path.join(self.index_dir, "embeddings.npy")

            if os.path.exists(annoy_path) and os.path.exists(embeddings_path):
                self.embeddings = np.load(embeddings_path)
                vector_dim = self.embeddings.shape[1]
                self.annoy_index = AnnoyIndex(vector_dim, metric="angular")
                self.annoy_index.load(annoy_path)
                self.is_loaded = True
                logger.info("Index loaded successfully")
            else:
                logger.warning("Index files not found")
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")

    def get_similar_movies(self, movie_idx, top_n=50):
        if not self.is_loaded or self.annoy_index is None:
            logger.warning("Index not loaded")
            return []

        try:
            if movie_idx < 0 or movie_idx >= len(self.movie_index):
                return []

            neighbors = self.annoy_index.get_nns_by_item(movie_idx, top_n + 1)
            return [n for n in neighbors if n != movie_idx][:top_n]
        except Exception as e:
            logger.error(f"Error getting similar movies: {str(e)}")
            return []

    def get_movies_by_indices(self, indices):
        if self.movie_index is None:
            return []

        try:
            result = []
            for idx in indices:
                if 0 <= idx < len(self.movie_index):
                    row = self.movie_index.iloc[idx]
                    result.append(
                        {
                            "index": idx,
                            "title": row["title"],
                            "vote_average": row["vote_average"],
                            "vote_count": row["vote_count"],
                            "release_date": row["release_date"],
                        }
                    )
            return result
        except Exception as e:
            logger.error(f"Error retrieving movies: {str(e)}")
            return []
