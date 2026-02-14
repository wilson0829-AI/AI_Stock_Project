import streamlit as st
import streamlit.components.v1 as components
from data_utils import fetch_market_data
# 修正處：指向新的獨立大盤圖表檔
from charts_market import generate_market_chart


def render_market_view():
    st.title("🏛️ 台股大盤概況")

    # 1. 大盤走勢圖
    df_market = fetch_market_data()
    if df_market is not None:
        latest = df_market.iloc[-1]
        prev = df_market.iloc[-2]
        m_change = latest['Close'] - prev['Close']
        m_pct = (m_change / prev['Close']) * 100
        m_color = "#ef232a" if m_change >= 0 else "#14b143"

        st.markdown(f"""
            <div style="background-color:#111; padding:15px; border-radius:5px; border-left:8px solid {m_color}; margin-bottom:10px;">
                <span style="color:#FFF; font-size:18px;">加權指數 (^TWII)</span><br/>
                <span style="color:{m_color}; font-size:36px; font-weight:bold;">{latest['Close']:.2f}</span>
                <span style="color:{m_color}; font-size:20px; margin-left:15px;">{m_change:+.2f} ({m_pct:+.2f}%)</span>
            </div>
        """, unsafe_allow_html=True)

        market_html = generate_market_chart(df_market)
        components.html(market_html, height=480)
    else:
        st.info("📊 正在連接交易所，請稍候...")
