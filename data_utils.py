import yfinance as yf
import requests
import re
import pandas as pd
import streamlit as st
import json
import os

USERS_DIR = "users"

@st.cache_data(ttl=86400)
def get_all_taiwan_stock_dict():
    try:
        url = "https://raw.githubusercontent.com/finmind/FinMindData/master/TaiwanStockInfo.csv"
        df = pd.read_csv(url)
        return dict(zip(df['stock_id'].astype(str), df['stock_name']))
    except:
        return {"2603": "長榮", "2330": "台積電", "2609": "陽明", "3006": "晶豪科"}

@st.cache_data(ttl=3600)
def get_chinese_name_from_web(full_sid):
    try:
        sid_only = str(full_sid).split('.')[0]
        url = f"https://tw.stock.yahoo.com/quote/{sid_only}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'utf-8'
        match = re.search(r'<title>(.*?)\(', response.text)
        if match: return match.group(1).strip()
    except: pass
    return None

def fetch_stock_history(sid_raw):
    target_sid = f"{sid_raw}.TW"
    tk = yf.Ticker(target_sid)
    df = tk.history(period="2y", auto_adjust=False)
    if df.empty or len(df) < 5:
        target_sid = f"{sid_raw}.TWO"
        tk = yf.Ticker(target_sid); df = tk.history(period="2y", auto_adjust=False)
    if not df.empty:
        df.index = df.index.tz_localize(None)
        return df, target_sid
    return None, None

def fetch_market_data():
    """抓取加權指數"""
    try:
        tk = yf.Ticker("^TWII")
        df = tk.history(period="1y", auto_adjust=False)
        if not df.empty:
            df.index = df.index.tz_localize(None)
            return df
    except: pass
    return None

@st.cache_data(ttl=600)
def fetch_stock_news(stock_id):
    news_list = []
    try:
        url = f"https://tw.stock.yahoo.com/quote/{stock_id}/news"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        blacklist = ['Yahoo', 'App', '下載', '服務說明', '廣告']
        pattern = r'href="([^"]*news/[^"]*)"[^>]*>.*?<h3[^>]*>(.*?)</h3>'
        matches = re.findall(pattern, response.text, re.DOTALL)
        for link, title in matches:
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            if any(word in clean_title for word in blacklist): continue
            full_link = link if "https" in link else "https://tw.stock.yahoo.com" + link
            if not any(n['title'] == clean_title for n in news_list):
                news_list.append({"title": clean_title, "link": full_link})
                if len(news_list) >= 8: break
    except: pass
    return news_list

def get_user_file_path(username, file_type="portfolio"):
    if not os.path.exists(USERS_DIR): os.makedirs(USERS_DIR)
    return f"{USERS_DIR}/{username}_{file_type}.json"

def load_portfolio(username):
    path = get_user_file_path(username, "portfolio")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_portfolio(username, portfolio):
    path = get_user_file_path(username, "portfolio")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(portfolio, f, indent=4, ensure_ascii=False)

def load_history(username):
    path = get_user_file_path(username, "history")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def save_history(username, history):
    path = get_user_file_path(username, "history")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
