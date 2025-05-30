import pandas as pd
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def normalize_title(title):
    return re.sub(r'[^\w\s]', '', title.lower()).strip()

def load_data(path='data/movies.csv'):
    df = pd.read_csv(path)
    df = df[['title', 'overview', 'genres', 'keywords', 'original_language',
             'release_date', 'vote_average', 'vote_count']].dropna()

    # Convert genres and keywords from string to list
    df['genres'] = df['genres'].apply(lambda x: " ".join([i['name'] for i in ast.literal_eval(x)]))
    df['keywords'] = df['keywords'].apply(lambda x: " ".join([i['name'] for i in ast.literal_eval(x)]))

    # Create a new 'tags' column by combining overview + genres + keywords
    df['tags'] = df['overview'] + " " + df['genres'] + " " + df['keywords']
    df['tags'] = df['tags'].str.lower()
    return df


def compute_similarity(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['tags'])
    return cosine_similarity(tfidf_matrix)

def get_recommendations(title, df, similarity_matrix, top_n=30, filters=None):
    title = normalize_title(title)

    matches = df[df['title'].apply(normalize_title).str.contains(title)]
    if matches.empty:
        print(f"No title match for: {title}")
        return []

    idx = matches.index[0]
    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]

    recs = df.iloc[[i[0] for i in sim_scores]].copy()

    # Apply filters if provided
    if filters:
        if "genres" in filters:
            recs = recs[recs['genres'].str.contains(filters["genres"], case=False)]

        if "language" in filters:
            recs = recs[recs['original_language'] == filters["language"]]

        if "min_year" in filters:
            recs = recs[recs['release_date'].str[:4].astype(int) >= filters["min_year"]]

        if "max_year" in filters:
            recs = recs[recs['release_date'].str[:4].astype(int) <= filters["max_year"]]

        if "min_rating" in filters:
            recs = recs[recs['vote_average'] >= filters["min_rating"]]

        if "min_votes" in filters:
            recs = recs[recs['vote_count'] >= filters["min_votes"]]
    return recs['title'].head(10).tolist()

