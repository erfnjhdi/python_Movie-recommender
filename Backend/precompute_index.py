import os
import pickle
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from annoy import AnnoyIndex
import pandas as pd
from recommender import load_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def precompute_index(output_dir='precomputed'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

    logger.info("Loading data...")
    df = load_data()

    logger.info("Computing TF-IDF embeddings...")
    tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = tfidf.fit_transform(df['tags'])
    embeddings = tfidf_matrix.toarray()

    logger.info(f"Building Annoy index with {len(embeddings)} items...")
    vector_dim = embeddings.shape[1]
    annoy_index = AnnoyIndex(vector_dim, metric='angular')

    for i, embedding in enumerate(embeddings):
        annoy_index.add_item(i, embedding)
        if (i + 1) % 1000 == 0:
            logger.info(f"Processed {i + 1} items")

    annoy_index.build(10)

    logger.info("Saving artifacts...")
    annoy_path = os.path.join(output_dir, 'movies.annoy')
    annoy_index.save(annoy_path)
    logger.info(f"Saved Annoy index to {annoy_path}")

    vectorizer_path = os.path.join(output_dir, 'vectorizer.pkl')
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(tfidf, f)
    logger.info(f"Saved vectorizer to {vectorizer_path}")

    movie_index_path = os.path.join(output_dir, 'movie_index.pkl')
    movie_index = df[['title', 'vote_average', 'vote_count', 'release_date']].reset_index(drop=True)
    with open(movie_index_path, 'wb') as f:
        pickle.dump(movie_index, f)
    logger.info(f"Saved movie index to {movie_index_path}")

    embeddings_path = os.path.join(output_dir, 'embeddings.npy')
    np.save(embeddings_path, embeddings)
    logger.info(f"Saved embeddings to {embeddings_path}")

    logger.info("Precomputation completed successfully")

if __name__ == "__main__":
    precompute_index()
