import streamlit as st
from data_utils import get_all_taiwan_stock_dict, get_chinese_name_from_web


def render_sidebar():
    """負責側邊欄的輸入控制項"""
    if st.session_state.get('logged_in'):
        st.sidebar.markdown(f"👤 **用戶：{st.session_state.username}**")
        if st.sidebar.button("登出系統"):
            st.session_state.logged_in = False;
            st.session_state.username = None;
            st.session_state.role = None;
            st.rerun()

    st.sidebar.header("⚙️ 個股搜尋")
    # --- 修正：預設門面改為台積電 ---
    if 'history' not in st.session_state:
        st.session_state.history = ["2330 台積電", "2317 鴻海", "2454 聯發科", "2603 長榮", "2609 陽明", "3006 晶豪科"]

    all_stocks = get_all_taiwan_stock_dict()
    search_input = st.sidebar.text_input("🔍 代號搜尋 (按 Enter)", key="search_box", value="")

    if search_input:
        search_input = search_input.strip()
        if search_input in all_stocks:
            stock_name = all_stocks[search_input]
        else:
            web_name = get_chinese_name_from_web(search_input)
            stock_name = web_name if web_name else "未知"
        new_entry = f"{search_input} {stock_name}"
        if new_entry in st.session_state.history: st.session_state.history.remove(new_entry)
        st.session_state.history.insert(0, new_entry)

    selected_option = st.sidebar.selectbox("📊 歷史紀錄", options=st.session_state.history, index=0)
    stock_id = selected_option.split(' ')[0]
    period = st.sidebar.selectbox("顯示期間", options=["1mo", "3mo", "6mo", "1y", "2y"], index=0)

    return stock_id, period
