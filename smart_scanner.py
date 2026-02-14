import streamlit as st
import pandas as pd
import yfinance as yf
import time
from indicators import calculate_all_indicators
from data_fetcher import get_all_taiwan_stock_dict, fetch_chips_data
from data_news import get_chinese_name_from_web
from data_scanner import save_scan_result, list_scan_history


def run_smart_scanner():
    username = st.session_state.get('username', 'guest')
    st.title("🤖 AI 智慧選股機器人 V4")

    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        st.subheader("🛠️ 選股公式庫")
        f_trend = st.checkbox("股價 > 多空線 (MA25)", value=True)
        f_kd = st.checkbox("KD 黃金交叉", value=True)
        f_macd = st.checkbox("MACD 柱狀體翻紅", value=False)
        f_foreign = st.checkbox("外資連續 2 日買超", value=False)
        f_trust = st.checkbox("投信今日買超", value=False)
        vol_limit = st.number_input("成交量門檻 (張)", value=1000, step=500)

    with col_right:
        st.subheader("📋 組合清單")
        scan_target = st.selectbox("掃描範圍", ["台股 50 成分股", "中型 100 成分股", "自訂追蹤清單"])

        if st.button("🚀 開始全自動暴力選股"):
            all_stocks = get_all_taiwan_stock_dict()
            if scan_target == "台股 50 成分股":
                codes = ["2330", "2317", "2454", "2603", "2609", "2881", "2882", "2308", "2382", "2412", "2303", "1301",
                         "1303", "2006"]
            elif scan_target == "中型 100 成分股":
                codes = ["2618", "2610", "2371", "3006", "2409", "3481", "2324", "2353"]
            else:
                codes = ["2330", "2317", "2454", "2603", "2609", "3006", "8046", "1414"]

            results = []
            progress = st.progress(0)
            yf_codes = [f"{c}.TW" for c in codes]
            data = yf.download(yf_codes, period="1y", group_by='ticker', auto_adjust=False, threads=True,
                               progress=False)
            time.sleep(1)

            for i, sid in enumerate(codes):
                try:
                    df = data[f"{sid}.TW"].copy()
                    if df.empty: continue
                    df = calculate_all_indicators(df);
                    today = df.iloc[-1];
                    yest = df.iloc[-2]
                    match = True
                    if today['Volume'] / 1000 < vol_limit: match = False
                    if f_trend and today['Close'] < today['LongShortLine']: match = False
                    if f_kd and today['K'] <= today['D']: match = False
                    if f_macd and today['MACD_HIST'] <= 0: match = False
                    if match and (f_foreign or f_trust):
                        k_dates = df.tail(5).index.strftime('%Y-%m-%d').tolist()
                        f_list, t_list, _ = fetch_chips_data(sid, k_dates)
                        if f_foreign and not (f_list[-1] > 0 and f_list[-2] > 0): match = False
                        if f_trust and t_list[-1] <= 0: match = False
                    if match:
                        name = all_stocks.get(sid) or get_chinese_name_from_web(sid) or sid
                        results.append({"股票代號": sid, "名稱": name, "收盤價": round(float(today['Close']), 2),
                                        "幅度": f"{round(float(today['PctChange']), 2)}%", "K": round(today['K'], 1),
                                        "MACD": round(today['MACD_HIST'], 2)})
                except:
                    continue
                progress.progress((i + 1) / len(codes))
            st.session_state.scan_results = pd.DataFrame(results)
            st.rerun()

    if st.session_state.get('scan_results') is not None:
        df_res = st.session_state.scan_results
        st.success(f"🎯 發現：{len(df_res)} 支")

        c1, c2 = st.columns([3, 1])
        s_name = c1.text_input("存檔名稱", value="績優選股")
        if c2.button("💾 儲存"):
            save_scan_result(username, df_res, s_name);
            st.toast("已存檔")

        sel = st.dataframe(df_res, use_container_width=True, hide_index=True, on_select="rerun",
                           selection_mode="single-row")
        if sel and sel.selection.rows:
            row = df_res.iloc[sel.selection.rows[0]]
            st.session_state.search_box_val = row["股票代號"]
            st.session_state.current_tab = "🔍 個股專業分析"
            st.rerun()

    st.write("---")
    st.subheader("📂 歷史紀錄")
    hist = list_scan_history(username)
    if hist:
        f = st.selectbox("選擇檔案", options=hist)
        if st.button("👁️ 載入"):
            st.session_state.scan_results = pd.read_json(f"users/scan_history/{f}");
            st.rerun()
