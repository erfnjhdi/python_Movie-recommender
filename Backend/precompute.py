"""Run during Docker build to precompute and cache the similarity matrix."""
from recommender import load_data, compute_similarity

print("Precomputing similarity matrix...")
df = load_data()
compute_similarity(df)
print("Similarity matrix cached to data/similarity_cache.npy")
