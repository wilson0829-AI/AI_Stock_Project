import yfinance as yf
import requests, re, pandas as pd, streamlit as st, json, os
from datetime import datetime, timedelta
from token_config import FINMIND_TOKEN

USERS_DIR = "users"
SCAN_RESULTS_DIR = "users/scan_history"

@st.cache_data(ttl=86400)
def get_all_taiwan_stock_dict():
    stock_dict = {}
    try:
        url = "https://raw.githubusercontent.com/ycm666/TaiwanStockList/master/stock_info.csv"
        df = pd.read_csv(url, encoding='utf-8')
        df['code'] = df['code'].astype(str)
        stock_dict = dict(zip(df['code'], df['name']))
    except: pass
    # 絕對精準校正
    corrections = {
        "2006": "東和鋼鐵", "1414": "東和紡織", "2330": "台積電", "2317": "鴻海",
        "2454": "聯發科", "2308": "台達電", "2382": "廣達", "2603": "長榮",
        "2609": "陽明", "3006": "晶豪科", "2303": "聯電", "2891": "中信金"
    }
    stock_dict.update(corrections)
    return stock_dict

def fetch_stock_history(sid_raw):
    try:
        target_sid = f"{sid_raw}.TW"
        tk = yf.Ticker(target_sid)
        df = tk.history(period="2y", auto_adjust=False)
        if df.empty:
            target_sid = f"{sid_raw}.TWO"; tk = yf.Ticker(target_sid); df = tk.history(period="2y", auto_adjust=False)
        if not df.empty:
            df.index = df.index.tz_localize(None); return df, target_sid
    except: pass
    return None, None

@st.cache_data(ttl=3600)
def fetch_chips_data(stock_id, k_line_dates):
    """抓取法人資料並強行對齊 K 線日期 (單位：張)"""
    empty_res = [0]*len(k_line_dates), [0]*len(k_line_dates), [0]*len(k_line_dates)
    if not FINMIND_TOKEN or "請在此處" in FINMIND_TOKEN: return empty_res
    url = "https://api.finmindtrade.com/api/v4/data"
    start_date = (datetime.now() - timedelta(days=160)).strftime('%Y-%m-%d')
    p = {"dataset": "TaiwanStockInstitutionalInvestorsBuySell", "data_id": stock_id, "start_date": start_date, "token": FINMIND_TOKEN}
    try:
        resp = requests.get(url, params=p); data = resp.json()
        if data['status'] == 200:
            raw_df = pd.DataFrame(data['data'])
            raw_df['net_buy'] = raw_df['buy'] - raw_df['sell']
            chips_df = raw_df.pivot_table(index='date', columns='name', values='net_buy', aggfunc='sum').fillna(0)
            chips_df.index = pd.to_datetime(chips_df.index).strftime('%Y-%m-%d')
            template = pd.DataFrame(index=pd.to_datetime(k_line_dates).strftime('%Y-%m-%d'))
            final = template.join(chips_df).fillna(0)
            dealer_cols = [c for c in final.columns if 'Dealer' in c]
            return (final.get('Foreign_Investor', [0]*len(k_line_dates))/1000).astype(int).tolist(), \
                   (final.get('Investment_Trust', [0]*len(k_line_dates))/1000).astype(int).tolist(), \
                   (final[dealer_cols].sum(axis=1)/1000).astype(int).tolist()
    except: pass
    return empty_res

def fetch_market_data():
    try:
        tk = yf.Ticker("^TWII"); df = tk.history(period="1y", auto_adjust=False)
        if not df.empty: df.index = df.index.tz_localize(None); return df
    except: pass
    return None

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
                news.append({"title": clean, "link": full_l});
                if len(news) >= 8: break
    except: pass
    return news

def get_chinese_name_from_web(full_sid):
    try:
        sid_only = str(full_sid).split('.')[0]
        url = f"https://tw.stock.yahoo.com/quote/{sid_only}"; headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=5)
        match = re.search(r'<title>(.*?)\(', resp.text)
        if match: return match.group(1).strip()
    except: pass
    return None

def load_portfolio(u):
    p = f"{USERS_DIR}/{u}_portfolio.json"
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f: return json.load(f)
    return {}

def save_portfolio(u, data):
    if not os.path.exists(USERS_DIR): os.makedirs(USERS_DIR)
    with open(f"{USERS_DIR}/{u}_portfolio.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_history(u):
    p = f"{USERS_DIR}/{u}_history.json"
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f: return json.load(f)
    return []

def save_history(u, data):
    with open(f"{USERS_DIR}/{u}_history.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def save_scan_result(u, result_df, name):
    if not os.path.exists(SCAN_RESULTS_DIR): os.makedirs(SCAN_RESULTS_DIR)
    fn = f"{SCAN_RESULTS_DIR}/{u}_{datetime.now().strftime('%Y%m%d')}_{name}.json"
    result_df.to_json(fn, orient="records", force_ascii=False)

def list_scan_history(u):
    if not os.path.exists(SCAN_RESULTS_DIR): return []
    return sorted([f for f in os.listdir(SCAN_RESULTS_DIR) if f.startswith(u)], reverse=True)
