import streamlit as st
import requests
import xml.etree.ElementTree as ET
import datetime
import pandas as pd
from dateutil import parser

# --- 網頁配置 ---
st.set_page_config(page_title="全球新聞情報站", layout="centered")

# 自定義手機版 CSS (加入點擊反饋效果)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .search-header { font-size: 24px; font-weight: 800; color: #1a73e8; margin-bottom: 20px; text-align: center; }
    .news-link { text-decoration: none; color: inherit; }
    .news-card {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
        border: 1px solid #eee;
    }
    .news-card:active { transform: scale(0.98); background-color: #f0f0f0; } /* 手機點擊反饋 */
    .pos-tag { color: #28a745; font-weight: bold; font-size: 12px; }
    .neg-tag { color: #dc3545; font-weight: bold; font-size: 12px; }
    .neu-tag { color: #6c757d; font-weight: bold; font-size: 12px; }
    .time-text { font-size: 11px; color: #888; margin-bottom: 4px; display: flex; justify-content: space-between; }
    .title-text { font-size: 16px; font-weight: 600; color: #202124; line-height: 1.4; margin-bottom: 8px; }
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
            for item in root.findall('.//item')[:25]: # 優化加載速度取25則
                title = item.find('title').text
                link = item.find('link').text # 提取連結
                pub_date = parser.parse(item.find('pubDate').text).astimezone(datetime.timezone(datetime.timedelta(hours=8)))
                news_data.append({"title": title, "date": pub_date, "link": link})
            return news_data
        except: return []

    @staticmethod
    def quick_analyze(title):
        pos = ['漲', '升', '獲利', '突破', '合作', '支持', '新高', '優於預期', '領', '補助']
        neg = ['跌', '慘', '危機', '裁員', '爭議', '崩盤', '警告', '壓力', '制裁', '跳水']
        for w in neg: 
            if w in title: return "🔴 負面趨勢", "neg-tag"
        for w in pos: 
            if w in title: return "🟢 正面動能", "pos-tag"
        return "⚪ 中性訊息", "neu-tag"

# --- UI 介面 ---
st.markdown('<div class="search-header">📰 全球情報搜尋</div>', unsafe_allow_html=True)

query = st.text_input("", placeholder="🔍 輸入關鍵字後點擊 Enter", help="輸入後請按手機鍵盤上的「前往」或「搜尋」")

if query:
    with st.spinner('正在調閱最新報導...'):
        data = NewsEngine.get_news(query)
        
        if data:
            st.caption(f"找到 {len(data)} 則最新相關新聞（點擊卡片閱讀全文）")
            
            for n in data:
                label, tag_class = NewsEngine.quick_analyze(n['title'])
                # 使用 <a> 標籤包裹整個卡片
                st.markdown(f"""
                    <a href="{n['link']}" target="_blank" class="news-link">
                        <div class="news-card">
                            <div class="time-text">
                                <span>{n['date'].strftime('%Y-%m-%d %H:%M')}</span>
                                <span>🔗 點擊閱讀</span>
                            </div>
                            <div class="title-text">{n['title']}</div>
                            <div>
                                <span class="{tag_class}">{label}</span>
                            </div>
                        </div>
                    </a>
                """, unsafe_allow_html=True)
        else:
            st.info("尚未搜尋到相關即時新聞，請嘗試其他關鍵字。")
else:
    st.markdown("""
    <div style="text-align: center; color: #888; margin-top: 50px; padding: 20px; border: 1px dashed #ccc; border-radius: 15px;">
        <p>📱 <b>手機使用提示</b></p>
        <p style="font-size: 13px;">搜尋後點擊新聞卡片即可跳轉原文</p>
        <p style="font-size: 12px; color: #bbb;">建議關鍵字：台積電、原油、美股、黃金</p>
    </div>
    """, unsafe_allow_html=True)
