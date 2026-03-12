This project is a full-stack Movie Recommendation Platform that lets users search for a movie and receive personalized suggestions based on content similarity. The platform combines a Python backend for machine learning logic with a React frontend for a smooth, modern user experience. 

The recommendation engine uses content-based filtering: movie metadata (genres, keywords, cast, director, and overview) is processed through TF-IDF vectorization, and cosine similarity is used to find the closest matches across a dataset of 5,000+ films. The similarity matrix is precomputed and cached at build time for fast startup.

Technologies & Stack
* Frontend: React 19, Framer Motion, CSS Variables, TMDb API
* Backend: Python, Flask, Gunicorn, pandas, scikit-learn, NumPy, RapidFuzz
* Machine Learning: TF-IDF Vectorization, Cosine Similarity, Content-Based Filtering
* Infrastructure: Azure App Service (containerized via Docker), Azure Container Registry, Vercel
* CI/CD: GitHub Actions, ACR Webhook
* Version Control: Git, GitHub

