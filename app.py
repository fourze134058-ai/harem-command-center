import streamlit as st
import requests
import random
import pandas as pd
import plotly.express as px

# === 0. 系統設定 ===
st.set_page_config(page_title="Harem Command Center", page_icon="👑", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; background: linear-gradient(90deg, #FF4081, #d81b60); color: white; border: none; }
    div[data-testid="stMetricValue"] { color: #FF4081; }
    </style>
    """, unsafe_allow_html=True)

# === 1. 安全閘門 ===
if "APP_PASSWORD" in st.secrets:
    password_attempt = st.sidebar.text_input("🛡️ 識別確認 (Password)", type="password")
    if password_attempt != st.secrets["APP_PASSWORD"]:
        st.warning("⚠️ 存取被拒：請輸入正確的指揮官密碼。")
        st.stop()

# === 2. 戰術核心 (移植自您的 run.py) ===
HEADERS = {
    "Authorization": f"Bearer {st.secrets['NOTION_TOKEN']}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 您的 Notion 欄位對照表 (從 run.py 搬過來的)
COLUMN_CONFIG = {
    "TIER": "顔抜きティア",   
    "FORMATION": "Formation",
    "TAGS": "タグ",          
    "FETISH": "フェチ",
    "BIRTHDAY": "生日狀態",   
    "AGE": "Age",
    "LAST_USED": "Lastヌキヌキ💦" 
}

def get_image_recursive(page_id):
    """深入 Block 抓圖 (V13 核心)"""
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
    """抓取資料庫"""
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload = {"page_size": 100} 
    res = requests.post(url, headers=HEADERS, json=payload)
    return res.json().get('results', [])

def extract_property(props, key_config):
    """通用欄位解析器"""
    prop = props.get(key_config)
    if not prop: return "N/A"
    
    prop_type = prop['type']
    if prop_type == 'select':
        return prop['select']['name'] if prop['select'] else "N/A"
    elif prop_type == 'multi_select':
        return ", ".join([t['name'] for t in prop['multi_select']])
    elif prop_type == 'number':
        return str(prop['number'])
    elif prop_type == 'date':
        return prop['date']['start'] if prop['date'] else "N/A"
    elif prop_type == 'formula':
        f_type = prop['formula']['type']
        if f_type == 'string': return prop['formula']['string'] or "N/A"
        if f_type == 'number': return str(prop['formula']['number'])
    
    return "N/A"

# === 3. 介面指揮塔 ===
st.sidebar.success("✅ 權限解鎖：Boss 蒞臨")
mode = st.sidebar.radio("切換戰術視角", ["⚔️ V13 戰略輪盤", "📊 V17 情報中心"])

if mode == "⚔️ V13 戰略輪盤":
    st.title("⚔️ V13 戰略輪盤")
    
    if st.button("🎲 啟動召喚 (Summon)"):
        with st.spinner('正在掃描資料庫...'):
            results = fetch_database(st.secrets["DB_GIRLS"])
            if results:
                target = random.choice(results)
                props = target['properties']
                
                # 1. 智慧抓取名字 (無視欄位名稱，自動鎖定 Title)
                name = "Unknown"
                for key, val in props.items():
                    if val["type"] == "title" and val["title"]:
                        name = val["title"][0]["text"]["content"]
                        break
                
                # 2. 抓取圖片
                img_url = get_image_recursive(target['id'])
                
                # 3. 抓取屬性
                tier = extract_property(props, COLUMN_CONFIG["TIER"])
                fetish = extract_property(props, COLUMN_CONFIG["FETISH"])
                age = extract_property(props, COLUMN_CONFIG["AGE"])
                last_used = extract_property(props, COLUMN_CONFIG["LAST_USED"])

                # 4. 顯示情報
                st.header(f"👑 {name}")
                st.image(img_url, use_column_width=True)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("階級", tier)
                c2.metric("年齡", age)
                c3.metric("上次", last_used)
                
                st.info(f"❤️ 屬性: {fetish}")
                
            else:
                st.error("資料庫抓取失敗，請檢查 Token 或 ID 是否正確。")

elif mode == "📊 V17 情報中心":
    st.title("📊 V17 戰略情報")
    if st.button("📡 刷新情報"):
        with st.spinner('統計中...'):
            data = fetch_database(st.secrets["DB_GIRLS"])
            total = len(data)
            
            # 統計階級
            tiers = []
            for p in data:
                t = extract_property(p['properties'], COLUMN_CONFIG["TIER"])
                tiers.append(t)
            
            df = pd.DataFrame(tiers, columns=["Tier"])
            counts = df["Tier"].value_counts().reset_index()
            counts.columns = ["Tier", "Count"]
            
            st.metric("總成員數", total)
            
            fig = px.pie(counts, values='Count', names='Tier', title='階級分佈', hole=0.4)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig)
