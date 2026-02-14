import streamlit as st
import pandas as pd


def render_chips_statistical_table(dates, close_prices, changes, foreign, trust, dealer):
    """
    渲染法人籌碼多週期統計表 (新增：本期總合計)
    """
    st.write("---")
    st.subheader("📊 法人多週期累計買賣超 (張)")

    # 1. 定義統計週期
    periods = [5, 10, 15, 20, 25, 30]
    summary_data = []
    data_len = len(foreign)

    # 2. 計算各週期累計
    for p in periods:
        actual_p = min(p, data_len)
        f_sum = sum(foreign[-actual_p:])
        t_sum = sum(trust[-actual_p:])
        d_sum = sum(dealer[-actual_p:])
        total_sum = f_sum + t_sum + d_sum

        summary_data.append({
            "統計週期": f"近 {p} 日累計",
            "外資累計": f_sum,
            "投信累計": t_sum,
            "自營累計": d_sum,
            "三大法人合計": total_sum
        })

    # --- 核心新增：計算本期總合計 (整段顯示期間的加總) ---
    f_total = sum(foreign)
    t_total = sum(trust)
    d_total = sum(dealer)
    all_total = f_total + t_total + d_total

    summary_data.append({
        "統計週期": "🚩 本期總合計",  # 用符號標示
        "外資累計": f_total,
        "投信累計": t_total,
        "自營累計": d_total,
        "三大法人合計": all_total
    })

    df_summary = pd.DataFrame(summary_data)

    # 3. 定義顏色邏輯
    def color_stat_values(val):
        if isinstance(val, (int, float)):
            if val > 0: return 'color: #ef232a; font-weight: bold;'
            if val < 0: return 'color: #14b143; font-weight: bold;'
        return 'color: #CCC;'

    # 4. 顯示累計統計表
    st.dataframe(
        df_summary.style.map(color_stat_values, subset=["外資累計", "投信累計", "自營累計", "三大法人合計"]),
        column_config={
            "統計週期": st.column_config.TextColumn("週期名稱"),
            "外資累計": st.column_config.NumberColumn("外資 (張)", format="%d"),
            "投信累計": st.column_config.NumberColumn("投信 (張)", format="%d"),
            "自營累計": st.column_config.NumberColumn("自營 (張)", format="%d"),
            "三大法人合計": st.column_config.NumberColumn("合計 (張)", format="%d"),
        },
        use_container_width=True,
        hide_index=True
    )

    st.write("")
    st.subheader("📋 每日法人買賣明細")

    # 5. 準備每日明細資料
    data = {
        "日期": dates,
        "收盤價": close_prices,
        "漲跌": changes,
        "外資(張)": foreign,
        "投信(張)": trust,
        "自營商(張)": dealer
    }

    df_daily = pd.DataFrame(data)
    df_daily["合計(張)"] = df_daily["外資(張)"] + df_daily["投信(張)"] + df_daily["自營商(張)"]

    # 轉為倒序 (最新日期在最上面)
    df_daily = df_daily.iloc[::-1].reset_index(drop=True)

    # 6. 渲染每日明細表
    st.dataframe(
        df_daily.style.map(lambda x: 'color: #ef232a; font-weight: bold;' if x > 0 else (
            'color: #14b143; font-weight: bold;' if x < 0 else 'color: #CCC;'),
                           subset=["漲跌", "外資(張)", "投信(張)", "自營商(張)", "合計(張)"]),
        column_config={
            "日期": st.column_config.TextColumn("日期"),
            "收盤價": st.column_config.NumberColumn("收盤價", format="%.2f"),
            "漲跌": st.column_config.NumberColumn("漲跌", format="%+.2f"),
            "外資(張)": st.column_config.NumberColumn("外資", format="%d"),
            "投信(張)": st.column_config.NumberColumn("投信", format="%d"),
            "自營商(張)": st.column_config.NumberColumn("自營", format="%d"),
            "合計(張)": st.column_config.NumberColumn("合計", format="%d"),
        },
        use_container_width=True,
        height=400,
        hide_index=True
    )
