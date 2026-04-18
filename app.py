import streamlit as st
import requests
import xml.etree.ElementTree as ET
import datetime
import pandas as pd
from dateutil import parser
import math
import plotly.express as px

# 設定網頁標題
st.set_page_config(page_title="趨勢推演引擎", layout="wide")

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
        except:
            return pd.DataFrame()

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
                    tags.append(label[:2])
                    break 
        return score, ("".join(list(set(tags))) if tags else "⚪中性")

# --- UI 介面 ---
st.title("🔮 全球動態趨勢推演引擎")
target = st.text_input("請輸入推演目標（如：台積電、美股、黃金）", placeholder="例如：比特幣")
days = st.slider("檢索天數", 1, 14, 5)

if target:
    with st.spinner('數據採集與演算法推演中...'):
        scout = DataScout()
        df = scout.fetch_news(target, days)

        if not df.empty:
            # 分析
            results = df.apply(lambda x: AnalyticsEngine.analyze(x['標題']), axis=1)
            df['評分'], df['性質'] = zip(*results)
            df['動能'] = df['評分'] * df['權重']
            
            # 指標計算
            total_e = df['動能'].sum()
            hour = datetime.datetime.now().hour
            t_factor = 1.5 if (23 <= hour or hour <= 5) else 1.0
            final_score = total_e * t_factor

            # 顯示看板
            col1, col2, col3 = st.columns(3)
            col1.metric("有效新聞數", len(df))
            col2.metric("綜合動能指數", f"{final_score:.2f}")
            col3.metric("天時係數", t_factor)

            # 結論與建議
            st.subheader("🔮 推演劇本")
            if final_score < -15: st.error("【威脅劇本】負面能量堆疊，風險極高。")
            elif final_score > 10: st.success("【機遇劇本】正面情緒連貫，動能強勁。")
            else: st.info("【盤整劇本】數據正負抵銷，動能不足。")

            # 視覺化圖表
            fig = px.bar(df, x='日期', y='動能', hover_data=['標題'], color='評分', title="新聞能量時序分佈")
            st.plotly_chart(fig, use_container_width=True)

            # 詳細列表
            st.subheader("📜 關鍵數據明細")
            st.dataframe(df[['日期', '性質', '權重', '標題']], use_container_width=True)
        else:
            st.warning("查無相關動態。")
