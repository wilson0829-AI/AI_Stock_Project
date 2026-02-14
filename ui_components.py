import streamlit as st

def render_price_header(s_name, stock_id, latest):
    p = latest['Close']; c = latest['Change']; pc = latest['PctChange']
    o = latest['Open']; h = latest['High']; l = latest['Low']; v = int(latest['Volume'])
    color = "#ef232a" if c >= 0 else "#14b143"; sign = "+" if c >= 0 else ""
    st.markdown(f"""
        <div style="background-color: #000; padding: 10px 15px; border: 1px solid #333; border-radius: 4px; display: flex; align-items: center; gap: 20px; margin-bottom: 10px; font-family: monospace;">
            <div style="color: #FFF; font-size: 18px; font-weight: bold;">{s_name} ({stock_id})</div>
            <div style="color: {color}; font-size: 36px; font-weight: bold;">{p:.2f}</div>
            <div style="color: {color}; font-size: 16px;">{sign}{c:.2f}<br/>{sign}{pc:.2f}%</div>
            <div style="color: #CCC; font-size: 12px;">開<br/><span style="color:#FFF; font-size:14px;">{o:.2f}</span></div>
            <div style="color: #CCC; font-size: 12px;">高<br/><span style="color:#ef232a; font-size:14px;">{h:.2f}</span></div>
            <div style="color: #CCC; font-size: 12px;">低<br/><span style="color:#14b143; font-size:14px;">{l:.2f}</span></div>
            <div style="color: #CCC; font-size: 12px;">量<br/><span style="color:#FFFF00; font-size:14px;">{v:,}</span></div>
        </div>
    """, unsafe_allow_html=True)

def render_ai_analysis_panel(analysis):
    c = "#00FF00" if analysis['score'] >= 10 else "#FF4B4B"
    with st.expander("🤖 查看 AI 智慧分析報告", expanded=True):
        col1, col2 = st.columns([1, 2])
        col1.metric("AI 綜合評分", f"{analysis['score']} / 100")
        col1.markdown(f"### 評等: <span style='color:{c}'>{analysis['rating']}</span>", unsafe_allow_html=True)
        col2.write("**AI 分析摘要：**")
        for r in analysis['reasons']: col2.write(f"✅ {r}")

def render_sidebar_news(analyzed_news, summary):
    st.sidebar.write("---")
    st.sidebar.subheader(f"📰 新聞 ({summary})")
    for n in analyzed_news:
        st.sidebar.markdown(f"""
            <div style="margin-bottom: 10px; padding: 8px; border-left: 4px solid {n['color']}; background-color: #1a1a1a; border-radius: 4px;">
                <span style="background-color: {n['color']}; color: #FFF; padding: 1px 4px; border-radius: 3px; font-size: 10px;">{n['sentiment']}</span><br/>
                <a href="{n['link']}" target="_blank" style="color: #DDD; text-decoration: none; font-size: 12px;">{n['title']}</a>
            </div>
        """, unsafe_allow_html=True)
