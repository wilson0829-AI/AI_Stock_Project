import numpy as np


def analyze_stock_trend(df, slope):
    latest = df.iloc[-1];
    prev = df.iloc[-2];
    score = 0;
    reasons = []

    # 趨勢線
    if slope > 0:
        score += 20; reasons.append(f"趨勢向上 (斜率:{round(slope, 2)})")
    else:
        score -= 15; reasons.append("趨勢向下")

    # 月線
    if latest['Close'] > latest['SMA20']:
        score += 20; reasons.append("站上月線")
    else:
        score -= 15; reasons.append("跌破月線")

    # KD
    if prev['K'] <= prev['D'] and latest['K'] > latest['D']: score += 20; reasons.append("KD黃金交叉")

    # --- 新增 MACD 評分 (權重提高) ---
    if latest['MACD_HIST'] > 0:
        score += 20
        reasons.append("MACD 柱狀體翻紅 (多頭攻擊)")
    if prev['MACD_HIST'] < 0 and latest['MACD_HIST'] > 0:
        score += 15
        reasons.append("MACD 剛由綠翻紅 (起漲點預警)")

    if score >= 40:
        rating = "強烈建議買進"
    elif 10 <= score < 40:
        rating = "持有/觀望"
    else:
        rating = "避開/減碼"

    return {"rating": rating, "score": score, "prediction": "看漲" if slope > 0 else "看跌", "reasons": reasons,
            "target_slope": round(float(slope), 2)}


# analyze_news_sentiment 維持不變...
def analyze_news_sentiment(news_list):
    bullish = ['利多', '創高', '接單', '轉盈', '增長', '看好', '買進', '漲停']
    bearish = ['利空', '衰退', '下修', '虧損', '賣出', '跌停']
    analyzed = [];
    b_count = 0;
    s_count = 0
    for item in news_list:
        t = item['title'];
        s = "中性";
        c = "#CCC"
        for k in bullish:
            if k in t: s = "利多"; c = "#ef232a"; b_count += 1; break
        if s == "中性":
            for k in bearish:
                if k in t: s = "利空"; c = "#14b143"; s_count += 1; break
        analyzed.append({"title": t, "link": item['link'], "sentiment": s, "color": c})
    sum_txt = "消息偏利多" if b_count > s_count else ("消息偏利空" if s_count > b_count else "消息平淡")
    return analyzed, sum_txt
