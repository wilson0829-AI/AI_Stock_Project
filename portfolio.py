import streamlit as st
from datetime import datetime
from data_utils import load_portfolio, save_portfolio, load_history, save_history, fetch_stock_history, get_chinese_name_from_web
from indicators import calculate_all_indicators, calculate_trend_line_data
from ai_analyst import analyze_stock_trend

def calculate_tw_fees(p, s, side, sid=""):
    amt = p * s; fee = max(20, round(amt * 0.001425))
    if side == "buy": return amt + fee
    tax = round(amt * (0.001 if sid.startswith("00") else 0.003))
    return amt - fee - tax

def render_portfolio_page():
    u = st.session_state.username; st.title(f"💼 {u} 的庫存監控")
    port = load_portfolio(u); hist = load_history(u)
    t1, t2 = st.tabs(["在庫持股", "歷史戰績"])
    with t1:
        with st.expander("➕ 新增資產"):
            c1, c2, c3, c4 = st.columns(4)
            nid = c1.text_input("代號"); d = c2.date_input("日期"); p = c3.number_input("價格"); s = c4.number_input("股數", value=1000)
            if st.button("加入"): port[nid] = {"date":str(d), "cost_price":p, "shares":s}; save_portfolio(u, port); st.rerun()
        for sid, info in list(port.items()):
            df, _ = fetch_stock_history(sid)
            if df is not None:
                df = calculate_all_indicators(df); l = df.iloc[-1]; cp = round(float(l['Close']), 2); bp = info['cost_price']; sh = info['shares']
                rc = calculate_tw_fees(bp, sh, "buy"); rv = calculate_tw_fees(cp, sh, "sell", sid); pl = rv - rc; plp = (pl/rc*100)
                st.markdown(f"**{sid}** 現價:{cp} | 成本:{bp} | 股數:{sh} | 損益:<span style='color:{'red' if pl>=0 else 'green'}'>{pl:,.0f} ({plp:.2f}%)</span>", unsafe_allow_html=True)
                if st.button("🗑️ 刪除", key=f"d_{sid}"): del port[sid]; save_portfolio(u, port); st.rerun()
    with t2: st.write("實現獲利紀錄顯示於此...")
