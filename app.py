"""
Mindful Work — Smart Stress Relief Pod Companion App
=====================================================
FutureForward Wellness | Design Thinking for Innovation — Year 1 Summative

Streamlit Cloud compatible single-file version.
Deploy at: https://streamlit.io/cloud

Run locally:
    pip install streamlit plotly
    streamlit run app.py
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import json, os, random, time, threading
from datetime import datetime
from typing import Optional

import streamlit as st
import plotly.graph_objects as go

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Mindful Work — Stress Relief Pod",
    page_icon="🧘",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Playfair+Display:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 700px; }

/* Cards */
.mw-card {
    background: #ffffff;
    border-radius: 18px;
    border: 1px solid #e8edf2;
    padding: 20px 22px;
    margin-bottom: 14px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.mw-card-sage  { background: linear-gradient(135deg,#e8f5f0,#edf5f2); border:1px solid #b8e0d2; }
.mw-card-blush { background: linear-gradient(135deg,#fff5f5,#fdecea); border:1px solid #ffc5c5; }
.mw-card-info  { background: linear-gradient(135deg,#e8f0fb,#edf3fb); border:1px solid #b5d4f4; }
.mw-card-hero  { background: linear-gradient(135deg,#6c9bcf,#4a7c9f); border-radius:18px; padding:24px; margin-bottom:14px; }

/* Tags */
.mw-tag { display:inline-block; padding:3px 10px; border-radius:8px; font-size:12px; font-weight:500; margin:2px; }
.mw-tag-sage  { background:#e8f5f0; color:#2d6a58; }
.mw-tag-blue  { background:#e8f0fb; color:#1a4f8a; }
.mw-tag-amber { background:#fdf5e4; color:#8a6200; }
.mw-tag-red   { background:#fdecea; color:#a32d2d; }

/* Headings */
.mw-heading { font-family:'Playfair Display',serif; font-size:26px; color:#2c3e50; margin-bottom:4px; }
.mw-sub     { font-size:14px; color:#7f8c8d; margin-bottom:0; }
.mw-section { font-family:'Playfair Display',serif; font-size:18px; color:#2c3e50; margin:18px 0 8px; }

/* Stat cards */
.mw-stat { text-align:center; background:#f8f9fd; border-radius:14px; padding:16px 10px; border:1px solid #e8edf2; }
.mw-stat-num { font-family:'Playfair Display',serif; font-size:28px; color:#6c9bcf; font-weight:500; }
.mw-stat-lbl { font-size:11px; color:#7f8c8d; text-transform:uppercase; letter-spacing:.06em; margin-top:2px; }

/* Stress level pills */
.stress-low    { background:#e8f5ef; color:#1a6a40; border:1px solid #b8e0d2; padding:6px 16px; border-radius:20px; font-weight:600; display:inline-block; }
.stress-medium { background:#fdf5e4; color:#8a6200; border:1px solid #f9d89a; padding:6px 16px; border-radius:20px; font-weight:600; display:inline-block; }
.stress-high   { background:#fdecea; color:#a32d2d; border:1px solid #f5c1c1; padding:6px 16px; border-radius:20px; font-weight:600; display:inline-block; }

/* Session card */
.session-item { display:flex; align-items:center; gap:12px; padding:10px 0; border-bottom:1px solid #f0f0ec; }
.session-item:last-child { border-bottom:none; }
.session-icon { width:38px; height:38px; border-radius:10px; background:#e8f5f0; display:flex; align-items:center; justify-content:center; font-size:18px; flex-shrink:0; }

/* Breathing circle */
.breathe-wrap { text-align:center; padding:30px 0; }
.breathe-circle { width:160px; height:160px; border-radius:50%; background:radial-gradient(circle,#e8f5f0,rgba(232,242,239,0.3));
    border:2px solid #b8e0d2; display:flex; align-items:center; justify-content:center;
    margin:0 auto 16px; flex-direction:column; }

/* AI pulse dot */
.ai-dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:#4a7c6f; margin-right:6px;
    animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }

/* Nav tabs override */
div[data-testid="stTabs"] [data-baseweb="tab-list"] { gap:4px; }
div[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius:10px; padding:8px 16px; font-size:13px; font-weight:500;
}

/* Progress bar */
.mw-prog-wrap { background:#e8f5f0; border-radius:8px; height:8px; width:100%; margin-top:6px; }
.mw-prog-bar  { background:#4a7c6f; border-radius:8px; height:8px; }

/* Divider */
.mw-divider { height:1px; background:#f0f0ec; margin:12px 0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS & PRESETS
# ══════════════════════════════════════════════════════════════════════════════

PRESETS = {
    "warm_lofi_lavender": {
        "name": "Sunset Calm", "emoji": "🌅",
        "lighting": "warm", "music": "lo-fi", "aroma": "lavender",
        "description": "Warm amber lighting with lo-fi beats and calming lavender",
    },
    "cool_nature_eucalyptus": {
        "name": "Forest Refresh", "emoji": "🌲",
        "lighting": "cool", "music": "nature", "aroma": "eucalyptus",
        "description": "Cool blue-white light with forest sounds and refreshing eucalyptus",
    },
    "color_binaural_citrus": {
        "name": "Focus Flow", "emoji": "⚡",
        "lighting": "color_therapy", "music": "binaural", "aroma": "citrus",
        "description": "Color-cycling therapy lights with binaural beats and energizing citrus",
    },
    "warm_classical_sandalwood": {
        "name": "Deep Unwind", "emoji": "🎻",
        "lighting": "warm", "music": "classical", "aroma": "sandalwood",
        "description": "Soft warm glow with classical piano and grounding sandalwood",
    },
}

LIGHTING_OPTIONS  = ["warm", "cool", "color_therapy"]
MUSIC_OPTIONS     = ["lo-fi", "nature", "binaural", "classical"]
AROMA_OPTIONS     = ["lavender", "eucalyptus", "citrus", "sandalwood"]
DURATION_OPTIONS  = [5, 10, 15, 20]
ROLES             = ["Software Engineer", "Project Manager", "Designer",
                     "Data Analyst", "HR Manager", "Marketing Lead", "Employee"]
MOOD_EMOJIS       = ["😌","🙂","😐","😕","😟","😣","😫","😰","😵","🤯"]

BREATHING_PATTERNS = {
    "box_breathing": {
        "name": "Box Breathing",
        "phases": [("Breathe In 🫁", 4), ("Hold 🤐", 4), ("Breathe Out 💨", 4), ("Hold 🤐", 4)],
    },
    "4_7_8_breathing": {
        "name": "4-7-8 Breathing",
        "phases": [("Breathe In 🫁", 4), ("Hold 🤐", 7), ("Breathe Out 💨", 8)],
    },
}

COLD_START = {"Low": "cool_nature_eucalyptus", "Medium": "warm_lofi_lavender", "High": "warm_classical_sandalwood"}
STRESS_AFFINITY = {
    "Low":    {"warm_lofi_lavender":0.8,"cool_nature_eucalyptus":1.2,"color_binaural_citrus":1.1,"warm_classical_sandalwood":0.7},
    "Medium": {"warm_lofi_lavender":1.2,"cool_nature_eucalyptus":1.0,"color_binaural_citrus":0.9,"warm_classical_sandalwood":1.0},
    "High":   {"warm_lofi_lavender":1.0,"cool_nature_eucalyptus":0.8,"color_binaural_citrus":0.7,"warm_classical_sandalwood":1.3},
}

# ══════════════════════════════════════════════════════════════════════════════
# STATE — Session state acts as our in-memory database (no files on Streamlit Cloud)
# ══════════════════════════════════════════════════════════════════════════════

def _init_state():
    defaults = {
        "screen": "login",
        "users": {},           # {user_id: user_dict}
        "current_user": None,  # user_id string
        "stress_score": 5.0,
        "stress_level": "Medium",
        "stress_explanation": "",
        "survey_score": 5.0,
        "wearable_hr": None,
        "wearable_hrv": None,
        "voice_score": None,
        "wearable_connected": False,
        "voice_done": False,
        "current_session": None,  # session dict
        "breathe_phase_idx": 0,
        "breathe_tick": 0,
        "breathe_running": False,
        "breathe_round": 0,
        "journal_before": 7.0,
        "journal_after": 3.0,
        "journal_text": "",
        "journal_mood": "😌 Calm",
        "journal_stars": 4,
        "selected_slot": None,
        "selected_dur": 15,
        "pod_preset": "warm_lofi_lavender",
        "pod_lighting": "warm",
        "pod_music": "lo-fi",
        "pod_aroma": "lavender",
        "pod_aroma_intensity": 5,
        "pod_meditation": "box_breathing",
        "pod_duration": 10,
        "session_elapsed": 0,
        "session_started": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    # Seed demo users
    if not st.session_state.users:
        st.session_state.users = {
            "priya": {
                "user_id":"priya","name":"Priya Sharma","role":"Software Engineer","emoji":"👩‍💻",
                "streak":3,"total_sessions":3,"total_minutes":35,
                "preset_weights":{"warm_lofi_lavender":1.4,"cool_nature_eucalyptus":1.0,"color_binaural_citrus":1.0,"warm_classical_sandalwood":1.0},
                "history":[
                    {"date":"2026-04-14","stress_score":7.5,"post_score":4.0,"preset":"warm_lofi_lavender","duration_minutes":10},
                    {"date":"2026-04-15","stress_score":6.0,"post_score":3.5,"preset":"cool_nature_eucalyptus","duration_minutes":15},
                    {"date":"2026-04-16","stress_score":8.0,"post_score":4.5,"preset":"warm_lofi_lavender","duration_minutes":10},
                ],
            },
            "rahul": {
                "user_id":"rahul","name":"Rahul Mehta","role":"Project Manager","emoji":"👨‍💼",
                "streak":2,"total_sessions":2,"total_minutes":35,
                "preset_weights":{"warm_lofi_lavender":1.0,"cool_nature_eucalyptus":1.0,"color_binaural_citrus":1.0,"warm_classical_sandalwood":1.5},
                "history":[
                    {"date":"2026-04-15","stress_score":6.5,"post_score":3.0,"preset":"warm_classical_sandalwood","duration_minutes":20},
                    {"date":"2026-04-16","stress_score":7.0,"post_score":3.5,"preset":"warm_classical_sandalwood","duration_minutes":15},
                ],
            },
        }

_init_state()

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def go(screen): st.session_state.screen = screen; st.rerun()

def mood_emoji(score):
    return MOOD_EMOJIS[max(0, min(9, int(round(score)) - 1))]

def stress_pill(level):
    cls = {"Low":"stress-low","Medium":"stress-medium","High":"stress-high"}.get(level,"stress-medium")
    icons = {"Low":"🟢","Medium":"🟡","High":"🔴"}
    return f'<span class="{cls}">{icons.get(level,"")} {level} Stress</span>'

def current_user():
    uid = st.session_state.current_user
    return st.session_state.users.get(uid) if uid else None

def save_user(u):
    st.session_state.users[u["user_id"]] = u

def compute_stress():
    s = st.session_state.survey_score
    components, weights = [s], [0.30]
    exp = [f"Self-report: {s:.1f}/10"]
    hr, hrv = st.session_state.wearable_hr, st.session_state.wearable_hrv
    if hr is not None and hrv is not None:
        hr_s  = ((max(55,min(120,hr)) - 55) / 65) * 10
        hrv_s = ((80 - max(15,min(80,hrv))) / 65) * 10
        physio = (hr_s + hrv_s) / 2
        components.append(physio); weights.append(0.35)
        exp.append(f"Wearable: HR={hr:.0f}bpm, HRV={hrv:.0f}ms")
    vs = st.session_state.voice_score
    if vs is not None:
        components.append(vs); weights.append(0.35)
        exp.append(f"Voice: {vs:.1f}/10")
    tw = sum(weights)
    score = max(1.0, min(10.0, sum(c*(w/tw) for c,w in zip(components,weights))))
    level = "Low" if score<=3.5 else ("Medium" if score<=6.5 else "High")
    st.session_state.stress_score = round(score,1)
    st.session_state.stress_level = level
    st.session_state.stress_explanation = " | ".join(exp)
    return round(score,1), level

def get_recommendation():
    u = current_user()
    level = st.session_state.stress_level
    if not u or not u.get("history"):
        key = COLD_START.get(level,"warm_lofi_lavender")
        return key, PRESETS[key], f"First-time default for {level.lower()} stress."
    weights = u.get("preset_weights",{k:1.0 for k in PRESETS})
    affinity = STRESS_AFFINITY.get(level, STRESS_AFFINITY["Medium"])
    scores = {k: weights.get(k,1.0)*affinity.get(k,1.0) for k in PRESETS}
    key = max(scores, key=scores.get)
    info = PRESETS[key]
    success = sum(1 for s in u["history"] if s.get("preset")==key and s.get("stress_score",5)-s.get("post_score",5)>0)
    total   = sum(1 for s in u["history"] if s.get("preset")==key)
    reason  = f"'{info['name']}' worked {success}/{total} times for you." if total else f"Best match for {level.lower()} stress."
    return key, info, reason

def update_weights(u, preset_key, pre, post):
    weights = u.get("preset_weights",{k:1.0 for k in PRESETS})
    delta = pre - post
    sr    = max(0.0, min(1.0, delta/pre)) if pre > 0 else 0.5
    old   = weights.get(preset_key,1.0)
    weights[preset_key] = round(max(0.3, min(3.0, 0.3*(1+sr)+0.7*old)), 3)
    u["preset_weights"] = weights

def get_ai_insight():
    u = current_user()
    if not u or not u.get("history"): return "Complete your first session to receive personalised insights!"
    if len(u["history"]) < 2: return "A few more sessions and AI will identify your best patterns."
    pd = {}
    for s in u["history"]:
        k = s.get("preset","unknown")
        pd.setdefault(k,[]).append(s.get("stress_score",5)-s.get("post_score",5))
    best = max(pd, key=lambda k: sum(pd[k])/len(pd[k]))
    avg  = sum(pd[best])/len(pd[best])
    p    = PRESETS.get(best,{})
    return f"You respond best to {p.get('aroma','').title()} + {p.get('music','').title()} ('{p.get('name',best)}'). Avg reduction: {avg:.1f} pts/session."

def get_stats():
    u = current_user()
    if not u: return {"total_sessions":0,"total_minutes":0,"streak":0,"avg_improvement":0.0}
    deltas = [s.get("stress_score",5)-s.get("post_score",5) for s in u.get("history",[])]
    return {
        "total_sessions": u.get("total_sessions",0),
        "total_minutes":  u.get("total_minutes",0),
        "streak":         u.get("streak",0),
        "avg_improvement": round(sum(deltas)/len(deltas),1) if deltas else 0.0,
    }

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: LOGIN
# ══════════════════════════════════════════════════════════════════════════════

def screen_login():
    st.markdown('<div style="text-align:center;padding:20px 0 10px">', unsafe_allow_html=True)
    st.markdown("# 🧘")
    st.markdown('<div class="mw-heading" style="text-align:center">Mindful Work</div>', unsafe_allow_html=True)
    st.markdown('<div class="mw-sub" style="text-align:center">Smart Stress Relief Pod · FutureForward Wellness</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

    users = st.session_state.users
    if users:
        st.markdown('<div class="mw-section">👤 Welcome back</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(users), 2))
        for i, (uid, u) in enumerate(users.items()):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="mw-card mw-card-sage" style="text-align:center;cursor:pointer">
                    <div style="font-size:36px">{u['emoji']}</div>
                    <div style="font-weight:600;font-size:15px;margin:6px 0 2px">{u['name']}</div>
                    <div style="font-size:12px;color:#7f8c8d">{u['role']}</div>
                    <div style="font-size:12px;color:#4a7c6f;margin-top:6px">🔥 {u.get('streak',0)} day streak · {u.get('total_sessions',0)} sessions</div>
                </div>""", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"Login", key=f"login_{uid}", use_container_width=True, type="primary"):
                        st.session_state.current_user = uid
                        go("home")
                with c2:
                    if st.button("🗑️", key=f"del_{uid}", use_container_width=True):
                        del st.session_state.users[uid]
                        st.rerun()

    st.markdown('<div class="mw-section">➕ New User</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="mw-card">', unsafe_allow_html=True)
        name = st.text_input("Full Name", placeholder="e.g. Riya Sharma")
        role = st.selectbox("Role", ROLES)
        if st.button("🚀 Register & Start", type="primary", use_container_width=True):
            if not name.strip():
                st.error("Please enter your name.")
            elif len(name.strip()) < 2:
                st.error("Name must be at least 2 characters.")
            else:
                uid = name.strip().lower().replace(" ","_")
                if uid in st.session_state.users:
                    st.error("A user with this name already exists.")
                else:
                    st.session_state.users[uid] = {
                        "user_id":uid,"name":name.strip(),"role":role,"emoji":"🧑",
                        "streak":0,"total_sessions":0,"total_minutes":0,
                        "preset_weights":{k:1.0 for k in PRESETS},"history":[],
                    }
                    st.session_state.current_user = uid
                    go("home")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align:center;font-size:12px;color:#aaa;margin-top:20px">Transform workplace stress into focus, calmness, and productivity</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: HOME
# ══════════════════════════════════════════════════════════════════════════════

def screen_home():
    u = current_user()
    if not u: go("login"); return

    # Top bar
    c1, c2 = st.columns([4,1])
    with c1:
        st.markdown(f'<div class="mw-heading">{u["emoji"]} Hi {u["name"].split()[0]}!</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="mw-sub">{u["role"]} · 🔥 {u.get("streak",0)} day streak</div>', unsafe_allow_html=True)
    with c2:
        if st.button("Logout", type="secondary"):
            st.session_state.current_user = None; go("login")

    # CTA hero
    st.markdown("""
    <div class="mw-card mw-card-hero">
        <div style="color:rgba(255,255,255,0.85);font-size:13px;margin-bottom:4px">FutureForward Wellness</div>
        <div style="font-family:'Playfair Display',serif;font-size:22px;color:white;margin-bottom:8px">Ready for a wellness break?</div>
        <div style="font-size:14px;color:rgba(255,255,255,0.8)">Check your stress and get a personalised pod session in 60 seconds.</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🧠  Begin Stress Check", type="primary", use_container_width=True):
        st.session_state.survey_score = 5.0
        st.session_state.wearable_hr = None; st.session_state.wearable_hrv = None
        st.session_state.voice_score = None; st.session_state.wearable_connected = False
        st.session_state.voice_done = False
        go("stress_check")

    # Stats
    st.markdown('<div class="mw-section">📊 Today\'s Summary</div>', unsafe_allow_html=True)
    stats = get_stats()
    cols = st.columns(4)
    for col, (emoji, lbl, val) in zip(cols, [
        ("🧘","Sessions",str(stats["total_sessions"])),
        ("⏱️","Minutes",str(stats["total_minutes"])),
        ("🔥","Streak",f"{stats['streak']}d"),
        ("📈","Avg Relief",f"{stats['avg_improvement']:+.1f}"),
    ]):
        with col:
            st.markdown(f'<div class="mw-stat"><div class="mw-stat-num">{val}</div><div class="mw-stat-lbl">{emoji} {lbl}</div></div>', unsafe_allow_html=True)

    # AI insight
    st.markdown('<div class="mw-section">💡 AI Insight</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mw-card mw-card-sage"><span class="ai-dot"></span><strong>MoodSync AI</strong><br><span style="font-size:14px;color:#2c3e50">{get_ai_insight()}</span></div>', unsafe_allow_html=True)

    # Recent sessions
    history = u.get("history",[])
    if history:
        st.markdown('<div class="mw-section">🕓 Recent Sessions</div>', unsafe_allow_html=True)
        st.markdown('<div class="mw-card">', unsafe_allow_html=True)
        for s in reversed(history[-3:]):
            preset  = PRESETS.get(s.get("preset",""),{})
            delta   = s.get("stress_score",5) - s.get("post_score",5)
            st.markdown(f"""
            <div class="session-item">
                <div class="session-icon">{preset.get('emoji','🧘')}</div>
                <div style="flex:1">
                    <div style="font-weight:500;font-size:14px">{preset.get('name','Session')}</div>
                    <div style="font-size:11px;color:#7f8c8d">{s.get('date','')} · {s.get('duration_minutes',10)} min</div>
                </div>
                <span class="mw-tag mw-tag-sage">-{delta:.1f} pts</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Quick links
    st.markdown('<div class="mw-section">⚡ Quick Actions</div>', unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("🫁\nBreathe", use_container_width=True): go("breathe")
    with q2:
        if st.button("📅\nSchedule", use_container_width=True): go("schedule")
    with q3:
        if st.button("📝\nJournal", use_container_width=True): go("journal")
    with q4:
        if st.button("📊\nProgress", use_container_width=True): go("progress")

    # Counselor card
    if len(history) >= 3 and all(s.get("stress_score",0) >= 8 for s in history[-3:]):
        st.warning("🤝 We've noticed consistently high stress levels. Consider speaking with your HR team or a wellness counselor. Your well-being matters.")

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: STRESS CHECK
# ══════════════════════════════════════════════════════════════════════════════

def screen_stress_check():
    c1, c2 = st.columns([1,5])
    with c1:
        if st.button("← Back"): go("home")
    with c2:
        st.markdown('<div class="mw-heading">Stress Check</div>', unsafe_allow_html=True)

    # Survey
    st.markdown('<div class="mw-card">', unsafe_allow_html=True)
    st.markdown("**😌 How are you feeling right now?**")
    score = st.slider("Stress level", 1, 10, int(st.session_state.survey_score), key="survey_slider_val")
    st.session_state.survey_score = float(score)
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<span style="color:#27ae60;font-size:12px">😌 Calm</span>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div style="text-align:center;font-size:28px">{mood_emoji(score)}</div>', unsafe_allow_html=True)
    with col3: st.markdown('<span style="color:#e74c3c;font-size:12px;float:right">😵 Stressed</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Wearable
    with st.expander("⌚ Wearable Data (Optional — click to expand)"):
        st.markdown("Connect your smartwatch for physiological stress indicators.")
        if not st.session_state.wearable_connected:
            if st.button("🔗 Connect Wearable (Simulated)", type="secondary"):
                hr  = random.uniform(68, 95)
                hrv = random.uniform(25, 60)
                st.session_state.wearable_hr  = hr
                st.session_state.wearable_hrv = hrv
                st.session_state.wearable_connected = True
                st.rerun()
        else:
            st.success(f"✅ Connected · ❤️ HR: {st.session_state.wearable_hr:.0f} bpm · 📊 HRV: {st.session_state.wearable_hrv:.0f} ms")
            if st.button("Disconnect"):
                st.session_state.wearable_connected = False
                st.session_state.wearable_hr = None; st.session_state.wearable_hrv = None
                st.rerun()

    # Voice
    with st.expander("🎙️ Voice Tone Analysis (Optional — click to expand)"):
        st.markdown("Simulate voice analysis to detect stress from your tone.")
        if not st.session_state.voice_done:
            if st.button("🎤 Analyse Voice (Simulated)", type="secondary"):
                st.session_state.voice_score = round(random.uniform(3.0, 8.5), 1)
                st.session_state.voice_done = True
                st.rerun()
        else:
            st.success(f"✅ Voice stress score: {st.session_state.voice_score:.1f} / 10")
            if st.button("Re-analyse"):
                st.session_state.voice_done = False; st.session_state.voice_score = None; st.rerun()

    st.markdown("---")
    if st.button("🧠 Compute Stress Score", type="primary", use_container_width=True):
        score, level = compute_stress()
        colors = {"Low":"#27ae60","Medium":"#f39c12","High":"#e74c3c"}
        st.markdown(f"""
        <div class="mw-card" style="border:2px solid {colors.get(level,'#6c9bcf')};text-align:center">
            <div style="font-size:13px;color:#7f8c8d;margin-bottom:8px">Your Stress Assessment</div>
            {stress_pill(level)}
            <div style="font-family:'Playfair Display',serif;font-size:48px;color:{colors.get(level,'#333')};margin:10px 0">{score}</div>
            <div style="font-size:13px;color:#7f8c8d;margin-bottom:4px">out of 10</div>
            <div style="font-size:12px;color:#7f8c8d">{st.session_state.stress_explanation}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.stress_explanation:
        if st.button("🎯 Get Pod Recommendation →", type="primary", use_container_width=True):
            rec_key, rec_info, _ = get_recommendation()
            st.session_state.pod_preset    = rec_key
            st.session_state.pod_lighting  = rec_info["lighting"]
            st.session_state.pod_music     = rec_info["music"]
            st.session_state.pod_aroma     = rec_info["aroma"]
            st.session_state.pod_duration  = 10 if st.session_state.stress_score <= 6 else (15 if st.session_state.stress_score <= 8 else 20)
            st.session_state.pod_aroma_intensity = min(10, max(1, int(st.session_state.stress_score)))
            go("pod_setup")

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: POD SETUP
# ══════════════════════════════════════════════════════════════════════════════

def screen_pod_setup():
    c1, c2 = st.columns([1,5])
    with c1:
        if st.button("← Back"): go("stress_check")
    with c2:
        st.markdown('<div class="mw-heading">Pod Setup</div>', unsafe_allow_html=True)

    rec_key, rec_info, reasoning = get_recommendation()
    score = st.session_state.stress_score
    level = st.session_state.stress_level

    # AI recommendation card
    st.markdown(f"""
    <div class="mw-card mw-card-sage">
        <div style="font-size:11px;font-weight:600;color:#4a7c6f;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px">
            <span class="ai-dot"></span>MoodSync AI — Recommended for you
        </div>
        <div style="font-size:22px;margin-bottom:4px">{rec_info['emoji']} {rec_info['name']}</div>
        <div style="font-size:14px;color:#2c3e50;margin-bottom:6px">{rec_info['description']}</div>
        <div style="font-size:12px;color:#4a7c6f">💡 {reasoning}</div>
        <div style="margin-top:8px">{stress_pill(level)} &nbsp;<span class="mw-tag mw-tag-blue">Score: {score}/10</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Preset selector
    st.markdown('<div class="mw-section">Choose a Preset</div>', unsafe_allow_html=True)
    preset_names = [f"{PRESETS[k]['emoji']} {PRESETS[k]['name']}" + (" ⭐" if k==rec_key else "") for k in PRESETS]
    preset_keys  = list(PRESETS.keys())
    current_idx  = preset_keys.index(st.session_state.pod_preset) if st.session_state.pod_preset in preset_keys else 0
    chosen_label = st.radio("Preset", preset_names, index=current_idx, horizontal=True, label_visibility="collapsed")
    chosen_idx   = preset_names.index(chosen_label)
    chosen_key   = preset_keys[chosen_idx]
    if chosen_key != st.session_state.pod_preset:
        p = PRESETS[chosen_key]
        st.session_state.pod_preset   = chosen_key
        st.session_state.pod_lighting = p["lighting"]
        st.session_state.pod_music    = p["music"]
        st.session_state.pod_aroma    = p["aroma"]
        st.rerun()

    # Fine-tune
    st.markdown('<div class="mw-section">⚙️ Fine-Tune Settings</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="mw-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            lighting = st.selectbox("💡 Lighting", LIGHTING_OPTIONS, index=LIGHTING_OPTIONS.index(st.session_state.pod_lighting) if st.session_state.pod_lighting in LIGHTING_OPTIONS else 0)
            st.session_state.pod_lighting = lighting
            aroma = st.selectbox("🌸 Aroma", AROMA_OPTIONS, index=AROMA_OPTIONS.index(st.session_state.pod_aroma) if st.session_state.pod_aroma in AROMA_OPTIONS else 0)
            st.session_state.pod_aroma = aroma
        with c2:
            music = st.selectbox("🎵 Music", MUSIC_OPTIONS, index=MUSIC_OPTIONS.index(st.session_state.pod_music) if st.session_state.pod_music in MUSIC_OPTIONS else 0)
            st.session_state.pod_music = music
            meditation = st.selectbox("🧘 Breathing", list(BREATHING_PATTERNS.keys()), index=0)
            st.session_state.pod_meditation = meditation

        intensity = st.slider("🌿 Aroma Intensity", 1, 10, st.session_state.pod_aroma_intensity)
        st.session_state.pod_aroma_intensity = intensity
        duration  = st.select_slider("⏱️ Duration (minutes)", DURATION_OPTIONS, value=st.session_state.pod_duration)
        st.session_state.pod_duration = duration
        st.markdown('</div>', unsafe_allow_html=True)

    # Preview
    light_icons = {"warm":"🔆","cool":"❄️","color_therapy":"🌈"}
    st.markdown(f"""
    <div class="mw-card mw-card-info" style="text-align:center">
        <div style="font-size:13px;color:#7f8c8d;margin-bottom:6px">Session Preview</div>
        <div style="font-size:16px;font-weight:600">
            {light_icons.get(lighting,'💡')} {lighting.replace('_',' ').title()} &nbsp;·&nbsp;
            🎵 {music.title()} &nbsp;·&nbsp;
            🌸 {aroma.title()} &nbsp;·&nbsp;
            ⏱️ {duration} min
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("▶️  Start Session", type="primary", use_container_width=True):
        st.session_state.current_session = {
            "preset_key": chosen_key, "lighting": lighting, "music": music, "aroma": aroma,
            "aroma_intensity": intensity, "meditation": meditation, "duration_minutes": duration,
            "stress_score": st.session_state.stress_score, "stress_level": st.session_state.stress_level,
            "started_at": datetime.now().isoformat(), "post_score": None, "completed": False,
        }
        st.session_state.session_elapsed = 0
        st.session_state.session_started = True
        go("active_session")

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: ACTIVE SESSION
# ══════════════════════════════════════════════════════════════════════════════

def screen_active_session():
    sess = st.session_state.current_session
    if not sess: go("home"); return

    preset = PRESETS.get(sess["preset_key"],{})
    dur    = sess["duration_minutes"]

    # Background colour based on lighting
    bg_colors = {"warm":"#fff5eb","cool":"#ebf3ff","color_therapy":"#f5ebff"}
    accent    = {"warm":"#c4845a","cool":"#5a8ec4","color_therapy":"#7c6fa8"}
    bg  = bg_colors.get(sess["lighting"],"#f0f5ff")
    acc = accent.get(sess["lighting"],"#6c9bcf")

    st.markdown(f"""
    <div style="background:{bg};border-radius:20px;padding:24px;margin-bottom:16px;text-align:center;border:1px solid {acc}22">
        <div style="font-size:11px;color:{acc};text-transform:uppercase;letter-spacing:.08em;font-weight:600;margin-bottom:8px">Session Active</div>
        <div style="font-size:36px;margin-bottom:4px">{preset.get('emoji','🧘')}</div>
        <div style="font-family:'Playfair Display',serif;font-size:24px;color:#2c3e50">{preset.get('name','Wellness Session')}</div>
        <div style="font-size:14px;color:#7f8c8d;margin-top:4px">
            💡 {sess['lighting'].replace('_',' ').title()} &nbsp;·&nbsp;
            🎵 {sess['music'].title()} &nbsp;·&nbsp;
            🌸 {sess['aroma'].title()}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Breathing guide
    pattern = BREATHING_PATTERNS.get(sess["meditation"], BREATHING_PATTERNS["box_breathing"])
    phases  = pattern["phases"]
    total_cycle = sum(p[1] for p in phases)
    elapsed = st.session_state.session_elapsed
    pos_in_cycle = elapsed % total_cycle if total_cycle else 0
    # Find current phase
    cumulative = 0
    current_phase_name = phases[0][0]
    for pname, pdur in phases:
        if pos_in_cycle < cumulative + pdur:
            current_phase_name = pname
            phase_progress = (pos_in_cycle - cumulative) / pdur
            break
        cumulative += pdur
    else:
        phase_progress = 1.0

    # Circle scale for visual feedback
    is_in  = "In" in current_phase_name
    is_out = "Out" in current_phase_name
    scale  = phase_progress if is_in else (1.0 - phase_progress if is_out else 0.8)
    size   = int(120 + scale * 60)

    st.markdown(f"""
    <div style="text-align:center;padding:20px 0">
        <div style="width:{size}px;height:{size}px;border-radius:50%;
            background:radial-gradient(circle,{acc}33,{acc}11);
            border:3px solid {acc}66;margin:0 auto 16px;
            display:flex;align-items:center;justify-content:center;
            transition:all 1s ease;font-size:14px;font-weight:600;color:{acc}">
            {current_phase_name}
        </div>
        <div style="font-size:13px;color:#7f8c8d">{pattern['name']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Timer
    elapsed_display = min(elapsed, dur * 60)
    remaining       = max(0, dur * 60 - elapsed_display)
    progress_frac   = min(1.0, elapsed_display / (dur * 60)) if dur > 0 else 0
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:16px">
        <div style="font-family:'Playfair Display',serif;font-size:48px;color:#2c3e50">
            {remaining//60:02d}:{remaining%60:02d}
        </div>
        <div style="font-size:12px;color:#7f8c8d">remaining of {dur} min</div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(progress_frac)

    # Auto-advance timer every rerun
    if st.session_state.session_started and elapsed < dur * 60:
        st.session_state.session_elapsed += 5  # advance 5s per interaction
        time.sleep(0.1)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏸ Pause / Resume", use_container_width=True):
            st.session_state.session_started = not st.session_state.session_started
    with col2:
        if st.button("⏹ End Session", use_container_width=True, type="primary"):
            go("journal")

    if elapsed >= dur * 60:
        st.success("✅ Session complete! Time to log how you feel.")
        if st.button("Go to Journal →", type="primary"):
            go("journal")
    else:
        if st.button("🔄 Tick timer (simulate time passing)", use_container_width=True):
            st.session_state.session_elapsed = min(dur * 60, st.session_state.session_elapsed + 60)
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: BREATHE WITH ME
# ══════════════════════════════════════════════════════════════════════════════

def screen_breathe():
    c1, c2 = st.columns([1,5])
    with c1:
        if st.button("← Back"): go("home")
    with c2:
        st.markdown('<div class="mw-heading">🫁 Breathe with Me</div>', unsafe_allow_html=True)
        st.markdown('<div class="mw-sub">Micro-meditation for instant stress relief</div>', unsafe_allow_html=True)

    technique = st.radio("Technique", ["4-7-8 Breathing", "Box Breathing"], horizontal=True)
    if technique == "4-7-8 Breathing":
        phases = [("Breathe In", 4, "🫁"), ("Hold", 7, "🤐"), ("Breathe Out", 8, "💨")]
        desc   = "Inhale for 4, hold for 7, exhale for 8. Quickly reduces anxiety."
    else:
        phases = [("Breathe In", 4, "🫁"), ("Hold", 4, "🤐"), ("Breathe Out", 4, "💨"), ("Hold", 4, "🤐")]
        desc   = "Equal counts for each phase. Great for focus and calm."

    st.markdown(f'<div class="mw-card mw-card-sage"><div style="font-size:14px;color:#2c3e50">{desc}</div></div>', unsafe_allow_html=True)

    round_num = st.session_state.breathe_round
    tick      = st.session_state.breathe_tick
    phase_idx = st.session_state.breathe_phase_idx % len(phases)
    p_name, p_dur, p_icon = phases[phase_idx]
    remaining_in_phase = max(0, p_dur - tick)

    # Scale based on phase
    scale = (tick / p_dur) if p_name == "Breathe In" else (1 - tick / p_dur) if p_name == "Breathe Out" else 0.7
    size  = int(120 + scale * 80)

    st.markdown(f"""
    <div style="text-align:center;padding:24px 0">
        <div style="width:{size}px;height:{size}px;border-radius:50%;
            background:radial-gradient(circle,#e8f5f0,rgba(232,242,239,0.2));
            border:3px solid #b8e0d2;margin:0 auto 16px;
            display:flex;flex-direction:column;align-items:center;justify-content:center;
            transition:all .8s ease">
            <div style="font-size:32px">{p_icon}</div>
            <div style="font-size:20px;font-weight:600;color:#4a7c6f">{remaining_in_phase}s</div>
        </div>
        <div style="font-family:'Playfair Display',serif;font-size:22px;color:#4a7c6f;margin-bottom:4px">{p_name}</div>
        <div style="font-size:13px;color:#7f8c8d">Round {round_num+1} of 4</div>
    </div>
    """, unsafe_allow_html=True)

    # Round dots
    dots = "".join(f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{"#4a7c6f" if i<=round_num else "#e0e0e0"};margin:0 3px"></span>' for i in range(4))
    st.markdown(f'<div style="text-align:center;margin-bottom:16px">{dots}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ Next step", type="primary", use_container_width=True):
            new_tick = tick + 1
            if new_tick >= p_dur:
                new_phase = st.session_state.breathe_phase_idx + 1
                new_tick  = 0
                if new_phase % len(phases) == 0:
                    st.session_state.breathe_round = min(3, round_num + 1)
                st.session_state.breathe_phase_idx = new_phase
            st.session_state.breathe_tick = new_tick
            st.rerun()
    with col2:
        if st.button("↺ Reset", use_container_width=True):
            st.session_state.breathe_phase_idx = 0
            st.session_state.breathe_tick = 0; st.session_state.breathe_round = 0; st.rerun()

    if round_num >= 3 and tick == 0 and phase_idx == 0:
        st.success("🎉 Session complete! You did 4 full rounds. Feeling calmer?")

    if st.button("📝 Log how you feel →", use_container_width=True): go("journal")

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: POD SCHEDULER
# ══════════════════════════════════════════════════════════════════════════════

def screen_schedule():
    c1, c2 = st.columns([1,5])
    with c1:
        if st.button("← Back"): go("home")
    with c2:
        st.markdown('<div class="mw-heading">📅 Pod Scheduler</div>', unsafe_allow_html=True)
        st.markdown('<div class="mw-sub">Book your stress relief pod session</div>', unsafe_allow_html=True)

    st.markdown('<div class="mw-card mw-card-info"><div style="font-size:14px;color:#2c3e50">Book a pod session in advance to guarantee availability. Booked slots are reserved for you.</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="mw-section">📍 Pod A — Floor 3, FutureForward HQ</div>', unsafe_allow_html=True)

    all_slots  = ["9:00","9:30","10:00","10:30","11:00","11:30","2:00 PM","2:30 PM","3:00 PM","3:30 PM"]
    booked     = ["9:00","9:30","11:00"]
    free_slots = [s for s in all_slots if s not in booked]

    st.markdown("**Available slots today:**")
    cols = st.columns(5)
    for i, slot in enumerate(free_slots):
        with cols[i % 5]:
            is_sel = st.session_state.selected_slot == slot
            label  = f"✅ {slot}" if is_sel else slot
            if st.button(label, key=f"slot_{slot}", use_container_width=True):
                st.session_state.selected_slot = slot; st.rerun()

    st.markdown("*🔴 Booked: " + ", ".join(booked) + "*")

    st.markdown('<div class="mw-section">⏱️ Session Duration</div>', unsafe_allow_html=True)
    dur_cols = st.columns(3)
    dur_opts  = [("15 min","Quick"),("30 min","Standard"),("45 min","Deep")]
    for i, (lbl, sub) in enumerate(dur_opts):
        with dur_cols[i]:
            mins = int(lbl.split()[0])
            is_s = st.session_state.selected_dur == mins
            if st.button(f"{'✅ ' if is_s else ''}{lbl}\n{sub}", key=f"dur_{mins}", use_container_width=True):
                st.session_state.selected_dur = mins; st.rerun()

    if st.session_state.selected_slot:
        st.markdown(f"""
        <div class="mw-card mw-card-sage">
            <div style="font-weight:600;font-size:16px">📋 Your Booking</div>
            <div style="font-size:15px;margin-top:6px">Today at {st.session_state.selected_slot} · {st.session_state.selected_dur} min</div>
            <div style="font-size:13px;color:#7f8c8d">Pod A · Floor 3 · FutureForward HQ</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("✅ Confirm Booking", type="primary", use_container_width=True):
            st.success(f"🎉 Pod booked for {st.session_state.selected_slot} ({st.session_state.selected_dur} min)! A reminder will be sent 5 minutes before.")
            st.session_state.selected_slot = None
    else:
        st.info("👆 Select a time slot above to continue")

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: POST-SESSION JOURNAL
# ══════════════════════════════════════════════════════════════════════════════

def screen_journal():
    c1, c2 = st.columns([1,5])
    with c1:
        if st.button("← Back"): go("home")
    with c2:
        st.markdown('<div class="mw-heading">📝 Post-Session Journal</div>', unsafe_allow_html=True)
        st.markdown('<div class="mw-sub">Track your stress reduction and reflect</div>', unsafe_allow_html=True)

    st.markdown('<div class="mw-card">', unsafe_allow_html=True)
    before = st.slider("Stress BEFORE session", 0, 100, int(st.session_state.journal_before * 10), format="%d%%")
    after  = st.slider("Stress AFTER session",  0, 100, int(st.session_state.journal_after  * 10), format="%d%%")
    st.session_state.journal_before = before / 10
    st.session_state.journal_after  = after  / 10

    diff = before - after
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Before", f"{before}%")
    with col2: st.metric("After",  f"{after}%", delta=f"-{diff}%" if diff > 0 else f"+{abs(diff)}%", delta_color="inverse")
    with col3: st.metric("Reduction", f"{diff}%", delta="✅ Great!" if diff > 20 else ("👍 Good" if diff > 0 else "😐 Same"))
    st.markdown('</div>', unsafe_allow_html=True)

    # Rating
    st.markdown('<div class="mw-section">⭐ Session Rating</div>', unsafe_allow_html=True)
    stars = st.select_slider("How was your session?", options=[1,2,3,4,5],
                              value=st.session_state.journal_stars,
                              format_func=lambda x: "⭐"*x)
    st.session_state.journal_stars = stars
    rating_labels = {1:"Poor",2:"Fair",3:"Good",4:"Very relaxing",5:"Perfect!"}
    st.markdown(f'<div style="text-align:center;font-size:13px;color:#7f8c8d">{rating_labels[stars]}</div>', unsafe_allow_html=True)

    # Mood tag
    st.markdown('<div class="mw-section">😊 Mood After</div>', unsafe_allow_html=True)
    mood_opts = ["😌 Calm", "🎯 Focused", "⚡ Energised", "😴 Sleepy", "😊 Happy"]
    mood = st.radio("Mood", mood_opts, index=mood_opts.index(st.session_state.journal_mood) if st.session_state.journal_mood in mood_opts else 0, horizontal=True, label_visibility="collapsed")
    st.session_state.journal_mood = mood

    # Reflection
    st.markdown('<div class="mw-section">✍️ Reflection</div>', unsafe_allow_html=True)
    reflection = st.text_area("How do you feel? What worked well? What would you change?",
                              value=st.session_state.journal_text, height=120,
                              placeholder="The lo-fi music and lavender aroma really helped me reset...")
    st.session_state.journal_text = reflection

    if st.button("💾 Save Journal Entry", type="primary", use_container_width=True):
        u = current_user()
        if u and st.session_state.current_session:
            sess = st.session_state.current_session
            sess["post_score"] = after / 10
            sess["completed"]  = True
            record = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "stress_score": sess.get("stress_score", before/10),
                "post_score":   after / 10,
                "preset":       sess.get("preset_key",""),
                "duration_minutes": sess.get("duration_minutes",10),
                "stars":        stars,
                "mood":         mood,
                "reflection":   reflection,
            }
            u.setdefault("history",[]).append(record)
            u["total_sessions"] = u.get("total_sessions",0) + 1
            u["total_minutes"]  = u.get("total_minutes",0)  + sess.get("duration_minutes",10)
            update_weights(u, sess.get("preset_key",""), sess.get("stress_score",5), after/10)
            save_user(u)
            st.session_state.current_session = None
        st.success("✅ Journal entry saved!")
        st.balloons()
        if st.button("📊 View Progress →"): go("progress")

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: PROGRESS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def screen_progress():
    c1, c2 = st.columns([1,5])
    with c1:
        if st.button("← Back"): go("home")
    with c2:
        st.markdown('<div class="mw-heading">📊 Stress Progress</div>', unsafe_allow_html=True)

    u = current_user()
    stats = get_stats()

    # Stat row
    cols = st.columns(4)
    for col, (e, lbl, val, color) in zip(cols, [
        ("🧘","Sessions",str(stats["total_sessions"]),"#6c9bcf"),
        ("⏱️","Minutes",str(stats["total_minutes"]),"#4a7c6f"),
        ("🔥","Streak",f"{stats['streak']}d","#e67e22"),
        ("📈","Avg Relief",f"{stats['avg_improvement']:+.1f}","#27ae60"),
    ]):
        with col:
            st.markdown(f'<div class="mw-stat"><div class="mw-stat-num" style="color:{color}">{val}</div><div class="mw-stat-lbl">{e} {lbl}</div></div>', unsafe_allow_html=True)

    history = (u or {}).get("history",[])

    if not history:
        st.markdown('<div class="mw-card" style="text-align:center;padding:40px"><div style="font-size:48px">🌱</div><div style="font-size:16px;color:#7f8c8d;margin-top:12px">No sessions yet!<br>Start your first stress check to begin tracking.</div></div>', unsafe_allow_html=True)
    else:
        # Stress trend chart
        st.markdown('<div class="mw-section">📈 Stress Trend</div>', unsafe_allow_html=True)
        x_labels = [s.get("date","") for s in history]
        pre_vals  = [s.get("stress_score",5) for s in history]
        post_vals = [s.get("post_score",5) for s in history]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_labels, y=pre_vals, name="Before session",
                                  line=dict(color="#e74c3c",width=2.5), mode="lines+markers",
                                  marker=dict(size=8,color="#e74c3c")))
        fig.add_trace(go.Scatter(x=x_labels, y=post_vals, name="After session",
                                  line=dict(color="#27ae60",width=2.5), mode="lines+markers",
                                  marker=dict(size=8,color="#27ae60")))
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10,r=10,t=10,b=10), height=250,
            legend=dict(orientation="h",y=1.1), yaxis=dict(range=[0,11],title="Stress Score"),
            xaxis=dict(title="Session Date"), font=dict(family="DM Sans",size=12),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Feature effectiveness
        st.markdown('<div class="mw-section">🎯 Feature Effectiveness</div>', unsafe_allow_html=True)
        st.markdown('<div class="mw-card">', unsafe_allow_html=True)
        preset_deltas = {}
        for s in history:
            k = s.get("preset","")
            preset_deltas.setdefault(k,[]).append(s.get("stress_score",5)-s.get("post_score",5))
        for key, deltas in preset_deltas.items():
            name = PRESETS.get(key,{}).get("name",key)
            avg  = sum(deltas)/len(deltas)
            pct  = min(100, int(avg * 12))
            st.markdown(f"""
            <div style="margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                    <span style="font-size:13px;font-weight:500">{PRESETS.get(key,{}).get('emoji','🧘')} {name}</span>
                    <span style="font-size:12px;color:#4a7c6f">{avg:.1f} pts avg · {len(deltas)} sessions</span>
                </div>
                <div class="mw-prog-wrap"><div class="mw-prog-bar" style="width:{pct}%"></div></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Badges
        st.markdown('<div class="mw-section">🏅 Badges</div>', unsafe_allow_html=True)
        total = stats["total_sessions"]
        streak = stats["streak"]
        badge_cols = st.columns(5)
        badges = [
            ("🌱","First session", total>=1),
            ("🔥","5-day streak",   streak>=5),
            ("🧘","Zen master",     total>=7),
            ("⭐","10 sessions",    total>=10),
            ("💎","Elite calm",     total>=20),
        ]
        for col, (icon, name, earned) in zip(badge_cols, badges):
            with col:
                st.markdown(f'<div style="text-align:center;opacity:{1 if earned else 0.3}"><div style="font-size:28px">{icon}</div><div style="font-size:10px;color:#7f8c8d;margin-top:4px">{name}</div></div>', unsafe_allow_html=True)

    # AI insight
    st.markdown('<div class="mw-section">💡 AI Insight</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mw-card mw-card-sage"><span class="ai-dot"></span>{get_ai_insight()}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧠 New Stress Check", type="primary", use_container_width=True): go("stress_check")
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            if u:
                u["history"] = []; u["total_sessions"] = 0; u["total_minutes"] = 0; u["streak"] = 0
                save_user(u); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════

SCREENS = {
    "login":          screen_login,
    "home":           screen_home,
    "stress_check":   screen_stress_check,
    "pod_setup":      screen_pod_setup,
    "active_session": screen_active_session,
    "breathe":        screen_breathe,
    "schedule":       screen_schedule,
    "journal":        screen_journal,
    "progress":       screen_progress,
}

screen_fn = SCREENS.get(st.session_state.screen, screen_login)
screen_fn()
