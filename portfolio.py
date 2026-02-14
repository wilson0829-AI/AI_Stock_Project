import streamlit as st
from datetime import datetime
import pandas as pd
from data_user import load_portfolio, save_portfolio, load_history, save_history
from data_fetcher import fetch_stock_history
from data_news import get_chinese_name_from_web
from indicators import calculate_all_indicators, calculate_trend_line_data
from ai_analyst import analyze_stock_trend


def fees(p, s, side, sid=""):
    a = p * s;
    f = max(20, round(a * 0.001425))
    if side == "buy": return a + f
    t = round(a * (0.001 if sid.startswith("00") else 0.003));
    return a - f - t


def render_portfolio_page():
    u = st.session_state.username;
    st.title(f"💼 {u} 的庫存中心")
    port = load_portfolio(u);
    hist = load_history(u)
    t1, t2 = st.tabs(["📈 持股監控", "📜 實現績效"])

    with t1:
        with st.expander("➕ 新增持股", expanded=False):
            c1, c2, c3, c4 = st.columns(4)
            nid = c1.text_input("代號");
            d = c2.date_input("日期", datetime.now())
            p = c3.number_input("單價", min_value=0.0);
            s = c4.number_input("股數", value=1000)
            if st.button("確認加入"):
                port[nid] = {"date": str(d), "cost_price": p, "shares": s}
                save_portfolio(u, port);
                st.rerun()

        if not port:
            st.info("無持股資料")
        else:
            total_c, total_v = 0, 0
            st.markdown(
                """<div style="background:#333;padding:8px;border-radius:4px;display:flex;font-weight:bold;color:#FFF;font-size:13px;"><div style="flex:1.5;">股票/日期</div><div style="flex:1.2;">現價/成本</div><div style="flex:2.0;">總成本/現值</div><div style="flex:1.2;">損益</div><div style="flex:0.5;">操作</div></div>""",
                unsafe_allow_html=True)
            for sid, i in list(port.items()):
                df, _ = fetch_stock_history(sid)
                if df is not None:
                    df = calculate_all_indicators(df);
                    l = df.iloc[-1]
                    cp = round(float(l['Close']), 2);
                    bp = i['cost_price'];
                    sh = i['shares']
                    rc = fees(bp, sh, "buy");
                    rv = fees(cp, sh, "sell", sid)
                    pl = rv - rc;
                    plp = (pl / rc * 100) if rc > 0 else 0
                    total_c += rc;
                    total_v += rv;
                    p_co = "#ef232a" if pl >= 0 else "#14b143"

                    st.markdown(f"""<div style="border-bottom:1px solid #eee; margin-bottom:-10px;"></div>""",
                                unsafe_allow_html=True)
                    cols = st.columns([1.5, 1.2, 2.0, 1.2, 0.5])
                    cols[0].markdown(f"**{sid}**<br/><span style='font-size:10px;color:#888;'>{i['date']}</span>",
                                     unsafe_allow_html=True)
                    cols[1].markdown(
                        f"<span style='color:{p_co};font-weight:bold;'>{cp}</span><br/><span style='color:black;font-size:11px;'>{bp}</span>",
                        unsafe_allow_html=True)
                    cols[2].markdown(
                        f"成:{rc:,.0f}<br/><span style='color:#E6B800;font-weight:bold;'>現:{rv:,.0f}</span>",
                        unsafe_allow_html=True)
                    cols[3].markdown(
                        f"<span style='color:{p_co};font-weight:bold;'>{pl:,.0f}</span><br/><span style='color:{p_co};font-size:11px;'>{plp:.2f}%</span>",
                        unsafe_allow_html=True)
                    if cols[4].button("🗑️", key=f"d_{sid}"): del port[sid]; save_portfolio(u, port); st.rerun()

            st.markdown("<div style='margin-top:20px;border-top:2px solid #333;'></div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("投入成本", f"{total_c:,.0f}");
            c2.metric("當前價值", f"{total_v:,.0f}");
            c3.metric("總盈虧", f"{total_v - total_c:,.0f}")
