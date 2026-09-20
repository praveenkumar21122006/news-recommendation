from datetime import datetime, timedelta
import random

CATEGORIES = ["Technology", "Sports", "Business", "Science", "Health", "Politics", "Entertainment"]

def generate_news():
    now = datetime.now()
    raw = [
        # Technology
        {"title": "OpenAI Unveils GPT-5 With Breakthrough Reasoning Capabilities", "category": "Technology", "content": "OpenAI announced GPT-5 today, showcasing dramatic improvements in reasoning, coding, and multimodal understanding. Early benchmarks show 40% improvement over GPT-4 in complex problem solving. The model will roll out to ChatGPT Plus users next month.", "image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600", "popularity": 96},
        {"title": "Apple Vision Pro 2 Leaks Reveal Lighter Design and 8K Displays", "category": "Technology", "content": "Apple's next-generation Vision Pro is rumored to weigh 30% less with micro-OLED 8K panels and a new R2 chip. Sources say battery life is extended to 4 hours. Release expected Q1 next year.", "image": "https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?w=600", "popularity": 88},
        {"title": "Quantum Computing Breakthrough Achieves 1000-Qubit Stability", "category": "Technology", "content": "Researchers at MIT achieved stable entanglement of 1000 qubits at room temperature, a milestone that could accelerate practical quantum computers by five years. The technique uses photonic error correction.", "image": "https://images.unsplash.com/photo-1639322537224-f012857c14d3?w=600", "popularity": 82},
        {"title": "Tesla's Humanoid Robot Optimus Now Working in Factories", "category": "Technology", "content": "Tesla deployed Optimus robots on its Fremont assembly line, handling repetitive tasks with 94% accuracy. Elon Musk claims 1 million units per year production target by 2027.", "image": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=600", "popularity": 90},
        {"title": "EU Passes Landmark AI Regulation With Strict Rules for Big Tech", "category": "Technology", "content": "The European Union approved the AI Act, requiring transparency, risk assessments, and human oversight for high-risk AI systems. Violations face fines up to 7% of global revenue.", "image": "https://images.unsplash.com/photo-1451187580459-43490279c429?w=600", "popularity": 78},
        {"title": "Google's New Chip Makes Android Phones 3x Faster in AI Tasks", "category": "Technology", "content": "Google unveiled Tensor G5, delivering triple performance in on-device AI for translation, photo editing, and voice assistance while cutting power consumption by 30%.", "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600", "popularity": 75},

        # Sports
        {"title": "Champions League Final: Real Madrid Clinch 15th Title in Dramatic Comeback", "category": "Sports", "content": "Real Madrid secured their 15th Champions League trophy after trailing 1-0, with two late goals from Vinicius Jr. The Santiago Bernabeu erupted as Ancelotti made history.", "image": "https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=600", "popularity": 94},
        {"title": "NBA: Victor Wembanyama Named MVP in Historic Rookie Season", "category": "Sports", "content": "San Antonio Spurs phenom Wembanyama averaged 28 points and 12 rebounds, becoming the first rookie MVP in decades. Analysts call him a generational talent.", "image": "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=600", "popularity": 89},
        {"title": "Olympics 2024: New World Records Shattered in Swimming", "category": "Sports", "content": "American swimmer Katie Ledecky broke her own 800m freestyle record while Chinese team set relay record. Paris Olympics delivered unforgettable moments.", "image": "https://images.unsplash.com/photo-1530549387789-4c1017266635?w=600", "popularity": 81},
        {"title": "Formula 1: Verstappen Wins 4th Consecutive World Championship", "category": "Sports", "content": "Max Verstappen dominated the season with 19 wins, securing Red Bull's constructors title with three races remaining. Rival teams vow major upgrades.", "image": "https://images.unsplash.com/photo-1511910849309-0dffb8785146?w=600", "popularity": 77},
        {"title": "Cricket World Cup: India Defeats Australia in Thrilling Final", "category": "Sports", "content": "India chased 320 with Virat Kohli's unbeaten 142, ending a 12-year World Cup drought. Celebrations swept across the nation.", "image": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=600", "popularity": 92},

        # Business
        {"title": "Fed Holds Rates Steady as Inflation Cools to 3.1%", "category": "Business", "content": "The Federal Reserve kept interest rates unchanged, signaling potential cuts next quarter as inflation shows signs of cooling. Markets rallied 2.5% on the news.", "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600", "popularity": 84},
        {"title": "Nvidia Surpasses $3 Trillion Market Cap on AI Demand", "category": "Business", "content": "Nvidia briefly overtook Apple as the world's most valuable company, fueled by insatiable demand for its H200 AI chips. Analysts predict continued growth.", "image": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=600", "popularity": 91},
        {"title": "Bitcoin Hits $95,000 as Institutional Adoption Soars", "category": "Business", "content": "Bitcoin reached a new all-time high near $95k after BlackRock's ETF saw record inflows. Ethereum also surged past $4,500 amid DeFi boom.", "image": "https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=600", "popularity": 86},
        {"title": "Startup Unicorn Raises $500M to Revolutionize Green Energy Storage", "category": "Business", "content": "Form Energy's iron-air battery promises 100-hour storage at one-tenth the cost of lithium-ion, attracting major climate investors.", "image": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=600", "popularity": 70},
        {"title": "Amazon to Invest $15B in AI-Powered Logistics Network", "category": "Business", "content": "Amazon announced autonomous warehouses and drone delivery expansion to 30 new cities, aiming to cut delivery times to under 2 hours.", "image": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=600", "popularity": 76},

        # Science
        {"title": "NASA's James Webb Discovers Ancient Galaxy Older Than Expected", "category": "Science", "content": "JWST spotted a galaxy formed just 300 million years after the Big Bang, challenging current cosmological models. The galaxy is unexpectedly massive and structured.", "image": "https://images.unsplash.com/photo-1446776877081-d282a0f896e2?w=600", "popularity": 87},
        {"title": "CRISPR Gene Editing Cures Genetic Blindness in Clinical Trial", "category": "Science", "content": "A CRISPR therapy restored vision in 12 of 14 patients with inherited blindness, with no serious side effects. FDA approval expected within a year.", "image": "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=600", "popularity": 83},
        {"title": "Artemis III: NASA Confirms Lunar Landing Site Near South Pole", "category": "Science", "content": "NASA selected Shackleton Crater region for its water ice reserves. The 2027 mission will be the first crewed lunar landing since Apollo.", "image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=600", "popularity": 80},
        {"title": "Deep Sea Expedition Discovers 50 New Species in Pacific", "category": "Science", "content": "Biologists cataloged bioluminescent creatures at 4000m depth, including a transparent octopus. Findings may help understand climate change impact on oceans.", "image": "https://images.unsplash.com/photo-1546026423-cc4642628d2b?w=600", "popularity": 68},
        {"title": "Fusion Breakthrough: Net Energy Gain Sustained for 5 Minutes", "category": "Science", "content": "Lawrence Livermore National Lab maintained fusion net positive energy for 300 seconds, tripling previous record. Commercial fusion moved closer to reality.", "image": "https://images.unsplash.com/photo-1464802686167-b939a6910659?w=600", "popularity": 85},

        # Health
        {"title": "New Alzheimer's Drug Shows 60% Slowdown in Early Trials", "category": "Health", "content": "Donanemab variant reduced cognitive decline by 60% in early Alzheimer's patients, with manageable side effects. Experts call it the most promising treatment yet.", "image": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=600", "popularity": 88},
        {"title": "WHO Declares End of Global Obesity Epidemic With New Guidelines", "category": "Health", "content": "WHO's updated nutrition and exercise guidelines contributed to 8% drop in obesity rates globally, alongside new GLP-1 medications.", "image": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600", "popularity": 72},
        {"title": "mRNA Vaccine for Universal Flu Enters Phase 3 Trials", "category": "Health", "content": "Moderna's universal flu mRNA vaccine targets all 20 influenza subtypes, potentially ending seasonal flu shots. Early data shows 85% efficacy.", "image": "https://images.unsplash.com/photo-1584118624012-df05638f1d26?w=600", "popularity": 79},
        {"title": "Sleep Study Reveals 7 Hours is Optimal for Brain Health", "category": "Health", "content": "A 10-year study of 500,000 participants found 7 hours of sleep linked to lowest dementia risk and best cognitive performance, debunking 8-hour myth.", "image": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=600", "popularity": 74},
        {"title": "Plant-Based Diet Cuts Heart Disease Risk by 32%, Study Finds", "category": "Health", "content": "Harvard research tracking 200,000 people over 20 years showed significant cardiovascular benefits, even with occasional meat consumption.", "image": "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=600", "popularity": 71},

        # Politics
        {"title": "Climate Summit Reaches Historic Agreement on Fossil Fuel Phase-Out", "category": "Politics", "content": "195 countries agreed to triple renewable capacity by 2030 and phase out unabated coal. The deal includes $100B annual climate finance for developing nations.", "image": "https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?w=600", "popularity": 86},
        {"title": "Supreme Court Rules on Landmark Digital Privacy Case", "category": "Politics", "content": "The Court ruled 7-2 that warrantless location tracking violates Fourth Amendment, setting precedent for digital age privacy protections.", "image": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=600", "popularity": 77},
        {"title": "Election 2024: Key Battleground States See Record Voter Turnout", "category": "Politics", "content": "Turnout exceeded 68% in swing states, driven by Gen Z and mail-in voting. Analysts analyze implications for future campaigns.", "image": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=600", "popularity": 80},
        {"title": "UN Announces Global Treaty to End Plastic Pollution by 2040", "category": "Politics", "content": "Binding treaty requires 50% reduction in plastic production and full recyclability. Major producers including US and China signed on.", "image": "https://images.unsplash.com/photo-1532996122728-e3c354a0b15b?w=600", "popularity": 73},

        # Entertainment
        {"title": "Dune: Part Three Breaks Box Office Records With $800M Opening", "category": "Entertainment", "content": "Denis Villeneuve's epic concluded the trilogy with stunning visuals and critical acclaim. Zendaya and Timothée Chalamet's performances praised as career-best.", "image": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=600", "popularity": 90},
        {"title": "Netflix's AI-Generated Series Sparks Hollywood Debate", "category": "Entertainment", "content": "Netflix premiered the first series with AI-assisted writing and visuals, igniting protests and negotiations with the Writers Guild over AI use.", "image": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600", "popularity": 82},
        {"title": "Taylor Swift Announces Final Eras Tour With Holographic Show", "category": "Entertainment", "content": "Taylor Swift revealed a holographic finale show that will tour globally after her record-breaking Eras Tour grossed $2 billion.", "image": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=600", "popularity": 93},
        {"title": "Gaming: GTA 6 Trailer Hits 250M Views in 24 Hours", "category": "Entertainment", "content": "Rockstar's GTA 6 trailer broke YouTube records, revealing Vice City and dual protagonists. Release scheduled for late 2025.", "image": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=600", "popularity": 95},
        {"title": "Oscars 2024: Oppenheimer Sweeps With 7 Wins Including Best Picture", "category": "Entertainment", "content": "Christopher Nolan's biopic dominated the ceremony, with Cillian Murphy winning Best Actor and Nolan Best Director in an emotional night.", "image": "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=600", "popularity": 78},
    ]

    articles = []
    for i, r in enumerate(raw):
        hours_ago = random.randint(1, 72)
        pub = now - timedelta(hours=hours_ago)
        # Add some variance to popularity
        pop = r["popularity"] + random.randint(-5, 5)
        pop = max(40, min(99, pop))
        articles.append({
            "id": i+1,
            "title": r["title"],
            "category": r["category"],
            "content": r["content"],
            "image": r["image"],
            "author": random.choice(["Alex Morgan", "Jamie Chen", "Taylor Reed", "Jordan Lee", "Casey Smith", "Morgan Blake"]),
            "publishedAt": pub.isoformat(),
            "readTime": random.randint(2, 8),
            "popularity": pop,
            "source": random.choice(["Reuters", "BBC News", "The Verge", "Bloomberg", "Nature", "ESPN"]),
        })
    return articles
