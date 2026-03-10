import pandas as pd
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz
import re

def normalize_title(title):
    return re.sub(r'[^\w\s]', '', title.lower()).strip()

def get_movie_by_fuzzy_match(query, df, threshold=80):
    normalized_query = normalize_title(query)
    best_match = None
    best_score = threshold

    for idx, row in df.iterrows():
        normalized_title = normalize_title(row['title'])
        score = fuzz.token_sort_ratio(normalized_query, normalized_title)
        if score > best_score:
            best_score = score
            best_match = idx

    return best_match

def load_data(path='data/movies.csv', credits_path='data/credits.csv'):
    df = pd.read_csv(path)
    df = df[['title', 'overview', 'genres', 'keywords', 'original_language',
             'release_date', 'vote_average', 'vote_count']].dropna()

    df['genres'] = df['genres'].apply(lambda x: " ".join([i['name'] for i in ast.literal_eval(x)]))
    df['keywords'] = df['keywords'].apply(lambda x: " ".join([i['name'] for i in ast.literal_eval(x)]))

    try:
        credits = pd.read_csv(credits_path)
        if 'cast' in credits.columns:
            credits['cast_names'] = credits['cast'].apply(lambda x: extract_cast_names(x, top_n=3))
        if 'crew' in credits.columns:
            credits['director'] = credits['crew'].apply(extract_director)

        credits = credits[['title', 'cast_names', 'director']].drop_duplicates(subset=['title'], keep='first')
        df = df.merge(credits, on='title', how='left')
        df['cast_names'] = df.get('cast_names', '').fillna('')
        df['director'] = df.get('director', '').fillna('')
    except Exception:
        df['cast_names'] = ''
        df['director'] = ''

    df['tags'] = df['overview'] + " " + df['genres'] + " " + df['keywords'] + " " + df.get('cast_names', '') + " " + df.get('director', '')
    df['tags'] = df['tags'].str.lower()
    return df

def extract_cast_names(cast_str, top_n=3):
    try:
        cast_list = ast.literal_eval(cast_str) if isinstance(cast_str, str) else []
        names = [actor['name'] for actor in cast_list[:top_n]]
        return " ".join(names)
    except Exception:
        return ""

def extract_director(crew_str):
    try:
        crew_list = ast.literal_eval(crew_str) if isinstance(crew_str, str) else []
        for crew_member in crew_list:
            if crew_member.get('job') == 'Director':
                return crew_member['name']
    except Exception:
        pass
    return ""

def compute_similarity(df):
    tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = tfidf.fit_transform(df['tags'])
    return cosine_similarity(tfidf_matrix)

def get_recommendations(title, df, similarity_matrix, top_n=30, filters=None, sort_by='similarity', title_weight=0.3):
    idx = get_movie_by_fuzzy_match(title, df)
    if idx is None:
        return []

    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    recs = df.iloc[[i[0] for i in sim_scores]].copy()
    recs['_similarity_score'] = [i[1] for i in sim_scores]

    original_title = df.iloc[idx]['title']
    recs['_title_similarity'] = recs['title'].apply(
        lambda x: fuzz.token_sort_ratio(original_title.lower(), x.lower()) / 100.0
    )

    recs['_combined_score'] = (recs['_similarity_score'] * (1 - title_weight)) + (recs['_title_similarity'] * title_weight)

    if filters:
        if "genres" in filters:
            recs = recs[recs['genres'].str.contains(filters["genres"], case=False)]

        if "language" in filters:
            recs = recs[recs['original_language'] == filters["language"]]

        if "min_year" in filters:
            try:
                min_year = int(filters["min_year"])
                recs = recs[recs['release_date'].str[:4].astype(int) >= min_year]
            except Exception:
                pass

        if "max_year" in filters:
            try:
                max_year = int(filters["max_year"])
                recs = recs[recs['release_date'].str[:4].astype(int) <= max_year]
            except Exception:
                pass

        if "min_rating" in filters:
            try:
                recs = recs[recs['vote_average'] >= float(filters["min_rating"])]
            except Exception:
                pass

        if "min_votes" in filters:
            try:
                recs = recs[recs['vote_count'] >= int(filters["min_votes"])]
            except Exception:
                pass

    if sort_by == 'rating':
        recs = recs.sort_values('vote_average', ascending=False)
    elif sort_by == 'votes':
        recs = recs.sort_values('vote_count', ascending=False)
    elif sort_by == 'release_date':
        recs = recs.sort_values('release_date', ascending=False)
    else:
        recs = recs.sort_values('_combined_score', ascending=False)

    return recs['title'].head(10).tolist()

