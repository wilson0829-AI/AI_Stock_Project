import yfinance as yf
import requests, pandas as pd, streamlit as st
from datetime import datetime, timedelta
from token_config import FINMIND_TOKEN

@st.cache_data(ttl=86400)
def get_all_taiwan_stock_dict():
    stock_dict = {}
    try:
        url = "https://raw.githubusercontent.com/ycm666/TaiwanStockList/master/stock_info.csv"
        df = pd.read_csv(url, encoding='utf-8')
        df['code'] = df['code'].astype(str)
        stock_dict = dict(zip(df['code'], df['name']))
    except: pass
    # 鋼鐵級校正：1414 東和紡織, 2006 東和鋼鐵
    corrections = {"2006": "東和鋼鐵", "1414": "東和紡織", "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "1303": "南亞", "2891": "中信金"}
    stock_dict.update(corrections)
    return stock_dict

def fetch_stock_history(sid_raw):
    try:
        target_sid = f"{sid_raw}.TW"
        tk = yf.Ticker(target_sid); df = tk.history(period="2y", auto_adjust=False)
        if df.empty:
            target_sid = f"{sid_raw}.TWO"; tk = yf.Ticker(target_sid); df = tk.history(period="2y", auto_adjust=False)
        if not df.empty:
            df.index = df.index.tz_localize(None); return df, target_sid
    except: pass
    return None, None

@st.cache_data(ttl=3600)
def fetch_chips_data(stock_id, k_line_dates):
    if not FINMIND_TOKEN or "請在此處" in FINMIND_TOKEN: return [0]*len(k_line_dates), [0]*len(k_line_dates), [0]*len(k_line_dates)
    url = "https://api.finmindtrade.com/api/v4/data"
    start = (datetime.now() - timedelta(days=160)).strftime('%Y-%m-%d')
    p = {"dataset": "TaiwanStockInstitutionalInvestorsBuySell", "data_id": stock_id, "start_date": start, "token": FINMIND_TOKEN}
    try:
        resp = requests.get(url, params=p); data = resp.json()
        if data['status'] == 200:
            raw = pd.DataFrame(data['data']); raw['net_buy'] = raw['buy'] - raw['sell']
            chips = raw.pivot_table(index='date', columns='name', values='net_buy', aggfunc='sum').fillna(0)
            chips.index = pd.to_datetime(chips.index).strftime('%Y-%m-%d')
            template = pd.DataFrame(index=pd.to_datetime(k_line_dates).strftime('%Y-%m-%d'))
            final = template.join(chips).fillna(0)
            dealer_cols = [c for c in final.columns if 'Dealer' in c]
            return (final.get('Foreign_Investor', [0]*len(k_line_dates))/1000).astype(int).tolist(), \
                   (final.get('Investment_Trust', [0]*len(k_line_dates))/1000).astype(int).tolist(), \
                   (final[dealer_cols].sum(axis=1)/1000).astype(int).tolist()
    except: pass
    return [0]*len(k_line_dates), [0]*len(k_line_dates), [0]*len(k_line_dates)

def fetch_market_data():
    try:
        tk = yf.Ticker("^TWII"); df = tk.history(period="1y", auto_adjust=False)
        if not df.empty: df.index = df.index.tz_localize(None); return df
    except: pass
    return None
