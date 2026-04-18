import streamlit as st
import requests
import xml.etree.ElementTree as ET
import datetime
from dateutil import parser
import urllib.parse

# --- 網頁配置 ---
st.set_page_config(page_title="全球動態情報站", layout="centered")

# CSS 增加「重大訊息」專用樣式
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .mops-card {
        background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
        color: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(26,115,232,0.3);
    }
    .mops-btn {
        background-color: white;
        color: #1a73e8;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: bold;
        text-decoration: none;
        display: inline-block;
        margin-top: 10px;
        font-size: 13px;
    }
    .news-card {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #eee;
    }
    .source-tag { font-size: 11px; padding: 2px 6px; border-radius: 4px; margin-right: 5px; }
    .tag-gov { background-color: #e8f0fe; color: #1967d2; }
    .tag-news { background-color: #f1f3f4; color: #5f6368; }
    </style>
    """, unsafe_allow_html=True)

class IntelligenceEngine:
    @staticmethod
    def fetch_rss(url, source_name, topic=""):
        headers = {'User-Agent': 'Mozilla/5.0'}
        results = []
        try:
            r = requests.get(url, headers=headers, timeout=10)
            root = ET.fromstring(r.content)
            for item in root.findall('.//item'):
                title = item.find('title').text
                if topic.lower() not in title.lower(): continue
                link = item.find('link').text
                pub_date = parser.parse(item.find('pubDate').text).astimezone(datetime.timezone(datetime.timedelta(hours=8)))
                results.append({"title": title, "date": pub_date, "link": link, "source": source_name})
            return results
        except: return []

# --- UI 介面 ---
st.markdown('<h2 style="text-align:center;">📰 全球情報搜尋系統</h2>', unsafe_allow_html=True)
query = st.text_input("", placeholder="🔍 輸入關鍵字（如：2330, 台積電, 石油）")

if query:
    # --- 優化點：重大訊息直達車 ---
    # 如果使用者輸入數字（可能是股號），或者特定的公司名
    encoded_query = urllib.parse.quote(query.encode('big5')) # MOPS 有時使用 big5 查詢
    mops_url = f"https://mops.twse.com.tw/mops/web/t05st01?stock_id={query}" 
    
    st.markdown(f"""
        <div class="mops-card">
            <div style="font-size: 12px; opacity: 0.9;">官方權威來源</div>
            <div style="font-size: 18px; font-weight: bold; margin-top: 5px;">公開資訊觀測站 - 重大訊息</div>
            <p style="font-size: 13px; margin-top: 8px;">正在檢索與「{query}」相關的公司申報資料...</p>
            <a href="{mops_url}" target="_blank" class="mops-btn">🏛️ 點此查看官方公告原文</a>
        </div>
    """, unsafe_allow_html=True)

    with st.spinner('同步掃描新聞與行政院公告...'):
        # 抓取資料
        news = IntelligenceEngine.fetch_rss(f"https://news.google.com/rss/search?q={query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant", "新聞報導", query)
        gov = IntelligenceEngine.fetch_rss("https://www.ey.gov.tw/Page/99B0999513076F03/RSS", "行政院", query)
        
        all_data = sorted(news + gov, key=lambda x: x['date'], reverse=True)

        if all_data:
            for n in all_data:
                tag_class = "tag-gov" if n['source'] == "行政院" else "tag-news"
                st.markdown(f"""
                    <a href="{n['link']}" target="_blank" style="text-decoration:none; color:inherit;">
                        <div class="news-card">
                            <div style="font-size:11px; color:#888; margin-bottom:5px;">
                                <span class="source-tag {tag_class}">{n['source']}</span> {n['date'].strftime('%m-%d %H:%M')}
                            </div>
                            <div style="font-size:16px; font-weight:600;">{n['title']}</div>
                        </div>
                    </a>
                """, unsafe_allow_html=True)
        else:
            st.info("新聞端暫無最新動態，建議點擊上方藍色卡片查看證交所原始公告。")
