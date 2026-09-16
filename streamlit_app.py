"""
FakeGuard AI — Cloud-Native Fake Profile Detection Platform
Streamlit Web Application
Supports: Instagram & Twitter/X profile risk analysis, Bulk CSV scanning,
Live Threat Dashboard, Audit Logs, and ML Architecture Explorer.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pickle
import json
import sqlite3
import os
import io
import time
from datetime import datetime

# ===================== STREAMLIT PAGE CONFIG =====================
st.set_page_config(
    page_title="FakeGuard AI | Fake Profile Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== DIRECTORY & PATH RESOLUTION =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
MODELS_DIR = os.path.join(BACKEND_DIR, "models")
DB_PATH = os.path.join(BACKEND_DIR, "predictions.db")

# Fallback if running from workspace root
if not os.path.exists(MODELS_DIR):
    MODELS_DIR = os.path.join(BASE_DIR, "FakeProfileDetector", "backend", "models")
    BACKEND_DIR = os.path.join(BASE_DIR, "FakeProfileDetector", "backend")
    DB_PATH = os.path.join(BACKEND_DIR, "predictions.db")

# ===================== CUSTOM CSS & STYLING =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Main Background & Cards */
    .stApp {
        background: radial-gradient(circle at top right, #131b2e 0%, #0b0f19 50%, #060911 100%);
    }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    .hero-banner {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 50%, rgba(236, 72, 153, 0.1) 100%);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 25px;
        box-shadow: 0 10px 40px -10px rgba(99, 102, 241, 0.25);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-top: 6px;
        line-height: 1.5;
    }
    
    /* Risk Badges */
    .badge-critical {
        background: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.5);
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    .badge-high {
        background: rgba(249, 115, 22, 0.2);
        color: #fdba74;
        border: 1px solid rgba(249, 115, 22, 0.5);
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    .badge-medium {
        background: rgba(234, 179, 8, 0.2);
        color: #fde047;
        border: 1px solid rgba(234, 179, 8, 0.5);
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    .badge-low {
        background: rgba(34, 197, 94, 0.2);
        color: #86efac;
        border: 1px solid rgba(34, 197, 94, 0.5);
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Metric pill */
    .metric-pill {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 14px 18px;
        text-align: center;
    }
    
    .metric-pill-val {
        font-size: 1.6rem;
        font-weight: 800;
        color: #f8fafc;
    }
    
    .metric-pill-lbl {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-top: 4px;
    }
    
    /* Highlight item in explanations */
    .reason-item {
        background: rgba(15, 23, 42, 0.5);
        border-left: 3px solid #6366f1;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 0 8px 8px 0;
        font-size: 0.92rem;
        color: #e2e8f0;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    /* Fix Plotly background in Streamlit */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# ===================== DATABASE INITIALIZATION =====================
def init_database():
    """Ensure predictions table exists in SQLite database."""
    os.makedirs(BACKEND_DIR, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                platform TEXT NOT NULL,
                username TEXT DEFAULT '',
                followers_count REAL,
                following_count REAL,
                follower_ratio REAL,
                posts_or_tweets REAL,
                bio_length REAL,
                engagement_rate REAL,
                prediction INTEGER,
                probability REAL,
                risk_level TEXT,
                source TEXT DEFAULT 'manual'
            )
        ''')
        conn.commit()

init_database()

# ===================== MODEL LOADING =====================
@st.cache_resource
def load_models_and_metadata():
    """Load pretrained ML models, scalers, and metadata with caching."""
    insta_model_path = os.path.join(MODELS_DIR, "insta_model.pkl")
    insta_scaler_path = os.path.join(MODELS_DIR, "insta_scaler.pkl")
    insta_meta_path = os.path.join(MODELS_DIR, "insta_metadata.json")

    twitter_model_path = os.path.join(MODELS_DIR, "twitter_model.pkl")
    twitter_scaler_path = os.path.join(MODELS_DIR, "twitter_scaler.pkl")
    twitter_meta_path = os.path.join(MODELS_DIR, "twitter_metadata.json")

    loaded_data = {
        "insta_model": None, "insta_scaler": None, "insta_meta": {},
        "twitter_model": None, "twitter_scaler": None, "twitter_meta": {},
        "ready": False, "error": None
    }

    try:
        if os.path.exists(insta_model_path):
            with open(insta_model_path, "rb") as f:
                loaded_data["insta_model"] = pickle.load(f)
            with open(insta_scaler_path, "rb") as f:
                loaded_data["insta_scaler"] = pickle.load(f)
            with open(insta_meta_path, "r") as f:
                loaded_data["insta_meta"] = json.load(f)

        if os.path.exists(twitter_model_path):
            with open(twitter_model_path, "rb") as f:
                loaded_data["twitter_model"] = pickle.load(f)
            with open(twitter_scaler_path, "rb") as f:
                loaded_data["twitter_scaler"] = pickle.load(f)
            with open(twitter_meta_path, "r") as f:
                loaded_data["twitter_meta"] = json.load(f)

        loaded_data["ready"] = True
    except Exception as e:
        loaded_data["error"] = str(e)

    return loaded_data

models_bundle = load_models_and_metadata()

# ===================== HELPER FUNCTIONS =====================
def get_risk_tier(prob: float):
    if prob >= 0.85:
        return "critical", "Critical Risk", "#EF4444", "badge-critical"
    elif prob >= 0.65:
        return "high", "High Risk", "#F97316", "badge-high"
    elif prob >= 0.45:
        return "medium", "Medium Risk", "#EAB308", "badge-medium"
    else:
        return "low", "Low Risk (Genuine)", "#22C55E", "badge-low"

def generate_explanations(platform: str, inputs: dict, is_fake: bool) -> list:
    """Explainable AI (XAI) feature signals generator."""
    explanations = []
    if is_fake:
        if platform == "instagram":
            if inputs.get("profile_pic", 1) == 0:
                explanations.append("🚫 No profile picture set — highly characteristic of synthetic/bot accounts.")
            if inputs.get("nums_length_username", 0) > 0.3:
                explanations.append("🔢 High proportion of digits in username — auto-generated handle signature.")
            if inputs.get("fullname_words", 2) == 0:
                explanations.append("📝 Full name field is missing or empty.")
            if inputs.get("description_length", 50) == 0:
                explanations.append("📄 Bio is blank — low effort profile creation.")
            if inputs.get("posts_count", 100) < 5:
                explanations.append("📸 Extremely low post count with active follower acquisition.")
            followers = inputs.get("followers_count", 0)
            following = inputs.get("following_count", 1)
            if followers < 15 and following > 150:
                explanations.append("⚠️ Highly skewed follow ratio (following hundreds but minimal followers).")
            if inputs.get("name_eq_username", 0) == 1 and inputs.get("nums_length_username", 0) > 0.2:
                explanations.append("🤖 Fullname is identical to numeric username.")
        else: # Twitter
            if inputs.get("retweet_count", 0) > 50:
                explanations.append("🔄 Unusually high retweet frequency — bot amplification behavior.")
            if inputs.get("mention_count", 0) > 4:
                explanations.append("💬 High mention density per post — mass tagging/spam pattern.")
            if inputs.get("follower_count_twitter", 0) < 100:
                explanations.append("👤 Low follower count relative to tweet/retweet velocity.")
            if inputs.get("verified", 0) == 0:
                explanations.append("❌ Account is unverified without organic reputation signals.")
        if not explanations:
            explanations.append("🔍 Composite behavioral indicators match known synthetic bot clusters.")
    else:
        if platform == "instagram":
            if inputs.get("profile_pic", 1) == 1:
                explanations.append("✅ Profile avatar is established.")
            if inputs.get("description_length", 50) > 20:
                explanations.append("📝 Descriptive bio present with natural phrasing.")
            if inputs.get("posts_count", 100) > 40:
                explanations.append("📸 Long-standing posting history and media archive.")
            if inputs.get("followers_count", 0) > 100:
                explanations.append("📊 Organic audience network.")
        else: # Twitter
            if inputs.get("verified", 0) == 1:
                explanations.append("✔️ Verified identity badge recognized.")
            if inputs.get("follower_count_twitter", 0) > 1000:
                explanations.append("📊 Solid follower foundation.")
            if inputs.get("mention_count", 0) < 3:
                explanations.append("💬 Natural conversational mention volume.")
        if not explanations:
            explanations.append("✅ Account characteristics align with authentic organic user behavior.")
    return explanations[:5]

def record_prediction(platform: str, username: str, followers: float, following: float,
                      posts: float, bio_len: float, pred: int, prob: float,
                      risk_level: str, source: str = "manual"):
    """Persist prediction to SQLite."""
    ratio = round(followers / max(following, 1), 4) if platform == 'instagram' else 0
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT INTO predictions (
                timestamp, platform, username, followers_count, following_count,
                follower_ratio, posts_or_tweets, bio_length,
                engagement_rate, prediction, probability, risk_level, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.utcnow().isoformat(),
            platform, username or 'anonymous',
            followers, following, ratio, posts, bio_len,
            0.0, pred, prob, risk_level, source
        ))
        conn.commit()

# ===================== UI HEADER =====================
col_h1, col_h2 = st.columns([3.5, 1.5])
with col_h1:
    st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-title">🛡️ FakeGuard AI Platform</h1>
        <p class="hero-subtitle">
            Enterprise-grade Fake Profile & Synthetic Identity Detection powered by 
            <strong>XGBoost</strong> and <strong>Random Forest</strong> algorithms.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    status_color = "#22C55E" if models_bundle["ready"] else "#EF4444"
    status_text = "Models Online" if models_bundle["ready"] else "Loading Failed"
    insta_name = models_bundle.get("insta_meta", {}).get("best_model", "XGBoost")
    tw_name = models_bundle.get("twitter_meta", {}).get("best_model", "Random Forest")
    st.markdown(f"""
    <div class="glass-card" style="padding: 16px 20px; text-align: center;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 6px;">
            <span style="height: 10px; width: 10px; border-radius: 50%; background: {status_color}; display: inline-block;"></span>
            <span style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">{status_text}</span>
        </div>
        <div style="font-size: 0.78rem; color: #94a3b8;">
            Instagram: <strong style="color: #c084fc;">{insta_name}</strong> | Twitter: <strong style="color: #38bdf8;">{tw_name}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===================== NAVIGATION TABS =====================
tabs = st.tabs([
    "🎯 Single Profile Scanner",
    "📁 Batch CSV Analysis",
    "📊 Threat Intelligence Dashboard",
    "📜 SQLite Audit History",
    "🧠 ML Models & Explainability"
])

# ==============================================================================
# TAB 1: SINGLE PROFILE SCANNER
# ==============================================================================
with tabs[0]:
    st.markdown("### 🔍 Real-Time Profile Risk Analysis")
    
    col_plat, col_preset = st.columns([2, 3])
    with col_plat:
        platform_choice = st.radio(
            "Select Social Media Platform",
            ["📷 Instagram", "🐦 Twitter / X"],
            horizontal=True,
            key="scanner_platform"
        )
        current_platform = "instagram" if "Instagram" in platform_choice else "twitter"
        
    with col_preset:
        st.write("⚡ Quick Test Presets:")
        preset_cols = st.columns(3)
        load_genuine = preset_cols[0].button("🟢 Genuine Profile", use_container_width=True)
        load_suspicious = preset_cols[1].button("🟡 Suspicious Profile", use_container_width=True)
        load_fake = preset_cols[2].button("🔴 Bot / Fake Profile", use_container_width=True)
        
    # State management for preset fields
    if "preset_type" not in st.session_state:
        st.session_state.preset_type = "default"
        
    if load_genuine:
        st.session_state.preset_type = "genuine"
    elif load_suspicious:
        st.session_state.preset_type = "suspicious"
    elif load_fake:
        st.session_state.preset_type = "fake"

    p_type = st.session_state.preset_type

    # Form setup based on platform
    with st.form("single_predict_form"):
        username_val = "john_doe_official" if p_type == "genuine" else ("user_4982713" if p_type == "fake" else "trend_reviewer_99")
        username = st.text_input("Username / Account Handle", value=username_val)

        if current_platform == "instagram":
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                has_pic_default = 1 if p_type in ("genuine", "suspicious") else 0
                has_pic = st.selectbox("Profile Avatar Present?", [1, 0], format_func=lambda x: "Yes (Profile Pic Set)" if x == 1 else "No (Default Avatar)", index=0 if has_pic_default == 1 else 1)
                
                num_ratio_default = 0.05 if p_type == "genuine" else (0.65 if p_type == "fake" else 0.25)
                nums_username = st.slider("Digits Ratio in Username", 0.0, 1.0, float(num_ratio_default), 0.01, help="e.g., 'user1234' is 4/8 = 0.5")
                
                fullname_words_default = 2 if p_type == "genuine" else (0 if p_type == "fake" else 1)
                fn_words = st.number_input("Full Name Word Count", 0, 10, int(fullname_words_default))
                
                nums_fn_default = 0.0 if p_type in ("genuine", "suspicious") else 0.4
                nums_fullname = st.slider("Digits Ratio in Full Name", 0.0, 1.0, float(nums_fn_default), 0.01)

            with col_f2:
                name_eq_default = 0 if p_type == "genuine" else (1 if p_type == "fake" else 0)
                name_eq_user = st.selectbox("Full Name Identical to Username?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes", index=name_eq_default)
                
                bio_len_default = 95 if p_type == "genuine" else (0 if p_type == "fake" else 15)
                bio_length = st.number_input("Bio Character Length", 0, 500, int(bio_len_default))
                
                has_url_default = 1 if p_type == "genuine" else 0
                has_url = st.selectbox("External Link in Bio?", [0, 1], format_func=lambda x: "No Link" if x == 0 else "Contains URL", index=has_url_default)
                
                is_priv_default = 0
                is_private = st.selectbox("Account Privacy", [0, 1], format_func=lambda x: "Public Account" if x == 0 else "Private Account", index=is_priv_default)

            with col_f3:
                posts_default = 150 if p_type == "genuine" else (2 if p_type == "fake" else 12)
                posts_cnt = st.number_input("Total Posts Published", 0, 50000, int(posts_default))
                
                followers_default = 1850 if p_type == "genuine" else (6 if p_type == "fake" else 120)
                followers_cnt = st.number_input("Followers Count", 0, 100000000, int(followers_default))
                
                following_default = 320 if p_type == "genuine" else (4500 if p_type == "fake" else 890)
                following_cnt = st.number_input("Following Count", 0, 1000000, int(following_default))
                
                # Computed ratio
                calc_ratio = round(followers_cnt / max(following_cnt, 1), 2)
                st.caption(f"Follower-to-Following Ratio: **{calc_ratio}**")

        else: # Twitter / X
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                retweet_default = 6 if p_type == "genuine" else (95 if p_type == "fake" else 35)
                retweet_cnt = st.slider("Average Retweet Velocity", 0, 200, int(retweet_default), help="High RT count with low original content is typical of bot syndicates.")
                
                mention_default = 1 if p_type == "genuine" else (12 if p_type == "fake" else 4)
                mention_cnt = st.slider("Mentions Density per Tweet", 0, 30, int(mention_default), help="Frequent mass mentions signal marketing bots or spam attacks.")

            with col_t2:
                tw_followers_default = 8500 if p_type == "genuine" else (8 if p_type == "fake" else 340)
                tw_followers = st.number_input("Follower Count", 0, 100000000, int(tw_followers_default))
                
                is_ver_default = 1 if p_type == "genuine" else 0
                is_verified = st.selectbox("Verified Badge (Blue/Gold/Grey)?", [0, 1], format_func=lambda x: "No (Unverified)" if x == 0 else "Yes (Verified Account)", index=is_ver_default)

        analyze_btn = st.form_submit_button("🚀 Run AI Deep Scan", use_container_width=True, type="primary")

    if analyze_btn:
        with st.spinner("Executing neural model inference & feature attribution..."):
            time.sleep(0.3)
            
            # Predict Logic
            if current_platform == "instagram":
                raw_inputs = {
                    "profile_pic": has_pic,
                    "nums_length_username": nums_username,
                    "fullname_words": fn_words,
                    "nums_length_fullname": nums_fullname,
                    "name_eq_username": name_eq_user,
                    "description_length": bio_length,
                    "external_url": has_url,
                    "private": is_private,
                    "posts_count": posts_cnt,
                    "followers_count": float(followers_cnt),
                    "following_count": float(following_cnt)
                }
                feature_vec = np.array([[
                    has_pic, nums_username, fn_words, nums_fullname,
                    name_eq_user, bio_length, has_url, is_private,
                    posts_cnt, followers_cnt, following_cnt
                ]])
                model = models_bundle["insta_model"]
                meta = models_bundle["insta_meta"]
                
                pred = int(model.predict(feature_vec)[0])
                prob = float(model.predict_proba(feature_vec)[0][1])
                
                record_prediction(
                    "instagram", username, followers_cnt, following_cnt,
                    posts_cnt, bio_length, pred, prob, get_risk_tier(prob)[0], "manual"
                )

            else: # Twitter
                raw_inputs = {
                    "retweet_count": retweet_cnt,
                    "mention_count": mention_cnt,
                    "follower_count_twitter": float(tw_followers),
                    "verified": is_verified
                }
                feature_vec = np.array([[retweet_cnt, mention_cnt, tw_followers, is_verified]])
                model = models_bundle["twitter_model"]
                meta = models_bundle["twitter_meta"]
                
                pred = int(model.predict(feature_vec)[0])
                prob = float(model.predict_proba(feature_vec)[0][1])
                
                record_prediction(
                    "twitter", username, tw_followers, 0,
                    0, 0, pred, prob, get_risk_tier(prob)[0], "manual"
                )

            tier_code, tier_label, tier_color, badge_class = get_risk_tier(prob)
            is_fake = pred == 1
            verdict_text = "⚠️ FAKE / SYNTHETIC ACCOUNT DETECTED" if is_fake else "✅ GENUINE / AUTHENTIC PROFILE"
            verdict_color = "#EF4444" if is_fake else "#22C55E"
            
            st.markdown("---")
            st.markdown(f"""
            <div class="glass-card" style="border-left: 6px solid {verdict_color};">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8;">Analysis Result for @{username or 'user'}</span>
                        <h2 style="color: {verdict_color}; margin: 4px 0 0 0; font-size: 1.8rem; font-weight: 800;">{verdict_text}</h2>
                    </div>
                    <div>
                        <span class="{badge_class}">{tier_label} ({prob*100:.1f}%)</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Details: Gauge + Explanations + Feature Importance
            col_res1, col_res2 = st.columns([1.8, 2.2])
            
            with col_res1:
                # Gauge Chart using Plotly
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=round(prob * 100, 1),
                    number={'suffix': "%", 'font': {'size': 38, 'color': tier_color}},
                    title={'text': "Fake Risk Probability", 'font': {'size': 16, 'color': '#94a3b8'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
                        'bar': {'color': tier_color, 'thickness': 0.28},
                        'bgcolor': "rgba(15, 23, 42, 0.6)",
                        'borderwidth': 1,
                        'bordercolor': "#334155",
                        'steps': [
                            {'range': [0, 45], 'color': "rgba(34, 197, 94, 0.15)"},
                            {'range': [45, 65], 'color': "rgba(234, 179, 8, 0.15)"},
                            {'range': [65, 85], 'color': "rgba(249, 115, 22, 0.15)"},
                            {'range': [85, 100], 'color': "rgba(239, 68, 68, 0.2)"}
                        ],
                        'threshold': {
                            'line': {'color': "#EF4444", 'width': 3},
                            'thickness': 0.8,
                            'value': 50
                        }
                    }
                ))
                fig_gauge.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=260,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
                
            with col_res2:
                st.markdown("#### 🧠 Explainable AI (XAI) Signals")
                explanations = generate_explanations(current_platform, raw_inputs, is_fake)
                for exp in explanations:
                    st.markdown(f'<div class="reason-item">{exp}</div>', unsafe_allow_html=True)
                    
            # Feature Importance
            st.markdown("#### 📊 Model Feature Importance Weights")
            feat_imp = meta.get("feature_importance", {})
            if feat_imp:
                df_imp = pd.DataFrame(list(feat_imp.items()), columns=["Feature", "Weight"]).sort_values("Weight", ascending=True)
                fig_imp = px.bar(
                    df_imp, x="Weight", y="Feature", orientation="h",
                    color="Weight", color_continuous_scale="Purp",
                    labels={"Weight": "Relative Importance", "Feature": ""},
                    height=280
                )
                fig_imp.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#cbd5e1",
                    margin=dict(l=10, r=10, t=10, b=10),
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_imp, use_container_width=True)

# ==============================================================================
# TAB 2: BATCH CSV ANALYSIS
# ==============================================================================
with tabs[1]:
    st.markdown("### 📁 High-Throughput Bulk CSV Batch Analyzer")
    st.markdown("Upload a CSV file containing multiple user profiles for instant automated security screening.")
    
    col_b_plat, col_b_sample = st.columns([2, 3])
    with col_b_plat:
        bulk_platform = st.radio("Platform for CSV Batch", ["Instagram", "Twitter / X"], horizontal=True, key="bulk_plat")
        b_plat_key = "instagram" if "Instagram" in bulk_platform else "twitter"
        
    with col_b_sample:
        st.write("📥 Quick Sample Template:")
        # Provide sample csv download
        sample_path = os.path.join(BASE_DIR, "sample_bulk_test.csv")
        if not os.path.exists(sample_path):
            sample_path = os.path.join(BASE_DIR, "FakeProfileDetector", "sample_bulk_test.csv")
            
        sample_df = pd.read_csv(sample_path) if os.path.exists(sample_path) else pd.DataFrame({
            "username": ["real_user", "bot_99"], "followers_count": [1200, 5],
            "following_count": [300, 4800], "posts_count": [80, 1],
            "has_profile_pic": [1, 0], "bio_length": [45, 0]
        })
        
        csv_buffer = io.BytesIO()
        sample_df.to_csv(csv_buffer, index=False)
        st.download_button(
            "⬇️ Download Sample Batch CSV",
            data=csv_buffer.getvalue(),
            file_name=f"sample_{b_plat_key}_profiles.csv",
            mime="text/csv",
            use_container_width=True
        )

    uploaded_file = st.file_uploader("Upload Profile CSV File", type=["csv"])
    
    load_demo_batch = st.button("🧪 Scan Included Demo Dataset (10 Profiles)", type="secondary")
    
    df_to_scan = None
    if uploaded_file is not None:
        try:
            df_to_scan = pd.read_csv(uploaded_file)
            st.success(f"Successfully loaded CSV with {len(df_to_scan)} profiles!")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
    elif load_demo_batch:
        df_to_scan = sample_df

    if df_to_scan is not None:
        st.dataframe(df_to_scan.head(5), use_container_width=True)
        
        run_bulk = st.button("⚡ Process All Profiles", type="primary", use_container_width=True)
        
        if run_bulk:
            with st.spinner("Processing batch records through detection pipeline..."):
                progress_bar = st.progress(0)
                results_list = []
                
                model = models_bundle["insta_model"] if b_plat_key == "instagram" else models_bundle["twitter_model"]
                
                for idx, row in df_to_scan.iterrows():
                    username_row = str(row.get("username", f"user_{idx}"))
                    
                    if b_plat_key == "instagram":
                        pic = int(float(row.get("profile pic", row.get("has_profile_pic", 1))))
                        nums_u = float(row.get("nums/length username", row.get("nums_username", 0.0)))
                        fn_w = int(float(row.get("fullname words", row.get("fullname_words", 2))))
                        nums_fn = float(row.get("nums/length fullname", row.get("nums_fullname", 0.0)))
                        nm_eq = int(float(row.get("name==username", row.get("name_eq_username", 0))))
                        bio_l = int(float(row.get("description length", row.get("bio_length", 50))))
                        ext_u = int(float(row.get("external URL", row.get("has_url_in_bio", 0))))
                        priv = int(float(row.get("private", row.get("is_private", 0))))
                        posts = int(float(row.get("#posts", row.get("posts_count", 50))))
                        foll = float(row.get("#followers", row.get("followers_count", 300)))
                        follin = float(row.get("#follows", row.get("following_count", 200)))
                        
                        f_vec = np.array([[pic, nums_u, fn_w, nums_fn, nm_eq, bio_l, ext_u, priv, posts, foll, follin]])
                        pred = int(model.predict(f_vec)[0])
                        prob = float(model.predict_proba(f_vec)[0][1])
                        
                        record_prediction("instagram", username_row, foll, follin, posts, bio_l, pred, prob, get_risk_tier(prob)[0], "bulk")
                    else:
                        retweets = int(float(row.get("Retweet Count", row.get("avg_retweets", 10))))
                        mentions = int(float(row.get("Mention Count", row.get("mention_count", 1))))
                        foll_tw = float(row.get("Follower Count", row.get("followers_count", 1000)))
                        ver = int(float(row.get("Verified", row.get("is_verified", 0))))
                        
                        f_vec = np.array([[retweets, mentions, foll_tw, ver]])
                        pred = int(model.predict(f_vec)[0])
                        prob = float(model.predict_proba(f_vec)[0][1])
                        
                        record_prediction("twitter", username_row, foll_tw, 0, 0, 0, pred, prob, get_risk_tier(prob)[0], "bulk")

                    tier_code, tier_label, _, _ = get_risk_tier(prob)
                    results_list.append({
                        "Username": username_row,
                        "Verdict": "Fake" if pred == 1 else "Genuine",
                        "Risk Tier": tier_label,
                        "Risk Probability": f"{prob*100:.1f}%",
                        "Raw Score": prob
                    })
                    progress_bar.progress((idx + 1) / len(df_to_scan))

                res_df = pd.DataFrame(results_list)
                total_cnt = len(res_df)
                fake_cnt = sum(res_df["Verdict"] == "Fake")
                real_cnt = total_cnt - fake_cnt
                fake_rate = (fake_cnt / total_cnt) * 100 if total_cnt else 0

                # Summary metric row
                st.markdown("---")
                st.markdown("#### 📊 Batch Screening Overview")
                m1, m2, m3, m4 = st.columns(4)
                m1.markdown(f'<div class="metric-pill"><div class="metric-pill-val">{total_cnt}</div><div class="metric-pill-lbl">Profiles Scanned</div></div>', unsafe_allow_html=True)
                m2.markdown(f'<div class="metric-pill"><div class="metric-pill-val" style="color: #EF4444;">{fake_cnt}</div><div class="metric-pill-lbl">Fake Profiles ({fake_rate:.1f}%)</div></div>', unsafe_allow_html=True)
                m3.markdown(f'<div class="metric-pill"><div class="metric-pill-val" style="color: #22C55E;">{real_cnt}</div><div class="metric-pill-lbl">Genuine Profiles</div></div>', unsafe_allow_html=True)
                m4.markdown(f'<div class="metric-pill"><div class="metric-pill-val">{res_df["Raw Score"].mean()*100:.1f}%</div><div class="metric-pill-lbl">Average Risk Score</div></div>', unsafe_allow_html=True)

                # Pie Chart
                fig_pie = px.pie(
                    res_df, names="Verdict", title="Batch Account Classification Breakdown",
                    color="Verdict", color_discrete_map={"Fake": "#EF4444", "Genuine": "#22C55E"},
                    hole=0.45
                )
                fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
                st.plotly_chart(fig_pie, use_container_width=True)

                st.markdown("#### 📋 Detailed Batch Output Table")
                st.dataframe(res_df.drop(columns=["Raw Score"]), use_container_width=True)

                # Download CSV
                out_buffer = io.BytesIO()
                res_df.to_csv(out_buffer, index=False)
                st.download_button(
                    "⬇️ Download Analysis Results CSV",
                    data=out_buffer.getvalue(),
                    file_name=f"fakeguard_batch_results_{int(time.time())}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )

# ==============================================================================
# TAB 3: THREAT INTELLIGENCE DASHBOARD
# ==============================================================================
with tabs[2]:
    st.markdown("### 📊 Global Threat Intelligence Dashboard")
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        total_scans = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        
        if total_scans == 0:
            st.info("No scan records currently found in the database. Run some single or batch scans to generate live analytics!")
        else:
            fake_total = conn.execute("SELECT COUNT(*) FROM predictions WHERE prediction = 1").fetchone()[0]
            real_total = total_scans - fake_total
            avg_p = conn.execute("SELECT AVG(probability) FROM predictions").fetchone()[0] or 0.0
            
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f'<div class="metric-pill"><div class="metric-pill-val">{total_scans}</div><div class="metric-pill-lbl">Total Scans Performed</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="metric-pill"><div class="metric-pill-val" style="color: #EF4444;">{fake_total}</div><div class="metric-pill-lbl">Fake Detections ({fake_total/total_scans*100:.1f}%)</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="metric-pill"><div class="metric-pill-val" style="color: #22C55E;">{real_total}</div><div class="metric-pill-lbl">Genuine Profiles</div></div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="metric-pill"><div class="metric-pill-val">{avg_p*100:.1f}%</div><div class="metric-pill-lbl">Average Risk Score</div></div>', unsafe_allow_html=True)

            col_ch1, col_ch2 = st.columns(2)
            
            # Platform breakdown chart
            with col_ch1:
                df_plat = pd.read_sql_query("SELECT platform, COUNT(*) as count, SUM(prediction) as fake_count FROM predictions GROUP BY platform", conn)
                df_plat["genuine_count"] = df_plat["count"] - df_plat["fake_count"]
                
                fig_pbar = px.bar(
                    df_plat, x="platform", y=["genuine_count", "fake_count"],
                    barmode="group",
                    title="Platform Detections (Genuine vs Fake)",
                    color_discrete_map={"genuine_count": "#22C55E", "fake_count": "#EF4444"},
                    labels={"value": "Number of Accounts", "variable": "Type", "platform": "Platform"}
                )
                fig_pbar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
                st.plotly_chart(fig_pbar, use_container_width=True)

            # Risk Distribution Chart
            with col_ch2:
                df_risk = pd.read_sql_query("SELECT risk_level, COUNT(*) as count FROM predictions GROUP BY risk_level", conn)
                fig_rpie = px.pie(
                    df_risk, names="risk_level", values="count",
                    title="Threat Risk Tier Breakdown",
                    color="risk_level",
                    color_discrete_map={"critical": "#EF4444", "high": "#F97316", "medium": "#EAB308", "low": "#22C55E"},
                    hole=0.4
                )
                fig_rpie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
                st.plotly_chart(fig_rpie, use_container_width=True)

            # Recent scans list
            st.markdown("#### 🕒 Recent Detections Stream")
            df_recent = pd.read_sql_query("SELECT id, timestamp, platform, username, followers_count, prediction, probability, risk_level, source FROM predictions ORDER BY id DESC LIMIT 10", conn)
            df_recent["Verdict"] = df_recent["prediction"].apply(lambda x: "Fake" if x == 1 else "Genuine")
            df_recent["Risk Score"] = df_recent["probability"].apply(lambda x: f"{x*100:.1f}%")
            st.dataframe(df_recent[["id", "timestamp", "platform", "username", "Verdict", "Risk Score", "risk_level", "source"]], use_container_width=True)

# ==============================================================================
# TAB 4: SQLITE AUDIT HISTORY
# ==============================================================================
with tabs[3]:
    st.markdown("### 📜 SQLite Prediction Audit Log")
    
    col_hf1, col_hf2, col_hf3 = st.columns([2, 2, 2])
    with col_hf1:
        hist_plat = st.selectbox("Filter Platform", ["All", "instagram", "twitter"])
    with col_hf2:
        hist_risk = st.selectbox("Filter Risk Level", ["All", "critical", "high", "medium", "low"])
    with col_hf3:
        clear_hist = st.button("🗑️ Clear Audit Database", type="secondary")
        
    if clear_hist:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM predictions")
            conn.commit()
        st.success("Audit history cleared successfully!")
        st.rerun()

    query = "SELECT * FROM predictions WHERE 1=1"
    params = []
    if hist_plat != "All":
        query += " AND platform = ?"
        params.append(hist_plat)
    if hist_risk != "All":
        query += " AND risk_level = ?"
        params.append(hist_risk)
    query += " ORDER BY id DESC"

    with sqlite3.connect(DB_PATH) as conn:
        df_hist = pd.read_sql_query(query, conn, params=params)
        
    st.markdown(f"**Total Records Matching Filter:** `{len(df_hist)}`")
    if not df_hist.empty:
        df_hist_display = df_hist.copy()
        df_hist_display["Verdict"] = df_hist_display["prediction"].apply(lambda x: "🔴 Fake" if x == 1 else "🟢 Genuine")
        df_hist_display["Probability"] = df_hist_display["probability"].apply(lambda x: f"{x*100:.2f}%")
        st.dataframe(df_hist_display, use_container_width=True)
        
        hist_buffer = io.BytesIO()
        df_hist.to_csv(hist_buffer, index=False)
        st.download_button(
            "⬇️ Export Filtered Audit History (CSV)",
            data=hist_buffer.getvalue(),
            file_name="fakeguard_audit_log.csv",
            mime="text/csv"
        )
    else:
        st.info("No records match the current filter selection.")

# ==============================================================================
# TAB 5: ML MODELS & EXPLAINABILITY
# ==============================================================================
with tabs[4]:
    st.markdown("### 🧠 Machine Learning Model Architectures & Benchmark Metrics")
    st.markdown("Compare trained algorithms, dataset distribution, and validation metrics.")
    
    col_m1, col_m2 = st.columns(2)
    
    # Instagram Model Card
    with col_m1:
        insta_m = models_bundle.get("insta_meta", {})
        res_i = insta_m.get("results", {})
        st.markdown(f"""
        <div class="glass-card" style="border-top: 4px solid #C084FC;">
            <h3 style="color: #C084FC; margin-top: 0;">📷 Instagram Classifier</h3>
            <p style="color: #cbd5e1; font-size: 0.9rem;">
                <strong>Active Algorithm:</strong> {insta_m.get('best_model', 'XGBoost')}<br>
                <strong>Training Dataset:</strong> instagram1 + instagram2 (5,052 profiles)<br>
                <strong>Feature Dimensions:</strong> 11 behavioral & metadata signals
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if res_i:
            df_i_metrics = pd.DataFrame(res_i).T[["accuracy", "precision", "recall", "f1_score", "auc_roc"]]
            df_i_metrics.columns = ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]
            st.dataframe(df_i_metrics.style.format("{:.4f}").background_gradient(cmap="Purples"), use_container_width=True)

    # Twitter Model Card
    with col_m2:
        tw_m = models_bundle.get("twitter_meta", {})
        res_t = tw_m.get("results", {})
        st.markdown(f"""
        <div class="glass-card" style="border-top: 4px solid #38BDF8;">
            <h3 style="color: #38BDF8; margin-top: 0;">🐦 Twitter / X Bot Detector</h3>
            <p style="color: #cbd5e1; font-size: 0.9rem;">
                <strong>Active Algorithm:</strong> {tw_m.get('best_model', 'Random Forest')}<br>
                <strong>Training Dataset:</strong> twitter1 bot_detection_data (50,000 tweets)<br>
                <strong>Feature Dimensions:</strong> 4 engagement & account verification signals
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if res_t:
            df_t_metrics = pd.DataFrame(res_t).T[["accuracy", "precision", "recall", "f1_score", "auc_roc"]]
            df_t_metrics.columns = ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]
            st.dataframe(df_t_metrics.style.format("{:.4f}").background_gradient(cmap="Blues"), use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📑 Dataset Schema & Feature Dictionary")
    st.markdown("""
    | Platform | Feature | Type | Description |
    | :--- | :--- | :--- | :--- |
    | **Instagram** | `profile pic` | Binary (0/1) | Whether account has a custom profile avatar |
    | **Instagram** | `nums/length username` | Float [0-1] | Proportion of numeric digits in username |
    | **Instagram** | `fullname words` | Integer | Word count in profile full name |
    | **Instagram** | `nums/length fullname` | Float [0-1] | Proportion of numeric digits in full name |
    | **Instagram** | `name==username` | Binary (0/1) | Whether username is identical to full name |
    | **Instagram** | `description length` | Integer | Bio character length |
    | **Instagram** | `external URL` | Binary (0/1) | Presence of link in bio |
    | **Instagram** | `private` | Binary (0/1) | Account privacy status |
    | **Instagram** | `#posts` | Integer | Lifetime post volume |
    | **Instagram** | `#followers` | Integer | Follower count |
    | **Instagram** | `#follows` | Integer | Following count |
    | **Twitter/X** | `Retweet Count` | Integer | Mean retweets generated |
    | **Twitter/X** | `Mention Count` | Integer | Mentions per post |
    | **Twitter/X** | `Follower Count` | Integer | Total audience size |
    | **Twitter/X** | `Verified` | Binary (0/1) | Identity verification badge |
    """)

# ===================== FOOTER =====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 15px 0;">
    FakeGuard AI Platform • Multi-Platform Fake Profile Detection • Built with Streamlit, FastAPI, XGBoost & Scikit-Learn
</div>
""", unsafe_allow_html=True)
