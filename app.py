import streamlit as st
import requests
import xml.etree.ElementTree as ET
import datetime
from dateutil import parser
import math

# --- 網頁配置 ---
st.set_page_config(page_title="動能情報站", layout="centered")

# CSS 優化：大字體與動能視覺化
st.markdown("""
    <style>
    .news-box {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #f0f0f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .title-link {
        font-size: 18px !important;
        font-weight: 700;
        color: #1a73e8;
        text-decoration: none;
        line-height: 1.4;
    }
    .momentum-bar-bg {
        background-color: #eee;
        border-radius: 10px;
        height: 12px;
        width: 100%;
        margin: 15px 0 5px 0;
        display: flex;
        overflow: hidden;
    }
    .score-tag {
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

class MomentumEngine:
    @staticmethod
    def analyze(title, days_ago):
        # 1. 基礎情緒分
        pos_kws = ['漲', '升', '獲利', '突破', '合作', '支持', '新高', '優於預期', '利多', '買入', '豁免']
        neg_kws = ['跌', '慘', '危機', '裁員', '爭議', '崩盤', '警告', '壓力', '跳水', '利空', '制裁']
        
        base_score = 0
        icon, color = "⚪", "#5f6368"
        
        for w in neg_kws:
            if w in title:
                base_score = -1.0
                icon, color = "🔴", "#d93025"
                break
        for w in pos_kws:
            if w in title:
                base_score = 1.0
                icon, color = "🟢", "#188038"
                break
        
        # 2. 時間衰減權重 (越新影響越大, 使用指數衰減 e^-0.2t)
        weight = math.exp(-0.2 * days_ago)
        
        # 3. 最終動能貢獻
        momentum_contribution = base_score * weight
        
        return momentum_contribution, icon, color, round(weight, 2)

    @staticmethod
    def fetch_and_rank(query):
        url = f"https://news.google.com/rss/search?q={query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        now = datetime.datetime.now(datetime.timezone.utc)
        results = []
        try:
            r = requests.get(url, timeout=10)
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:30]:
                full_title = item.find('title').text
                link = item.find('link').text
                pub_date = parser.parse(item.find('pubDate').text)
                
                days_ago = (now - pub_date).total_seconds() / 86400
                m_score, icon, color, w = MomentumEngine.analyze(full_title, days_ago)
                
                title = full_title.rsplit(' - ', 1)[0] if ' - ' in full_title else full_title
                source = full_title.rsplit(' - ', 1)[1] if ' - ' in full_title else "新聞"
                
                results.append({
                    "title": title, "link": link, "date": pub_date.astimezone(datetime.timezone(datetime.timedelta(hours=8))),
                    "source": source, "m_score": m_score, "icon": icon, "color": color, "weight": w
                })
            
            # 按時間排序
            results.sort(key=lambda x: x['date'], reverse=True)
            return results
        except: return []

# --- UI ---
st.title("🚀 情報動能搜尋")
query = st.text_input("", placeholder="輸入關鍵字計算即時動能...")

if query:
    data = MomentumEngine.fetch_and_rank(query)
    
    if data:
        # 計算總體動能
        total_momentum = sum(n['m_score'] for n in data)
        pos_count = len([n for n in data if n['m_score'] > 0])
        neg_count = len([n for n in data if n['m_score'] < 0])
        
        # 顯示動能看板
        st.subheader("📊 即時動能報告")
        c1, c2, c3 = st.columns(3)
        c1.metric("多方訊號", f"{pos_count} 則")
        c2.metric("空方訊號", f"{neg_count} 則")
        c3.metric("總動能值", f"{total_momentum:.2f}")

        # 動能進度條視覺化
        # 歸一化處理，假設 -10 到 10 為區間
        display_score = max(min(total_momentum, 10), -10)
        pos_width = 50 + (display_score * 5) # 0分在50%處
        
        st.markdown(f"""
            <div style="font-size:13px; color:#5f6368; margin-bottom:5px;">市場體感溫度：{"看多" if total_momentum > 0 else "看空" if total_momentum < 0 else "中性"}</div>
            <div class="momentum-bar-bg">
                <div style="width: {pos_width}%; background-color: {'#188038' if total_momentum >= 0 else '#d93025'}; transition: 0.5s;"></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()

        # 新聞列表
        for n in data:
            st.markdown(f"""
                <div class="news-box">
                    <a href="{n['link']}" target="_blank" class="title-link">{n['icon']} {n['title']}</a>
                    <div style="display: flex; justify-content: space-between; font-size: 12px; color: #5f6368; margin-top:8px;">
                        <span>{n['source']} | {n['date'].strftime('%m/%d %H:%M')}</span>
                        <span style="color:{n['color']}; font-weight:bold;">影響權重: {n['weight']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("查無數據。")
