import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
import json

class NewsRecommender:
    def __init__(self, articles):
        self.articles = articles
        self.article_ids = [a['id'] for a in articles]
        self.id_to_index = {a['id']: i for i, a in enumerate(articles)}
        # Build corpus for TF-IDF
        corpus = [f"{a['title']} {a['category']} {a['content']} {a['category']} {a['category']}" for a in articles]
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000, ngram_range=(1,2))
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        # Precompute norms for speed
        self.users = {}  # user_id -> profile

    def get_or_create_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {
                'preferences': {},  # category -> weight 0-1
                'liked': [],
                'disliked': [],
                'bookmarked': [],
                'history': [],
                'profile_vector': None
            }
        return self.users[user_id]

    def update_preferences(self, user_id, categories):
        user = self.get_or_create_user(user_id)
        # Reset preferences
        prefs = {}
        for cat in categories:
            prefs[cat] = 1.0
        user['preferences'] = prefs
        self._rebuild_profile(user_id)
        return user

    def record_interaction(self, user_id, article_id, action):
        user = self.get_or_create_user(user_id)
        if article_id not in self.article_ids:
            return None
        
        if action == 'like':
            if article_id not in user['liked']:
                user['liked'].append(article_id)
            if article_id in user['disliked']:
                user['disliked'].remove(article_id)
        elif action == 'dislike':
            if article_id not in user['disliked']:
                user['disliked'].append(article_id)
            if article_id in user['liked']:
                user['liked'].remove(article_id)
        elif action == 'bookmark':
            if article_id not in user['bookmarked']:
                user['bookmarked'].append(article_id)
            else:
                user['bookmarked'].remove(article_id)
                return user  # toggle off, no profile rebuild needed
        elif action == 'view':
            if article_id not in user['history']:
                user['history'].append(article_id)
            # keep history max 50
            user['history'] = user['history'][-50:]
        elif action == 'unbookmark':
            if article_id in user['bookmarked']:
                user['bookmarked'].remove(article_id)

        if action in ('like', 'dislike', 'view'):
            self._rebuild_profile(user_id)
        return user

    def _rebuild_profile(self, user_id):
        user = self.get_or_create_user(user_id)
        vectors = []
        weights = []

        # Liked articles: strong positive signal
        for aid in user['liked']:
            idx = self.id_to_index[aid]
            vectors.append(self.tfidf_matrix[idx].toarray()[0])
            weights.append(2.0)

        # Bookmarked: also strong
        for aid in user['bookmarked']:
            if aid not in user['liked']:
                idx = self.id_to_index[aid]
                vectors.append(self.tfidf_matrix[idx].toarray()[0])
                weights.append(1.5)

        # History: weak signal
        for aid in user['history'][-10:]:
            if aid not in user['liked'] and aid not in user['bookmarked']:
                idx = self.id_to_index[aid]
                vectors.append(self.tfidf_matrix[idx].toarray()[0])
                weights.append(0.5)

        # Category preferences: synthesize vector from category centroid
        if user['preferences']:
            for cat, w in user['preferences'].items():
                cat_indices = [i for i, a in enumerate(self.articles) if a['category'] == cat]
                if cat_indices:
                    cat_vectors = self.tfidf_matrix[cat_indices].toarray().mean(axis=0)
                    vectors.append(cat_vectors)
                    weights.append(w * 1.2)

        if vectors:
            weights = np.array(weights)
            weights = weights / weights.sum()
            profile = np.average(vectors, axis=0, weights=weights)
            user['profile_vector'] = profile
        else:
            user['profile_vector'] = None

    def recommend(self, user_id, n=12, exclude_interacted=False):
        user = self.get_or_create_user(user_id)
        scores = []
        now = datetime.now()

        for article in self.articles:
            aid = article['id']
            idx = self.id_to_index[aid]

            # Optionally exclude disliked
            if aid in user['disliked']:
                continue
            if exclude_interacted and (aid in user['liked'] or aid in user['history']):
                continue

            # Content similarity
            if user['profile_vector'] is not None:
                sim = cosine_similarity(
                    [user['profile_vector']],
                    self.tfidf_matrix[idx]
                )[0][0]
            else:
                sim = 0.0

            # Category preference boost
            cat_pref = user['preferences'].get(article['category'], 0.0)
            # If no preferences set, neutral 0.5
            if not user['preferences']:
                cat_score = 0.5
            else:
                cat_score = cat_pref

            # Recency score (0-1, newer higher)
            try:
                pub_date = datetime.fromisoformat(article['publishedAt'])
            except:
                pub_date = now - timedelta(hours=12)
            hours_ago = (now - pub_date).total_seconds() / 3600
            recency = max(0, 1 - (hours_ago / 72))  # decay over 3 days

            # Popularity
            popularity = article.get('popularity', 50) / 100.0

            # Liked brand boost if cold start: trending
            if user['profile_vector'] is None:
                final = 0.4 * cat_score + 0.3 * recency + 0.3 * popularity
            else:
                final = 0.50 * sim + 0.25 * cat_score + 0.15 * recency + 0.10 * popularity

            # Penalty for already seen low weight but don't hide
            if aid in user['history'] and aid not in user['liked']:
                final *= 0.85

            # Explainability reason
            reason = self._explain(article, sim, cat_pref, user)

            scores.append((article, final, sim, reason))

        scores.sort(key=lambda x: x[1], reverse=True)
        result = []
        for article, score, sim, reason in scores[:n]:
            art = dict(article)
            art['recommendation_score'] = round(float(score), 3)
            art['similarity'] = round(float(sim), 3)
            art['reason'] = reason
            result.append(art)
        return result

    def _explain(self, article, sim, cat_pref, user):
        if not user['preferences'] and not user['liked']:
            if article.get('popularity', 0) > 80:
                return "Trending now"
            return "Popular in " + article['category']
        if cat_pref >= 0.9:
            return f"Because you like {article['category']}"
        if sim > 0.18:
            return "Similar to your reading history"
        if article.get('popularity', 0) > 85:
            return "Trending in " + article['category']
        return f"Recommended in {article['category']}"

    def trending(self, n=6):
        sorted_articles = sorted(self.articles, key=lambda x: x.get('popularity', 0), reverse=True)
        return sorted_articles[:n]

    def search(self, query, category=None):
        query = query.lower().strip()
        results = []
        for a in self.articles:
            if category and category != 'All' and a['category'] != category:
                continue
            if not query:
                results.append(a)
            else:
                text = f"{a['title']} {a['content']} {a['category']}".lower()
                if query in text:
                    results.append(a)
                else:
                    # fuzzy via TF-IDF similarity
                    q_vec = self.vectorizer.transform([query])
                    idx = self.id_to_index[a['id']]
                    sim = cosine_similarity(q_vec, self.tfidf_matrix[idx])[0][0]
                    if sim > 0.1:
                        results.append(a)
        return results
