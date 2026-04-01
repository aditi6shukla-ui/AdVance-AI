import streamlit as st
import hashlib
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import anthropic
import base64

st.set_page_config(page_title="MarketOS", page_icon="📡", layout="wide", initial_sidebar_state="expanded")

if "_MKT_USERS" not in st.__dict__: st._MKT_USERS = {}
if "_MKT_DATA"  not in st.__dict__: st._MKT_DATA  = {}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
:root{--amber:#F59E0B;--amber2:#FCD34D;--blue:#06B6D4;--blue2:#67E8F9;--red:#EF4444;--green:#10B981;--bg:#080C10;--bg2:#0F1419;--bg3:#161D26;--border:#1E2A38;--border2:#253444;--text:#E2E8F0;--muted:#64748B;--shadow:4px 4px 0 #000;--r:6px;}
.stApp{background:var(--bg)!important;font-family:'IBM Plex Sans',sans-serif;color:var(--text);}
.block-container{padding:1.2rem 2rem!important;max-width:1200px;}
#MainMenu,footer,header{visibility:hidden;}.stDeployButton{display:none;}
[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] .block-container{padding:0.8rem!important;}
h1,h2,h3{font-family:'Syne',sans-serif!important;}
.stButton>button{background:var(--amber)!important;color:#000!important;font-family:'Syne',sans-serif!important;font-weight:700!important;font-size:0.85rem!important;border:2px solid #000!important;border-radius:var(--r)!important;box-shadow:var(--shadow)!important;padding:0.55rem 1.3rem!important;transition:all 0.08s ease!important;text-transform:uppercase;}
.stButton>button:hover{transform:translate(-2px,-2px)!important;box-shadow:6px 6px 0 #000!important;}
.stButton>button:active{transform:translate(2px,2px)!important;box-shadow:2px 2px 0 #000!important;}
.stButton>button:disabled{background:#1E2A38!important;color:#4A5568!important;box-shadow:none!important;}
.stTextInput>div>div>input,.stTextArea textarea,.stSelectbox>div>div,.stNumberInput>div>div>input{background:var(--bg3)!important;border:1px solid var(--border2)!important;color:var(--text)!important;border-radius:var(--r)!important;font-family:'IBM Plex Sans',sans-serif!important;}
.stTextInput>div>div>input:focus,.stTextArea textarea:focus{border-color:var(--amber)!important;box-shadow:0 0 0 2px rgba(245,158,11,0.2)!important;}
.stTextInput>label,.stTextArea>label,.stSelectbox>label,.stNumberInput>label,.stSlider>label,.stRadio>label{color:var(--muted)!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.75rem!important;text-transform:uppercase;letter-spacing:0.08em;}
.stRadio [data-testid="stMarkdownContainer"] p{color:var(--text)!important;}
.stSlider>div>div>div>div{background:var(--amber)!important;}
.stTabs [data-baseweb="tab-list"]{background:transparent;gap:0.4rem;border-bottom:1px solid var(--border);}
.stTabs [data-baseweb="tab"]{background:transparent!important;border:none!important;color:var(--muted)!important;font-family:'Syne',sans-serif!important;font-size:0.82rem!important;font-weight:600;padding:0.6rem 1rem!important;border-bottom:2px solid transparent!important;}
.stTabs [aria-selected="true"]{color:var(--amber)!important;border-bottom:2px solid var(--amber)!important;}
.stTabs [data-baseweb="tab-panel"]{background:transparent!important;padding:1.2rem 0!important;}
.stProgress>div>div{background:var(--amber)!important;}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:var(--r);padding:1.2rem;margin-bottom:0.8rem;}
.card-amber{background:var(--bg2);border:1px solid var(--amber);border-radius:var(--r);padding:1.2rem;box-shadow:0 0 20px rgba(245,158,11,0.1);margin-bottom:0.8rem;}
.card-blue{background:var(--bg2);border:1px solid var(--blue);border-radius:var(--r);padding:1.2rem;box-shadow:0 0 20px rgba(6,182,212,0.1);margin-bottom:0.8rem;}
.metric-pill{display:inline-block;padding:0.2rem 0.8rem;border-radius:999px;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;font-weight:600;border:1px solid;}
.pill-amber{background:rgba(245,158,11,0.12);color:var(--amber);border-color:var(--amber);}
.pill-blue{background:rgba(6,182,212,0.12);color:var(--blue2);border-color:var(--blue);}
.pill-green{background:rgba(16,185,129,0.12);color:#34D399;border-color:var(--green);}
.pill-red{background:rgba(239,68,68,0.12);color:#FCA5A5;border-color:var(--red);}
.div{border:none;border-top:1px solid var(--border);margin:1.2rem 0;}
.section-heading{font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:var(--text);margin-bottom:0.2rem;}
.section-sub{color:var(--muted);font-size:0.82rem;margin-bottom:1.2rem;}
.ai-output{background:var(--bg3);border:1px solid var(--blue);border-radius:var(--r);padding:1.2rem;font-family:'IBM Plex Sans',sans-serif;font-size:0.88rem;line-height:1.7;color:var(--text);box-shadow:0 0 25px rgba(6,182,212,0.08);}
.budget-row{display:flex;align-items:center;gap:0.8rem;margin:0.4rem 0;}
.budget-label{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:var(--muted);width:140px;}
.budget-bar-wrap{flex:1;background:var(--border);border-radius:3px;height:8px;overflow:hidden;}
.budget-bar-fill{height:100%;border-radius:3px;}
.budget-amount{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:var(--text);width:80px;text-align:right;}
.info-strip{background:rgba(6,182,212,0.08);border-left:3px solid var(--blue);border-radius:0 var(--r) var(--r) 0;padding:0.7rem 1rem;font-size:0.84rem;color:var(--blue2);margin:0.8rem 0;}
.warn-strip{background:rgba(245,158,11,0.08);border-left:3px solid var(--amber);border-radius:0 var(--r) var(--r) 0;padding:0.7rem 1rem;font-size:0.84rem;color:var(--amber2);margin:0.8rem 0;}
.success-strip{background:rgba(16,185,129,0.08);border-left:3px solid var(--green);border-radius:0 var(--r) var(--r) 0;padding:0.7rem 1rem;font-size:0.84rem;color:#6EE7B7;margin:0.8rem 0;}
.error-strip{background:rgba(239,68,68,0.08);border-left:3px solid var(--red);border-radius:0 var(--r) var(--r) 0;padding:0.7rem 1rem;font-size:0.84rem;color:#FCA5A5;margin:0.8rem 0;}
code,pre{font-family:'IBM Plex Mono',monospace!important;background:var(--bg3)!important;border:1px solid var(--border2)!important;}
</style>
"""

def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()
def check_pw(p,h): return hash_pw(p)==h

def empty_data():
    return {"brand_profile":{},"campaigns":[],"saved_calendars":[],"saved_analyses":[],"api_key":""}

def load_user(u):
    d=st._MKT_DATA.get(u,empty_data())
    st.session_state.brand_profile=d["brand_profile"]
    st.session_state.campaigns=d["campaigns"]
    st.session_state.saved_calendars=d["saved_calendars"]
    st.session_state.saved_analyses=d["saved_analyses"]
    st.session_state.api_key=d.get("api_key","")

def save_user(u):
    st._MKT_DATA[u]={"brand_profile":st.session_state.brand_profile,"campaigns":st.session_state.campaigns,
        "saved_calendars":st.session_state.saved_calendars,"saved_analyses":st.session_state.saved_analyses,
        "api_key":st.session_state.api_key}

def init():
    for k,v in {"logged_in":False,"username":"","auth_tab":"login","auth_error":"","auth_ok":"",
                "page":"dashboard","brand_profile":{},"campaigns":[],"saved_calendars":[],
                "saved_analyses":[],"api_key":""}.items():
        if k not in st.session_state: st.session_state[k]=v

def do_register(u,p,c):
    u=u.strip().lower()
    if not u or not p: st.session_state.auth_error="Fields cannot be empty.";return
    if len(u)<3: st.session_state.auth_error="Username must be ≥ 3 chars.";return
    if len(p)<6: st.session_state.auth_error="Password must be ≥ 6 chars.";return
    if p!=c: st.session_state.auth_error="Passwords don't match.";return
    if u in st._MKT_USERS: st.session_state.auth_error="Username taken.";return
    st._MKT_USERS[u]={"pw_hash":hash_pw(p)}
    st._MKT_DATA[u]=empty_data()
    st.session_state.auth_error=""
    st.session_state.auth_ok=f"Account created! Welcome, {u} — now log in."
    st.session_state.auth_tab="login"

def do_login(u,p):
    u=u.strip().lower()
    if u not in st._MKT_USERS: st.session_state.auth_error="Username not found.";return
    if not check_pw(p,st._MKT_USERS[u]["pw_hash"]): st.session_state.auth_error="Wrong password.";return
    st.session_state.auth_error=""
    st.session_state.logged_in=True
    st.session_state.username=u
    load_user(u)
    st.session_state.page="dashboard"

def get_ai_client():
    key=st.session_state.api_key.strip()
    if not key: return None
    try: return anthropic.Anthropic(api_key=key)
    except: return None

def ai_call(system_prompt,user_prompt,max_tokens=1500):
    client=get_ai_client()
    if not client: return None,"❌ No API key set. Go to ⚙️ Settings and add your Anthropic API key."
    try:
        msg=client.messages.create(model="claude-opus-4-5",max_tokens=max_tokens,
            system=system_prompt,messages=[{"role":"user","content":user_prompt}])
        return msg.content[0].text,None
    except anthropic.AuthenticationError: return None,"❌ Invalid API key. Check your key in ⚙️ Settings."
    except anthropic.RateLimitError: return None,"⚠️ Rate limit hit. Wait a moment and try again."
    except Exception as e: return None,f"❌ Error: {str(e)}"

def brand_summary():
    bp=st.session_state.brand_profile
    if not bp: return "No brand profile set up yet."
    return (f"Business: {bp.get('name','?')} | Type: {bp.get('type','?')} | "
            f"Location: {bp.get('location','?')} | Audience: {bp.get('audience','?')} | "
            f"USP: {bp.get('usp','?')} | Platforms: {bp.get('platforms','?')} | Tone: {bp.get('tone','?')}")

# ── AUTH ──
def render_auth():
    st.markdown('<div style="text-align:center;padding:2rem 0 1rem;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#F59E0B;letter-spacing:0.35em;margin-bottom:0.6rem;">📡 MARKETOS</div><div style="font-family:Syne,sans-serif;font-size:2rem;font-weight:800;color:#E2E8F0;">Marketing Command Centre</div><div style="color:#64748B;font-size:0.85rem;margin-top:0.4rem;">Built for Indian businesses. Powered by AI.</div></div>',unsafe_allow_html=True)
    st.markdown('<div style="display:flex;justify-content:center;gap:0.5rem;flex-wrap:wrap;margin:1rem 0 1.5rem;"><span class="metric-pill pill-amber">🔍 Competitor Spy</span><span class="metric-pill pill-blue">📅 Content Calendar</span><span class="metric-pill pill-green">💰 Budget Allocator</span><span class="metric-pill pill-red">📊 Campaign Tracker</span></div>',unsafe_allow_html=True)
    st.markdown("<hr class='div'/>",unsafe_allow_html=True)
    cl,cr=st.columns(2)
    with cl:
        if st.button("🔓  Log In",use_container_width=True,key="tab_li"):
            st.session_state.auth_tab="login";st.session_state.auth_error="";st.rerun()
    with cr:
        if st.button("✨  Register",use_container_width=True,key="tab_reg"):
            st.session_state.auth_tab="register";st.session_state.auth_error="";st.rerun()
    active=st.session_state.auth_tab
    st.markdown(f'<div style="display:flex;margin-bottom:1.5rem;"><div style="flex:1;height:2px;background:{"#F59E0B" if active=="login" else "#1E2A38"};border-radius:2px 0 0 2px;"></div><div style="flex:1;height:2px;background:{"#F59E0B" if active=="register" else "#1E2A38"};border-radius:0 2px 2px 0;"></div></div>',unsafe_allow_html=True)
    if st.session_state.auth_error: st.markdown(f'<div class="error-strip">⚠️ {st.session_state.auth_error}</div>',unsafe_allow_html=True)
    if st.session_state.auth_ok:    st.markdown(f'<div class="success-strip">✅ {st.session_state.auth_ok}</div>',unsafe_allow_html=True)
    if active=="login":
        u=st.text_input("Username",placeholder="your_username",key="li_u")
        p=st.text_input("Password",type="password",placeholder="••••••••",key="li_p")
        st.markdown("")
        if st.button("⚡  Log In & Enter",use_container_width=True,key="li_btn"): do_login(u,p);st.rerun()
    else:
        u=st.text_input("Choose a Username",placeholder="coolmarketer (min 3 chars)",key="reg_u")
        p=st.text_input("Choose a Password",type="password",placeholder="Min. 6 characters",key="reg_p")
        c=st.text_input("Confirm Password",type="password",placeholder="Repeat password",key="reg_c")
        st.markdown("")
        if st.button("🚀  Create Account",use_container_width=True,key="reg_btn"): do_register(u,p,c);st.rerun()
    st.markdown('<div style="text-align:center;margin-top:2rem;padding:0.8rem;background:#0F1419;border:1px dashed #1E2A38;border-radius:6px;font-size:0.75rem;color:#4A5568;">💾 All your data — campaigns, calendars, analyses — auto-saves to your account.</div>',unsafe_allow_html=True)

# ── SIDEBAR ──
PAGES=[("dashboard","🏠","Dashboard"),("brand","🏢","Brand Profile"),("competitor","🔍","Competitor Spy"),
       ("calendar","📅","Content Calendar"),("budget","💰","Budget Allocator"),
       ("tracker","📊","Campaign Tracker"),("settings","⚙️","Settings")]

def render_sidebar():
    bp=st.session_state.brand_profile
    name=bp.get("name",st.session_state.username)
    camps=st.session_state.campaigns
    total_spend=sum(c.get("spend",0) for c in camps)
    with st.sidebar:
        st.markdown(f'<div style="padding:0.8rem 0.4rem 0.6rem;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.55rem;color:#F59E0B;letter-spacing:0.3em;">📡 MARKETOS</div><div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#E2E8F0;margin-top:0.1rem;">{name}</div><div style="font-size:0.72rem;color:#4A5568;">@{st.session_state.username}</div></div>',unsafe_allow_html=True)
        st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;margin-bottom:0.8rem;"><div style="background:#0F1419;border:1px solid #1E2A38;border-radius:6px;padding:0.5rem;text-align:center;"><div style="font-family:IBM Plex Mono,monospace;font-size:1rem;color:#F59E0B;">{len(camps)}</div><div style="font-size:0.65rem;color:#4A5568;">Campaigns</div></div><div style="background:#0F1419;border:1px solid #1E2A38;border-radius:6px;padding:0.5rem;text-align:center;"><div style="font-family:IBM Plex Mono,monospace;font-size:1rem;color:#06B6D4;">₹{total_spend:,}</div><div style="font-size:0.65rem;color:#4A5568;">Total Spend</div></div></div>',unsafe_allow_html=True)
        st.markdown("<hr class='div' style='margin:0.5rem 0;'/>",unsafe_allow_html=True)
        cur=st.session_state.page
        for pid,icon,label in PAGES:
            if st.button(f"{icon}  {label}",key=f"nav_{pid}",use_container_width=True):
                st.session_state.page=pid;st.rerun()
        st.markdown("<hr class='div' style='margin:0.5rem 0;'/>",unsafe_allow_html=True)
        if st.button("🚪  Log Out",use_container_width=True):
            save_user(st.session_state.username)
            for k in ["logged_in","username","brand_profile","campaigns","saved_calendars","saved_analyses","api_key","page"]:
                st.session_state.pop(k,None)
            st.rerun()

# ── DASHBOARD ──
def page_dashboard():
    bp=st.session_state.brand_profile;camps=st.session_state.campaigns
    name=bp.get("name",st.session_state.username)
    st.markdown(f'<div style="margin-bottom:1.5rem;"><div style="font-family:Syne,sans-serif;font-size:1.7rem;font-weight:800;color:#E2E8F0;">Good day, {name} 👋</div><div style="color:#64748B;font-size:0.85rem;">{datetime.now().strftime("%A, %d %B %Y")} — Your marketing command centre is ready.</div></div>',unsafe_allow_html=True)
    total_spend=sum(c.get("spend",0) for c in camps)
    total_rev=sum(c.get("revenue",0) for c in camps)
    total_leads=sum(c.get("leads",0) for c in camps)
    avg_roas=round(total_rev/total_spend,2) if total_spend else 0
    c1,c2,c3,c4=st.columns(4)
    for col,val,lbl in[(c1,len(camps),"Total Campaigns"),(c2,f"₹{total_spend:,}","Total Ad Spend"),(c3,total_leads,"Total Leads"),(c4,f"{avg_roas}x","Avg. ROAS")]:
        with col:
            st.markdown(f'<div class="card" style="text-align:center;padding:1rem;"><div style="font-family:IBM Plex Mono,monospace;font-size:1.5rem;color:#E2E8F0;">{val}</div><div style="font-size:0.75rem;color:#64748B;">{lbl}</div></div>',unsafe_allow_html=True)
    st.markdown("<hr class='div'/>",unsafe_allow_html=True)
    left,right=st.columns([3,2])
    with left:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;margin-bottom:0.5rem;">📊 Campaign Performance</div>',unsafe_allow_html=True)
        if camps:
            df=pd.DataFrame(camps)
            fig=go.Figure()
            fig.add_trace(go.Bar(name="Spend (₹)",x=df["name"],y=df["spend"],marker_color="#F59E0B",opacity=0.9))
            if "revenue" in df.columns: fig.add_trace(go.Bar(name="Revenue (₹)",x=df["name"],y=df["revenue"],marker_color="#06B6D4",opacity=0.9))
            fig.update_layout(barmode="group",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#94A3B8",legend=dict(bgcolor="rgba(0,0,0,0)"),margin=dict(l=0,r=0,t=10,b=0),height=260,xaxis=dict(gridcolor="#1E2A38"),yaxis=dict(gridcolor="#1E2A38"))
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.markdown('<div class="warn-strip">No campaigns yet. Go to 📊 Campaign Tracker to add your first.</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;margin-bottom:0.5rem;">🗂️ Quick Access</div>',unsafe_allow_html=True)
        if not bp: st.markdown('<div class="warn-strip">⚠️ Set up your Brand Profile first!</div>',unsafe_allow_html=True)
        for pid,icon,label,desc in[("competitor","🔍","Competitor Spy","Analyse any competitor's strategy"),("calendar","📅","Content Calendar","Generate 30 days of post ideas"),("budget","💰","Budget Allocator","Split your ad budget smartly"),("tracker","📊","Campaign Tracker","Log & track your campaigns")]:
            st.markdown(f'<div class="card" style="padding:0.7rem;margin-bottom:0.3rem;"><div style="font-weight:600;font-size:0.85rem;">{icon} {label}</div><div style="color:#64748B;font-size:0.75rem;">{desc}</div></div>',unsafe_allow_html=True)
            if st.button(f"Open {label} →",key=f"dash_{pid}",use_container_width=True): st.session_state.page=pid;st.rerun()

# ── BRAND ──
def page_brand():
    st.markdown('<div class="section-heading">🏢 Brand Profile</div><div class="section-sub">Fill this in once — all AI tools use it to personalise results for your business.</div>',unsafe_allow_html=True)
    bp=st.session_state.brand_profile
    BIZ_TYPES=["Retail / E-commerce","Food & Beverage","Fashion & Apparel","Health & Wellness","Beauty & Skincare","Education / Coaching","Real Estate","Tech / SaaS","Finance / Insurance","Travel & Tourism","Fitness / Gym","Other"]
    BUDGETS=["Under ₹5,000","₹5,000 – ₹15,000","₹15,000 – ₹50,000","₹50,000 – ₹1,50,000","₹1,50,000+"]
    TONES=["Friendly & Warm","Professional & Trustworthy","Fun & Playful","Luxury & Premium","Bold & Energetic","Informative & Educational"]
    def idx(lst,val,default=0): return lst.index(val) if val in lst else default
    with st.form("brand_form"):
        c1,c2=st.columns(2)
        with c1:
            name=st.text_input("Business Name",value=bp.get("name",""),placeholder="e.g. Meera's Bakehouse")
            btype=st.selectbox("Business Type",BIZ_TYPES,index=idx(BIZ_TYPES,bp.get("type","")))
            location=st.text_input("City / Location",value=bp.get("location",""),placeholder="e.g. Mumbai")
            budget=st.selectbox("Monthly Marketing Budget",BUDGETS,index=idx(BUDGETS,bp.get("budget","")))
        with c2:
            audience=st.text_input("Target Audience",value=bp.get("audience",""),placeholder="e.g. Women aged 25–40 in Mumbai")
            usp=st.text_input("Your USP",value=bp.get("usp",""),placeholder="e.g. Handmade, no preservatives")
            platforms=st.multiselect("Active Platforms",["Instagram","Facebook","WhatsApp","YouTube","LinkedIn","Twitter/X","Zomato/Swiggy","Google Ads"],default=bp.get("platforms",[]) or ["Instagram","WhatsApp"])
            tone=st.selectbox("Brand Tone",TONES,index=idx(TONES,bp.get("tone","")))
        about=st.text_area("About Your Business",value=bp.get("about",""),placeholder="What you sell, who you serve, why customers love you.",height=80)
        if st.form_submit_button("💾  Save Brand Profile",use_container_width=True):
            st.session_state.brand_profile={"name":name,"type":btype,"location":location,"budget":budget,"audience":audience,"usp":usp,"platforms":platforms,"tone":tone,"about":about}
            save_user(st.session_state.username)
            st.markdown('<div class="success-strip">✅ Brand profile saved! All AI tools are now personalised.</div>',unsafe_allow_html=True)
    if bp:
        st.markdown("<hr class='div'/>",unsafe_allow_html=True)
        st.markdown(f'<div class="card-amber" style="font-size:0.85rem;line-height:1.9;"><strong style="color:#F59E0B;">{bp.get("name","")}</strong> — {bp.get("type","")} in {bp.get("location","")}<br/>🎯 Audience: {bp.get("audience","")}<br/>💡 USP: {bp.get("usp","")}<br/>📣 Platforms: {", ".join(bp.get("platforms",[]))}<br/>💬 Tone: {bp.get("tone","")}<br/>💰 Budget: {bp.get("budget","")}</div>',unsafe_allow_html=True)

# ── COMPETITOR SPY ──
def page_competitor():
    st.markdown('<div class="section-heading">🔍 Competitor Spy</div><div class="section-sub">Enter a competitor\'s name — get a deep strategic analysis and exactly how to beat them.</div>',unsafe_allow_html=True)
    if not st.session_state.api_key: st.markdown('<div class="warn-strip">⚠️ Add your Anthropic API key in ⚙️ Settings to use this tool.</div>',unsafe_allow_html=True);return
    if not st.session_state.brand_profile: st.markdown('<div class="warn-strip">⚠️ Set up your Brand Profile first for a tailored analysis.</div>',unsafe_allow_html=True)
    with st.form("comp_form"):
        c1,c2=st.columns(2)
        with c1:
            comp_name=st.text_input("Competitor Name / Brand",placeholder="e.g. Wow Skin Science")
            comp_type=st.text_input("Their Business Type",placeholder="e.g. D2C Skincare Brand")
        with c2:
            comp_platform=st.multiselect("Their Main Platforms",["Instagram","Facebook","YouTube","LinkedIn","Google Ads","Amazon","Flipkart"],default=["Instagram"])
            comp_size=st.selectbox("Their Estimated Size",["Small (local)","Medium (city-wide)","Large (national)","Enterprise (pan-India/global)"])
        extra=st.text_area("Anything else you know about them?",placeholder="e.g. Heavy discounts, target college students, post daily reels...",height=60)
        go=st.form_submit_button("🔍  Spy on Competitor",use_container_width=True)
    if go and comp_name:
        system="You are a senior marketing strategist with 15 years in the Indian market. Give sharp, specific, India-focused competitive intelligence. Use emojis for section headers."
        prompt=f"""Analyse this competitor for an Indian business owner:

COMPETITOR: {comp_name}
TYPE: {comp_type}
PLATFORMS: {', '.join(comp_platform)}
SIZE: {comp_size}
EXTRA: {extra}
MY BUSINESS: {brand_summary()}

Provide:
1. 📊 Their Likely Strategy
2. 🎯 Content Themes they probably focus on
3. 💪 Their Strengths
4. 🔓 Their Weaknesses & Gaps
5. ⚔️ How to Beat Them — specific tactics
6. 🚀 Opportunity Areas they're ignoring
7. 📝 3 Immediate Actions I can take THIS WEEK

Be India-specific. Reference actual Indian market context."""
        with st.spinner("🔍 Analysing competitor strategy..."):
            result,err=ai_call(system,prompt,max_tokens=2000)
        if err: st.markdown(f'<div class="error-strip">{err}</div>',unsafe_allow_html=True)
        elif result:
            st.markdown("<hr class='div'/>",unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#F59E0B;margin-bottom:0.8rem;">ANALYSIS: {comp_name.upper()}</div>',unsafe_allow_html=True)
            st.markdown(f'<div class="ai-output">{result.replace(chr(10),"<br/>")}</div>',unsafe_allow_html=True)
            if st.button("💾  Save This Analysis"):
                st.session_state.saved_analyses.append({"competitor":comp_name,"date":datetime.now().strftime("%d %b %Y"),"result":result})
                save_user(st.session_state.username)
                st.markdown('<div class="success-strip">✅ Saved!</div>',unsafe_allow_html=True)
    if st.session_state.saved_analyses:
        st.markdown("<hr class='div'/>",unsafe_allow_html=True)
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#64748B;margin-bottom:0.5rem;">SAVED ANALYSES</div>',unsafe_allow_html=True)
        for a in reversed(st.session_state.saved_analyses):
            with st.expander(f"🔍 {a['competitor']} — {a['date']}"):
                st.markdown(f'<div class="ai-output">{a["result"].replace(chr(10),"<br/>")}</div>',unsafe_allow_html=True)

# ── CONTENT CALENDAR ──
def page_calendar():
    st.markdown('<div class="section-heading">📅 Content Calendar Generator</div><div class="section-sub">Generate a full month of post ideas tailored to your business and platform.</div>',unsafe_allow_html=True)
    if not st.session_state.api_key: st.markdown('<div class="warn-strip">⚠️ Add your Anthropic API key in ⚙️ Settings.</div>',unsafe_allow_html=True);return
    if not st.session_state.brand_profile: st.markdown('<div class="warn-strip">⚠️ Set up your Brand Profile first.</div>',unsafe_allow_html=True)
    MONTHS=["January","February","March","April","May","June","July","August","September","October","November","December"]
    with st.form("cal_form"):
        c1,c2,c3=st.columns(3)
        with c1: month=st.selectbox("Month",MONTHS,index=datetime.now().month-1)
        with c2: platform=st.selectbox("Primary Platform",["Instagram","Facebook","LinkedIn","YouTube","WhatsApp","Twitter/X"])
        with c3: ppw=st.selectbox("Posts Per Week",["3 posts/week","5 posts/week","7 posts/week (daily)"])
        focus=st.text_input("Special Focus / Events",placeholder="e.g. Diwali sale, new product launch, anniversary...")
        go=st.form_submit_button("📅  Generate Content Calendar",use_container_width=True)
    if go:
        system="You are a top social media strategist for Indian brands. Create culturally relevant, platform-native content calendars with Indian festivals and trends."
        prompt=f"""Create a 30-day social media content calendar for {month}:

MY BUSINESS: {brand_summary()}
PLATFORM: {platform}
FREQUENCY: {ppw}
SPECIAL FOCUS: {focus or "None"}

For each week:
- Weekly theme
- Each post: Date, Content Type (Reel/Carousel/Story/Static), Concept + caption idea
- Best posting time for Indian audiences
- Hashtag groups

Format: WEEK 1 — [Theme] then daily entries.
Include Indian festivals in {month}.
End with 5 content pillars for this brand."""
        with st.spinner("📅 Crafting your content calendar..."):
            result,err=ai_call(system,prompt,max_tokens=3000)
        if err: st.markdown(f'<div class="error-strip">{err}</div>',unsafe_allow_html=True)
        elif result:
            st.markdown("<hr class='div'/>",unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#F59E0B;margin-bottom:0.8rem;">{month.upper()} CONTENT CALENDAR — {platform.upper()}</div>',unsafe_allow_html=True)
            st.markdown(f'<div class="ai-output">{result.replace(chr(10),"<br/>")}</div>',unsafe_allow_html=True)
            cs,cd=st.columns(2)
            with cs:
                if st.button("💾  Save Calendar"):
                    st.session_state.saved_calendars.append({"month":month,"platform":platform,"date":datetime.now().strftime("%d %b %Y"),"result":result})
                    save_user(st.session_state.username)
                    st.markdown('<div class="success-strip">✅ Saved!</div>',unsafe_allow_html=True)
            with cd:
                b64=base64.b64encode(result.encode()).decode()
                st.markdown(f'<a href="data:text/plain;base64,{b64}" download="{month}_calendar.txt" style="text-decoration:none;"><div style="display:inline-block;background:#F59E0B;color:#000;font-family:Syne,sans-serif;font-weight:700;border:2px solid #000;border-radius:6px;box-shadow:4px 4px 0 #000;padding:0.55rem 1.3rem;cursor:pointer;font-size:0.82rem;text-transform:uppercase;">📥 Download .txt</div></a>',unsafe_allow_html=True)
    if st.session_state.saved_calendars:
        st.markdown("<hr class='div'/>",unsafe_allow_html=True)
        for cal in reversed(st.session_state.saved_calendars):
            with st.expander(f"📅 {cal['month']} — {cal['platform']} ({cal['date']})"):
                st.markdown(f'<div class="ai-output">{cal["result"].replace(chr(10),"<br/>")}</div>',unsafe_allow_html=True)

# ── BUDGET ALLOCATOR ──
BUDGET_ALLOC={"Awareness":{"Instagram Ads":30,"Facebook Ads":20,"Google Display":15,"YouTube Ads":15,"Content Creation":20},"Lead Generation":{"Google Search Ads":35,"Instagram Ads":25,"Facebook Ads":20,"WhatsApp Marketing":10,"Content Creation":10},"Sales / E-commerce":{"Google Shopping":30,"Instagram Ads":25,"Facebook Retargeting":20,"Amazon/Flipkart Ads":15,"Content Creation":10},"App Installs":{"Google UAC":40,"Instagram Ads":30,"Facebook Ads":20,"Influencer":10},"Local Footfall":{"Google My Business":20,"Instagram Local":25,"Facebook Local":20,"WhatsApp Broadcast":20,"Offline/Print":15}}
COLORS=["#F59E0B","#06B6D4","#10B981","#EF4444","#8B5CF6","#EC4899"]

def page_budget():
    st.markdown('<div class="section-heading">💰 Ad Budget Allocator</div><div class="section-sub">Enter your monthly budget and goal — get a smart channel split plus AI tips on maximising ROI.</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1: budget=st.number_input("Monthly Budget (₹)",min_value=1000,max_value=1000000,value=10000,step=1000)
    with c2: goal=st.selectbox("Campaign Goal",list(BUDGET_ALLOC.keys()))
    with c3: industry=st.selectbox("Industry",["E-commerce","Food & Beverage","Fashion","Health & Wellness","Education","Real Estate","Finance","Travel","Tech","Other"])
    alloc=BUDGET_ALLOC[goal]
    st.markdown("<hr class='div'/>",unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#F59E0B;margin-bottom:1rem;">RECOMMENDED SPLIT — ₹{budget:,} FOR {goal.upper()}</div>',unsafe_allow_html=True)
    rows=""
    for i,(plat,pct) in enumerate(alloc.items()):
        amt=int(budget*pct/100);color=COLORS[i%len(COLORS)]
        rows+=f'<div class="budget-row"><div class="budget-label">{plat}</div><div class="budget-bar-wrap"><div class="budget-bar-fill" style="width:{pct}%;background:{color};"></div></div><div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#94A3B8;width:35px;text-align:right;">{pct}%</div><div class="budget-amount">₹{amt:,}</div></div>'
    st.markdown(f'<div class="card">{rows}</div>',unsafe_allow_html=True)
    fig=go.Figure(go.Pie(labels=list(alloc.keys()),values=[budget*p/100 for p in alloc.values()],hole=0.5,marker_colors=COLORS[:len(alloc)],textfont_color="#E2E8F0"))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",font_color="#94A3B8",showlegend=True,legend=dict(bgcolor="rgba(0,0,0,0)"),margin=dict(l=0,r=0,t=10,b=0),height=250,annotations=[dict(text=f"₹{budget:,}",x=0.5,y=0.5,font_size=14,font_color="#E2E8F0",showarrow=False)])
    st.plotly_chart(fig,use_container_width=True)
    if st.session_state.api_key:
        if st.button("🤖  Get AI Tips to Maximise This Budget"):
            system="You are an expert performance marketer for Indian SMBs. Give practical, specific, budget-conscious advice."
            prompt=f"""Smart tips to maximise ROI for this Indian marketing budget:
Budget: ₹{budget:,}/month | Goal: {goal} | Industry: {industry}
Brand: {brand_summary()}
Split: {json.dumps(alloc)}

Give:
1. 💡 3 Quick Wins — first week actions
2. 🚫 Common Mistakes to avoid
3. 📈 How to scale when it starts working
4. 🇮🇳 India-specific tips (WhatsApp, vernacular, regional targeting)
5. 📊 Key metrics to track"""
            with st.spinner("🤖 Generating tips..."): result,err=ai_call(system,prompt,max_tokens=1500)
            if err: st.markdown(f'<div class="error-strip">{err}</div>',unsafe_allow_html=True)
            elif result: st.markdown(f'<div class="ai-output" style="margin-top:1rem;">{result.replace(chr(10),"<br/>")}</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-strip">💡 Add your API key in ⚙️ Settings to get AI tips on maximising this budget.</div>',unsafe_allow_html=True)

# ── CAMPAIGN TRACKER ──
def page_tracker():
    st.markdown('<div class="section-heading">📊 Campaign Tracker</div><div class="section-sub">Log campaigns, track performance, and get AI insights on what\'s working.</div>',unsafe_allow_html=True)
    tab1,tab2,tab3=st.tabs(["➕ Log Campaign","📋 All Campaigns","💡 AI Insights"])
    with tab1:
        with st.form("camp_form"):
            c1,c2=st.columns(2)
            with c1:
                camp_name=st.text_input("Campaign Name",placeholder="e.g. Diwali Sale Instagram")
                platform=st.selectbox("Platform",["Instagram Ads","Facebook Ads","Google Search","Google Display","YouTube Ads","WhatsApp","Influencer","Email","Organic","Other"])
                camp_goal=st.selectbox("Goal",["Awareness","Leads","Sales","Installs","Engagement","Traffic"])
                start_date=st.date_input("Start Date",value=datetime.now())
            with c2:
                spend=st.number_input("Spend (₹)",min_value=0,step=500)
                revenue=st.number_input("Revenue Generated (₹)",min_value=0,step=500)
                leads=st.number_input("Leads / Conversions",min_value=0,step=1)
                impressions=st.number_input("Impressions / Reach",min_value=0,step=100)
            notes=st.text_area("Notes / Learnings",placeholder="What worked? What didn't?",height=60)
            if st.form_submit_button("➕  Add Campaign",use_container_width=True) and camp_name:
                roas=round(revenue/spend,2) if spend>0 else 0
                cpl=round(spend/leads,2) if leads>0 else 0
                st.session_state.campaigns.append({"name":camp_name,"platform":platform,"goal":camp_goal,"date":start_date.strftime("%d %b %Y"),"spend":spend,"revenue":revenue,"leads":leads,"impressions":impressions,"roas":roas,"cpl":cpl,"notes":notes})
                save_user(st.session_state.username)
                st.markdown('<div class="success-strip">✅ Campaign logged!</div>',unsafe_allow_html=True)
    with tab2:
        camps=st.session_state.campaigns
        if not camps: st.markdown('<div class="warn-strip">No campaigns yet. Log your first in the ➕ tab.</div>',unsafe_allow_html=True)
        else:
            df=pd.DataFrame(camps)
            ts=df["spend"].sum();tr=df["revenue"].sum();tl=df["leads"].sum()
            ar=round(tr/ts,2) if ts>0 else 0
            m1,m2,m3,m4=st.columns(4)
            for col,val,lbl in[(m1,f"₹{ts:,}","Total Spend"),(m2,f"₹{tr:,}","Total Revenue"),(m3,tl,"Total Leads"),(m4,f"{ar}x","Avg ROAS")]:
                with col: st.markdown(f'<div class="card" style="text-align:center;padding:0.8rem;"><div style="font-family:IBM Plex Mono,monospace;font-size:1.2rem;color:#E2E8F0;">{val}</div><div style="font-size:0.72rem;color:#64748B;">{lbl}</div></div>',unsafe_allow_html=True)
            dcols=[c for c in ["name","platform","goal","date","spend","revenue","leads","roas","cpl"] if c in df.columns]
            st.dataframe(df[dcols].rename(columns={"name":"Campaign","platform":"Platform","goal":"Goal","date":"Date","spend":"Spend ₹","revenue":"Revenue ₹","leads":"Leads","roas":"ROAS","cpl":"CPL ₹"}),use_container_width=True,hide_index=True)
            if len(camps)>1:
                st.markdown("<hr class='div'/>",unsafe_allow_html=True)
                ch1,ch2=st.columns(2)
                with ch1:
                    fig=px.bar(df,x="name",y=["spend","revenue"],barmode="group",color_discrete_map={"spend":"#EF4444","revenue":"#10B981"},title="Spend vs Revenue")
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#94A3B8",margin=dict(l=0,r=0,t=30,b=0),height=260,xaxis=dict(gridcolor="#1E2A38"),yaxis=dict(gridcolor="#1E2A38"),legend=dict(bgcolor="rgba(0,0,0,0)"))
                    st.plotly_chart(fig,use_container_width=True)
                with ch2:
                    ps=df.groupby("platform")["spend"].sum().reset_index()
                    fig2=px.pie(ps,names="platform",values="spend",title="Spend by Platform",hole=0.4,color_discrete_sequence=COLORS)
                    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",font_color="#94A3B8",margin=dict(l=0,r=0,t=30,b=0),height=260,legend=dict(bgcolor="rgba(0,0,0,0)"))
                    st.plotly_chart(fig2,use_container_width=True)
            if st.button("🗑️  Clear All Campaigns"): st.session_state.campaigns=[];save_user(st.session_state.username);st.rerun()
    with tab3:
        if not st.session_state.api_key: st.markdown('<div class="warn-strip">⚠️ Add your API key in ⚙️ Settings.</div>',unsafe_allow_html=True);return
        camps=st.session_state.campaigns
        if not camps: st.markdown('<div class="warn-strip">Log at least one campaign first.</div>',unsafe_allow_html=True);return
        if st.button("🤖  Analyse My Campaigns",use_container_width=True):
            summary="\n".join([f"- {c['name']}: {c['platform']}, Spend ₹{c.get('spend',0):,}, Revenue ₹{c.get('revenue',0):,}, Leads {c.get('leads',0)}, ROAS {c.get('roas',0)}x" for c in camps])
            system="You are a data-driven marketing analyst for Indian businesses. Give sharp, actionable campaign insights."
            prompt=f"""Analyse these campaigns for {brand_summary()}:

{summary}

Provide:
1. 🏆 Best Performing Campaign & Why
2. 💸 Worst Performing & How to Fix It
3. 📊 Overall Patterns — what's working?
4. 🚀 Top 3 Recommendations for next month
5. 💡 Budget Shift — where should more/less money go?
6. ⚠️ Warning Signs — any concerning trends?

Reference actual numbers. Be specific."""
            with st.spinner("🤖 Analysing campaigns..."): result,err=ai_call(system,prompt,max_tokens=1500)
            if err: st.markdown(f'<div class="error-strip">{err}</div>',unsafe_allow_html=True)
            elif result: st.markdown(f'<div class="ai-output">{result.replace(chr(10),"<br/>")}</div>',unsafe_allow_html=True)

# ── SETTINGS ──
def page_settings():
    st.markdown('<div class="section-heading">⚙️ Settings</div>',unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#64748B;margin-bottom:0.5rem;">ANTHROPIC API KEY</div>',unsafe_allow_html=True)
    st.markdown('<div class="info-strip">🔑 All AI features need an Anthropic API key. Get yours free at <strong>console.anthropic.com</strong> → API Keys → Create Key.</div>',unsafe_allow_html=True)
    with st.form("api_form"):
        api_key=st.text_input("Anthropic API Key",value=st.session_state.api_key,type="password",placeholder="sk-ant-api03-...")
        if st.form_submit_button("💾  Save API Key",use_container_width=True):
            st.session_state.api_key=api_key.strip()
            save_user(st.session_state.username)
            st.markdown('<div class="success-strip">✅ API key saved! All AI tools are now active.</div>',unsafe_allow_html=True)
    if st.session_state.api_key: st.markdown('<div class="success-strip">✅ API key is set. All AI tools are active.</div>',unsafe_allow_html=True)
    st.markdown("<hr class='div'/>",unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#64748B;margin-bottom:0.5rem;">ACCOUNT INFO</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="card"><div style="font-size:0.85rem;">Username: <strong style="color:#F59E0B;">@{st.session_state.username}</strong></div><div style="font-size:0.8rem;color:#64748B;margin-top:0.3rem;">Campaigns: {len(st.session_state.campaigns)} &nbsp;|&nbsp; Saved Calendars: {len(st.session_state.saved_calendars)} &nbsp;|&nbsp; Saved Analyses: {len(st.session_state.saved_analyses)}</div></div>',unsafe_allow_html=True)
    st.markdown("<hr class='div'/>",unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#64748B;margin-bottom:0.5rem;">DEPLOY WITH SECRETS (PRODUCTION)</div>',unsafe_allow_html=True)
    st.markdown('<div class="card" style="font-size:0.82rem;line-height:1.8;">Store your key securely on Streamlit Cloud:<br/>1. App → <strong>Settings → Secrets</strong><br/>2. Add: <code>ANTHROPIC_API_KEY = "sk-ant-..."</code><br/>3. It loads automatically on deploy.</div>',unsafe_allow_html=True)

# ── MAIN ──
def main():
    st.markdown(CSS,unsafe_allow_html=True)
    init()
    if not st.session_state.api_key:
        try: st.session_state.api_key=st.secrets.get("ANTHROPIC_API_KEY","")
        except: pass
    if not st.session_state.logged_in: render_auth();return
    render_sidebar()
    page=st.session_state.page
    if   page=="dashboard":  page_dashboard()
    elif page=="brand":      page_brand()
    elif page=="competitor": page_competitor()
    elif page=="calendar":   page_calendar()
    elif page=="budget":     page_budget()
    elif page=="tracker":    page_tracker()
    elif page=="settings":   page_settings()

if __name__=="__main__":
    main()
