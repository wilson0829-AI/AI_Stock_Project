import streamlit as st
from data_fetcher import get_all_taiwan_stock_dict
from data_news import get_chinese_name_from_web


def render_sidebar():
    if st.session_state.get('logged_in'):
        st.sidebar.markdown(f"👤 **目前用戶：{st.session_state.username}**")
        if st.sidebar.button("登出系統"):
            st.session_state.logged_in = False;
            st.session_state.username = None;
            st.rerun()

    st.sidebar.header("⚙️ 個股分析設定")
    if 'history' not in st.session_state:
        st.session_state.history = ["2330 台積電", "2454 聯發科", "2317 鴻海", "2603 長榮", "3006 晶豪科"]

    all_stocks = get_all_taiwan_stock_dict()

    # 同步智慧選股跳轉過來的數值
    val = st.session_state.get('search_box_val', '')
    search_input = st.sidebar.text_input("🔍 代號搜尋 (按 Enter)", value=val, key="search_box")

    if search_input and search_input != st.session_state.get('search_box_val', ''):
        search_input = search_input.strip()
        stock_name = all_stocks.get(search_input) or get_chinese_name_from_web(search_input) or "未知"
        new_entry = f"{search_input} {stock_name}"
        if new_entry in st.session_state.history: st.session_state.history.remove(new_entry)
        st.session_state.history.insert(0, new_entry)
        st.session_state.search_box_val = search_input

    selected_option = st.sidebar.selectbox("📊 歷史紀錄", options=st.session_state.history, index=0)
    stock_id = selected_option.split(' ')[0]
    period = st.sidebar.selectbox("顯示期間", options=["1mo", "3mo", "6mo", "1y", "2y"], index=0)

    return stock_id, period
