import streamlit as st
import requests
import xml.etree.ElementTree as ET
import datetime
import pandas as pd
from dateutil import parser
import math

# --- 網頁配置 (App 化) ---
st.set_page_config(page_title="全球新聞情報站", layout="centered")

# 自定義手機版 CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .search-header { font-size: 24px; font-weight: 800; color: #1a73e8; margin-bottom: 20px; }
    .news-card {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .pos-tag { color: #28a745; font-weight: bold; }
    .neg-tag { color: #dc3545; font-weight: bold; }
    .neu-tag { color: #6c757d; font-weight: bold; }
    .time-text { font-size: 12px; color: #888; margin-bottom: 4px; }
    .title-text { font-size: 16px; font-weight: 600; color: #202124; line-height: 1.4; }
    </style>
    """, unsafe_allow_html=True)

class NewsEngine:
    @staticmethod
    def get_news(topic):
        url = f"https://news.google.com/rss/search?q={topic}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        headers = {'User-Agent': 'Mozilla/5.0'}
        news_data = []
        try:
            r = requests.get(url, headers=headers, timeout=10)
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:30]: # 取前30則最相關
                title = item.find('title').text
                pub_date = parser.parse(item.find('pubDate').text).astimezone(datetime.timezone(datetime.timedelta(hours=8)))
                news_data.append({"title": title, "date": pub_date})
            return news_data
        except: return []

    @staticmethod
    def quick_analyze(title):
        # 簡易語義判斷
        pos = ['漲', '升', '獲利', '突破', '合作', '支持', '新高', '優於預期']
        neg = ['跌', '慘', '危機', '裁員', '爭議', '崩盤', '警告', '壓力']
        for w in neg: 
            if w in title: return "🔴 負面趨勢", "neg-tag"
        for w in pos: 
            if w in title: return "🟢 正面動能", "pos-tag"
        return "⚪ 中性訊息", "neu-tag"

# --- UI 介面 ---
st.markdown('<div class="search-header">📰 全球情報搜尋</div>', unsafe_allow_html=True)

# 搜尋列
query = st.text_input("", placeholder="🔍 輸入關鍵字（如：台積電、原油、AI...）")

# 快捷標籤
st.caption("熱門搜尋：美股、比特幣、黃金、加權指數")

if query:
    data = NewsEngine.get_news(query)
    
    if data:
        # 計算簡易指標
        pos_count = 0
        neg_count = 0
        
        # 預處理分析
        for n in data:
            label, _ = NewsEngine.quick_analyze(n['title'])
            if "正面" in label: pos_count += 1
            if "負面" in label: neg_count += 1
        
        # 能量儀表板
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"📊 搜尋結果: {len(data)} 則")
        with col2:
            sentiment_score = pos_count - neg_count
            emo = "📈" if sentiment_score > 0 else "📉" if sentiment_score < 0 else "⚖️"
            st.write(f"動態情緒: {emo}")

        st.divider()

        # 新聞列表
        for n in data:
            label, tag_class = NewsEngine.quick_analyze(n['title'])
            st.markdown(f"""
                <div class="news-card">
                    <div class="time-text">{n['date'].strftime('%Y-%m-%d %H:%M')}</div>
                    <div class="title-text">{n['title']}</div>
                    <div style="margin-top:8px;">
                        <span class="{tag_class}" style="font-size:12px;">{label}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("尚未搜尋到相關即時新聞。")
else:
    # 初始歡迎畫面
    st.markdown("""
    <div style="text-align: center; color: #888; margin-top: 50px;">
        <p>請在上方輸入關鍵字開始搜尋</p>
        <p style="font-size: 12px;">系統將自動分析近期的市場情緒與趨勢</p>
    </div>
    """, unsafe_allow_html=True)
