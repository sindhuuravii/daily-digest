"""
Sindhu's Daily Digest — digest.py
====================================
A personal daily news dashboard generator.

SETUP:
1. pip install requests feedparser
2. Add GROQ_API_KEY as a GitHub Secret
3. Run via GitHub Actions or: python digest.py
"""

import feedparser
import requests
import json
import os
import random
from datetime import datetime, timezone, timedelta

# ─────────────────────────────────────────
# GROQ API KEY (from GitHub Secrets)
# ─────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# ─────────────────────────────────────────
# FUN FACTS (rotating list)
# ─────────────────────────────────────────
FUN_FACTS = [
    "Honey never spoils. Archaeologists have found 3,000-year-old honey in Egyptian tombs that was still edible.",
    "A group of flamingos is called a flamboyance.",
    "The shortest war in history lasted only 38–45 minutes — between Britain and Zanzibar in 1896.",
    "Octopuses have three hearts, blue blood, and can edit their own RNA.",
    "The average person walks about 100,000 miles in their lifetime — roughly four times around the Earth.",
    "Bananas are berries, but strawberries are not.",
    "Nintendo was founded in 1889 — originally as a playing card company.",
    "There are more possible iterations of a game of chess than there are atoms in the observable universe.",
    "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
    "A day on Venus is longer than a year on Venus.",
    "Wombat poop is cube-shaped — the only known animal to produce cubic feces.",
    "The inventor of the Pringles can is buried in one.",
    "Oxford University is older than the Aztec Empire.",
    "Sharks are older than trees — they've existed for over 450 million years.",
    "The dot over the letter 'i' is called a tittle.",
]

# ─────────────────────────────────────────
# RSS FEEDS BY SECTION
# ─────────────────────────────────────────
FEEDS = {
    "World Affairs": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
    ],
    "India & Policy": [
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://indianexpress.com/section/india/feed/",
        "https://feeds.feedburner.com/ndtvnews-india-news",
    ],
    "Geopolitics": [
        "https://foreignpolicy.com/feed/",
        "https://feeds.reuters.com/reuters/worldNews",
        "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    ],
    "Business & Economy": [
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
        "https://www.livemint.com/rss/money",
    ],
    "Indian Startups": [
        "https://yourstory.com/feed",
        "https://entrackr.com/feed/",
        "https://inc42.com/feed/",
    ],
    "Global Markets": [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://www.investing.com/rss/news_25.rss",
        "https://feeds.reuters.com/reuters/businessNews",
    ],
    "Macroeconomics": [
        "https://feeds.feedburner.com/typepad/krugman",
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.economist.com/finance-and-economics/rss.xml",
    ],
    "Technology": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
    ],
    "AI & Machine Learning": [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://venturebeat.com/category/ai/feed/",
    ],
    "Semiconductors": [
        "https://www.anandtech.com/rss/",
        "https://semianalysis.com/feed/",
        "https://techcrunch.com/feed/",
    ],
    "Advertising & Campaigns": [
        "https://www.adweek.com/feed/",
        "https://feeds.feedburner.com/adage/digital",
        "https://www.marketingweek.com/feed/",
    ],
    "Consumer Trends": [
        "https://www.adweek.com/feed/",
        "https://feeds.feedburner.com/adage/digital",
        "https://www.businessoffashion.com/rss/news",
    ],
    "Fashion": [
        "https://www.vogue.com/feed/rss",
        "https://www.businessoffashion.com/rss/news",
        "https://wwd.com/feed/",
    ],
    "Culture & Entertainment": [
        "https://pitchfork.com/feed/feed-news/rss",
        "https://www.theguardian.com/culture/rss",
        "https://variety.com/feed/",
    ],
    "Bangalore News": [
        "https://www.thehindu.com/news/cities/bangalore/feeder/default.rss",
        "https://bangaloremirror.indiatimes.com/rssfeeds/20800/list.cms",
        "https://indianexpress.com/section/cities/bangalore/feed/",
    ],
    "Karnataka News": [
        "https://www.deccanherald.com/rss/state.rss",
        "https://www.thehindu.com/news/national/karnataka/feeder/default.rss",
        "https://indianexpress.com/section/cities/bangalore/feed/",
    ],
}

# ─────────────────────────────────────────
# FETCH RSS HEADLINES
# ─────────────────────────────────────────
def fetch_headlines(feed_urls, limit=5):
    articles = []
    seen = set()
    for url in feed_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "#")
                if title and title not in seen:
                    seen.add(title)
                    articles.append({"title": title, "link": link})
                if len(articles) >= limit:
                    break
        except Exception as e:
            print(f"  [warn] Feed failed: {url} — {e}")
        if len(articles) >= limit:
            break
    return articles[:limit]

# ─────────────────────────────────────────
# AI SUMMARY VIA GROQ
# ─────────────────────────────────────────
def get_ai_summary(section_name, headlines):
    if not headlines or not GROQ_API_KEY:
        return "Add your Groq API key to enable AI summaries."
    try:
        headline_text = "\n".join([f"- {h['title']}" for h in headlines])
        prompt = (
            f"You are a sharp analyst briefing a senior executive. "
            f"Based on these headlines from the '{section_name}' section, "
            f"write a 3-4 sentence analytical summary. "
            f"Be concise, smart, and focus on 'why it matters' — like a young MBA operator. "
            f"Do NOT repeat the headlines. Just give the synthesis.\n\nHeadlines:\n{headline_text}"
        )
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
                "temperature": 0.6,
            },
            timeout=15,
        )
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  [warn] Groq summary failed for {section_name}: {e}")
        return "Summary unavailable."

# ─────────────────────────────────────────
# ON THIS DAY (Wikipedia API — real events for today's date)
# ─────────────────────────────────────────
def get_on_this_day():
    try:
        IST = timezone(timedelta(hours=5, minutes=30))
        today = datetime.now(IST)
        month = today.month
        day = today.day
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
        headers = {"User-Agent": "SindhuDailyDigest/1.0"}
        r = requests.get(url, headers=headers, timeout=8)
        data = r.json()
        events = data.get("events", [])
        if len(events) >= 3:
            picks = [events[0], events[len(events) // 2], events[-1]]
        else:
            picks = events
        result = []
        for e in picks:
            year = e.get("year", "")
            text = e.get("text", "")
            result.append(f"<strong>{year}:</strong> {text}")
        return result
    except Exception as e:
        print(f"  [warn] On This Day fetch failed: {e}")
        return ["Could not load today's historical events."]

# ─────────────────────────────────────────
# WELLNESS TIP (AI-generated daily via Groq)
# ─────────────────────────────────────────
def get_wellness_tip():
    if not GROQ_API_KEY:
        return ("💪 Wellness", "Add your Groq API key to enable daily wellness tips.")
    try:
        IST = timezone(timedelta(hours=5, minutes=30))
        today = datetime.now(IST).strftime("%A, %d %B")
        prompt = (
            f"Today is {today}. Generate one daily wellness tip for a sharp, ambitious young professional in Bengaluru, India. "
            f"It can be a workout tip, mental health insight, productivity hack, stoic quote with reflection, or recovery tip. "
            f"Make it specific, actionable, and genuinely useful — not generic. "
            f"Format your response as JSON with two fields: 'label' (an emoji + 2-3 word title) and 'tip' (2-3 sentences). "
            f"Return only valid JSON, no markdown, no backticks."
        )
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150,
                "temperature": 0.9,
            },
            timeout=15,
        )
        data = response.json()
        text = data["choices"][0]["message"]["content"].strip()
        text = text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(text)
        return (parsed["label"], parsed["tip"])
    except Exception as e:
        print(f"  [warn] Wellness tip failed: {e}")
        return ("💪 Wellness", "Take a 10-minute walk today. Even brief movement resets your nervous system and sharpens focus for the rest of the day.")

# ─────────────────────────────────────────
# WEATHER (Open-Meteo — no API key needed)
# ─────────────────────────────────────────
def get_bangalore_weather():
    weather_map = {
        0: ("☀️", "Clear sky"), 1: ("🌤️", "Mainly clear"), 2: ("⛅", "Partly cloudy"),
        3: ("☁️", "Overcast"), 45: ("🌫️", "Foggy"), 48: ("🌫️", "Icy fog"),
        51: ("🌦️", "Light drizzle"), 53: ("🌦️", "Drizzle"), 55: ("🌧️", "Heavy drizzle"),
        61: ("🌧️", "Light rain"), 63: ("🌧️", "Rain"), 65: ("🌧️", "Heavy rain"),
        80: ("🌦️", "Showers"), 81: ("🌧️", "Heavy showers"), 82: ("⛈️", "Violent showers"),
        95: ("⛈️", "Thunderstorm"), 96: ("⛈️", "Thunderstorm + hail"),
    }
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=12.9716&longitude=77.5946"
            "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
            "&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max"
            "&timezone=Asia%2FKolkata"
            "&forecast_days=7"
        )
        r = requests.get(url, timeout=8)
        data = r.json()
        current = data["current"]
        daily = data["daily"]

        temp = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
        code = current["weather_code"]
        emoji, desc = weather_map.get(code, ("🌡️", "Unknown"))

        forecast = []
        for i in range(7):
            date_str = daily["time"][i]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            day_name = date_obj.strftime("%a %d %b")
            max_t = daily["temperature_2m_max"][i]
            min_t = daily["temperature_2m_min"][i]
            d_code = daily["weather_code"][i]
            rain_prob = daily["precipitation_probability_max"][i]
            d_emoji, d_desc = weather_map.get(d_code, ("🌡️", "Unknown"))
            forecast.append({
                "day": day_name, "emoji": d_emoji, "desc": d_desc,
                "max": max_t, "min": min_t, "rain": rain_prob,
            })

        return {
            "temp": temp, "humidity": humidity, "wind": wind,
            "desc": desc, "emoji": emoji, "forecast": forecast,
        }
    except Exception as e:
        print(f"  [warn] Weather fetch failed: {e}")
        return {"temp": "N/A", "humidity": "N/A", "wind": "N/A", "desc": "Unavailable", "emoji": "🌡️", "forecast": []}

# ─────────────────────────────────────────
# MARKETS (Yahoo Finance — no key needed)
# ─────────────────────────────────────────
def get_market_data():
    symbols = {
        "Rambus (RMBS)": "RMBS",
        "Nifty 50": "^NSEI",
        "Bitcoin": "BTC-USD",
    }
    results = {}
    for name, symbol in symbols.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, timeout=8)
            data = r.json()
            closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            closes = [c for c in closes if c is not None]
            if len(closes) >= 2:
                prev, curr = closes[-2], closes[-1]
                change = curr - prev
                pct = (change / prev) * 100
            elif closes:
                curr = closes[-1]
                change, pct = 0, 0
            else:
                raise ValueError("No close data")
            results[name] = {"price": round(curr, 2), "change": round(change, 2), "pct": round(pct, 2)}
        except Exception as e:
            print(f"  [warn] Market fetch failed for {name}: {e}")
            results[name] = {"price": "N/A", "change": 0, "pct": 0}
    return results

# ─────────────────────────────────────────
# HTML GENERATION
# ─────────────────────────────────────────
def build_html(sections_data, weather, markets, fun_fact, generated_at, on_this_day, wellness):

    def market_ticker_html(markets):
        items = []
        for name, d in markets.items():
            price = d["price"]
            pct = d["pct"]
            if isinstance(price, (float, int)):
                arrow = "▲" if pct >= 0 else "▼"
                color_class = "up" if pct >= 0 else "down"
                items.append(
                    f'<span class="ticker-item">'
                    f'<span class="ticker-name">{name}</span>'
                    f'<span class="ticker-price">{price:,.2f}</span>'
                    f'<span class="ticker-change {color_class}">{arrow} {abs(pct):.2f}%</span>'
                    f'</span>'
                )
            else:
                items.append(
                    f'<span class="ticker-item">'
                    f'<span class="ticker-name">{name}</span>'
                    f'<span class="ticker-price">N/A</span>'
                    f'</span>'
                )
        return "".join(items)

    def section_html(section_name, articles, summary):
        headlines_html = ""
        for a in articles:
            headlines_html += (
                f'<li class="headline-item">'
                f'<a href="{a["link"]}" target="_blank" class="headline-link">{a["title"]}</a>'
                f'</li>'
            )
        if not headlines_html:
            headlines_html = '<li class="headline-item no-data">No headlines available right now.</li>'
        return f"""
        <div class="section-card">
            <div class="section-header">
                <h3 class="section-title">{section_name}</h3>
            </div>
            <div class="ai-summary">
                <span class="ai-badge">AI BRIEF</span>
                <p class="summary-text">{summary}</p>
            </div>
            <ul class="headline-list">{headlines_html}</ul>
        </div>
        """

    def group_html(group_title, section_names, sections_data):
        cards = ""
        for name in section_names:
            articles = sections_data[name]["articles"]
            summary = sections_data[name]["summary"]
            cards += section_html(name, articles, summary)
        return f"""
        <div class="group-block">
            <div class="group-label"><span>{group_title}</span></div>
            <div class="sections-grid">{cards}</div>
        </div>
        """

    w = weather
    ticker = market_ticker_html(markets)
    wellness_label, wellness_text = wellness

    # 7-day forecast HTML
    forecast_html = ""
    for day in w.get("forecast", []):
        forecast_html += f"""
        <div class="forecast-day">
            <div class="forecast-name">{day['day']}</div>
            <div class="forecast-emoji">{day['emoji']}</div>
            <div class="forecast-desc">{day['desc']}</div>
            <div class="forecast-temps"><strong>{day['max']}°</strong> / {day['min']}°</div>
            <div class="forecast-rain">🌧 {day['rain']}%</div>
        </div>
        """

    on_this_day_html = "<br>".join(on_this_day)

    groups = [
        ("CORE NEWS", ["World Affairs", "India & Policy", "Geopolitics"]),
        ("BUSINESS & ECONOMY", ["Business & Economy", "Indian Startups", "Global Markets", "Macroeconomics"]),
        ("TECH", ["Technology", "AI & Machine Learning", "Semiconductors"]),
        ("MARKETING & CULTURE", ["Advertising & Campaigns", "Consumer Trends", "Fashion", "Culture & Entertainment"]),
        ("LOCAL", ["Bangalore News", "Karnataka News"]),
    ]

    groups_html = ""
    for g_title, g_sections in groups:
        groups_html += group_html(g_title, g_sections, sections_data)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sindhu's Daily Digest</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Jost:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
    :root {{
        --burgundy: #5C1A2B;
        --burgundy-dark: #3D0F1C;
        --burgundy-mid: #7A2438;
        --cream: #FAF6EF;
        --cream-dark: #F0E8DA;
        --gold: #C9A84C;
        --gold-light: #E8C97A;
        --text-dark: #1A0A10;
        --text-mid: #4A2030;
        --text-light: #8A6070;
        --card-bg: #FFFFFF;
        --border: rgba(92,26,43,0.15);
    }}

    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
        background-color: var(--cream);
        font-family: 'Jost', sans-serif;
        color: var(--text-dark);
        font-size: 15px;
        line-height: 1.6;
    }}

    .ticker-bar {{
        background: var(--burgundy-dark);
        color: var(--cream);
        padding: 10px 32px;
        display: flex;
        align-items: center;
        gap: 32px;
        overflow-x: auto;
        white-space: nowrap;
        font-size: 13px;
        letter-spacing: 0.04em;
    }}
    .ticker-label {{ color: var(--gold); font-weight: 600; font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; flex-shrink: 0; }}
    .ticker-item {{ display: inline-flex; align-items: center; gap: 8px; padding: 0 16px; border-left: 1px solid rgba(201,168,76,0.3); }}
    .ticker-name {{ color: var(--cream-dark); font-weight: 500; }}
    .ticker-price {{ color: #fff; font-weight: 600; }}
    .ticker-change.up {{ color: #5DD68A; }}
    .ticker-change.down {{ color: #FF7A6E; }}

    .masthead {{
        background: var(--burgundy);
        padding: 40px 48px 32px;
        text-align: center;
        border-bottom: 3px solid var(--gold);
        position: relative;
        overflow: hidden;
    }}
    .masthead::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(ellipse at 50% 0%, rgba(201,168,76,0.12) 0%, transparent 70%);
        pointer-events: none;
    }}
    .masthead-eyebrow {{ font-size: 11px; font-weight: 600; letter-spacing: 0.25em; text-transform: uppercase; color: var(--gold); margin-bottom: 12px; }}
    .masthead-title {{ font-family: 'Playfair Display', serif; font-size: clamp(2.4rem, 5vw, 4rem); font-weight: 700; color: var(--cream); line-height: 1.1; margin-bottom: 8px; }}
    .masthead-title em {{ font-style: italic; color: var(--gold-light); }}
    .masthead-dateline {{ font-size: 13px; color: rgba(250,246,239,0.6); letter-spacing: 0.08em; font-weight: 300; margin-top: 10px; }}

    .weather-strip {{
        background: var(--burgundy-mid);
        color: var(--cream);
        padding: 16px 48px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        font-size: 13px;
        border-bottom: 1px solid rgba(201,168,76,0.25);
    }}
    .weather-current {{ display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }}
    .weather-city {{ font-weight: 600; font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; color: var(--gold); }}
    .weather-data {{ display: flex; align-items: center; gap: 20px; }}
    .weather-emoji {{ font-size: 20px; }}
    .weather-desc {{ color: rgba(250,246,239,0.9); }}
    .weather-stat {{ color: rgba(250,246,239,0.65); font-size: 12px; }}
    .weather-stat strong {{ color: var(--cream); }}

    .forecast-strip {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .forecast-day {{
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(201,168,76,0.2);
        border-radius: 4px;
        padding: 8px 12px;
        text-align: center;
        min-width: 86px;
        font-size: 12px;
        color: var(--cream);
    }}
    .forecast-name {{ font-weight: 600; font-size: 10px; margin-bottom: 4px; color: var(--gold); letter-spacing: 0.05em; }}
    .forecast-emoji {{ font-size: 18px; margin: 4px 0; }}
    .forecast-desc {{ font-size: 10px; color: rgba(250,246,239,0.65); margin-bottom: 4px; }}
    .forecast-temps {{ font-size: 12px; color: var(--cream); }}
    .forecast-rain {{ font-size: 10px; color: rgba(250,246,239,0.55); margin-top: 3px; }}

    .fact-strip {{
        background: var(--cream-dark);
        border-bottom: 1px solid var(--border);
        padding: 12px 48px;
        display: flex;
        align-items: flex-start;
        gap: 14px;
        font-size: 13px;
    }}
    .fact-label {{
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--burgundy);
        background: rgba(92,26,43,0.08);
        padding: 3px 8px;
        border-radius: 2px;
        white-space: nowrap;
        flex-shrink: 0;
        margin-top: 2px;
    }}
    .fact-text {{ color: var(--text-mid); font-style: italic; line-height: 1.6; }}

    .onthisday-strip {{
        background: #f5ede0;
        border-bottom: 1px solid var(--border);
        padding: 12px 48px;
        display: flex;
        align-items: flex-start;
        gap: 14px;
        font-size: 13px;
    }}
    .onthisday-label {{
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--burgundy);
        background: rgba(92,26,43,0.1);
        padding: 3px 8px;
        border-radius: 2px;
        white-space: nowrap;
        flex-shrink: 0;
        margin-top: 2px;
    }}
    .onthisday-text {{ color: var(--text-mid); line-height: 1.9; }}

    .wellness-strip {{
        background: #f0f5ed;
        border-bottom: 1px solid rgba(46,125,82,0.15);
        padding: 12px 48px;
        display: flex;
        align-items: flex-start;
        gap: 14px;
        font-size: 13px;
    }}
    .wellness-label {{
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #2E7D52;
        background: rgba(46,125,82,0.1);
        padding: 3px 8px;
        border-radius: 2px;
        white-space: nowrap;
        flex-shrink: 0;
        margin-top: 2px;
    }}
    .wellness-text {{ color: #1a3a2a; font-style: italic; line-height: 1.6; }}

    .main-content {{ max-width: 1320px; margin: 0 auto; padding: 40px 32px 80px; }}

    .group-block {{ margin-bottom: 56px; }}
    .group-label {{ display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }}
    .group-label span {{
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        color: var(--burgundy);
        padding-bottom: 4px;
        border-bottom: 2px solid var(--gold);
    }}

    .sections-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 24px; }}

    .section-card {{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-top: 3px solid var(--burgundy);
        padding: 24px;
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }}
    .section-card:hover {{ box-shadow: 0 8px 32px rgba(92,26,43,0.12); transform: translateY(-2px); }}
    .section-header {{ margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border); }}
    .section-title {{ font-family: 'Playfair Display', serif; font-size: 1.15rem; font-weight: 600; color: var(--burgundy-dark); line-height: 1.3; }}

    .ai-summary {{
        background: rgba(92,26,43,0.04);
        border-left: 3px solid var(--gold);
        padding: 12px 16px;
        margin-bottom: 18px;
        border-radius: 0 2px 2px 0;
    }}
    .ai-badge {{ display: inline-block; font-size: 9px; font-weight: 700; letter-spacing: 0.18em; color: var(--gold); border: 1px solid var(--gold); padding: 2px 6px; margin-bottom: 8px; }}
    .summary-text {{ font-size: 13px; color: var(--text-mid); line-height: 1.65; }}

    .headline-list {{ list-style: none; display: flex; flex-direction: column; gap: 10px; }}
    .headline-item {{ padding: 8px 0; border-bottom: 1px dashed rgba(92,26,43,0.1); font-size: 13.5px; line-height: 1.5; }}
    .headline-item:last-child {{ border-bottom: none; }}
    .headline-link {{ color: var(--text-dark); text-decoration: none; font-weight: 400; transition: color 0.15s ease; display: block; }}
    .headline-link:hover {{ color: var(--burgundy); text-decoration: underline; text-decoration-color: var(--gold); text-underline-offset: 3px; }}
    .headline-link::before {{ content: '→ '; color: var(--gold); font-size: 12px; font-weight: 600; }}
    .no-data {{ color: var(--text-light); font-style: italic; }}

    .footer {{
        background: var(--burgundy-dark);
        color: rgba(250,246,239,0.45);
        text-align: center;
        padding: 24px;
        font-size: 12px;
        letter-spacing: 0.06em;
        border-top: 2px solid var(--gold);
    }}
    .footer strong {{ color: var(--gold); font-weight: 500; }}

    @media (max-width: 768px) {{
        .masthead {{ padding: 28px 24px; }}
        .main-content {{ padding: 24px 16px; }}
        .weather-strip, .fact-strip, .onthisday-strip, .wellness-strip {{ padding: 12px 20px; }}
        .ticker-bar {{ padding: 10px 20px; }}
        .sections-grid {{ grid-template-columns: 1fr; }}
        .forecast-strip {{ gap: 8px; }}
        .forecast-day {{ min-width: 76px; }}
    }}
</style>
</head>
<body>

<div class="ticker-bar">
    <span class="ticker-label">Markets</span>
    {ticker}
    <span style="color:rgba(250,246,239,0.35);font-size:11px;margin-left:auto;flex-shrink:0;">Yahoo Finance · {generated_at}</span>
</div>

<div class="masthead">
    <div class="masthead-eyebrow">Your Personal Intelligence Briefing</div>
    <div class="masthead-title"><em>Sindhu's</em> Daily Digest</div>
    <div class="masthead-dateline">{generated_at} &nbsp;·&nbsp; Bengaluru, India</div>
</div>

<div class="weather-strip">
    <div class="weather-current">
        <span class="weather-city">🌆 Bengaluru Weather</span>
        <div class="weather-data">
            <span class="weather-emoji">{w['emoji']}</span>
            <span class="weather-desc">{w['desc']}</span>
            <span class="weather-stat"><strong>{w['temp']}°C</strong> · Humidity <strong>{w['humidity']}%</strong> · Wind <strong>{w['wind']} km/h</strong></span>
        </div>
    </div>
    <div class="forecast-strip">{forecast_html}</div>
</div>

<div class="fact-strip">
    <span class="fact-label">✦ Today's Fact</span>
    <span class="fact-text">{fun_fact}</span>
</div>

<div class="onthisday-strip">
    <span class="onthisday-label">📅 On This Day</span>
    <span class="onthisday-text">{on_this_day_html}</span>
</div>

<div class="wellness-strip">
    <span class="wellness-label">{wellness_label}</span>
    <span class="wellness-text">{wellness_text}</span>
</div>

<div class="main-content">
    {groups_html}
</div>

<div class="footer">
    Generated by <strong>Sindhu's Daily Digest</strong> · Powered by Groq AI, Open-Meteo & Yahoo Finance ·
    Sources: BBC, NYT, Al Jazeera, The Hindu, TechCrunch, The Verge, Adweek &amp; more ·
    <strong>{generated_at}</strong>
</div>

</body>
</html>"""
    return html


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    print("\n🗞  Sindhu's Daily Digest — Starting up...\n")

    IST = timezone(timedelta(hours=5, minutes=30))
    generated_at = datetime.now(IST).strftime("%A, %d %B %Y · %I:%M %p")
    fun_fact = random.choice(FUN_FACTS)

    print("📈 Fetching market data...")
    markets = get_market_data()

    print("🌤  Fetching Bangalore weather + 7-day forecast...")
    weather = get_bangalore_weather()

    print("📅 Fetching On This Day...")
    on_this_day = get_on_this_day()

    print("🧘 Generating wellness tip...")
    wellness = get_wellness_tip()

    print("\n📰 Fetching headlines & generating AI summaries...\n")
    sections_data = {}
    for section_name, feed_urls in FEEDS.items():
        print(f"  → {section_name}...")
        articles = fetch_headlines(feed_urls, limit=5)
        summary = get_ai_summary(section_name, articles)
        sections_data[section_name] = {"articles": articles, "summary": summary}

    print("\n🎨 Building HTML dashboard...")
    html = build_html(sections_data, weather, markets, fun_fact, generated_at, on_this_day, wellness)

    output_file = "dashboard.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Dashboard saved → {output_file}")
    print("Done! Enjoy your digest, Sindhu ☕\n")


if __name__ == "__main__":
    main()
