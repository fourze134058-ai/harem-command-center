import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# === 0. 系統設定 (System Config) ===
st.set_page_config(page_title="Harem Command Center", page_icon="👑", layout="centered")

# CSS 優化 (Dark Mode + 手機適配)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# === 1. 安全閘門 (Security) ===
# 密碼建議設為簡單好記的，例如 'boss'
password_attempt = st.sidebar.text_input("🛡️ 識別確認 (Password)", type="password")
if password_attempt != st.secrets["APP_PASSWORD"]:
    st.warning("⚠️ 存取被拒：請輸入正確的指揮官密碼。")
    st.stop()

# === 2. 核心邏輯 (Logic Core) ===
HEADERS = {
    "Authorization": f"Bearer {st.secrets['NOTION_TOKEN']}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_image_recursive(page_id):
    """V13 核心：深入 Block 尋找圖片"""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    try:
        res = requests.get(url, headers=HEADERS)
        for block in res.json().get('results', []):
            if block['type'] == 'image':
                img = block['image']
                return img.get('file', {}).get('url') or img.get('external', {}).get('url')
    except:
        pass
    return "https://via.placeholder.com/400x300?text=No+Image+Found"

def fetch_database(db_id):
    """通用資料庫抓取"""
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    res = requests.post(url, headers=HEADERS, json={"page_size": 100})
    return res.json().get('results', [])

# === 3. 介面指揮塔 (UI Control) ===
st.sidebar.success("✅ 權限解鎖：Boss 蒞臨")
mode = st.sidebar.radio("切換戰術視角", ["⚔️ V13 戰略輪盤", "📊 V17 情報中心"])

# --- V13 介面 ---
if mode == "⚔️ V13 戰略輪盤":
    st.title("⚔️ V13 戰略輪盤")
    st.caption("隨機召喚一名後宮成員進行檢閱...")
    
    if st.button("🎲 啟動召喚 (Summon)"):
        with st.spinner('正在掃描資料庫與 Block...'):
            results = fetch_database(st.secrets["DB_GIRLS"])
            if results:
                import random
                target = random.choice(results)
                
                # 解析資料 (需根據您的 Notion 欄位微調)
                props = target['properties']
                # 假設您的標題欄位叫 "Name"
                name_list = props.get('Name', {}).get('title', [])
                name = name_list[0]['plain_text'] if name_list else "Unknown"
                
                # 深入抓圖
                img_url = get_image_recursive(target['id'])
                
                # 顯示
                st.header(f"👑 {name}")
                st.image(img_url, use_column_width=True)
                
                # 顯示屬性 (範例)
                status = props.get('Status', {}).get('select', {}).get('name', 'N/A')
                st.info(f"當前狀態：{status}")
            else:
                st.error("資料庫讀取失敗或為空！")

# --- V17 介面 ---
elif mode == "📊 V17 情報中心":
    st.title("📊 V17 戰略情報")
    if st.button("📡 刷新情報"):
        with st.spinner('正在統計戰果...'):
            data = fetch_database(st.secrets["DB_GIRLS"])
            total_count = len(data)
            
            # 簡單統計狀態 (範例)
            status_list = []
            for p in data:
                s = p['properties'].get('Status', {}).get('select', {})
                if s: status_list.append(s.get('name'))
            
            df = pd.DataFrame(status_list, columns=["Status"])
            status_counts = df["Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            
            # 顯示 KPI
            col1, col2 = st.columns(2)
            col1.metric("總成員數", total_count)
            col2.metric("活躍狀態", len(status_counts))
            
            # 顯示圖表
            st.subheader("成員狀態分佈")
            fig = px.pie(status_counts, values='Count', names='Status', hole=0.4)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig, use_container_width=True)