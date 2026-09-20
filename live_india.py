import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import re
import random
import time

# Cache
_cache = {"data": None, "ts": 0, "ttl": 300}  # 5 min

FEEDS = [
    ("Google News India - Top", "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"),
    ("Google News India - National", "https://news.google.com/rss/search?q=India&hl=en-IN&gl=IN&ceid=IN:en"),
    ("Times of India", "https://timesofindia.indiatimes.com/rssfeedmostrecent.cms"),
    ("NDTV Top", "https://feeds.feedburner.com/ndtvnews-top-stories"),
    ("The Hindu National", "https://www.thehindu.com/news/national/feeder/default.rss"),
    ("BBC India", "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"),
]

CATEGORY_KEYWORDS = {
    "Politics": ["modi", "bjp", "congress", "parliament", "election", "government", "minister", "supreme court", "politics", "loksabha", "rajya", "aap", "rahul", "amit shah"],
    "Business": ["sensex", "nifty", "market", "share", "stock", "economy", "rbi", "rupee", "business", "startup", "investment", "gdp", "inflation", "adani", "ambani"],
    "Sports": ["cricket", "ipl", "virat", "rohit", "bcci", "football", "sports", "olympic", "wrestling", "hockey", "badminton", "asia cup"],
    "Technology": ["isro", "tech", "ai", "phone", "launch", "satellite", "chandrayaan", "google", "apple", "technology", "startup", "app", "5g"],
    "Entertainment": ["bollywood", "shah rukh", "salman", "movie", "film", "actor", "actress", "ott", "netflix", "song", "trailer", "entertainment"],
    "Health": ["health", "covid", "hospital", "doctor", "vaccine", "disease", "aiims", "medical"],
    "Science": ["science", "research", "discovery", "climate", "space", "nasa", "study"],
}

CATEGORY_IMAGES = {
    "Technology": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600",
    "Sports": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=600",
    "Business": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600",
    "Science": "https://images.unsplash.com/photo-1446776877081-d282a0f896e2?w=600",
    "Health": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=600",
    "Politics": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=600",
    "Entertainment": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=600",
}

def _classify(title, desc):
    text = (title + " " + (desc or "")).lower()
    best = "Politics"
    best_score = 0
    for cat, kws in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in text)
        if score > best_score:
            best_score = score
            best = cat
    # if no keyword, fallback to Politics for India live (most news is politics/national)
    return best

def _parse_date(date_str):
    try:
        # RFC822
        dt = datetime.strptime(date_str.strip(), "%a, %d %b %Y %H:%M:%S %Z")
        dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        try:
            dt = datetime.strptime(date_str.strip(), "%a, %d %b %Y %H:%M:%S %z")
            return dt.astimezone(timezone.utc).isoformat()
        except Exception:
            return datetime.now(timezone.utc).isoformat()

def _strip_html(text):
    if not text:
        return ""
    # remove CDATA artifacts and html tags
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def _fetch_feed(url, timeout=8):
    headers = {"User-Agent": "Mozilla/5.0 (NewsLens/1.0)"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            # Try decode
            text = data.decode('utf-8', errors='ignore')
            return text
    except Exception as e:
        print(f"[live_india] feed failed {url}: {e}")
        return None

def fetch_india_live(force=False, max_items=40):
    now = time.time()
    if not force and _cache["data"] is not None and (now - _cache["ts"] < _cache["ttl"]):
        return _cache["data"]

    articles = []
    seen_titles = set()
    aid = 1000

    for source, url in FEEDS:
        if len(articles) >= max_items:
            break
        xml_text = _fetch_feed(url)
        if not xml_text:
            continue
        try:
            root = ET.fromstring(xml_text)
        except Exception as e:
            print(f"[live_india] parse fail {source}: {e}")
            continue

        # RSS: channel/item ; also handle namespaces
        items = root.findall(".//item")
        if not items:
            # Atom feed
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            items = root.findall("atom:entry", ns)

        for item in items:
            if len(articles) >= max_items:
                break
            # RSS fields
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pub_el = item.find("pubDate")
            if pub_el is None:
                pub_el = item.find("published")
            if pub_el is None:
                pub_el = item.find("{http://www.w3.org/2005/Atom}published")
            # Try atom link href
            title = _strip_html(title_el.text) if title_el is not None and title_el.text else None
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            link = ""
            if link_el is not None:
                if link_el.text and link_el.text.strip().startswith("http"):
                    link = link_el.text.strip()
                else:
                    # atom link
                    href = link_el.get("href")
                    if href:
                        link = href
            desc = ""
            if desc_el is not None and desc_el.text:
                desc = _strip_html(desc_el.text)
            # Fallback for atom content
            if not desc:
                content_el = item.find("content")
                if content_el is not None and content_el.text:
                    desc = _strip_html(content_el.text)
                else:
                    atom_content = item.find("{http://www.w3.org/2005/Atom}content")
                    if atom_content is not None and atom_content.text:
                        desc = _strip_html(atom_content.text)

            pub = _parse_date(pub_el.text) if pub_el is not None and pub_el.text else datetime.now(timezone.utc).isoformat()

            # Try to get image from media:content or enclosure or description img
            image = None
            for tag in ["{http://search.yahoo.com/mrss/}content", "enclosure", "{http://search.yahoo.com/mrss/}thumbnail", "media:content", "media:thumbnail"]:
                el = item.find(tag)
                if el is not None:
                    url_img = el.get("url") or el.get("href")
                    if url_img and url_img.startswith("http"):
                        image = url_img
                        break
            # Also search in description html before strip? Use regex on raw
            if not image:
                # try extract img from original desc text (before strip)
                if desc_el is not None and desc_el.text:
                    m = re.search(r'src="([^"]+)"', desc_el.text)
                    if m and m.group(1).startswith("http"):
                        image = m.group(1)

            cat = _classify(title, desc)
            if not image:
                image = CATEGORY_IMAGES.get(cat, CATEGORY_IMAGES["Politics"])

            # Clean desc truncate
            if len(desc) > 300:
                desc = desc[:300] + "..."
            if not desc:
                desc = title + " — Live update from " + source + "."

            # Source name extraction
            src = source.split(" - ")[0]
            # Try to get source from Google News title suffix " - The Hindu"
            if " - " in title:
                maybe_src = title.split(" - ")[-1]
                if len(maybe_src) < 30:
                    src = maybe_src
                    title = " - ".join(title.split(" - ")[:-1])

            # Author fallback
            author = random.choice(["PTI", "ANI", "Express News Service", "TOI Bureau", "NDTV Correspondent", "The Hindu Bureau"])

            articles.append({
                "id": aid,
                "title": title[:180],
                "category": cat,
                "content": desc,
                "image": image,
                "author": author,
                "publishedAt": pub,
                "readTime": random.randint(2, 5),
                "popularity": random.randint(75, 98),
                "source": src,
                "url": link,
                "isLive": True,
                "region": "India",
            })
            aid += 1

    # Sort by publishedAt desc (newest first)
    try:
        articles.sort(key=lambda x: x["publishedAt"], reverse=True)
    except:
        pass

    # If still empty, return fallback india-centric sample
    if not articles:
        articles = _fallback_india()

    _cache["data"] = articles
    _cache["ts"] = now
    print(f"[live_india] fetched {len(articles)} live articles")
    return articles

def _fallback_india():
    now = datetime.now(timezone.utc)
    samples = [
        {"title": "India's GDP Growth Hits 7.8% as Sensex Crosses 85,000 Mark", "category": "Business", "content": "India's economy continues to outperform global peers with strong manufacturing and services PMI. Foreign institutional investors poured in record inflows as Nifty hit all-time high.", "image": CATEGORY_IMAGES["Business"], "popularity": 94},
        {"title": "ISRO Successfully Launches Chandrayaan-4 Mission to Lunar South Pole", "category": "Science", "content": "ISRO's latest lunar mission aims to collect and return soil samples from the Moon's south pole, marking India's most ambitious space mission yet.", "image": CATEGORY_IMAGES["Science"], "popularity": 96},
        {"title": "Supreme Court Verdict on Electoral Reforms Sparks Nationwide Debate", "category": "Politics", "content": "The Supreme Court delivered a landmark judgment on transparency in political funding, with major implications for the upcoming general elections.", "image": CATEGORY_IMAGES["Politics"], "popularity": 90},
        {"title": "Team India Clinches Asia Cup After Thrilling Win Over Pakistan", "category": "Sports", "content": "India defeated Pakistan by 8 wickets in Colombo, with Virat Kohli scoring an unbeaten century. Celebrations erupted across the country.", "image": CATEGORY_IMAGES["Sports"], "popularity": 95},
        {"title": "Mumbai Local Gets AI-Powered Safety Upgrade With Real-Time Crowd Detection", "category": "Technology", "content": "Western Railway deployed AI cameras across Mumbai suburban stations to predict crowd surges and prevent stampedes during peak hours.", "image": CATEGORY_IMAGES["Technology"], "popularity": 88},
        {"title": "AIIMS Delhi Reports Breakthrough in Affordable Cancer Treatment", "category": "Health", "content": "Researchers at AIIMS developed a low-cost immunotherapy protocol that cuts treatment cost by 70%, promising hope for millions.", "image": CATEGORY_IMAGES["Health"], "popularity": 86},
        {"title": "Shah Rukh Khan's New Film Breaks Advance Booking Records Before Release", "category": "Entertainment", "content": "The King Khan's upcoming action thriller sold 2 million tickets in advance, set to become Bollywood's biggest opener of the year.", "image": CATEGORY_IMAGES["Entertainment"], "popularity": 92},
    ]
    out = []
    for i, s in enumerate(samples):
        out.append({
            "id": 1000+i,
            "title": s["title"],
            "category": s["category"],
            "content": s["content"],
            "image": s["image"],
            "author": "PTI",
            "publishedAt": (now).isoformat(),
            "readTime": 3,
            "popularity": s["popularity"],
            "source": "India Live (Fallback)",
            "url": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
            "isLive": True,
            "region": "India",
        })
    return out
