import streamlit as st
import requests
import xml.etree.ElementTree as ET
import datetime
from dateutil import parser
import urllib.parse

# --- 網頁配置 (專為手機窄螢幕優化) ---
st.set_page_config(page_title="情報搜尋", layout="centered")

# 自定義 CSS：加強易讀性
st.markdown("""
    <style>
    /* 調整主容器間距 */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* 搜尋框加大 */
    .stTextInput input {
        font-size: 18px !important;
        padding: 12px !important;
        border-radius: 10px !important;
    }

    /* 新聞卡片優化 */
    .news-box {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #eef0f2;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .title-text {
        font-size: 18px !important; /* 加大標題字體 */
        font-weight: 700;
        color: #1A1C1E;
        line-height: 1.4;
        margin-bottom: 8px;
        display: block;
        text-decoration: none;
    }
    .meta-text {
        font-size: 13px;
        color: #6A7074;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .tag {
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    .tag-blue { background-color: #E8F0FE; color: #1967D2; }
    .tag-gray { background-color: #F1F3F4; color: #5F6368; }
    </style>
    """, unsafe_allow_html=True)

class NewsScanner:
    @staticmethod
    def fetch_data(query):
        # 抓取 Google News
        url = f"https://news.google.com/rss/search?q={query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        results = []
        try:
            r = requests.get(url, timeout=10)
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:20]: # 限制 20 則減少負擔
                title = item.find('title').text
                link = item.find('link').text
                pub_date = parser.parse(item.find('pubDate').text).astimezone(datetime.timezone(datetime.timedelta(hours=8)))
                results.append({"title": title, "link": link, "date": pub_date})
            return results
        except: return []

# --- 主畫面 ---
st.title("🔍 情報搜尋站")

# 搜尋框
query = st.text_input("", placeholder="輸入公司名、股號或關鍵字...")

if query:
    # 快速導航區 (保留簡潔的按鈕)
    mops_url = f"https://mops.twse.com.tw/mops/web/t05st01?stock_id={query}"
    st.link_button(f"🏛️ 前往「{query}」公開資訊觀測站", mops_url, use_container_width=True)
    
    st.divider()

    with st.spinner('搜尋中...'):
        data = NewsScanner.fetch_data(query)
        
        if data:
            for n in data:
                # 判斷來源標籤 (簡化版)
                source = n['title'].split(' - ')[-1] if ' - ' in n['title'] else "新聞"
                display_title = n['title'].split(' - ')[0]

                # 渲染卡片
                st.markdown(f"""
                    <div class="news-box">
                        <a href="{n['link']}" target="_blank" class="title-text">{display_title}</a>
                        <div class="meta-text">
                            <div><span class="tag tag-gray">{source}</span></div>
                            <div>{n['date'].strftime('%m/%d %H:%M')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("查無資料，請更換關鍵字。")
else:
    st.write("請輸入搜尋目標，系統將即時調閱最新動態。")
