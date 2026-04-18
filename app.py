import streamlit as st
import requests
import xml.etree.ElementTree as ET
import datetime
from dateutil import parser

# --- 網頁配置 ---
st.set_page_config(page_title="最新情報搜尋", layout="centered")

# CSS 優化：強調時間與標題
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    .stTextInput input { font-size: 16px !important; }
    
    .news-box {
        background-color: white;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
        border: 1px solid #f0f0f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .title-link {
        font-size: 18px !important;
        font-weight: 600;
        color: #1a73e8; /* 連結藍色，更像搜尋結果 */
        line-height: 1.4;
        text-decoration: none;
        display: block;
        margin-bottom: 6px;
    }
    .meta-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        color: #5f6368;
    }
    .time-badge {
        color: #d93025; /* 紅色強調最新時間 */
        font-weight: bold;
    }
    .source-badge {
        background-color: #f1f3f4;
        padding: 2px 6px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

class NewsScanner:
    @staticmethod
    def fetch_data(query):
        url = f"https://news.google.com/rss/search?q={query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        results = []
        try:
            r = requests.get(url, timeout=10)
            root = ET.fromstring(r.content)
            for item in root.findall('.//item'):
                full_title = item.find('title').text
                link = item.find('link').text
                # 處理日期
                pub_date = parser.parse(item.find('pubDate').text).astimezone(datetime.timezone(datetime.timedelta(hours=8)))
                
                # 拆分標題與來源
                if ' - ' in full_title:
                    title = full_title.rsplit(' - ', 1)[0]
                    source = full_title.rsplit(' - ', 1)[1]
                else:
                    title = full_title
                    source = "新聞"
                
                results.append({
                    "title": title, 
                    "link": link, 
                    "date": pub_date, 
                    "source": source
                })
            
            # --- 核心邏輯：依照時間排序 (由近到遠) ---
            results.sort(key=lambda x: x['date'], reverse=True)
            
            return results[:30] # 回傳前30則最即時的新聞
        except: return []

# --- UI 介面 ---
st.title("📰 即時情報掃描")

query = st.text_input("", placeholder="請輸入關鍵字...")

if query:
    mops_url = f"https://mops.twse.com.tw/mops/web/t05st01?stock_id={query}"
    st.link_button(f"🏛️ 查看「{query}」官方重大訊息", mops_url, use_container_width=True)

    with st.spinner('正在獲取最新消息...'):
        data = NewsScanner.fetch_data(query)
        
        if data:
            st.caption(f"已按時間排序，顯示前 {len(data)} 則最新動態")
            for n in data:
                # 格式化日期顯示
                time_display = n['date'].strftime('%m/%d %H:%M')
                
                st.markdown(f"""
                    <div class="news-box">
                        <a href="{n['link']}" target="_blank" class="title-link">{n['title']}</a>
                        <div class="meta-row">
                            <span class="source-badge">{n['source']}</span>
                            <span class="time-badge">🕒 {time_display}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("查無相關新聞，請嘗試簡短關鍵字。")
else:
    st.info("輸入後將自動列出最新發布的新聞。")
