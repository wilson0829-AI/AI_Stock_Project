import streamlit as st
import streamlit.components.v1 as components
from sidebar import render_sidebar
from data_utils import fetch_stock_history, get_chinese_name_from_web, fetch_stock_news
from indicators import calculate_all_indicators, calculate_trend_line_data
from charts import generate_stock_chart
from ui_components import render_price_header, render_ai_analysis_panel, render_sidebar_news
from ai_analyst import analyze_stock_trend, analyze_news_sentiment
from portfolio import render_portfolio_page
from market_view import render_market_view
import auth

st.set_page_config(page_title="專業 AI 選股系統 V3", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False;
    st.session_state.username = None;
    st.session_state.role = None

tabs_list = ["🏛️ 台股大盤概況", "🔍 個股專業分析", "💼 我的庫存股"]
if st.session_state.role == "admin": tabs_list.append("⚙️ 系統管理後台")

main_tabs = st.tabs(tabs_list)

with main_tabs[0]:
    render_market_view()

with main_tabs[1]:
    raw_stock_id, period = render_sidebar()
    df_raw, full_sid = fetch_stock_history(raw_stock_id)
    if df_raw is not None:
        df_ind = calculate_all_indicators(df_raw)
        p_map = {"1mo": 22, "3mo": 65, "6mo": 130, "1y": 250, "2y": 500}
        view_df = df_ind.tail(p_map.get(period, 22))
        trend_vals, slope = calculate_trend_line_data(view_df)
        ai_report = analyze_stock_trend(view_df, slope)
        raw_news = fetch_stock_news(raw_stock_id)
        analyzed_news, news_summary = analyze_news_sentiment(raw_news)

        render_price_header(get_chinese_name_from_web(full_sid) or full_sid, raw_stock_id, view_df.iloc[-1])
        render_ai_analysis_panel(ai_report)
        render_sidebar_news(analyzed_news, news_summary)

        # 修正：確保趨勢線與數據完整傳入
        chart_html = generate_stock_chart(get_chinese_name_from_web(full_sid) or full_sid, raw_stock_id, view_df,
                                          trend_vals)
        components.html(chart_html, height=1150)
    else:
        st.error(f"❌ 找不到股票 '{raw_stock_id}'。")

with main_tabs[2]:
    if not st.session_state.logged_in:
        st.title("🔐 庫存股監控 - 請登入")
        u = st.text_input("帳號", key="l_u");
        p = st.text_input("密碼", type="password", key="l_p")
        if st.button("登入"):
            success, role = auth.check_login(u, p)
            if success:
                st.session_state.logged_in = True;
                st.session_state.username = u;
                st.session_state.role = role;
                st.rerun()
            else:
                st.error("❌ 錯誤")
    else:
        render_portfolio_page()
