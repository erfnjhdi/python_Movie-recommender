from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender import load_data, compute_similarity, get_recommendations, normalize_title

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Load data and precompute similarity once
df = load_data()
similarity = compute_similarity(df)

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    title = data.get("title", "")
    filters = data.get("filters", {})

    recs = get_recommendations(title=title, df=df, similarity_matrix=similarity, filters=filters)

    # Fallback: if no recommendations found, use top-rated movies in the same genre
    if not recs:
        print(f"No recommendations found for '{title}'. Using fallback...")

        # Get a partial match using first 2 words from the input title
        partial_title = " ".join(normalize_title(title).split()[:2])
        movie_row = df[df['title'].apply(normalize_title).str.contains(partial_title)]

        movie_row = df[df['title'].str.lower().str.contains(partial_title)]
        if not movie_row.empty:
            movie_genres = movie_row.iloc[0]['genres']
            print("Fallback using genre from:", movie_row.iloc[0]['title'])
            if movie_genres:
                main_genre = movie_genres.split()[0]
                fallback_recs = (
                    df[df['genres'].str.contains(main_genre, case=False)]
                    .sort_values(by=['vote_average', 'vote_count'], ascending=False)
                    .head(10)['title']
                    .tolist()
                )
                recs = fallback_recs

    return jsonify({"recommendations": recs})

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").lower()
    matches = df[df['title'].str.lower().str.contains(query)]['title'].tolist()
    return jsonify({"results": matches[:10]})  # return top 10 matches

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
