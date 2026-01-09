import streamlit as st
import requests
import random
import pandas as pd
import plotly.express as px
from datetime import datetime

# === 0. 系統設定 (Notion Style) ===
st.set_page_config(page_title="Harem Command Center", page_icon="👑", layout="wide")

# CSS 強制覆寫為 Notion 風格 (白底、深灰字、簡約按鈕)
st.markdown("""
    <style>
    /* 全域背景設定 (Notion White) */
    .stApp, [data-testid="stAppViewContainer"] { 
        background-color: #FFFFFF; 
    }
    
    /* 側邊欄背景 (Notion Sidebar Gray) */
    [data-testid="stSidebar"] { 
        background-color: #F7F7F5; 
        border-right: 1px solid #E9E9E8;
    }

    /* 全域文字顏色 (Notion Black) */
    h1, h2, h3, h4, p, div, span, label { 
        color: #37352F !important; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
    }

    /* 按鈕優化 (簡約灰框) */
    .stButton>button { 
        width: 100%; 
        border: 1px solid #D3D1CB; 
        background-color: #FFFFFF; 
        color: #37352F; 
        border-radius: 4px; 
        font-weight: 500;
        transition: 0.2s;
    }
    .stButton>button:hover { 
        background-color: #EFEFEF; 
        border-color: #A0A0A0;
    }

    /* KPI 數值顏色 (Notion Orange Accent) */
    div[data-testid="stMetricValue"] { 
        color: #D44C47 !important; /* Notion Red/Orange */
        font-weight: 600;
    }
    
    /* 分隔線 */
    hr { border-color: #E9E9E8; }
    </style>
    """, unsafe_allow_html=True)

# === 1. 安全閘門 ===
if "APP_PASSWORD" in st.secrets:
    password_attempt = st.sidebar.text_input("🛡️ 識別確認", type="password")
    if password_attempt != st.secrets["APP_PASSWORD"]:
        st.warning("⚠️ 請輸入指揮官密碼以解鎖介面。")
        st.stop()

# === 2. 戰術核心 ===
HEADERS = {
    "Authorization": f"Bearer {st.secrets['NOTION_TOKEN']}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

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
    """深入 Block 抓圖"""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    try:
        res = requests.get(url, headers=HEADERS)
        for block in res.json().get('results', []):
            if block['type'] == 'image':
                img = block['image']
                return img.get('file', {}).get('url') or img.get('external', {}).get('url')
    except: pass
    return "https://via.placeholder.com/400x300?text=No+Image+Found"

def fetch_database(db_id):
    """抓取資料庫 (包含分頁處理)"""
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload = {"page_size": 100} 
    results = []
    has_more = True
    start_cursor = None
    
    while has_more:
        if start_cursor: payload["start_cursor"] = start_cursor
        res = requests.post(url, headers=HEADERS, json=payload).json()
        results.extend(res.get('results', []))
        has_more = res.get('has_more', False)
        start_cursor = res.get('next_cursor')
        
    return results

def extract_property(props, key_config):
    """強力欄位解析器"""
    prop = props.get(key_config)
    if not prop: return None 

    try:
        p_type = prop['type']
        if p_type == 'select':
            return prop['select']['name'] if prop['select'] else None
        elif p_type == 'multi_select':
            return [t['name'] for t in prop['multi_select']] 
        elif p_type == 'number':
            return prop['number']
        elif p_type == 'date':
            return prop['date']['start'] if prop['date'] else None
        elif p_type == 'formula':
            f_type = prop['formula']['type']
            if f_type == 'string': return prop['formula']['string']
            if f_type == 'number': return prop['formula']['number']
            if f_type == 'date': return prop['formula']['date']['start']
    except:
        return None
    return None

def calculate_days_since(date_str):
    """計算閒置天數"""
    if not date_str: return 999
    try:
        clean_date = date_str.split('T')[0]
        d = datetime.strptime(clean_date, "%Y-%m-%d")
        delta = datetime.now() - d
        return delta.days
    except:
        return 0

# === 3. 介面指揮塔 ===
st.sidebar.success("✅ Boss 蒞臨 (Notion Mode)")
mode = st.sidebar.radio("切換視角", ["⚔️ V13 戰略輪盤", "📊 V17 情報中心"])

@st.cache_data(ttl=600)
def load_data():
    return fetch_database(st.secrets["DB_GIRLS"])

if mode == "⚔️ V13 戰略輪盤":
    st.title("⚔️ V13 戰略輪盤")
    st.caption("隨機抽選一名成員進行檢閱...")
    
    if st.button("🎲 啟動召喚 (Summon)", use_container_width=True):
        with st.spinner('正在掃描資料庫...'):
            raw_data = load_data()
            if raw_data:
                target = random.choice(raw_data)
                props = target['properties']
                
                name = "Unknown"
                for key, val in props.items():
                    if val["type"] == "title" and val["title"]:
                        name = val["title"][0]["text"]["content"]
                        break
                
                img_url = get_image_recursive(target['id'])
                
                tier = extract_property(props, COLUMN_CONFIG["TIER"]) or "未分類"
                fetish_list = extract_property(props, COLUMN_CONFIG["FETISH"]) or []
                age = extract_property(props, COLUMN_CONFIG["AGE"]) or 0
                
                last_used_str = extract_property(props, COLUMN_CONFIG["LAST_USED"])
                days_since = calculate_days_since(last_used_str)
                days_text = f"{days_since} 天前" if days_since < 999 else "未使用 (New)"

                # 卡片式佈局
                col_img, col_info = st.columns([1, 1])
                
                with col_img:
                    st.image(img_url, caption=f"ID: {target['id'][-4:]}", use_container_width=True)
                
                with col_info:
                    st.subheader(f"👑 {name}")
                    st.divider()
                    c1, c2 = st.columns(2)
                    c1.metric("階級", tier)
                    c2.metric("年齡", f"{age} 歲" if age > 0 else "?")
                    
                    st.metric("上次寵幸", days_text)
                    
                    st.write("❤️ **屬性 (Fetish):**")
                    if fetish_list:
                        # 使用 Notion 風格的 Tag 顯示
                        tags_html = "".join([f"<span style='background:#F1F1EF; color:#37352F; padding:2px 8px; border-radius:4px; margin-right:5px; font-size:0.9em;'>{f}</span>" for f in fetish_list])
                        st.markdown(tags_html, unsafe_allow_html=True)
                    else:
                        st.write("無")

            else:
                st.error("資料庫讀取失敗")

elif mode == "📊 V17 情報中心":
    st.title("📊 V17 戰略情報")
    
    if st.button("📡 刷新全域戰況", key="refresh_v17"):
        with st.spinner('正在分析大數據...'):
            raw_data = load_data()
            
            df_list = []
            all_fetishes = []
            
            for p in raw_data:
                props = p['properties']
                age = extract_property(props, COLUMN_CONFIG["AGE"]) or 0
                tier = extract_property(props, COLUMN_CONFIG["TIER"]) or "N/A"
                fetishes = extract_property(props, COLUMN_CONFIG["FETISH"]) or []
                if isinstance(fetishes, list):
                    all_fetishes.extend(fetishes)
                
                df_list.append({"Tier": tier, "Age": age})
            
            df = pd.DataFrame(df_list)
            
            # --- KPI 區塊 ---
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("總人數", len(df))
            avg_age = df[df["Age"] > 0]["Age"].mean()
            kpi2.metric("平均年齡", f"{avg_age:.1f} 歲" if not pd.isna(avg_age) else "N/A")
            top_fetish = pd.Series(all_fetishes).mode()[0] if all_fetishes else "無"
            kpi3.metric("最熱門屬性", top_fetish)
            
            st.divider()

            # --- 圖表區 (修正為深色文字以適配白底) ---
            chart_c1, chart_c2 = st.columns(2)
            
            text_color_notion = "#37352F" # 設定圖表文字顏色為深灰
            
            with chart_c1:
                st.subheader("階級分佈 (Tier)")
                counts = df["Tier"].value_counts().reset_index()
                counts.columns = ["Tier", "Count"]
                # 使用較柔和的配色 (Pastel)
                fig_tier = px.pie(counts, values='Count', names='Tier', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_tier.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=text_color_notion)
                st.plotly_chart(fig_tier, use_container_width=True)
            
            with chart_c2:
                st.subheader("屬性偏好 (Top 10)")
                if all_fetishes:
                    fetish_counts = pd.Series(all_fetishes).value_counts().head(10).reset_index()
                    fetish_counts.columns = ["Fetish", "Count"]
                    fig_fetish = px.bar(fetish_counts, x="Count", y="Fetish", orientation='h', color="Count", color_continuous_scale='Teal')
                    fig_fetish.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=text_color_notion, yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_fetish, use_container_width=True)
                else:
                    st.info("尚無屬性資料")

            st.subheader("年齡分佈")
            if not df[df["Age"] > 0].empty:
                fig_age = px.histogram(df[df["Age"] > 0], x="Age", nbins=20)
                fig_age.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=text_color_notion, plot_bgcolor="rgba(0,0,0,0)")
                fig_age.update_xaxes(showgrid=False) # 讓圖表更簡潔像 Notion
                fig_age.update_yaxes(showgrid=True, gridcolor="#E9E9E8")
                st.plotly_chart(fig_age, use_container_width=True)
