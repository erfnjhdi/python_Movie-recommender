import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender import load_data, compute_similarity, get_recommendations, get_movie_by_fuzzy_match

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

df = load_data()
similarity = compute_similarity(df)

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request body"}), 400

        title = data.get("title", "").strip()
        if not title:
            return jsonify({"error": "Title parameter is required"}), 400

        if len(title) > 200:
            return jsonify({"error": "Title parameter exceeds maximum length"}), 400

        filters = data.get("filters", {})
        sort_by = data.get("sort_by", "similarity")

        recs = get_recommendations(title=title, df=df, similarity_matrix=similarity, filters=filters, sort_by=sort_by)

        if not recs:
            idx = get_movie_by_fuzzy_match(title, df, threshold=60)
            if idx is not None:
                movie_genres = df.iloc[idx]['genres']
                if movie_genres:
                    main_genre = movie_genres.split()[0]
                    fallback_recs = (
                        df[df['genres'].str.contains(main_genre, case=False)]
                        .sort_values(by=['vote_average', 'vote_count'], ascending=False)
                        .head(10)['title']
                        .tolist()
                    )
                    if fallback_recs:
                        logger.info(f"Fallback recommendation used for: {title}")
                        recs = fallback_recs

        return jsonify({"recommendations": recs})

    except Exception as e:
        logger.error(f"Error processing recommendation request: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/search", methods=["GET"])
def search():
    try:
        query = request.args.get("q", "").strip().lower()
        if not query:
            return jsonify({"results": []}), 200

        if len(query) > 200:
            return jsonify({"error": "Query exceeds maximum length"}), 400

        matches = df[df['title'].str.lower().str.contains(query, na=False)]['title'].tolist()
        return jsonify({"results": matches[:10]})

    except Exception as e:
        logger.error(f"Error processing search request: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
