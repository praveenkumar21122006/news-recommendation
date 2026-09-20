# NewsLens — Personalized News Recommendation Web App

AI-powered personalized news feed with content-based filtering, real-time learning, and modern UI.

## ✨ Features
- **Personalized Feed (For You)** — TF-IDF + cosine similarity, category weighting, recency & popularity boosting
- **Cold-start handling** — trending + category preferences when no history
- **Real-time learning** — like / dislike / bookmark / view updates profile instantly
- **Explainable** — each card shows `92% match • Because you like Technology`
- **Explore / Trending / Bookmarks** tabs
- **Category filtering** & live search
- **Onboarding modal** to pick interests (Technology, Sports, Business, Science, Health, Politics, Entertainment)
- **Article drawer** with full content, similarity score, and actions
- **Trending sidebar** + "How it works" explainer
- **Responsive** — Tailwind CSS, mobile bottom nav, glass header

## 🧠 Recommendation Algorithm
`Score = 0.50×cosine_sim(profile, article) + 0.25×category_pref + 0.15×recency + 0.10×popularity`

- Corpus: `title + category×3 + content` → TF-IDF (max 5000 features, 1-2 gram)
- Profile = weighted average of liked (2.0), bookmarked (1.5), history (0.5), category centroids (1.2)
- Cold start: `0.4×category + 0.3×recency + 0.3×popularity`
- Disliked articles excluded, history decayed 0.85×

`recommendation_engine.py:1`

## 📁 Structure
```
app.py                  Flask server & API routes
recommendation_engine.py  NewsRecommender class (TF-IDF + ranking)
data.py                 35 curated articles across 7 categories
templates/index.html    Single-page app (Tailwind CDN + vanilla JS)
requirements.txt
```

## 🚀 Run
```bash
pip install -r requirements.txt --break-system-packages  # or venv
python app.py          # defaults to PORT=5001 (override with PORT=5002)
open http://localhost:5001
```

API:
- `GET /api/news?category=&search=&sort=latest|popular`
- `GET /api/recommend?user_id=&n=12`
- `GET /api/trending`
- `POST /api/preferences` `{categories: ["Technology","Science"]}`
- `POST /api/interact` `{user_id, article_id, action: like|dislike|bookmark|view}`

Data is in-memory (resets on restart). User ID stored in `localStorage`.

## 🎨 UI
Tailwind CDN, Inter + Merriweather fonts, card grid, shimmer skeletons, drawer, toast, modals. No build step.

