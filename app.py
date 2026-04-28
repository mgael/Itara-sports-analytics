import streamlit as st
import pandas as pd
import numpy as np
import io, base64, hashlib, datetime, warnings
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="ITARA Sports Analytics", page_icon="⚽",
                   layout="wide", initial_sidebar_state="collapsed")

# ─────────────────────────────────────────────
# CSS  — Claude AI palette
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;0,9..144,800&display=swap');
:root{--bg:#f5f0e8;--bg-card:#faf7f2;--bg-dark:#1c1917;--accent:#d97757;--accent-dk:#b85e3a;
      --accent-lt:#f5e6dc;--text-pri:#1c1917;--text-sec:#57534e;--text-muted:#a8a29e;
      --border:#e7e0d5;--white:#ffffff;}
html,body,[class*="css"]{font-family:'Sora',sans-serif;color:var(--text-pri);}
h1,h2,h3{font-family:'Fraunces',serif!important;font-weight:800!important;
          color:var(--text-pri)!important;letter-spacing:-0.01em!important;}
.main,.stApp{background-color:var(--bg)!important;}
.block-container{padding-top:1.2rem!important;background-color:var(--bg)!important;}
section[data-testid="stSidebar"]{background:var(--bg-dark)!important;border-right:1px solid #2c2825;}
section[data-testid="stSidebar"] *{color:#d6d3d1!important;}
section[data-testid="stSidebar"] [data-testid="stMetricValue"]{color:var(--accent)!important;font-weight:700!important;}
section[data-testid="stSidebar"] div[data-baseweb="select"]>div{background:#2c2825!important;border-color:#3d3530!important;color:#d6d3d1!important;}
div[data-testid="metric-container"]{background:var(--bg-card);border:1px solid var(--border);
    border-radius:10px;padding:14px 18px;box-shadow:0 1px 4px rgba(0,0,0,0.06);}
div[data-testid="metric-container"] [data-testid="stMetricValue"]{color:var(--accent)!important;font-weight:700;}
div[data-testid="stDataFrame"]{border-radius:10px;overflow:hidden;border:1px solid var(--border);}
.stButton>button{background:var(--accent);color:#fff;border:none;border-radius:8px;
    font-family:'Sora',sans-serif;font-weight:600;font-size:0.88rem;padding:0.5rem 1.2rem;
    transition:all 0.18s ease;box-shadow:0 2px 8px rgba(217,119,87,0.25);}
.stButton>button:hover{background:var(--accent-dk);transform:translateY(-1px);
    box-shadow:0 4px 14px rgba(217,119,87,0.35);}
.stDownloadButton>button{background:var(--text-pri)!important;color:var(--bg)!important;
    border:none!important;border-radius:8px!important;font-weight:600!important;}
div[data-testid="stForm"]{background:var(--bg-card);border:1px solid var(--border);
    border-radius:12px;padding:20px;box-shadow:0 1px 4px rgba(0,0,0,0.05);}
.stTabs [data-baseweb="tab-list"]{background:var(--bg-card);border:1px solid var(--border);
    border-radius:10px;gap:2px;padding:4px;}
.stTabs [data-baseweb="tab"]{background:transparent;color:var(--text-sec);
    font-family:'Sora',sans-serif;font-weight:600;font-size:0.85rem;border-radius:7px;}
.stTabs [aria-selected="true"]{background:var(--accent)!important;color:#fff!important;border-radius:7px;}
div[data-baseweb="select"]>div{background:var(--bg-card)!important;border-color:var(--border)!important;color:var(--text-pri)!important;}
input,textarea{background:var(--bg-card)!important;color:var(--text-pri)!important;border-color:var(--border)!important;}
div[data-testid="stAlert"]{border-radius:10px!important;border-left:4px solid var(--accent)!important;background:var(--bg-card)!important;}
hr{border-color:var(--border)!important;}
.stCaption,small{color:var(--text-muted)!important;}
label{color:var(--text-sec)!important;font-size:0.85rem!important;}
div[data-testid="stProgress"]>div>div{background:linear-gradient(90deg,var(--accent),var(--accent-dk))!important;border-radius:4px;}

/* Homepage */
.home-hero{background:linear-gradient(135deg,#1c1917 0%,#2c2218 60%,#1c1917 100%);
    border-radius:20px;padding:52px 48px;margin-bottom:32px;position:relative;
    overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,0.18);}
.home-hero::before{content:'';position:absolute;top:0;right:0;bottom:0;width:45%;
    background:linear-gradient(135deg,rgba(217,119,87,0.12),rgba(217,119,87,0.03));
    clip-path:polygon(20% 0%,100% 0%,100% 100%,0% 100%);}
.home-tagline{font-family:'Fraunces',serif;font-size:2.5rem;font-weight:800;color:#fff;line-height:1.15;margin:0 0 12px 0;}
.home-tagline span{color:var(--accent);}
.home-sub{color:#a8a29e;font-size:0.95rem;line-height:1.75;max-width:580px;margin-bottom:20px;}
.badge-rw{display:inline-flex;align-items:center;gap:6px;background:rgba(217,119,87,0.15);
    border:1px solid rgba(217,119,87,0.35);border-radius:20px;padding:5px 14px;
    font-size:0.78rem;color:var(--accent);font-weight:600;letter-spacing:0.05em;}
.feature-card{background:var(--bg-card);border:1px solid var(--border);border-radius:14px;
    padding:24px;text-align:center;transition:all 0.2s;box-shadow:0 2px 8px rgba(0,0,0,0.04);height:100%;}
.plan-card{background:var(--bg-card);border:2px solid var(--border);border-radius:16px;padding:28px 20px;text-align:center;}
.plan-card.featured{border-color:var(--accent);background:linear-gradient(135deg,#fff8f4,var(--bg-card));
    box-shadow:0 6px 24px rgba(217,119,87,0.18);}
.plan-price{font-family:'Fraunces',serif;font-size:2rem;font-weight:800;color:var(--accent);}
.plan-name{font-size:1rem;font-weight:700;color:var(--text-pri);margin-bottom:4px;}
.paywall-box{background:linear-gradient(135deg,#fff8f4,var(--bg-card));border:2px solid var(--accent);
    border-radius:16px;padding:40px 32px;text-align:center;max-width:520px;margin:0 auto;}
.mtn-badge{background:#ffcc00;color:#1c1917;font-weight:700;font-size:0.88rem;
    border-radius:8px;padding:7px 18px;display:inline-block;margin-bottom:16px;}
.hero-banner{background:linear-gradient(135deg,var(--accent) 0%,var(--accent-dk) 100%);
    border-radius:14px;padding:28px 36px;margin-bottom:24px;position:relative;
    overflow:hidden;box-shadow:0 4px 20px rgba(217,119,87,0.3);}
.hero-banner::before{content:'⚽';position:absolute;right:28px;top:50%;transform:translateY(-50%);font-size:72px;opacity:0.12;}
.hero-title{font-family:'Fraunces',serif;font-size:2.2rem;font-weight:800;color:#fff;line-height:1.1;margin:0;}
.hero-sub{color:rgba(255,255,255,0.75);font-size:0.88rem;margin-top:8px;letter-spacing:0.05em;text-transform:uppercase;}
.info-box{background:var(--bg-card);border:1px solid var(--border);border-radius:14px;padding:28px 28px;margin-bottom:16px;}
.info-box h4{font-family:'Fraunces',serif;font-size:1.1rem;font-weight:700;color:var(--accent);margin-bottom:10px;}
.role-badge{display:inline-block;padding:3px 12px;border-radius:20px;font-size:0.75rem;font-weight:700;letter-spacing:0.04em;}
.role-manager{background:#dbeafe;color:#1e40af;}
.role-agent{background:#fce7f3;color:#9d174d;}
.role-admin{background:#d1fae5;color:#065f46;}
.role-scout{background:#fef3c7;color:#92400e;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def img_b64():
    try:
        with open("logo.png","rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

LOGO = img_b64()

def logo_html(w=160):
    if LOGO:
        return f'<img src="data:image/png;base64,{LOGO}" width="{w}" style="display:block;">'
    return '<span style="font-family:Fraunces,serif;font-size:1.6rem;font-weight:800;color:#d97757;">⚽ ITARA</span>'

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def init():
    D = {
        'page':'home','logged_in':False,'user':None,'auth_tab':'signin',
        'users_db':{
            'admin@itara.rw':{'name':'ITARA Admin','role':'League Admin','team':None,
                'pw':hash_pw('demo1234'),'subscribed':True,'sub_expires':'2026-12-31'},
            'manager@aprfc.rw':{'name':'APR FC Manager','role':'Team Manager','team':'APR FC',
                'pw':hash_pw('demo1234'),'subscribed':True,'sub_expires':'2026-12-31'},
            'agent@itara.rw':{'name':'Scout Agent','role':'Football Agent','team':None,
                'pw':hash_pw('demo1234'),'subscribed':True,'sub_expires':'2026-12-31'},
            'scout@itara.rw':{'name':'Field Scout','role':'Scout','team':None,
                'pw':hash_pw('demo1234'),'subscribed':True,'sub_expires':'2026-12-31'},
        },
        'feedback':[],
        'selected_season':'2024/25',
        'seasons':['2022/23','2023/24','2024/25','2025/26'],
        'teams':["APR FC","Rayon Sports","Police FC","Kiyovu Sports","Mukura VS"],
        'data': pd.DataFrame(columns=['Player','Team','Position','Age','Goals','Assists',
            'Matches','Minutes_Played','Shots_on_Target','Pass_Accuracy',
            'Dribbles_Completed','Tackles_Won','Health_Score','Performance_Index','Season']),
        'match_results': pd.DataFrame(columns=[
            'Home_Team','Away_Team','Home_Goals','Away_Goals','Matchday','Season']),
    }
    for k,v in D.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

# ─────────────────────────────────────────────
# ANALYTICS
# ─────────────────────────────────────────────
def xG(r):
    s=max(r.get('Shots_on_Target',0),0); m=max(r.get('Matches',1),1)
    return round(s/m*0.32*m,2)
def xA(r):
    a=r.get('Assists',0); p=r.get('Pass_Accuracy',75)/100
    return round(max(a*(1+(p-0.75)),0),2)
def prog(r):
    d=r.get('Dribbles_Completed',0); t=r.get('Tackles_Won',0); m=max(r.get('Matches',1),1)
    return round(min(((d/m)*0.6+(t/m)*0.4)*1.5,10),2)
def market_val(r):
    pi=r['Performance_Index']; m=max(r.get('Matches',1),1); age=r.get('Age',25)
    af=max(0.6,1.0-abs(age-25)*0.015)
    return round((pi*1_250_000)*(1+(m*0.05))*af,-3)
def cpr(r):
    m=max(r.get('Matches',1),1)
    g=min(r.get('Goals',0)/m*10,10); a=min(r.get('Assists',0)/m*10,10)
    pa=r.get('Pass_Accuracy',75)/10; h=r.get('Health_Score',100)/10
    pr=prog(r); pi=r.get('Performance_Index',5)
    return round(min(pi*0.40+g*0.20+a*0.15+pa*0.10+h*0.10+pr*0.05,10),2)
def form_label(pi):
    if pi>=8.5: return "Elite"
    if pi>=7.0: return "Strong"
    if pi>=5.0: return "Developing"
    return "Underperforming"
def avail(h):
    if h>=85: return "✅ Match Ready"
    if h>=70: return "⚠️ Light Training"
    if h>=50: return "🟠 Monitored"
    return "🔴 Unavailable"
def league_table(mr, teams):
    tbl={t:{'MP':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0} for t in teams}
    for _,row in mr.iterrows():
        ht,at=row['Home_Team'],row['Away_Team']
        hg,ag=int(row['Home_Goals']),int(row['Away_Goals'])
        for t in [ht,at]:
            if t not in tbl: tbl[t]={'MP':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0}
        tbl[ht]['MP']+=1;tbl[at]['MP']+=1
        tbl[ht]['GF']+=hg;tbl[ht]['GA']+=ag;tbl[at]['GF']+=ag;tbl[at]['GA']+=hg
        if hg>ag:   tbl[ht]['W']+=1;tbl[ht]['Pts']+=3;tbl[at]['L']+=1
        elif hg==ag:tbl[ht]['D']+=1;tbl[ht]['Pts']+=1;tbl[at]['D']+=1;tbl[at]['Pts']+=1
        else:       tbl[at]['W']+=1;tbl[at]['Pts']+=3;tbl[ht]['L']+=1
    for t in tbl: tbl[t]['GD']=tbl[t]['GF']-tbl[t]['GA']
    df=pd.DataFrame(tbl).T.reset_index().rename(columns={'index':'Club'})
    df=df.sort_values(['Pts','GD','GF'],ascending=False).reset_index(drop=True)
    df.index=df.index+1; df.index.name='Pos'
    return df

# ─────────────────────────────────────────────
# PLOT DEFAULTS
# ─────────────────────────────────────────────
PL = dict(template='plotly_white',plot_bgcolor='#faf7f2',paper_bgcolor='#faf7f2',
          font_color='#1c1917',title_font_size=13)
CL = ['#d97757','#b85e3a','#92400e','#f0c4b0','#78716c','#c9a84c']
FC = {'Elite':'#d97757','Strong':'#b85e3a','Developing':'#f59e0b','Underperforming':'#ef4444'}

# ─────────────────────────────────────────────
# PDF ENGINE
# ─────────────────────────────────────────────
def _styles():
    s=getSampleStyleSheet()
    T=ParagraphStyle('T',parent=s['Title'],fontSize=16,alignment=TA_CENTER,
                     textColor=colors.HexColor('#d97757'),spaceAfter=4)
    S=ParagraphStyle('S',parent=s['Normal'],fontSize=8,alignment=TA_CENTER,
                     textColor=colors.HexColor('#57534e'),spaceAfter=6)
    H=ParagraphStyle('H',parent=s['Heading2'],fontSize=11,
                     textColor=colors.HexColor('#b85e3a'),spaceBefore=10,spaceAfter=5)
    N=ParagraphStyle('N',parent=s['Normal'],fontSize=7,textColor=colors.HexColor('#78716c'))
    return T,S,H,N
def _ts():
    return TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#d97757')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,0),8),('FONTSIZE',(0,1),(-1,-1),7.5),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#e7e0d5')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#faf7f2')]),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
    ])
def make_pdf_manager(df,team,season,ldf=None):
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=0.6*inch,rightMargin=0.6*inch,
                          topMargin=0.6*inch,bottomMargin=0.6*inch)
    T,S,H,N=_styles(); els=[]
    els.append(Paragraph("ITARA SPORTS ANALYTICS",T))
    els.append(Paragraph(f"Team Report — {team} | Season {season}",S))
    els.append(Paragraph("🇷🇼 Made in Rwanda · African Football Intelligence Platform",S))
    els.append(Spacer(1,0.12*inch))
    tdf=df[df['Team']==team].copy() if team else df.copy()
    tdf['CPR']=tdf.apply(cpr,axis=1); tdf['xG_v']=tdf.apply(xG,axis=1)
    tdf['Form']=tdf['Performance_Index'].apply(form_label)
    tdf['Value']=tdf.apply(market_val,axis=1)
    els.append(Paragraph("Squad Performance",H))
    hdr=["Player","Pos","Age","CPR","PI","xG","G","A","Fit%","Form","Value(RWF)"]
    data=[hdr]+[[r.get('Player',''),r.get('Position',''),int(r.get('Age',0)),
                 f"{r['CPR']:.1f}",f"{r['Performance_Index']:.1f}",f"{r['xG_v']:.1f}",
                 int(r.get('Goals',0)),int(r.get('Assists',0)),
                 f"{r.get('Health_Score',0):.0f}%",r['Form'],f"{int(r['Value']):,}"]
                for _,r in tdf.iterrows()]
    t=Table(data,repeatRows=1); t.setStyle(_ts()); els.append(t)
    if ldf is not None and not ldf.empty:
        els.append(Spacer(1,0.12*inch)); els.append(Paragraph("League Standings",H))
        lt=Table([list(ldf.columns)]+[[str(v) for v in r] for _,r in ldf.iterrows()],repeatRows=1)
        lt.setStyle(_ts()); els.append(lt)
    els.append(Spacer(1,0.18*inch))
    els.append(Paragraph("CPR=0.40×PI+0.20×G/M+0.15×A/M+0.10×Pass+0.10×Health+0.05×Prog | V=PI×κ×(1+ΔM)×AgeFactor, κ=1,250,000 RWF",N))
    doc.build(els); return buf.getvalue()

def make_pdf_agent(df,season):
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=0.6*inch,rightMargin=0.6*inch,
                          topMargin=0.6*inch,bottomMargin=0.6*inch)
    T,S,H,N=_styles(); els=[]
    els.append(Paragraph("ITARA SPORTS ANALYTICS",T))
    els.append(Paragraph(f"League Scouting Report | Season {season}",S))
    els.append(Paragraph("🇷🇼 Made in Rwanda · Confidential — Agent Use Only",S))
    els.append(Spacer(1,0.12*inch))
    df2=df.copy(); df2['CPR']=df2.apply(cpr,axis=1); df2['xG_v']=df2.apply(xG,axis=1)
    df2['xA_v']=df2.apply(xA,axis=1); df2['Form']=df2['Performance_Index'].apply(form_label)
    df2['Value']=df2.apply(market_val,axis=1); df2=df2.sort_values('CPR',ascending=False)
    els.append(Paragraph("Top Performers — League Wide",H))
    hdr=["Player","Team","Pos","CPR","xG","xA","G","A","Form","Value(RWF)"]
    data=[hdr]+[[r.get('Player',''),r.get('Team',''),r.get('Position',''),
                 f"{r['CPR']:.1f}",f"{r['xG_v']:.1f}",f"{r['xA_v']:.1f}",
                 int(r.get('Goals',0)),int(r.get('Assists',0)),r['Form'],f"{int(r['Value']):,}"]
                for _,r in df2.iterrows()]
    t=Table(data,repeatRows=1); t.setStyle(_ts()); els.append(t)
    els.append(Spacer(1,0.18*inch))
    els.append(Paragraph("CPR: 40%×PI + 20%×GoalRate + 15%×AssistRate + 10%×PassAcc + 10%×Fitness + 5%×ProgScore",N))
    doc.build(els); return buf.getvalue()

def make_pdf_admin(df,season,ldf=None,mr=None):
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=0.5*inch,rightMargin=0.5*inch,
                          topMargin=0.6*inch,bottomMargin=0.6*inch)
    T,S,H,N=_styles(); els=[]
    els.append(Paragraph("ITARA SPORTS ANALYTICS",T))
    els.append(Paragraph(f"Full Platform Admin Report | Season {season}",S))
    els.append(Paragraph("🇷🇼 Made in Rwanda · League Administration Export",S))
    els.append(Spacer(1,0.12*inch))
    if ldf is not None and not ldf.empty:
        els.append(Paragraph("League Standings",H))
        lt=Table([list(ldf.columns)]+[[str(v) for v in r] for _,r in ldf.iterrows()],repeatRows=1)
        lt.setStyle(_ts()); els.append(lt); els.append(Spacer(1,0.1*inch))
    df2=df.copy(); df2['CPR']=df2.apply(cpr,axis=1)
    df2['Form']=df2['Performance_Index'].apply(form_label); df2['Value']=df2.apply(market_val,axis=1)
    els.append(Paragraph("All Players",H))
    hdr=["Player","Team","Pos","CPR","PI","G","A","Fit%","Form","Value(RWF)"]
    data=[hdr]+[[r.get('Player',''),r.get('Team',''),r.get('Position',''),
                 f"{r['CPR']:.1f}",f"{r['Performance_Index']:.1f}",
                 int(r.get('Goals',0)),int(r.get('Assists',0)),
                 f"{r.get('Health_Score',0):.0f}%",r['Form'],f"{int(r['Value']):,}"]
                for _,r in df2.iterrows()]
    t=Table(data,repeatRows=1); t.setStyle(_ts()); els.append(t)
    doc.build(els); return buf.getvalue()

# ─────────────────────────────────────────────
# AUTH + SUBSCRIPTION HELPERS
# ─────────────────────────────────────────────
def role_badge_html(role):
    cls={'Team Manager':'role-manager','Football Agent':'role-agent',
         'League Admin':'role-admin','Scout':'role-scout'}.get(role,'role-scout')
    return f'<span class="role-badge {cls}">{role}</span>'

def subscribed(u): return u.get('subscribed',False)

def season_data(user,season):
    df=st.session_state.data.copy()
    if 'Season' in df.columns and season!='All Seasons':
        df=df[df['Season']==season]
    if user['role']=='Team Manager' and user.get('team'):
        df=df[df['Team']==user['team']]
    return df

# ═══════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════
def pg_home():
    # Nav bar
    n1,n2,n3=st.columns([2,4,2])
    with n1: st.markdown(logo_html(155),unsafe_allow_html=True)
    with n3:
        st.markdown("<div style='padding-top:10px;'>",unsafe_allow_html=True)
        ca,cb=st.columns(2)
        if ca.button("Sign In",key="nav_si"):
            st.session_state.page='auth'; st.rerun()
        if cb.button("Register",key="nav_reg"):
            st.session_state.page='auth'; st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("<hr style='margin:10px 0 24px 0;border-color:#e7e0d5;'>",unsafe_allow_html=True)

    # Hero
    st.markdown(f"""
    <div class="home-hero">
        <div style="margin-bottom:18px;">{logo_html(190)}</div>
        <div class="home-tagline">African Football<br><span>Intelligence Platform</span></div>
        <p class="home-sub">
            ITARA Sports Analytics is Rwanda's first data-driven football intelligence platform —
            a one-stop centre for athlete data, performance tracking, scouting intelligence,
            and strategic decision-making across the African football ecosystem.
        </p>
        <div class="badge-rw">🇷🇼 Made in Rwanda &nbsp;·&nbsp; 
    </div>
    """,unsafe_allow_html=True)

    # About
    c1,c2=st.columns(2)
    with c1:
        st.markdown("""<div class="info-box"><h4>📖 Introduction</h4>
        <p style="color:#57534e;font-size:0.9rem;line-height:1.75;">
        ITARA Sports Analytics transforms data into a competitive edge. We partner with teams,
        athletes and organizations to unlock the power of data through advanced analytics,
        cutting-edge technology and deep sports expertise.<br><br>
        From performance analysis and opponent scouting to talent identification and strategic
        decision-making, we deliver insights that drive smarter choices and better results —
        on and off the field.</p></div>""",unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="info-box"><h4>🎯 Our Vision</h4>
        <p style="color:#57534e;font-size:0.9rem;line-height:1.75;">
        To be a global leader in sports analytics, empowering every competitive journey
        with data, insight and impact.<br><br>
        ITARA was born from Rwanda's government initiative to develop and promote the sports
        industry as a pillar of economic transformation. Our contribution: using data science
        to keep all athlete records on a single, secure, professional platform — accessible
        to clubs, agents, coaches and league administrators across Africa.</p></div>""",unsafe_allow_html=True)

    # Features
    st.markdown("<h3 style='text-align:center;margin:32px 0 18px;'>Platform Features</h3>",unsafe_allow_html=True)
    feats=[("🏆","League Intelligence","Full FIFA/UEFA standings, match results, and season comparisons."),
           ("📊","Performance Analytics","CPR, xG, xA and market valuation via internationally recognised formulas."),
           ("🧠","Coach Decision Center","Data-driven Starting XI selection, risk flags, position reports."),
           ("⚖️","Player Comparison","Head-to-head radar overlays with ITARA verdict engine."),
           ("🏥","Health & Fitness","Real-time fitness monitoring with clinical availability thresholds."),
           ("📤","Professional Reports","Role-specific PDF & Excel exports for every user type.")]
    cols=st.columns(3)
    for i,(icon,title,desc) in enumerate(feats):
        with cols[i%3]:
            st.markdown(f"""<div class="feature-card">
                <div style="font-size:2rem;margin-bottom:10px;">{icon}</div>
                <div style="font-family:Fraunces,serif;font-size:1rem;font-weight:700;color:#1c1917;margin-bottom:8px;">{title}</div>
                <div style="font-size:0.82rem;color:#57534e;line-height:1.6;">{desc}</div>
            </div>""",unsafe_allow_html=True)
            st.markdown("<div style='height:10px;'></div>",unsafe_allow_html=True)

    # Plans
    st.markdown("<h3 style='text-align:center;margin:36px 0 6px;'>Subscription Plans</h3>",unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#a8a29e;font-size:0.85rem;margin-bottom:22px;'>Billed monthly via MTN Mobile Money Rwanda</p>",unsafe_allow_html=True)
    plans=[
        ("Scout","15,000","RWF/mo",["League standings","Player stats (read-only)","Basic PDF export"],False),
        ("Football Agent","35,000","RWF/mo",["Player comparison","xG / xA metrics","Scouting PDF reports","League-wide access"],True),
        ("Team Manager","55,000","RWF/mo",["Full team dashboard","Health & fitness monitor","Coach decision center","Team PDF reports"],False),
        ("League Admin","90,000","RWF/mo",["Full platform access","All teams & players","Match management","Admin PDF reports"],False),
    ]
    pc=st.columns(4)
    for col,(name,price,period,perks,featured) in zip(pc,plans):
        with col:
            cls="plan-card featured" if featured else "plan-card"
            li="".join(f"<li style='font-size:0.78rem;color:#57534e;text-align:left;margin:4px 0;'>✓ {p}</li>" for p in perks)
            st.markdown(f"""<div class="{cls}">
                <div class="plan-name">{name}</div>
                <div class="plan-price">{price}</div>
                <div style="font-size:0.78rem;color:#a8a29e;">{period}</div>
                <ul style="padding-left:14px;margin-top:12px;">{li}</ul>
            </div>""",unsafe_allow_html=True)
            st.markdown("<div style='height:8px;'></div>",unsafe_allow_html=True)

    st.markdown("<div style='text-align:center;margin:28px 0 16px;'>",unsafe_allow_html=True)
    _,cc,_=st.columns([3,2,3])
    if cc.button("🚀 Create Account — Get Started",key="cta"):
        st.session_state.page='auth'; st.rerun()
    st.markdown("</div>",unsafe_allow_html=True)

    # Feedback
    st.markdown("<hr style='margin:36px 0 24px;'>",unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;margin-bottom:4px;'>💬 Share Your Feedback</h3>",unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#a8a29e;font-size:0.84rem;margin-bottom:20px;'>Help us build the best sports analytics platform in Africa</p>",unsafe_allow_html=True)
    _,fc,_=st.columns([1,2,1])
    with fc:
        with st.form("fb"):
            fb_name=st.text_input("Your Name")
            fb_email=st.text_input("Email")
            fb_role=st.selectbox("Your Role",["Club Official","Football Agent","Coach","Scout","Journalist","Fan","Other"])
            fb_rating=st.select_slider("Rate the Platform",options=[1,2,3,4,5],value=5)
            fb_msg=st.text_area("Message / Suggestion",height=100)
            if st.form_submit_button("📨 Submit Feedback",use_container_width=True):
                if fb_name and fb_msg:
                    st.session_state.feedback.append({'name':fb_name,'email':fb_email,
                        'role':fb_role,'rating':fb_rating,'message':fb_msg,
                        'time':datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
                    st.success("✅ Thank you! Your feedback has been received.")
                else:
                    st.error("Please enter your name and a message.")

    # Footer
    st.markdown("""
    <div style="text-align:center;padding:28px 0 12px;border-top:1px solid #e7e0d5;margin-top:40px;">
        <div style="font-family:Fraunces,serif;font-size:1.05rem;font-weight:700;color:#d97757;margin-bottom:6px;">ITARA Sports Analytics</div>
        <div style="color:#a8a29e;font-size:0.76rem;letter-spacing:0.06em;">
            🇷🇼 Kigali, Rwanda &nbsp;·&nbsp; African Football Intelligence &nbsp;·&nbsp;
            Inspired by Rwanda's Sport Industry Development Initiative<br>
            © 2025 ITARA Analytics Ltd. All rights reserved.
        </div>
    </div>""",unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# PAGE: AUTH
# ═══════════════════════════════════════════════
def pg_auth():
    _,cc,_=st.columns([1,2,1])
    with cc:
        st.markdown(f"<div style='text-align:center;margin-bottom:20px;'>{logo_html(150)}</div>",unsafe_allow_html=True)
        tab_si,tab_reg=st.tabs(["🔐 Sign In","📝 Create Account"])
        with tab_si:
            with st.form("sf"):
                email=st.text_input("Email Address",placeholder="you@example.com")
                pw=st.text_input("Password",type="password")
                if st.form_submit_button("Sign In →",use_container_width=True):
                    db=st.session_state.users_db
                    if email in db and db[email]['pw']==hash_pw(pw):
                        u=db[email].copy(); u['email']=email
                        st.session_state.user=u; st.session_state.logged_in=True
                        st.session_state.page='subscribe' if not subscribed(u) else 'app'
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
            st.caption("Demo — admin@itara.rw | manager@aprfc.rw | agent@itara.rw | scout@itara.rw — pw: demo1234")
        with tab_reg:
            with st.form("rf"):
                r_name=st.text_input("Full Name")
                r_email=st.text_input("Email Address")
                r_role=st.selectbox("Your Role",["Team Manager","Football Agent","League Admin","Scout"])
                r_team=st.text_input("Team (Team Manager only)",placeholder="e.g. APR FC")
                r_pw=st.text_input("Password",type="password")
                r_pw2=st.text_input("Confirm Password",type="password")
                r_terms=st.checkbox("I agree to the Terms of Service")
                if st.form_submit_button("Create Account →",use_container_width=True):
                    if not all([r_name,r_email,r_pw]): st.error("Fill in all required fields.")
                    elif r_pw!=r_pw2: st.error("Passwords do not match.")
                    elif not r_terms: st.error("Accept the terms to continue.")
                    elif r_email in st.session_state.users_db: st.error("Account already exists.")
                    else:
                        nu={'name':r_name,'role':r_role,'team':r_team if r_role=='Team Manager' else None,
                            'pw':hash_pw(r_pw),'subscribed':False,'sub_expires':None}
                        st.session_state.users_db[r_email]=nu
                        nu['email']=r_email
                        st.session_state.user=nu; st.session_state.logged_in=True
                        st.session_state.page='subscribe'; st.rerun()
    if st.button("← Back to Home",key="ab"):
        st.session_state.page='home'; st.rerun()

# ═══════════════════════════════════════════════
# PAGE: SUBSCRIBE
# ═══════════════════════════════════════════════
def pg_subscribe():
    u=st.session_state.user; role=u['role']
    prices={'Scout':'15,000','Football Agent':'35,000','Team Manager':'55,000','League Admin':'90,000'}
    price=prices.get(role,'35,000')
    _,cc,_=st.columns([1,2,1])
    with cc:
        st.markdown(f"<div style='text-align:center;margin-bottom:18px;'>{logo_html(140)}</div>",unsafe_allow_html=True)
        st.markdown(f"""<div class="paywall-box">
            <div style="font-size:2.2rem;margin-bottom:8px;">🔒</div>
            <div style="font-family:Fraunces,serif;font-size:1.7rem;font-weight:800;color:#1c1917;margin-bottom:8px;">Activate Subscription</div>
            <p style="color:#57534e;font-size:0.9rem;line-height:1.6;margin-bottom:20px;">
                Hello <strong>{u['name']}</strong>! As a <strong>{role}</strong>,
                a monthly subscription is required to access ITARA.<br><br>
                Your plan: <strong>{role}</strong> — <strong>{price} RWF / month</strong>
            </p>
            <div class="mtn-badge">📱 MTN Mobile Money Rwanda</div>
        </div>""",unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**📲 How to Pay via MTN MoMo**")
        st.info(f"""
**Step 1:** Dial `*182*8*1*0788ITARA01*{price.replace(',','')}#` on your MTN line  
**Step 2:** Use merchant code: **ITARA2025**  
**Step 3:** Confirm on your phone and wait for the confirmation SMS  
**Step 4:** Enter your MTN number and transaction reference below
        """)
        with st.form("mtn"):
            mtn=st.text_input("MTN Number",placeholder="e.g. 0788123456")
            ref=st.text_input("Transaction Reference",placeholder="e.g. TXN-2025-XXXXXX")
            if st.form_submit_button("✅ Verify & Activate Access",use_container_width=True):
                if mtn and ref:
                    exp=(datetime.datetime.now()+datetime.timedelta(days=30)).strftime("%Y-%m-%d")
                    st.session_state.user['subscribed']=True
                    st.session_state.user['sub_expires']=exp
                    st.session_state.users_db[u['email']]['subscribed']=True
                    st.session_state.users_db[u['email']]['sub_expires']=exp
                    st.success("🎉 Payment verified! Opening your dashboard...")
                    st.session_state.page='app'; st.rerun()
                else:
                    st.error("Enter your MTN number and transaction reference.")
        st.caption("💡 Demo: use any number e.g. '0788000000' / ref 'DEMO-2025'")
        if st.button("← Sign Out"):
            st.session_state.logged_in=False; st.session_state.user=None
            st.session_state.page='home'; st.rerun()

# ═══════════════════════════════════════════════
# PAGE: MAIN APP
# ═══════════════════════════════════════════════
def pg_app():
    u=st.session_state.user; role=u['role']

    # Sidebar
    with st.sidebar:
        st.markdown(f"<div style='text-align:center;padding:6px 0 4px;'>{logo_html(120)}</div>",unsafe_allow_html=True)
        st.markdown(f"""<div style='text-align:center;padding-bottom:12px;border-bottom:1px solid #2c2825;'>
            <div style='color:#d6d3d1;font-size:0.85rem;font-weight:600;margin-top:6px;'>{u['name']}</div>
            <div style='margin-top:4px;'>{role_badge_html(role)}</div>
            {'<div style="color:#78716c;font-size:0.72rem;margin-top:3px;">'+str(u.get('team',''))+'</div>' if u.get('team') else ''}
        </div>""",unsafe_allow_html=True)

        # Season selector
        season=st.selectbox("📅 Season",
            ['All Seasons']+st.session_state.seasons,
            index=(['All Seasons']+st.session_state.seasons).index(
                st.session_state.selected_season)
                if st.session_state.selected_season in ['All Seasons']+st.session_state.seasons else 0)
        st.session_state.selected_season=season

        # Role-based nav
        if role=='Team Manager':
            opts=["🏠 Dashboard","📊 Data Management","🏆 League Table",
                  "🧠 Coach Decision Center","🏥 Health Reports","📤 Export Center"]
        elif role in ['Football Agent','Scout']:
            opts=["🏠 Dashboard","🏆 League Table","⚖️ Player Comparison",
                  "🤖 Agent Intelligence","📤 Export Center"]
        else:
            opts=["🏠 Dashboard","📊 Data Management","🏆 League Table","⚖️ Player Comparison",
                  "🧠 Coach Decision Center","🏥 Health Reports","🤖 Agent Intelligence","📤 Export Center"]

        nav=st.selectbox("Navigation",opts)
        st.markdown("---")
        st.metric("Players",len(st.session_state.data))
        st.metric("Teams",len(st.session_state.teams))
        st.metric("Matches",len(st.session_state.match_results))
        st.caption(f"Sub expires: {u.get('sub_expires','N/A')}")
        st.markdown("---")
        if st.button("🚪 Sign Out"):
            st.session_state.logged_in=False; st.session_state.user=None
            st.session_state.page='home'; st.rerun()
        st.caption("ITARA · African Football Intelligence · 🇷🇼")

    df_all=season_data(u,season)

    # ── DASHBOARD ──
    if nav=="🏠 Dashboard":
        st.markdown(f"""<div class='hero-banner'>
            <div class='hero-title'>African Football Intelligence{(' — '+u['team']) if u.get('team') else ''}</div>
            <div class='hero-sub'>{u['name']} · {role} · Season {season}</div>
        </div>""",unsafe_allow_html=True)
        if not df_all.empty:
            df=df_all.copy()
            df['CPR']=df.apply(cpr,axis=1); df['MV']=df.apply(market_val,axis=1)
            df['xG_v']=df.apply(xG,axis=1); df['Form']=df['Performance_Index'].apply(form_label)
            c1,c2,c3,c4,c5=st.columns(5)
            c1.metric("⚽ Goals",int(df['Goals'].sum()))
            c2.metric("🎯 Avg CPR",f"{df['CPR'].mean():.2f}")
            c3.metric("📈 Avg xG",f"{df['xG_v'].mean():.2f}")
            c4.metric("💰 Top Value",f"{df['MV'].max():,.0f}")
            c5.metric("❤️ Avg Fitness",f"{df['Health_Score'].mean():.0f}%")
            st.markdown("---")
            t1,t2,t3=st.tabs(["📊 Visuals","🌐 Radar","📋 Squad"])
            with t1:
                col1,col2=st.columns(2)
                with col1:
                    fig=px.bar(df.sort_values('CPR',ascending=False).head(10),x='Player',y='CPR',
                               color='Team',title='Top 10 by CPR',color_discrete_sequence=CL)
                    fig.update_layout(**PL); st.plotly_chart(fig,use_container_width=True)
                with col2:
                    fig2=px.scatter(df,x='Performance_Index',y='MV',color='Form',size='Matches',
                                    hover_data=['Player','Team'],title='Market Value vs PI',
                                    color_discrete_map=FC)
                    fig2.update_layout(**PL); st.plotly_chart(fig2,use_container_width=True)
                col3,col4=st.columns(2)
                with col3:
                    fig3=px.bar(df.groupby('Team')[['Goals','Assists']].sum().reset_index(),
                                x='Team',y=['Goals','Assists'],barmode='group',
                                title='Goals & Assists by Team',color_discrete_sequence=['#d97757','#b85e3a'])
                    fig3.update_layout(**PL); st.plotly_chart(fig3,use_container_width=True)
                with col4:
                    fig4=px.histogram(df,x='Health_Score',nbins=10,color='Team',
                                      title='Fitness Distribution',color_discrete_sequence=CL)
                    fig4.update_layout(**PL); st.plotly_chart(fig4,use_container_width=True)
            with t2:
                sel=st.selectbox("Player for radar",df['Player'].unique())
                p=df[df['Player']==sel].iloc[0]; m=max(p.get('Matches',1),1)
                cats=['Scoring','Creativity','Passing','Physical','Fitness','Overall']
                vals=[min(p.get('Goals',0)/m*10,10),min(p.get('Assists',0)/m*10,10),
                      p.get('Pass_Accuracy',75)/10,prog(p),p.get('Health_Score',100)/10,
                      p.get('Performance_Index',5)]
                fig_r=go.Figure(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],
                    fill='toself',fillcolor='rgba(217,119,87,0.18)',
                    line=dict(color='#d97757',width=2),name=sel))
                fig_r.update_layout(polar=dict(bgcolor='#faf7f2',
                    radialaxis=dict(visible=True,range=[0,10],color='#57534e',gridcolor='#e7e0d5'),
                    angularaxis=dict(color='#1c1917',gridcolor='#e7e0d5')),
                    paper_bgcolor='#faf7f2',font_color='#1c1917',
                    title=dict(text=f"Radar — {sel}",font_size=14),showlegend=False,height=420)
                st.plotly_chart(fig_r,use_container_width=True)
            with t3:
                d=df[['Player','Team','Position','Age','Goals','Assists','Matches',
                       'CPR','Performance_Index','Form','Health_Score']].copy()
                d.columns=['Player','Team','Pos','Age','G','A','MP','CPR','PI','Form','Fit%']
                st.dataframe(d.style.background_gradient(subset=['CPR','PI'],cmap='Oranges'),
                             use_container_width=True)
        else:
            st.info("No data for this season. Add players in Data Management.")

    # ── DATA MANAGEMENT ──
    elif nav=="📊 Data Management":
        st.subheader("📊 Data Management")
        tb1,tb2,tb3=st.tabs(["📂 Upload Excel","✏️ Manual Entry","⚽ Log Match"])
        with tb1:
            uf=st.file_uploader("Upload Scout Excel (.xlsx)",type=["xlsx"])
            if uf:
                udf=pd.read_excel(uf)
                for col,dfl in [('Position','MF'),('Age',24),('Minutes_Played',0),
                                 ('Shots_on_Target',0),('Pass_Accuracy',75),
                                 ('Dribbles_Completed',0),('Tackles_Won',0),('Season',season)]:
                    if col not in udf.columns: udf[col]=dfl
                st.session_state.data=pd.concat(
                    [st.session_state.data,udf],ignore_index=True
                ).drop_duplicates(subset=['Player','Team','Season'])
                st.success(f"✅ {len(udf)} records merged!")
                st.dataframe(udf.head(),use_container_width=True)
        with tb2:
            cl,cr=st.columns([1,2])
            with cl:
                st.markdown("**Register Team**")
                nt=st.text_input("Team Name")
                if st.button("➕ Add") and nt:
                    if nt not in st.session_state.teams:
                        st.session_state.teams.append(nt); st.success(f"'{nt}' added!"); st.rerun()
                for t in st.session_state.teams: st.markdown(f"• {t}")
            with cr:
                with st.form("pf"):
                    rc=st.columns(2)
                    pn=rc[0].text_input("Player Name"); pt=rc[1].selectbox("Team",st.session_state.teams)
                    rc2=st.columns(3)
                    pp=rc2[0].selectbox("Position",["GK","CB","LB","RB","CDM","CM","CAM","LW","RW","ST"])
                    pa=rc2[1].number_input("Age",15,45,24); pm=rc2[2].number_input("Matches",1,100,10)
                    rc3=st.columns(3)
                    pg_=rc3[0].number_input("Goals",0,100,0); pas=rc3[1].number_input("Assists",0,100,0)
                    pmin=rc3[2].number_input("Minutes",0,9000,900)
                    rc4=st.columns(3)
                    psh=rc4[0].number_input("Shots on Target",0,200,5)
                    ppa=rc4[1].number_input("Pass Acc%",0,100,75)
                    pdr=rc4[2].number_input("Dribbles",0,300,10)
                    rc5=st.columns(3)
                    ptk=rc5[0].number_input("Tackles",0,300,10)
                    ppi=rc5[1].slider("PI",0.0,10.0,5.0,0.1)
                    phs=rc5[2].slider("Fitness%",0,100,100)
                    if st.form_submit_button("💾 Save Player"):
                        if pn:
                            st.session_state.data=pd.concat([st.session_state.data,
                                pd.DataFrame([{'Player':pn,'Team':pt,'Position':pp,'Age':pa,
                                    'Goals':pg_,'Assists':pas,'Matches':pm,'Minutes_Played':pmin,
                                    'Shots_on_Target':psh,'Pass_Accuracy':ppa,'Dribbles_Completed':pdr,
                                    'Tackles_Won':ptk,'Health_Score':phs,'Performance_Index':ppi,
                                    'Season':season}])],ignore_index=True)
                            st.success(f"✅ {pn} saved!")
                        else: st.error("Name required.")
        with tb3:
            with st.form("mf"):
                mc=st.columns(3)
                hm=mc[0].selectbox("Home",st.session_state.teams,key="hm")
                md=mc[1].number_input("Matchday",1,50,1)
                aw=mc[2].selectbox("Away",st.session_state.teams,key="aw")
                sc=st.columns(2)
                hg=sc[0].number_input("Home Goals",0,20,0)
                ag=sc[1].number_input("Away Goals",0,20,0)
                if st.form_submit_button("📝 Log Result"):
                    if hm!=aw:
                        st.session_state.match_results=pd.concat([st.session_state.match_results,
                            pd.DataFrame([{'Home_Team':hm,'Away_Team':aw,'Home_Goals':hg,
                                'Away_Goals':ag,'Matchday':md,'Season':season}])],ignore_index=True)
                        st.success(f"✅ {hm} {hg}–{ag} {aw} logged!")
                    else: st.error("Teams must differ.")
            if not st.session_state.match_results.empty:
                st.dataframe(st.session_state.match_results,use_container_width=True)

    # ── LEAGUE TABLE ──
    elif nav=="🏆 League Table":
        st.subheader("🏆 League Standings — FIFA/UEFA Points System")
        mr=st.session_state.match_results.copy()
        if season!='All Seasons' and 'Season' in mr.columns: mr=mr[mr['Season']==season]
        if not mr.empty:
            ldf=league_table(mr,st.session_state.teams)
            st.markdown("**W=3 · D=1 · L=0 · Sorted by Pts → GD → GF**")
            def slt(df):
                return df.style.apply(lambda r:[
                    'background-color:#fff3ee;color:#d97757;font-weight:bold' if r.name==1
                    else 'background-color:#fff5f5;color:#ef4444' if r.name>=len(df)-1
                    else '' for _ in r],axis=1)
            st.dataframe(slt(ldf),use_container_width=True,height=280)
            c1,c2=st.columns(2)
            with c1:
                fig=px.bar(ldf.reset_index(),x='Club',y='Pts',color='Pts',
                           color_continuous_scale='Oranges',title='Points by Club',text='Pts')
                fig.update_traces(textposition='outside'); fig.update_layout(**PL,showlegend=False)
                st.plotly_chart(fig,use_container_width=True)
            with c2:
                fig2=px.bar(ldf.reset_index(),x='Club',y='GD',color='GD',
                            color_continuous_scale='RdYlGn',title='Goal Difference',text='GD')
                fig2.update_traces(textposition='outside'); fig2.update_layout(**PL,showlegend=False)
                st.plotly_chart(fig2,use_container_width=True)
            st.markdown("**📅 Results Log**")
            st.dataframe(mr,use_container_width=True)
        else:
            st.info("No match results yet. Log results in Data Management.")

    # ── PLAYER COMPARISON ──
    elif nav=="⚖️ Player Comparison":
        st.subheader("⚖️ Head-to-Head Player Comparison")
        if len(df_all)>=2:
            df=df_all.copy()
            df['CPR']=df.apply(cpr,axis=1); df['xG_v']=df.apply(xG,axis=1)
            df['xA_v']=df.apply(xA,axis=1); df['MV']=df.apply(market_val,axis=1)
            df['Form']=df['Performance_Index'].apply(form_label)
            col1,col2=st.columns(2)
            p1n=col1.selectbox("Player A",df['Player'].unique(),key='p1')
            p2n=col2.selectbox("Player B",[p for p in df['Player'].unique() if p!=p1n],key='p2')
            p1=df[df['Player']==p1n].iloc[0]; p2=df[df['Player']==p2n].iloc[0]
            st.markdown("---")
            metrics=[('CPR','CPR',2),('Performance Index','Performance_Index',1),
                     ('xG','xG_v',2),('xA','xA_v',2),('Goals','Goals',0),('Assists','Assists',0),
                     ('Matches','Matches',0),('Pass Accuracy%','Pass_Accuracy',1),
                     ('Fitness%','Health_Score',0),('Market Value RWF','MV',0)]
            c1,cm,c3=st.columns([2,1,2])
            cm.markdown("<div style='text-align:center;padding-top:32px;color:#d97757;font-family:Fraunces,serif;font-size:1.4rem;font-weight:800;'>VS</div>",unsafe_allow_html=True)
            for lbl,fld,dec in metrics:
                v1,v2=float(p1.get(fld,0)),float(p2.get(fld,0))
                fmt=f"{{:,.{dec}f}}"
                c1.metric(lbl,fmt.format(v1),f"{'+' if v1-v2>0 else ''}{fmt.format(round(v1-v2,dec))} vs {p2n}")
                c3.metric(lbl,fmt.format(v2),f"{'+' if v2-v1>0 else ''}{fmt.format(round(v2-v1,dec))} vs {p1n}")
            st.markdown("---")
            def rv(p):
                m=max(p.get('Matches',1),1)
                return [round(min(p.get('Goals',0)/m*10,10),2),round(min(p.get('Assists',0)/m*10,10),2),
                        round(p.get('Pass_Accuracy',75)/10,2),round(prog(p),2),
                        round(p.get('Health_Score',100)/10,2),round(p.get('Performance_Index',5),2)]
            cats=['Scoring','Creativity','Passing','Physical','Fitness','Overall']
            fig_c=go.Figure()
            for vals,name,clr in [(rv(p1),p1n,'#d97757'),(rv(p2),p2n,'#57534e')]:
                fig_c.add_trace(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],
                    fill='toself',name=name,line=dict(color=clr,width=2),fillcolor=clr+'26'))
            fig_c.update_layout(polar=dict(bgcolor='#faf7f2',
                radialaxis=dict(visible=True,range=[0,10],color='#57534e',gridcolor='#e7e0d5'),
                angularaxis=dict(color='#1c1917',gridcolor='#e7e0d5')),
                paper_bgcolor='#faf7f2',font_color='#1c1917',
                title=dict(text=f"{p1n} vs {p2n}",font_size=14),height=420,
                legend=dict(bgcolor='#faf7f2',bordercolor='#e7e0d5',borderwidth=1))
            st.plotly_chart(fig_c,use_container_width=True)
            st.markdown("---")
            cpr1,cpr2=float(p1['CPR']),float(p2['CPR'])
            if cpr1>cpr2: st.success(f"**ITARA Verdict:** {p1n} leads by **{round(cpr1-cpr2,2)} CPR points**.")
            elif cpr2>cpr1: st.success(f"**ITARA Verdict:** {p2n} leads by **{round(cpr2-cpr1,2)} CPR points**.")
            else: st.info("Both players rated equally.")
        else:
            st.warning("Add at least 2 players to use comparison.")

    # ── COACH DECISION CENTER ──
    elif nav=="🧠 Coach Decision Center":
        st.subheader("🧠 Coach Decision Center")
        if not df_all.empty:
            df=df_all.copy()
            df['CPR']=df.apply(cpr,axis=1); df['Form']=df['Performance_Index'].apply(form_label)
            df['Availability']=df['Health_Score'].apply(avail)
            tb1,tb2,tb3=st.tabs(["📋 Starting XI","📉 Risk Analysis","📊 Position Reports"])
            with tb1:
                c1,c2=st.columns(2)
                mf=c1.slider("Min Fitness%",0,100,70); mc=c2.slider("Min CPR",0.0,10.0,4.0,0.1)
                elig=df[(df['Health_Score']>=mf)&(df['CPR']>=mc)].sort_values('CPR',ascending=False)
                st.markdown(f"**{len(elig)} eligible players**")
                if not elig.empty:
                    st.dataframe(elig[['Player','Team','Position','CPR','Performance_Index',
                                       'Goals','Assists','Health_Score','Form','Availability']
                                      ].style.background_gradient(subset=['CPR'],cmap='Oranges'),
                                 use_container_width=True)
                    st.markdown("---"); st.markdown("**🤖 Auto-Select Best XI**")
                    xi=elig.head(11).reset_index(drop=True); xi.index+=1; xi.index.name='#'
                    st.dataframe(xi[['Player','Team','Position','CPR','Form','Availability']],use_container_width=True)
                    ac=xi['CPR'].mean(); af=xi['Health_Score'].mean()
                    st.success(f"Avg CPR {ac:.2f} | Avg Fitness {af:.0f}% | {'Strong ✅' if ac>=6 else 'Developing ⚠️'}")
            with tb2:
                risk=df.copy()
                risk['Risk']=risk.apply(lambda r:
                    "🔴 HIGH" if r['Health_Score']<50 or r['Performance_Index']<3 else
                    "🟠 MEDIUM" if r['Health_Score']<70 or r['Performance_Index']<5 else "🟢 LOW",axis=1)
                st.dataframe(risk[['Player','Team','Position','Health_Score','Performance_Index','CPR','Risk','Availability']].sort_values('Health_Score'),use_container_width=True)
                rc2=risk['Risk'].value_counts().reset_index(); rc2.columns=['Risk','Count']
                fig_r=px.pie(rc2,names='Risk',values='Count',title='Risk Distribution',
                             color_discrete_sequence=['#d97757','#f59e0b','#22c55e'])
                fig_r.update_layout(**PL); st.plotly_chart(fig_r,use_container_width=True)
            with tb3:
                if 'Position' in df.columns:
                    pr=df.groupby('Position').agg(Players=('Player','count'),Avg_CPR=('CPR','mean'),
                        Avg_Fitness=('Health_Score','mean'),Total_Goals=('Goals','sum'),
                        Total_Assists=('Assists','sum')).round(2).reset_index()
                    st.dataframe(pr,use_container_width=True)
                    fig_p=px.bar(pr,x='Position',y='Avg_CPR',color='Avg_Fitness',
                                 color_continuous_scale='RdYlGn',title='Avg CPR by Position',text='Avg_CPR')
                    fig_p.update_traces(textposition='outside'); fig_p.update_layout(**PL)
                    st.plotly_chart(fig_p,use_container_width=True)
        else:
            st.warning("No data for this season.")

    # ── HEALTH REPORTS ──
    elif nav=="🏥 Health Reports":
        st.subheader("🏥 Health & Fitness Monitor")
        if not df_all.empty:
            df=df_all.copy()
            c1,c2=st.columns([1,3])
            sel=c1.selectbox("Select Player",df['Player'].unique())
            pd_=df[df['Player']==sel].iloc[0]
            with c2:
                cc=st.columns(4)
                cc[0].metric("Fitness",f"{pd_['Health_Score']}%")
                cc[1].metric("PI",f"{pd_['Performance_Index']:.1f}/10")
                cc[2].metric("Matches",int(pd_.get('Matches',0)))
                cc[3].metric("Minutes",int(pd_.get('Minutes_Played',0)))
            s=avail(pd_['Health_Score'])
            if pd_['Health_Score']>=85: st.success(f"**Status:** {s}")
            elif pd_['Health_Score']>=70: st.warning(f"**Status:** {s}")
            else: st.error(f"**Status:** {s}")
            st.progress(int(pd_['Health_Score'])/100)
            st.markdown("---")
            hdf=df[['Player','Team','Health_Score','Matches']].copy()
            hdf['Status']=hdf['Health_Score'].apply(avail)
            hdf=hdf.sort_values('Health_Score',ascending=False)
            fig_h=px.bar(hdf,x='Player',y='Health_Score',color='Health_Score',
                         color_continuous_scale='RdYlGn',title='Squad Fitness',text='Health_Score')
            fig_h.update_traces(textposition='outside')
            fig_h.add_hline(y=70,line_dash='dash',line_color='orange',annotation_text='70% Threshold')
            fig_h.add_hline(y=85,line_dash='dash',line_color='green',annotation_text='85% Match Ready')
            fig_h.update_layout(**PL); st.plotly_chart(fig_h,use_container_width=True)
            st.dataframe(hdf,use_container_width=True)
        else:
            st.warning("No data available.")

    # ── AGENT INTELLIGENCE ──
    elif nav=="🤖 Agent Intelligence":
        st.subheader("🤖 Agent Intelligence — Valuation & Prediction")
        if not df_all.empty:
            df=df_all.copy()
            df['CPR']=df.apply(cpr,axis=1); df['xG_v']=df.apply(xG,axis=1)
            df['xA_v']=df.apply(xA,axis=1); df['MV']=df.apply(market_val,axis=1)
            df['Form']=df['Performance_Index'].apply(form_label)
            df['Potential']=(df['Performance_Index']*1.12).clip(upper=10.0).round(2)
            df['Prog']=df.apply(prog,axis=1)
            st.caption("CPR, P2V, xG/xA — ITARA proprietary algorithms.")
            st.dataframe(df[['Player','Team','Position','Age','CPR','Form','Performance_Index',
                              'Potential','xG_v','xA_v','Prog','MV']
                             ].style.background_gradient(subset=['CPR','MV'],cmap='Oranges'),
                         use_container_width=True)
            st.markdown("---")
            c1,c2=st.columns(2)
            with c1:
                fig_v=px.bar(df.sort_values('MV',ascending=False).head(10),
                             x='Player',y='MV',color='Team',title='Top 10 Market Values (RWF)',
                             color_discrete_sequence=CL)
                fig_v.update_layout(**PL); st.plotly_chart(fig_v,use_container_width=True)
            with c2:
                fig_p=px.scatter(df,x='Performance_Index',y='Potential',color='Form',
                                 size='CPR',hover_data=['Player','Team'],
                                 title='Current PI vs Potential',color_discrete_map=FC)
                fig_p.update_layout(**PL); st.plotly_chart(fig_p,use_container_width=True)
        else:
            st.warning("No data available.")

    # ── EXPORT CENTER ──
    elif nav=="📤 Export Center":
        st.subheader("📤 Export Center")
        st.markdown(f"Reports for **{role}** · Season **{season}**")
        if not df_all.empty:
            df=df_all.copy()
            mr=st.session_state.match_results.copy()
            if season!='All Seasons' and 'Season' in mr.columns: mr=mr[mr['Season']==season]
            ldf=league_table(mr,st.session_state.teams).reset_index() if not mr.empty else None
            col1,col2,col3=st.columns(3)
            sfx=season.replace('/','_')
            if role=='Team Manager':
                pdf=make_pdf_manager(df,u.get('team'),season,ldf)
                col1.download_button("📄 Team PDF Report",pdf,f"ITARA_{u.get('team','Team')}_{sfx}.pdf",mime="application/pdf")
                col1.caption("Full team intelligence brief.")
            elif role in ['Football Agent','Scout']:
                pdf=make_pdf_agent(df,season)
                col1.download_button("📄 Scouting PDF",pdf,f"ITARA_Scouting_{sfx}.pdf",mime="application/pdf")
                col1.caption("League-wide scouting report.")
            else:
                pdf=make_pdf_admin(df,season,ldf,mr if not mr.empty else None)
                col1.download_button("📄 Admin PDF",pdf,f"ITARA_Admin_{sfx}.pdf",mime="application/pdf")
                col1.caption("Full platform admin report.")
            excel=io.BytesIO()
            with pd.ExcelWriter(excel,engine='openpyxl') as w:
                df.to_excel(w,sheet_name='Players',index=False)
                if ldf is not None: ldf.to_excel(w,sheet_name='League Table',index=False)
                if not mr.empty: mr.to_excel(w,sheet_name='Match Results',index=False)
            col2.download_button("📥 Excel Workbook",excel.getvalue(),
                f"ITARA_Data_{sfx}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            col2.caption("Multi-sheet Excel file.")
            col3.download_button("📊 CSV Export",df.to_csv(index=False).encode(),
                f"ITARA_Players_{sfx}.csv",mime="text/csv")
            col3.caption("Raw player data.")
            st.markdown("---"); st.markdown("**📋 Preview**")
            df['CPR']=df.apply(cpr,axis=1); df['Form']=df['Performance_Index'].apply(form_label)
            df['MV']=df.apply(market_val,axis=1)
            st.dataframe(df[['Player','Team','Position','CPR','Performance_Index','Form','Health_Score','MV']],
                         use_container_width=True)
        else:
            st.error("No data for this season.")

# ═══════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════
pg=st.session_state.page
if pg=='home': pg_home()
elif pg=='auth': pg_auth()
elif pg=='subscribe':
    if st.session_state.logged_in and st.session_state.user: pg_subscribe()
    else: st.session_state.page='home'; st.rerun()
elif pg=='app':
    if st.session_state.logged_in and st.session_state.user and subscribed(st.session_state.user):
        pg_app()
    elif st.session_state.logged_in and st.session_state.user:
        st.session_state.page='subscribe'; st.rerun()
    else:
        st.session_state.page='home'; st.rerun()
else:
    st.session_state.page='home'; st.rerun()
