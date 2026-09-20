from flask import Flask, jsonify, request, render_template, send_from_directory
from data import generate_news
from recommendation_engine import NewsRecommender
from live_india import fetch_india_live

app = Flask(__name__)

articles = generate_news()
recommender = NewsRecommender(articles)

CATEGORIES = ["All", "Technology", "Sports", "Business", "Science", "Health", "Politics", "Entertainment"]
INDIA_CATEGORIES = ["All", "Politics", "Business", "Sports", "Technology", "Entertainment", "Science", "Health"]

@app.route("/")
def index():
    return render_template("index.html", categories=[c for c in CATEGORIES if c != "All"])

@app.route("/api/news")
def api_news():
    category = request.args.get("category", "All")
    search = request.args.get("search", "")
    sort = request.args.get("sort", "latest")
    results = recommender.search(search, category)
    if sort == "popular":
        results = sorted(results, key=lambda x: x.get("popularity", 0), reverse=True)
    elif sort == "latest":
        results = sorted(results, key=lambda x: x.get("publishedAt", ""), reverse=True)
    return jsonify(results)

@app.route("/api/trending")
def api_trending():
    return jsonify(recommender.trending(8))

@app.route("/api/recommend")
def api_recommend():
    user_id = request.args.get("user_id", "default_user")
    n = int(request.args.get("n", 12))
    recs = recommender.recommend(user_id, n=n)
    return jsonify(recs)

@app.route("/api/preferences", methods=["POST", "GET"])
def api_preferences():
    user_id = request.args.get("user_id", "default_user")
    if request.method == "GET":
        user = recommender.get_or_create_user(user_id)
        return jsonify({
            "preferences": user["preferences"],
            "liked": user["liked"],
            "disliked": user["disliked"],
            "bookmarked": user["bookmarked"],
            "history": user["history"]
        })
    data = request.get_json() or {}
    # Support both {categories: []} and {preferences: {}}
    cats = data.get("categories") or data.get("preferences") or []
    if isinstance(cats, dict):
        cats = [k for k, v in cats.items() if v]
    user = recommender.update_preferences(user_id, cats)
    return jsonify({"status": "ok", "preferences": user["preferences"]})

@app.route("/api/interact", methods=["POST"])
def api_interact():
    data = request.get_json() or {}
    user_id = data.get("user_id", "default_user")
    article_id = data.get("article_id")
    action = data.get("action")  # like, dislike, bookmark, view, unbookmark
    if not article_id or not action:
        return jsonify({"error": "article_id and action required"}), 400
    aid = int(article_id)
    # Handle India Live IDs (>=1000) - local bookmark/history without TF-IDF
    if aid >= 1000:
        user = recommender.get_or_create_user(user_id)
        if action == 'bookmark':
            if aid not in user['bookmarked']:
                user['bookmarked'].append(aid)
            else:
                user['bookmarked'].remove(aid)
        elif action == 'unbookmark':
            if aid in user['bookmarked']:
                user['bookmarked'].remove(aid)
        elif action == 'like':
            if aid not in user['liked']:
                user['liked'].append(aid)
        elif action == 'dislike':
            if aid not in user['disliked']:
                user['disliked'].append(aid)
        elif action == 'view':
            if aid not in user['history']:
                user['history'].append(aid)
                user['history'] = user['history'][-50:]
        return jsonify({"status": "ok", "user": {
            "liked": user["liked"],
            "disliked": user["disliked"],
            "bookmarked": user["bookmarked"],
            "history": user["history"],
            "preferences": user["preferences"]
        }})
    user = recommender.record_interaction(user_id, aid, action)
    if user is None:
        return jsonify({"error": "article not found"}), 404
    return jsonify({"status": "ok", "user": {
        "liked": user["liked"],
        "disliked": user["disliked"],
        "bookmarked": user["bookmarked"],
        "history": user["history"],
        "preferences": user["preferences"]
    }})

@app.route("/api/user/<user_id>")
def api_user(user_id):
    user = recommender.get_or_create_user(user_id)
    return jsonify({
        "preferences": user["preferences"],
        "liked": user["liked"],
        "disliked": user["disliked"],
        "bookmarked": user["bookmarked"],
        "history": user["history"]
    })

@app.route("/api/india-live")
def api_india_live():
    category = request.args.get("category", "All")
    search = request.args.get("search", "")
    force = request.args.get("force", "0") == "1"
    live = fetch_india_live(force=force)
    # filter category/search
    filtered = []
    q = search.lower().strip()
    for a in live:
        if category != "All" and a["category"] != category:
            continue
        if q and q not in (a["title"] + " " + a["content"] + " " + a["category"]).lower():
            continue
        filtered.append(a)
    return jsonify(filtered)

@app.route("/api/india-recommend")
def api_india_recommend():
    user_id = request.args.get("user_id", "default_user")
    n = int(request.args.get("n", 12))
    # Score live articles against user profile without retraining vectorizer
    # Use recommender's vectorizer + profile_vector for ranking if available
    live = fetch_india_live()
    user = recommender.get_or_create_user(user_id)
    profile = user.get("profile_vector")
    scored = []
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    for a in live:
        # vectorize title+content
        try:
            vec = recommender.vectorizer.transform([f"{a['title']} {a['category']} {a['content']}"])
            sim = cosine_similarity([profile], vec)[0][0] if profile is not None else 0.0
        except Exception:
            sim = 0.0
        cat_pref = user.get("preferences", {}).get(a["category"], 0.5 if not user.get("preferences") else 0.0)
        # recency
        try:
            pub = datetime.fromisoformat(a["publishedAt"].replace("Z","+00:00"))
            hours_ago = (now - pub).total_seconds()/3600
            recency = max(0, 1 - hours_ago/48)
        except:
            recency = 0.7
        popularity = a.get("popularity", 80)/100
        if profile is None:
            score = 0.4*cat_pref + 0.3*recency + 0.3*popularity
        else:
            score = 0.55*sim + 0.25*cat_pref + 0.12*recency + 0.08*popularity
        reason = f"Live • {a['category']}"
        if profile is not None and sim > 0.12:
            reason = f"Live • Similar to your taste"
        elif cat_pref >= 0.9:
            reason = f"Live • Because you like {a['category']}"
        art = dict(a)
        art["recommendation_score"] = round(float(score), 3)
        art["similarity"] = round(float(sim), 3)
        art["reason"] = reason
        scored.append((art, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return jsonify([a for a,_ in scored[:n]])

@app.route("/api/categories")
def api_categories():
    return jsonify(CATEGORIES)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
