import requests, re, streamlit as st

@st.cache_data(ttl=600)
def fetch_stock_news(stock_id):
    news = []
    try:
        url = f"https://tw.stock.yahoo.com/quote/{stock_id}/news"; headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        matches = re.findall(r'href="([^"]*news/[^"]*)"[^>]*>.*?<h3[^>]*>(.*?)</h3>', resp.text, re.DOTALL)
        for link, title in matches:
            clean = re.sub(r'<[^>]+>', '', title).strip()
            full_l = link if "https" in link else "https://tw.stock.yahoo.com" + link
            if not any(n['title'] == clean for n in news):
                news.append({"title": clean, "link": full_l})
                if len(news) >= 8: break
    except: pass
    return news

def get_chinese_name_from_web(full_sid):
    try:
        sid = str(full_sid).split('.')[0]
        url = f"https://tw.stock.yahoo.com/quote/{sid}"; headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=5)
        match = re.search(r'<title>(.*?)\(', resp.text)
        if match: return match.group(1).strip()
    except: pass
    return None
