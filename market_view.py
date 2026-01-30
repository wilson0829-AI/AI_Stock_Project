import streamlit as st
import streamlit.components.v1 as components
from data_utils import fetch_market_data
from charts import generate_market_chart


def render_market_view():
    st.title("🏛️ 台股大盤看板")

    df_market = fetch_market_data()
    if df_market is not None:
        latest = df_market.iloc[-1]
        prev = df_market.iloc[-2]
        m_change = latest['Close'] - prev['Close']
        m_pct = (m_change / prev['Close']) * 100
        m_color = "#ef232a" if m_change >= 0 else "#14b143"

        st.markdown(f"""
            <div style="background-color:#111; padding:20px; border-radius:10px; border-left:10px solid {m_color}; margin-bottom:20px;">
                <span style="color:#FFF; font-size:20px;">加權指數 (^TWII)</span><br/>
                <span style="color:{m_color}; font-size:48px; font-weight:bold;">{latest['Close']:.2f}</span>
                <span style="color:{m_color}; font-size:24px; margin-left:20px;">{m_change:+.2f} ({m_pct:+.2f}%)</span>
            </div>
        """, unsafe_allow_html=True)

        # 渲染大盤圖表
        market_html = generate_market_chart(df_market)
        components.html(market_html, height=500)
    else:
        st.warning("⚠️ 大盤資料讀取中...")
