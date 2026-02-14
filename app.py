import streamlit as st
import streamlit.components.v1 as components
from sidebar import render_sidebar
from data_fetcher import fetch_stock_history, fetch_chips_data
from data_news import fetch_stock_news, get_chinese_name_from_web
from indicators import calculate_all_indicators, calculate_trend_line_data
from charts_market import generate_market_chart
from charts_technical import generate_stock_chart
from charts_chips import generate_chips_chart
from ui_components import render_price_header, render_ai_analysis_panel, render_sidebar_news
from ui_chips_table import render_chips_statistical_table
from ai_analyst import analyze_stock_trend, analyze_news_sentiment
from portfolio import render_portfolio_page
from market_view import render_market_view
from smart_scanner import run_smart_scanner
import auth

# 設定頁面配置
st.set_page_config(page_title="專業 AI 選股系統 V4", layout="wide")

# 分頁清單
tabs_list = ["🏛️ 台股大盤概況", "🔍 個股專業分析", "👤 法人籌碼分析", "🤖 智慧選股", "💼 我的庫存股"]

# 初始化狀態
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = tabs_list[0]
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 管理者權限
if st.session_state.get('role') == "admin" and "⚙️ 系統管理後台" not in tabs_list:
    tabs_list.append("⚙️ 系統管理後台")

# --- 側邊欄導覽 (Radio 強制同步版) ---
st.sidebar.title("🚀 功能導覽")
try:
    start_idx = tabs_list.index(st.session_state.current_tab)
except:
    start_idx = 1  # 預設個股分析

selected_tab = st.sidebar.radio("前往頁面", tabs_list, index=start_idx)
st.session_state.current_tab = selected_tab

# --- 分頁渲染邏輯 ---
if selected_tab in ["🔍 個股專業分析", "👤 法人籌碼分析"]:
    raw_stock_id, period = render_sidebar()
    df_raw, full_sid = fetch_stock_history(raw_stock_id)
    if df_raw is not None:
        s_name = get_chinese_name_from_web(full_sid) or full_sid
        df_ind = calculate_all_indicators(df_raw)
        p_map = {"1mo": 22, "3mo": 65, "6mo": 130, "1y": 250, "2y": 500}
        view_df = df_ind.tail(p_map.get(period, 22))

        render_price_header(s_name, raw_stock_id, view_df.iloc[-1])

        if selected_tab == "🔍 個股專業分析":
            trend_vals, slope = calculate_trend_line_data(view_df)
            render_ai_analysis_panel(analyze_stock_trend(view_df, slope))
            raw_news = fetch_stock_news(raw_stock_id)
            n_data = analyze_news_sentiment(raw_news)
            render_sidebar_news(n_data[0], n_data[1])
            components.html(generate_stock_chart(s_name, raw_stock_id, view_df, trend_vals), height=1150)

        elif selected_tab == "👤 法人籌碼分析":
            k_dates = view_df.index.strftime('%Y-%m-%d').tolist()
            f, t, d = fetch_chips_data(raw_stock_id, k_dates)
            components.html(generate_chips_chart(s_name, raw_stock_id, k_dates, f, t, d), height=760)
            render_chips_statistical_table(k_dates, view_df['Close'].tolist(), view_df['Change'].tolist(), f, t, d)
    else:
        st.warning("🏮 資料獲取中，請稍候。")

elif selected_tab == "🏛️ 台股大盤概況":
    render_market_view()

elif selected_tab == "🤖 智慧選股":
    run_smart_scanner()

elif selected_tab == "💼 我的庫存股":
    if not st.session_state.logged_in:
        st.title("🔐 庫存管理 - 請登入")
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
                st.error("❌ 帳號密碼錯誤")
    else:
        render_portfolio_page()

elif selected_tab == "⚙️ 系統管理後台":
    st.title("👨‍💼 管理員後台")
    # 管理員相關邏輯...
