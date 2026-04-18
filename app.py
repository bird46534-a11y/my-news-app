import streamlit as st
import requests
import xml.etree.ElementTree as ET
import datetime
import pandas as pd
from dateutil import parser
import math
import plotly.express as px

# --- 網頁配置 (針對手機優化) ---
st.set_page_config(page_title="趨勢推演", layout="centered") # 使用 centered 讓內容更集中

# 自定義 CSS 讓介面更像 App
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 1rem; }
    .news-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #ccc;
    }
    .pos-card { border-left: 5px solid #28a745; background-color: #f0fff4; }
    .neg-card { border-left: 5px solid #dc3545; background-color: #fff5f5; }
    .news-title { font-size: 16px; font-weight: bold; margin-bottom: 5px; color: #1e1e1e; }
    .news-meta { font-size: 12px; color: #666; }
    .tag-label { font-size: 12px; padding: 2px 6px; border-radius: 4px; background: #eee; }
    </style>
    """, unsafe_allow_html=True)

class DataScout:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def fetch_news(self, topic, days_limit=5):
        url = f"https://news.google.com/rss/search?q={topic}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        now = datetime.datetime.now(datetime.timezone.utc)
        news_list = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title').text
                pub_date = parser.parse(item.find('pubDate').text)
                days_ago = (now - pub_date).total_seconds() / 86400
                if days_ago <= days_limit:
                    weight = round(math.exp(-0.2 * days_ago), 2)
                    news_list.append({
                        "標題": title,
                        "日期": pub_date.astimezone(datetime.timezone(datetime.timedelta(hours=8))),
                        "權重": weight
                    })
            return pd.DataFrame(news_list)
        except: return pd.DataFrame()

class AnalyticsEngine:
    KWS = {
        "🔴極負": (['崩盤', '破產', '開戰', '倒閉', '災難', '暴跌'], -5.0),
        "🟠負面": (['跌', '慘', '危機', '裁員', '爭議', '糾紛', '警告'], -2.5),
        "🟢正面": (['升', '獲利', '突破', '合作', '補助', '進步', '漲'], 2.0),
        "🔵極正": (['新高', '成功', '冠軍', '翻倍', '奇蹟', '爆發'], 4.5)
    }
    @classmethod
    def analyze(cls, title):
        score, tags = 0, []
        for label, (keywords, val) in cls.KWS.items():
            for word in keywords:
                if word in title:
                    score += val
                    tags.append(label)
                    break 
        return score, (tags[0] if tags else "⚪中性")

# --- UI 介面 ---
st.title("🔮 趨勢推演引擎")
target = st.text_input("輸入目標", placeholder="例如：比特幣")

if target:
    with st.spinner('分析中...'):
        df = DataScout().fetch_news(target)

        if not df.empty:
            results = df.apply(lambda x: AnalyticsEngine.analyze(x['標題']), axis=1)
            df['評分'], df['性質'] = zip(*results)
            df['動能'] = df['評分'] * df['權重']
            
            # 指標看板
            total_score = df['動能'].sum()
            st.metric("綜合動能指數", f"{total_score:.2f}")

            # 推演結論 (簡化版適合手機閱讀)
            if total_score < -15: st.error("🚩 威脅：風險極高，建議避險。")
            elif total_score > 10: st.success("🏳️ 機遇：情緒向好，建議關注。")
            else: st.info("🏴 盤整：多空拉鋸，動能不足。")

            # --- 核心優化：手機卡片式列表 ---
            st.subheader("📜 關鍵動態")
            for _, row in df.sort_values('日期', ascending=False).iterrows():
                # 根據性質決定卡片顏色
                card_class = "news-card"
                if "正" in row['性質']: card_class += " pos-card"
                elif "負" in row['性質']: card_class += " neg-card"
                
                # HTML 渲染卡片
                st.markdown(f"""
                    <div class="{card_class}">
                        <div class="news-meta">
                            <span class="tag-label">{row['性質']}</span> | {row['日期'].strftime('%m-%d %H:%M')}
                        </div>
                        <div class="news-title">{row['標題']}</div>
                        <div class="news-meta">影響權重: {row['權重']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("查無數據。")
