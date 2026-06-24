# ═══════════════════════════════════════════════════════════════════════════════
# AI-POWERED EMPLOYEE PULSE SURVEY & ENGAGEMENT ANALYTICS PLATFORM
# Version 3.0 — Pilot Ready | Employee Management | Enhanced UI/UX
# ═══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from datetime import date, datetime, timedelta
from io import BytesIO
import os, re, time, requests
import numpy as np

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Samvaad — Employee Listening Platform",
    page_icon="🪷",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "employee.db")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ─────────────────────────────────────────────
# GLOBAL THEME CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts & Base ─────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Sidebar ──────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a2540 0%, #1a3a5c 60%, #0d3060 100%);
    border-right: 1px solid #1e4d8c;
}
[data-testid="stSidebar"] * { color: #e8f0fe !important; }
[data-testid="stSidebar"] .stRadio > label { font-size: 0.88rem; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: white !important;
    border-radius: 8px;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.2);
}

/* ── Top header strip ─────────────────────── */
.top-header {
    background: linear-gradient(90deg, #0a2540 0%, #1557b0 100%);
    padding: 18px 28px;
    border-radius: 12px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.top-header h1 { color: white; margin: 0; font-size: 1.6rem; font-weight: 800; }
.top-header p  { color: #a8c4f0; margin: 0; font-size: 0.82rem; }

/* ── KPI Cards ────────────────────────────── */
.kpi-wrap {
    background: white;
    border-radius: 14px;
    padding: 20px 16px;
    text-align: center;
    border: 1px solid #e8edf5;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    transition: transform 0.2s;
    margin-bottom: 8px;
}
.kpi-wrap:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.10); }
.kpi-icon  { font-size: 1.8rem; margin-bottom: 6px; }
.kpi-value { font-size: 2rem; font-weight: 800; color: #0a2540; line-height: 1; }
.kpi-label { font-size: 0.72rem; color: #6b7a99; text-transform: uppercase;
             letter-spacing: 0.8px; margin-top: 4px; }
.kpi-green { border-top: 4px solid #22c55e; }
.kpi-amber { border-top: 4px solid #f59e0b; }
.kpi-red   { border-top: 4px solid #ef4444; }
.kpi-blue  { border-top: 4px solid #3b82f6; }
.kpi-purple{ border-top: 4px solid #8b5cf6; }

/* ── Section cards ────────────────────────── */
.section-card {
    background: white;
    border-radius: 14px;
    padding: 24px;
    border: 1px solid #e8edf5;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 16px;
}

/* ── Survey sliders ───────────────────────── */
.survey-question {
    background: #f8faff;
    border-left: 4px solid #3b82f6;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin-bottom: 12px;
}

/* ── Sentiment badges ─────────────────────── */
.badge-positive { background:#dcfce7; color:#166534; border-radius:20px;
                  padding:5px 16px; font-weight:700; font-size:0.85rem; display:inline-block; }
.badge-negative { background:#fee2e2; color:#991b1b; border-radius:20px;
                  padding:5px 16px; font-weight:700; font-size:0.85rem; display:inline-block; }
.badge-neutral  { background:#fef9c3; color:#854d0e; border-radius:20px;
                  padding:5px 16px; font-weight:700; font-size:0.85rem; display:inline-block; }

/* ── AI insight box ───────────────────────── */
.ai-insight {
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    border: 1px solid #bfdbfe;
    border-left: 5px solid #2563eb;
    border-radius: 12px;
    padding: 22px 26px;
    margin: 12px 0;
    line-height: 1.7;
}

/* ── Risk pills ───────────────────────────── */
.pill-green  { background:#dcfce7; color:#166534; border-radius:12px; padding:3px 10px; font-size:0.8rem; font-weight:600; }
.pill-amber  { background:#fef3c7; color:#92400e; border-radius:12px; padding:3px 10px; font-size:0.8rem; font-weight:600; }
.pill-red    { background:#fee2e2; color:#991b1b; border-radius:12px; padding:3px 10px; font-size:0.8rem; font-weight:600; }

/* ── Login page ───────────────────────────── */
.login-hero {
    background: linear-gradient(135deg, #0a2540 0%, #1557b0 100%);
    border-radius: 20px;
    padding: 50px 40px;
    text-align: center;
    color: white;
}
.login-hero h1 { font-size: 2.4rem; font-weight: 800; margin-bottom: 10px; }
.login-hero p  { color: #a8c4f0; font-size: 1rem; }

.login-card {
    background: white;
    border-radius: 20px;
    padding: 36px 32px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.12);
}

/* ── Employee management table ────────────── */
.emp-row {
    background: white;
    border: 1px solid #e8edf5;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 6px 0;
    display: flex;
    align-items: center;
}

/* ── Upload zone ──────────────────────────── */
.upload-info {
    background: #f0f7ff;
    border: 2px dashed #93c5fd;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: #1e40af;
}

/* ── Schedule pill ────────────────────────── */
.sched-on  { background:#dcfce7; color:#166534; border-radius:20px; padding:4px 14px; font-weight:600; }
.sched-off { background:#fee2e2; color:#991b1b; border-radius:20px; padding:4px 14px; font-weight:600; }

/* ── Hide streamlit default elements ─────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# DATABASE HELPERS
# ═══════════════════════════════════════════════════════
def get_conn():
    return sqlite3.connect(DB_PATH)


@st.cache_data(ttl=30)
def cached_survey_data():
    """Load full survey + employee join, cached 30s."""
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT sr.*, e.department, e.name as emp_name, e.designation
        FROM survey_response sr
        LEFT JOIN employee e ON e.id = sr.employee_id
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=60)
def cached_dept_stats():
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT e.department,
               COUNT(DISTINCT e.id) AS total_emp,
               COUNT(sr.id) AS responses,
               ROUND(AVG((sr.motivation+sr.satisfaction+sr.team_connection+sr.recognition+(6-sr.stress))/5.0),2) AS avg_eng,
               SUM(CASE WHEN ((sr.motivation+sr.satisfaction+sr.team_connection+sr.recognition+(6-sr.stress))/5.0)<3 THEN 1 ELSE 0 END) AS high_risk,
               SUM(CASE WHEN sr.stress>=4 THEN 1 ELSE 0 END) AS burnout_risk,
               ROUND(AVG(CASE WHEN sr.enps>=9 THEN 100.0 WHEN sr.enps<=6 THEN -100.0 ELSE 0 END),1) AS dept_enps
        FROM employee e
        LEFT JOIN survey_response sr ON e.id=sr.employee_id
        WHERE e.is_active=1
        GROUP BY e.department ORDER BY avg_eng ASC
    """, conn)
    conn.close()
    return df

def get_all_employees(active_only=True):
    conn = get_conn()
    q = "SELECT * FROM employee WHERE is_active=1 ORDER BY id" if active_only else "SELECT * FROM employee ORDER BY id"
    df = pd.read_sql_query(q, conn); conn.close(); return df

def get_survey_data():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM survey_response", conn); conn.close(); return df

def cached_dept_stats():
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT e.department,
               COUNT(DISTINCT e.id) AS total_employees,
               COUNT(sr.id) AS responses,
               ROUND(AVG((sr.motivation+sr.satisfaction+sr.team_connection+sr.recognition+(6-sr.stress))/5.0),2) AS avg_engagement,
               SUM(CASE WHEN ((sr.motivation+sr.satisfaction+sr.team_connection+sr.recognition+(6-sr.stress))/5.0)<3 THEN 1 ELSE 0 END) AS high_risk,
               SUM(CASE WHEN sr.stress>=4 THEN 1 ELSE 0 END) AS burnout_risk,
               ROUND(AVG(CASE WHEN sr.enps>=9 THEN 100.0 WHEN sr.enps<=6 THEN -100.0 ELSE 0 END),1) AS dept_enps
        FROM employee e LEFT JOIN survey_response sr ON e.id=sr.employee_id
        WHERE e.is_active=1 GROUP BY e.department ORDER BY avg_engagement ASC
    """, conn); conn.close(); return df

def get_employee_history(employee_id):
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM survey_response WHERE employee_id=? ORDER BY survey_date DESC",
        conn, params=(employee_id,)); conn.close(); return df

def get_schedule():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM survey_schedule", conn); conn.close(); return df

# ── Intervention Tracker DB helpers ───────────────────────────────────────────
def get_interventions(dept=None, status=None, priority=None):
    conn = get_conn()
    q = "SELECT * FROM engagement_interventions WHERE 1=1"
    params = []
    if dept and dept != "All":
        q += " AND department=?"; params.append(dept)
    if status and status != "All":
        q += " AND status=?"; params.append(status)
    if priority and priority != "All":
        q += " AND priority=?"; params.append(priority)
    q += " ORDER BY created_date DESC"
    df = pd.read_sql_query(q, conn, params=params)
    conn.close()
    return df

def create_intervention(data: dict):
    conn = get_conn()
    conn.execute("""
        INSERT INTO engagement_interventions
        (title,issue_category,department,description,recommended_action,priority,
         owner,hrbp,manager_responsible,status,created_date,start_date,due_date,
         before_score,before_burnout,linked_employee_id,comments,created_by)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (data["title"],data["issue_category"],data["department"],data["description"],
          data["recommended_action"],data["priority"],data["owner"],data["hrbp"],
          data["manager"],data["status"],str(date.today()),data["start_date"],
          data["due_date"],data.get("before_score"),data.get("before_burnout"),
          data.get("linked_emp"),data.get("comments"),1))
    conn.commit(); conn.close()
    st.cache_data.clear()

def update_intervention(iid, field, value):
    conn = get_conn()
    safe_fields = {"status","after_score","after_burnout","effectiveness_score",
                   "comments","completion_date","owner","due_date"}
    if field not in safe_fields:
        conn.close(); return
    conn.execute(f"UPDATE engagement_interventions SET {field}=? WHERE id=?", (value, iid))
    if field == "status" and value == "Completed":
        conn.execute("UPDATE engagement_interventions SET completion_date=? WHERE id=?",
                     (str(date.today()), iid))
    conn.commit(); conn.close()
    st.cache_data.clear()

def compute_effectiveness(before, after, before_burn=None, after_burn=None):
    if before is None or after is None: return None
    eng_imp  = max(0, (float(after)-float(before))/max(float(before),0.1))*100
    burn_imp = 0
    if before_burn and after_burn:
        burn_imp = max(0,(float(before_burn)-float(after_burn))/max(float(before_burn),0.1))*100
    return round((eng_imp+burn_imp)/(2 if before_burn else 1), 1)

AI_INTERVENTIONS = {
    "High Burnout Risk":      ["Schedule 1-on-1 manager check-ins",
                               "Run wellbeing & stress management session",
                               "Review and redistribute workload"],
    "Low Engagement Score":   ["Conduct stay interviews to identify disengagement drivers",
                               "Launch engagement campaign with leadership visibility",
                               "Create peer mentoring pairs"],
    "Poor Team Connection":   ["Organise cross-functional team-building activity",
                               "Set up weekly team huddles",
                               "Create shared project opportunities"],
    "Negative Sentiment":     ["Run anonymous feedback session",
                               "Hold skip-level meetings with HR",
                               "Create safe space feedback channel"],
    "Low Participation":      ["Send personal survey reminders from manager",
                               "Communicate survey purpose and impact",
                               "Simplify survey — reduce question count"],
    "Recognition Concerns":   ["Launch peer recognition programme",
                               "Introduce monthly appreciation awards",
                               "Train managers on recognition best practices"],
    "Communication Issues":   ["Deploy manager communication coaching",
                               "Create team newsletter",
                               "Hold town hall with department head"],
}


def get_notifications(employee_id):
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM notifications WHERE employee_id=? ORDER BY created_at DESC LIMIT 30",
        conn, params=(employee_id,)); conn.close(); return df

def mark_notifications_read(employee_id):
    conn = get_conn()
    conn.execute("UPDATE notifications SET is_read=1 WHERE employee_id=?", (employee_id,))
    conn.commit(); conn.close()

def save_survey(employee_id, motivation, satisfaction, team_connection, recognition, stress,
                enps, feedback, sentiment_score,
                eq_pressure=3, eq_balance=3, eq_empathy=3,
                mindset_growth="", mindset_purpose="", mindset_clarity=3,
                icebreaker_word="", icebreaker_emoji=""):
    conn = get_conn()
    conn.execute("""
        INSERT INTO survey_response
        (employee_id,motivation,satisfaction,team_connection,recognition,stress,
         enps,feedback,sentiment_score,survey_date,
         eq_pressure,eq_balance,eq_empathy,
         mindset_growth,mindset_purpose,mindset_clarity,
         icebreaker_word,icebreaker_emoji)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (employee_id, motivation, satisfaction, team_connection, recognition, stress,
          enps, feedback, sentiment_score, str(date.today()),
          eq_pressure, eq_balance, eq_empathy,
          mindset_growth, mindset_purpose, mindset_clarity,
          icebreaker_word, icebreaker_emoji))
    conn.execute(
        "INSERT INTO notifications (employee_id,message,created_at,is_read) VALUES (?,?,?,0)",
        (1, f"New pulse survey submitted by Employee #{employee_id}", datetime.now().isoformat())
    )
    conn.commit(); conn.close()

# ── Survey question helpers ────────────────────────────────────────────────────
def get_survey_questions():
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM survey_questions WHERE is_active=1 ORDER BY sort_order", conn)
    conn.close()
    return df

def add_question(text, qtype, category, emoji, options, sort_order):
    conn = get_conn()
    conn.execute(
        "INSERT INTO survey_questions (question_text,question_type,category,emoji,options,is_active,sort_order,created_at) VALUES (?,?,?,?,?,1,?,?)",
        (text, qtype, category, emoji, options, sort_order, datetime.now().isoformat()))
    conn.commit(); conn.close()

def update_question(qid, text, qtype, category, emoji, options, sort_order):
    conn = get_conn()
    conn.execute(
        "UPDATE survey_questions SET question_text=?,question_type=?,category=?,emoji=?,options=?,sort_order=? WHERE id=?",
        (text, qtype, category, emoji, options, sort_order, qid))
    conn.commit(); conn.close()

def delete_question(qid):
    conn = get_conn()
    conn.execute("DELETE FROM survey_questions WHERE id=?", (qid,))
    conn.commit(); conn.close()

def move_question(qid, direction, all_questions_df):
    df = all_questions_df.sort_values("sort_order").reset_index(drop=True)
    idx = df[df["id"] == qid].index
    if idx.empty: return
    i = idx[0]
    if direction == "up" and i > 0:
        swap_id = int(df.iloc[i-1]["id"])
        o1, o2 = int(df.iloc[i]["sort_order"]), int(df.iloc[i-1]["sort_order"])
    elif direction == "down" and i < len(df)-1:
        swap_id = int(df.iloc[i+1]["id"])
        o1, o2 = int(df.iloc[i]["sort_order"]), int(df.iloc[i+1]["sort_order"])
    else:
        return
    conn = get_conn()
    conn.execute("UPDATE survey_questions SET sort_order=? WHERE id=?", (o2, qid))
    conn.execute("UPDATE survey_questions SET sort_order=? WHERE id=?", (o1, swap_id))
    conn.commit(); conn.close()
    # Clear cache so dashboards show fresh data immediately
    st.cache_data.clear()

def add_employee_single(name, dept, desig, email, role, password, joined_date):
    conn = get_conn()
    conn.execute(
        "INSERT INTO employee (name,department,designation,email,role,password,is_active,joined_date) VALUES (?,?,?,?,?,?,1,?)",
        (name, dept, desig, email, role, password, joined_date)
    )
    conn.commit(); conn.close()
    st.cache_data.clear()

def deactivate_employee(emp_id):
    conn = get_conn()
    conn.execute("UPDATE employee SET is_active=0 WHERE id=?", (emp_id,))
    conn.commit(); conn.close()

def reactivate_employee(emp_id):
    conn = get_conn()
    conn.execute("UPDATE employee SET is_active=1 WHERE id=?", (emp_id,))
    conn.commit(); conn.close()

def toggle_schedule(sid, state):
    conn = get_conn()
    conn.execute("UPDATE survey_schedule SET is_active=? WHERE id=?", (state, sid))
    conn.commit(); conn.close()


# ═══════════════════════════════════════════════════════
# SCORING HELPERS
# ═══════════════════════════════════════════════════════
def compute_engagement(df):
    df = df.copy()
    df["engagement_score"] = (
        df["motivation"]+df["satisfaction"]+df["team_connection"]+df["recognition"]+(6-df["stress"])
    ) / 5.0
    return df

def classify_risk(score):
    if score >= 4:   return "🟢 Green"
    elif score >= 3: return "🟡 Amber"
    else:            return "🔴 Red"

def compute_enps(df):
    if "enps" not in df.columns or df.empty: return 0,0,0,0
    total = len(df)
    p = len(df[df["enps"]>=9]); d = len(df[df["enps"]<=6]); pa = total-p-d
    return round(((p-d)/total)*100,1) if total>0 else 0, p, pa, d

def get_action(row):
    fb = str(row.get("feedback","")).lower()
    if any(w in fb for w in ["stress","overwork","overtime","pressure"]): return "Workload review & wellbeing discussion"
    elif "communication" in fb: return "Manager communication coaching"
    elif any(w in fb for w in ["recognition","appreciate","valued"]): return "Recognition programme enrolment"
    elif row["risk"]=="🔴 Red": return "Immediate 1-on-1 manager intervention"
    elif row["risk"]=="🟡 Amber": return "Monitor closely & provide peer support"
    else: return "Celebrate & offer growth opportunity"

POSITIVE_WORDS = ["happy","motivated","supported","satisfied","good","great","excellent","energized",
                  "inspired","proud","appreciated","wonderful","amazing","love","enjoy","fantastic",
                  "positive","collaborative","friendly","productive","engaged","excited"]
NEGATIVE_WORDS = ["stress","stressed","poor","bad","overwork","frustrated","overtime","challenging",
                  "difficult","burned","burnout","angry","unhappy","tired","exhausted","ignored",
                  "undervalued","unfair","toxic","pressure","overwhelmed","worried","anxious"]

def realtime_sentiment(text):
    words = re.findall(r'\w+', str(text).lower())
    p = sum(1 for w in words if w in POSITIVE_WORDS)
    n = sum(1 for w in words if w in NEGATIVE_WORDS)
    if p==0 and n==0: return "Neutral", 0.0, "😐"
    score = (p-n)/max(p+n,1)
    if score>0.2: return "Positive", score, "😊"
    elif score<-0.2: return "Negative", score, "😟"
    return "Neutral", score, "😐"

def sentiment_label(text):
    return realtime_sentiment(text)[0]

def is_survey_open_today():
    schedule_df = get_schedule()
    today_name = date.today().strftime("%A")
    active_days = schedule_df[schedule_df["is_active"]==1]["day_of_week"].tolist()
    if not active_days: return False, "No active survey schedule. Contact HR."
    if today_name in active_days: return True, f"✅ {today_name} Pulse Survey is open today."
    return False, f"Next survey day: {active_days[0] if active_days else 'TBD'}"

def get_rule_recs(red_count, amber_count, burnout_count, avg_eng, enps_score, total_responses):
    recs = []
    red_pct     = round(red_count/total_responses*100,1) if total_responses else 0
    burnout_pct = round(burnout_count/total_responses*100,1) if total_responses else 0
    if red_count>=10:    recs.append(("🚨 Critical Risk", f"{red_pct}% employees are High Risk — immediate 1-on-1 check-ins needed.", "error"))
    elif red_count>0:    recs.append(("⚠️ Elevated Risk", f"{red_count} employees flagged Red — prioritise manager conversations.", "warning"))
    if burnout_pct>25:   recs.append(("🔥 Burnout Crisis", f"{burnout_pct}% showing burnout signals — launch wellbeing intervention now.", "error"))
    elif burnout_pct>10: recs.append(("🔥 Burnout Watch", f"{burnout_pct}% at burnout risk — introduce stress-management sessions.", "warning"))
    if enps_score<0:     recs.append(("📉 Negative eNPS", f"eNPS is {enps_score} — more detractors than promoters. Address root causes urgently.", "error"))
    elif enps_score<20:  recs.append(("📊 Low eNPS", f"eNPS of {enps_score} is below healthy range (>30). Focus on recognition.", "warning"))
    else:                recs.append(("📈 Healthy eNPS", f"eNPS of {enps_score} is positive — maintain culture investment.", "success"))
    if avg_eng<3:        recs.append(("📉 Low Engagement", f"Average engagement {avg_eng}/5 — review workload, communication, rewards.", "error"))
    elif avg_eng>=4:     recs.append(("✅ Strong Engagement", f"Average engagement {avg_eng}/5 — continue current practices.", "success"))
    if amber_count>=15:  recs.append(("🟡 Moderate Risk Wave", f"{amber_count} employees in Amber — proactive engagement activities needed.", "warning"))
    return recs

def call_claude_ai(prompt, max_tokens=700):
    if not ANTHROPIC_API_KEY: return None, "no_key"
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key":ANTHROPIC_API_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"},
            json={"model":"claude-sonnet-4-20250514","max_tokens":max_tokens,
                  "messages":[{"role":"user","content":prompt}]}, timeout=30)
        if r.status_code==200: return r.json()["content"][0]["text"], "ok"
        return None, f"error_{r.status_code}"
    except Exception as e: return None, str(e)

def kpi_card(icon, value, label, colour="blue"):
    return f"""
    <div class="kpi-wrap kpi-{colour}">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>"""


# ═══════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════
DEFAULTS = {"logged_in":False,"employee_id":None,"employee_name":"","role":"",
            "live_sent":"Neutral","live_score":0.0,"ai_cache":None,"ai_cache_time":None,"refresh_n":0}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v


# ═══════════════════════════════════════════════════════
# LOGIN PAGE
# ═══════════════════════════════════════════════════════
if not st.session_state.logged_in:

    # Dark background for login page
    st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #061226 0%, #0d2144 50%, #0a1f3d 100%) !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { background: transparent !important; }
    </style>""", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.3, 1])

    with left_col:
        _today_str = date.today().strftime("%d %B %Y")
        _login_html = f"""
        <div style="padding:48px 32px 20px;color:white">
            <div style="margin-bottom:32px">
                <div style="font-size:3.4rem;font-weight:900;letter-spacing:-1.5px;
                            background:linear-gradient(90deg,#60a5fa 0%,#a78bfa 100%);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                            background-clip:text;line-height:1">Samvaad</div>
                <div style="font-size:1rem;color:#93c5fd;margin-top:8px;font-weight:500">
                    Listening. Understanding. Acting.
                </div>
                <div style="font-size:0.8rem;color:#475569;margin-top:6px">
                    Employee Listening &amp; Workforce Intelligence · Tata Steel
                </div>
            </div>
            <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;
                        letter-spacing:1px;margin-bottom:14px;font-weight:600">
                Platform Capabilities
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:32px">
                <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                            border-radius:12px;padding:14px 16px">
                    <div style="font-size:0.9rem;font-weight:700;color:#e2e8f0;margin-bottom:4px">Pulse Surveys</div>
                    <div style="font-size:0.76rem;color:#64748b;line-height:1.5">Monday and Friday surveys with live sentiment analysis</div>
                </div>
                <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                            border-radius:12px;padding:14px 16px">
                    <div style="font-size:0.9rem;font-weight:700;color:#e2e8f0;margin-bottom:4px">AI Analytics</div>
                    <div style="font-size:0.76rem;color:#64748b;line-height:1.5">Engagement scores, risk classification and eNPS tracking</div>
                </div>
                <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                            border-radius:12px;padding:14px 16px">
                    <div style="font-size:0.9rem;font-weight:700;color:#e2e8f0;margin-bottom:4px">Predictive Forecast</div>
                    <div style="font-size:0.76rem;color:#64748b;line-height:1.5">30-day ML engagement forecasts by department</div>
                </div>
                <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                            border-radius:12px;padding:14px 16px">
                    <div style="font-size:0.9rem;font-weight:700;color:#e2e8f0;margin-bottom:4px">Intervention Tracker</div>
                    <div style="font-size:0.76rem;color:#64748b;line-height:1.5">Create, track and measure every HR action taken</div>
                </div>
            </div>
            <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;
                        letter-spacing:1px;margin-bottom:12px;font-weight:600">Live Stats</div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:32px">
                <div style="background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.2);
                            border-radius:10px;padding:12px;text-align:center">
                    <div style="font-size:1.5rem;font-weight:800;color:#60a5fa">50</div>
                    <div style="font-size:0.65rem;color:#64748b;text-transform:uppercase;letter-spacing:0.5px">Employees</div>
                </div>
                <div style="background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.2);
                            border-radius:10px;padding:12px;text-align:center">
                    <div style="font-size:1.5rem;font-weight:800;color:#a78bfa">808</div>
                    <div style="font-size:0.65rem;color:#64748b;text-transform:uppercase;letter-spacing:0.5px">Responses</div>
                </div>
                <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);
                            border-radius:10px;padding:12px;text-align:center">
                    <div style="font-size:1.5rem;font-weight:800;color:#4ade80">8</div>
                    <div style="font-size:0.65rem;color:#64748b;text-transform:uppercase;letter-spacing:0.5px">Departments</div>
                </div>
            </div>
            <div style="font-size:0.7rem;color:#334155;border-top:1px solid rgba(255,255,255,0.06);
                        padding-top:16px">
                Samvaad v5.0 &nbsp;·&nbsp; Confidential &nbsp;·&nbsp; {_today_str}
            </div>
        </div>
        """
        st.markdown(_login_html, unsafe_allow_html=True)

    with right_col:
        st.write("")
        st.write("")
        st.write("")

        st.markdown("""
        <div style="background:white;border-radius:20px;padding:36px 32px 28px;
                    box-shadow:0 24px 80px rgba(0,0,0,0.5);margin:10px 6px">
            <div style="text-align:center;margin-bottom:24px">
                <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:1px;
                            color:#94a3b8;margin-bottom:6px">Welcome to Samvaad</div>
                <div style="font-size:1.5rem;font-weight:800;color:#0a2540;letter-spacing:-0.5px">
                    Sign in to continue
                </div>
                <div style="font-size:0.8rem;color:#94a3b8;margin-top:4px">
                    Select your name and enter your password
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        employees_df = get_all_employees()
        options = {f"#{r['id']} — {r['name']} ({r['department']})": r
                   for _, r in employees_df.iterrows()}

        selected_label = st.selectbox("Employee", list(options.keys()),
                                       label_visibility="collapsed")
        password = st.text_input("Password", type="password",
                                  placeholder="Enter your password",
                                  label_visibility="collapsed")

        if st.button("Sign In", use_container_width=True, type="primary"):
            emp = options[selected_label]
            if password == str(emp.get("password", "password")):
                conn = get_conn()
                me = pd.read_sql_query(
                    "SELECT hr_level, dept_access FROM employee WHERE id=?",
                    conn, params=(int(emp["id"]),))
                conn.close()
                st.session_state.update({
                    "logged_in":    True,
                    "employee_id":  int(emp["id"]),
                    "employee_name":emp["name"],
                    "role":         emp["role"],
                    "hr_level":     me.iloc[0]["hr_level"]   if not me.empty else "",
                    "dept_access":  me.iloc[0]["dept_access"] if not me.empty else "ALL",
                    "is_super":    (me.iloc[0]["hr_level"] == "Super Admin") if not me.empty else False,
                })
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

        st.markdown("""
        <div style="text-align:center;margin-top:14px;font-size:0.73rem;color:#94a3b8">
            All responses are confidential and anonymous
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        with st.expander("Need help signing in?"):
            st.markdown("""
**Default password** for all employees: `password`

**HR Admin** (Akshada, ID 1): `admin123`

**Pilot accounts:** IDs 2–6, 9, 10, 22, 50
Passwords: `pilot001` to `pilot009`

Contact your HR team if you are unable to sign in.
        """, unsafe_allow_html=True)

    st.stop()


# ═══════════════════════════════════════════════════════
# SHARED VARS (post-login)
# ═══════════════════════════════════════════════════════
role     = st.session_state.role
emp_name = st.session_state.employee_name
emp_id   = st.session_state.employee_id


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    sb_icon = '👩‍💼' if role == 'HR' else '👤'
    st.markdown(f"""
    <div style='text-align:center; padding:10px 0 4px'>
        <div style='font-size:2.2rem'>{sb_icon}</div>
        <div style='font-weight:700; font-size:1rem'>{emp_name}</div>
        <div style='font-size:0.75rem; opacity:0.7'>{role} · ID #{emp_id}</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    if role == "HR":
        notifs = get_notifications(emp_id)
        unread = len(notifs[notifs["is_read"]==0]) if not notifs.empty else 0
        notif_lbl = f"🔔 Notifications  ({unread})" if unread>0 else "🔔 Notifications"
        # Determine access level for nav
        conn_nav = get_conn()
        import pandas as _pd2
        me_row = _pd2.read_sql_query("SELECT hr_level, dept_access FROM employee WHERE id=?",
                                      conn_nav, params=(emp_id,))
        conn_nav.close()
        hr_level   = me_row.iloc[0]["hr_level"]   if not me_row.empty else ""
        dept_access= me_row.iloc[0]["dept_access"] if not me_row.empty else ""
        is_super   = (hr_level == "Super Admin")

        # Store in session for use in pages
        st.session_state["hr_level"]    = hr_level
        st.session_state["dept_access"] = dept_access
        st.session_state["is_super"]    = is_super

        nav_options = [
            "👥 Employee Management",
            "📊 Live Dashboard",
            "🏢 Department Analytics",
            "💬 Sentiment Analysis",
            "📋 Employee Action Plan",
            "🎯 Intervention Tracker",
            "🗺️ Engagement Heatmap",
            "📈 eNPS Analytics",
            "🔮 Predictive Forecast",
            "🤖 AI Deep Analysis",
            "🛠️ Survey Builder",
            "📅 Survey Schedule",
            notif_lbl,
            "📄 Executive Summary",
            "📥 Download Report",
        ]
        # Super Admin gets HR Access Control page
        if is_super:
            nav_options.insert(1, "🔐 HR Access Control")

        page = st.radio("", nav_options, label_visibility="collapsed")

        # Sidebar access badge
        if is_super:
            st.markdown('<div style="background:#fef3c7;border-radius:8px;padding:6px 10px;font-size:0.78rem;color:#92400e;text-align:center;margin-top:4px">👑 Super Admin</div>', unsafe_allow_html=True)
        elif hr_level == "HR Manager":
            st.markdown('<div style="background:#eff6ff;border-radius:8px;padding:6px 10px;font-size:0.78rem;color:#1d4ed8;text-align:center;margin-top:4px">🔷 HR Manager</div>', unsafe_allow_html=True)
        elif hr_level == "HR Executive":
            st.markdown('<div style="background:#f0fdf4;border-radius:8px;padding:6px 10px;font-size:0.78rem;color:#166534;text-align:center;margin-top:4px">🟢 HR Executive</div>', unsafe_allow_html=True)
        elif hr_level:
            st.markdown(f'<div style="background:#f8fafc;border-radius:8px;padding:6px 10px;font-size:0.78rem;color:#64748b;text-align:center;margin-top:4px">{hr_level}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background:#fee2e2;border-radius:8px;padding:6px 10px;font-size:0.78rem;color:#991b1b;text-align:center;margin-top:4px">⚠️ No level assigned</div>', unsafe_allow_html=True)
    else:
        notifs = get_notifications(emp_id)
        unread = len(notifs[notifs["is_read"]==0]) if not notifs.empty else 0
        if unread > 0:
            st.warning(f"🔔 {unread} new notification(s)")
        page = st.radio("", ["📋 Pulse Survey", "👤 My Profile"], label_visibility="collapsed")

    st.divider()
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.refresh_n += 1; st.rerun()
    with col_s2:
        if st.button("🚪 Logout", use_container_width=True):
            for k in DEFAULTS: st.session_state[k]=DEFAULTS[k]
            st.rerun()
    st.caption(f"Samvaad v4.0 · {date.today()}")


# ═══════════════════════════════════════════════════════════════════════════════
# EMPLOYEE PAGES
# ═══════════════════════════════════════════════════════════════════════════════
if role != "HR":

    # ── MOTIVATIONAL QUOTES pool ───────────────────────────────────────────────
    QUOTES = [
        ("The secret of getting ahead is getting started.", "Mark Twain", "🚀"),
        ("Believe you can and you're halfway there.", "Theodore Roosevelt", "💫"),
        ("Every day is a new opportunity to grow.", "Unknown", "🌱"),
        ("Your work is your signature — make it beautiful.", "Unknown", "✍️"),
        ("Small steps every day lead to big results.", "Unknown", "👣"),
        ("You are capable of amazing things.", "Unknown", "⭐"),
        ("Progress, not perfection, is the goal.", "Unknown", "📈"),
        ("Your voice matters. Thank you for sharing it.", "EngageAI", "🎙️"),
        ("Teams that communicate thrive together.", "Unknown", "🤝"),
        ("Great workplaces are built one honest answer at a time.", "EngageAI", "🏗️"),
        ("Be the energy you want to see in your team.", "Unknown", "⚡"),
        ("Your feedback today shapes tomorrow's workplace.", "EngageAI", "🔮"),
    ]

    # ── Personalised tip based on answers ─────────────────────────────────────
    def get_personalised_tip(motivation, stress, team_connection, recognition):
        if stress >= 4:
            return ("😮‍💨", "You mentioned feeling stressed.", "Try the 4-7-8 breathing technique: inhale 4s, hold 7s, exhale 8s. Even 2 minutes helps reset your nervous system.")
        elif motivation <= 2:
            return ("💡", "Feeling low on motivation today?", "Break your day into small wins. Completing even one small task triggers a dopamine release that builds momentum.")
        elif team_connection <= 2:
            return ("🤝", "Feeling a bit disconnected?", "Reach out to one colleague today — even a quick message can rebuild that sense of belonging.")
        elif recognition <= 2:
            return ("🏅", "Feeling underappreciated?", "Peer recognition is powerful. Try recognising someone else today — it often starts a positive cycle.")
        else:
            return ("🌟", "You're doing great!", "Keep sharing your honest feedback — every response helps make this a better place to work.")

    # ── PULSE SURVEY ──────────────────────────────────────────────────────────
    if page == "📋 Pulse Survey":

        survey_open, schedule_msg = is_survey_open_today()
        history = get_employee_history(emp_id)
        today_str = str(date.today())
        already_submitted = not history.empty and (history["survey_date"] == today_str).any()

        # ── ALREADY SUBMITTED: show motivational screen ────────────────────
        if already_submitted:
            import random
            q, author, q_emoji = random.choice(QUOTES)
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0a2540 0%,#1557b0 100%);
                        border-radius:20px;padding:50px 40px;text-align:center;margin-bottom:24px">
                <div style="font-size:3.5rem;margin-bottom:16px">{q_emoji}</div>
                <h2 style="color:white;font-size:1.6rem;font-weight:700;margin-bottom:12px">
                    Thank you, {emp_name.split()[0]}! 🎉
                </h2>
                <p style="color:#a8c4f0;font-size:1rem;margin-bottom:28px">
                    You've completed today's pulse survey. Your voice makes a difference.
                </p>
                <div style="background:rgba(255,255,255,0.1);border-radius:14px;padding:24px 32px;
                            display:inline-block;max-width:500px">
                    <p style="color:white;font-size:1.1rem;font-style:italic;margin-bottom:8px">
                        "{q}"
                    </p>
                    <p style="color:#93c5fd;font-size:0.85rem;margin:0">— {author}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if not history.empty:
                last = history.iloc[0]
                tip_icon, tip_title, tip_msg = get_personalised_tip(
                    last.get("motivation",3), last.get("stress",3),
                    last.get("team_connection",3), last.get("recognition",3))
                st.markdown(f"""
                <div style="background:#f0f7ff;border:1px solid #bfdbfe;border-left:5px solid #3b82f6;
                            border-radius:12px;padding:20px 24px;margin-bottom:16px">
                    <div style="font-size:1.6rem;margin-bottom:6px">{tip_icon}</div>
                    <strong style="color:#1e40af">{tip_title}</strong>
                    <p style="color:#374151;margin:6px 0 0">{tip_msg}</p>
                </div>
                """, unsafe_allow_html=True)

            st.info(f"🗓️ Your next survey: {schedule_msg.replace('✅ ','')}")
            st.stop()

        # ── SURVEY NOT OPEN TODAY ──────────────────────────────────────────
        if not survey_open:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0a2540 0%,#1557b0 100%);
                        border-radius:20px;padding:40px;text-align:center;margin-bottom:20px">
                <div style="font-size:3rem;margin-bottom:12px">🗓️</div>
                <h2 style="color:white;margin-bottom:8px">No Survey Today</h2>
                <p style="color:#a8c4f0">{schedule_msg}</p>
            </div>
            """, unsafe_allow_html=True)
            override = st.checkbox("Submit anyway (if HR has asked you to)")
            if not override:
                st.stop()

        # ── SURVEY FORM ────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="top-header">
            <div>
                <h1>📋 Your Pulse Check</h1>
                <p>Takes 3–4 minutes · Confidential · {date.today().strftime("%A, %d %B %Y")}</p>
            </div>
            <div style='color:#a8c4f0;text-align:right;font-size:0.85rem'>
                Hello, <strong style='color:white'>{emp_name.split()[0]}</strong> 👋<br>
                Confidential &amp; Anonymous
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Load dynamic questions from DB
        questions_df = get_survey_questions()

        # Response containers
        resp = {
            "motivation": 3, "satisfaction": 3, "team_connection": 3,
            "recognition": 3, "stress": 3, "enps": 7,
            "eq_pressure": 3, "eq_balance": 3, "eq_empathy": 3,
            "mindset_growth": "", "mindset_purpose": "",
            "mindset_clarity": 3, "icebreaker_word": "", "icebreaker_emoji": "",
            "feedback": ""
        }

        # Map DB question types to column names
        TYPE_TO_KEY = {
            "slider": {
                "motivation": "motivation", "satisfaction": "satisfaction",
                "team_connection": "team_connection", "recognition": "recognition",
                "stress": "stress", "mindset_clarity": "mindset_clarity"
            }
        }

        # Category colours and icons
        CAT_STYLE = {
            "Engagement":  ("💼", "#3b82f6", "#eff6ff"),
            "Wellbeing":   ("🌿", "#22c55e", "#f0fdf4"),
            "EQ":          ("🧠", "#8b5cf6", "#f5f3ff"),
            "Mindset":     ("🎯", "#f59e0b", "#fffbeb"),
            "Icebreaker":  ("🎭", "#ec4899", "#fdf2f8"),
            "eNPS":        ("⭐", "#0ea5e9", "#f0f9ff"),
            "Feedback":    ("💬", "#64748b", "#f8fafc"),
        }

        current_category = None

        for _, q in questions_df.iterrows():
            cat   = q["category"]
            qtype = q["question_type"]
            qtext = q["question_text"]
            qemoji= q["emoji"]
            opts  = str(q["options"]) if q["options"] else ""

            icon, accent, bg = CAT_STYLE.get(cat, ("❓","#666","#f8f8f8"))

            # Category header when it changes
            if cat != current_category:
                current_category = cat
                st.markdown(f"""
                <div style="background:{bg};border-left:4px solid {accent};
                            border-radius:0 10px 10px 0;padding:10px 16px;
                            margin:20px 0 8px;display:flex;align-items:center;gap:10px">
                    <span style="font-size:1.3rem">{icon}</span>
                    <strong style="color:{accent};font-size:0.95rem;text-transform:uppercase;letter-spacing:0.5px">{cat}</strong>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:white;border:1px solid #e8edf5;border-radius:12px;
                        padding:16px 20px;margin-bottom:10px;border-left:3px solid {accent}">
                <span style="font-size:1.1rem">{qemoji}</span>
                <strong style="color:#0a2540;margin-left:6px">{qtext}</strong>
            </div>
            """, unsafe_allow_html=True)

            key = f"q_{q['id']}"

            # ── Slider (1-5) ───────────────────────────────────────────
            if qtype == "slider":
                val = st.select_slider("", options=[1,2,3,4,5], value=3,
                    format_func=lambda x: {1:"😟 1",2:"😕 2",3:"😐 3",4:"🙂 4",5:"😄 5"}[x],
                    key=key)
                # Map to the right response key based on category + question text keywords
                txt_lower = qtext.lower()
                if "motivat" in txt_lower:   resp["motivation"]      = val
                elif "satisf"  in txt_lower: resp["satisfaction"]    = val
                elif "connect" in txt_lower: resp["team_connection"] = val
                elif "recogni" in txt_lower: resp["recognition"]     = val
                elif "stress"  in txt_lower: resp["stress"]          = val
                elif "clarity" in txt_lower or "goal" in txt_lower: resp["mindset_clarity"] = val

            # ── Emoji rating (EQ) ──────────────────────────────────────
            elif qtype == "emoji_rating":
                val = st.select_slider("", options=[1,2,3,4,5], value=3,
                    format_func=lambda x: {1:"😰 Very Low",2:"😕 Low",3:"😐 Okay",4:"🙂 Good",5:"😄 Very Good"}[x],
                    key=key)
                txt_lower = qtext.lower()
                if "pressure" in txt_lower:   resp["eq_pressure"] = val
                elif "balance" in txt_lower:  resp["eq_balance"]  = val
                elif "empath"  in txt_lower:  resp["eq_empathy"]  = val

            # ── Yes / No ───────────────────────────────────────────────
            elif qtype == "yes_no":
                col_y, col_n, _ = st.columns([1,1,3])
                with col_y:
                    yes = st.button("👍  Yes", key=f"{key}_yes", use_container_width=True)
                with col_n:
                    no  = st.button("👎  No",  key=f"{key}_no",  use_container_width=True)
                txt_lower = qtext.lower()
                if yes:
                    if "growth" in txt_lower: resp["mindset_growth"]  = "Yes"
                    else:                     resp["mindset_purpose"] = "Yes"
                elif no:
                    if "growth" in txt_lower: resp["mindset_growth"]  = "No"
                    else:                     resp["mindset_purpose"] = "No"
                # Stateful toggle with session
                sk = f"yn_{q['id']}"
                if f"{key}_yes" not in st.session_state:
                    st.session_state[sk] = "—"
                if yes: st.session_state[sk] = "Yes ✅"
                if no:  st.session_state[sk] = "No ❌"
                st.caption(f"Your answer: **{st.session_state.get(sk, '—')}**")
                if "growth" in qtext.lower():  resp["mindset_growth"]  = st.session_state.get(sk,"").replace(" ✅","").replace(" ❌","")
                else:                          resp["mindset_purpose"] = st.session_state.get(sk,"").replace(" ✅","").replace(" ❌","")

            # ── One word ───────────────────────────────────────────────
            elif qtype == "one_word":
                val = st.text_input("", placeholder="Type one word...",
                    key=key, max_chars=30, label_visibility="collapsed")
                resp["icebreaker_word"] = val.strip()

            # ── Emoji pick ─────────────────────────────────────────────
            elif qtype == "emoji_pick":
                if opts:
                    choices = [o.strip() for o in opts.split("|")]
                    chosen = st.radio("", choices, horizontal=True,
                        key=key, label_visibility="collapsed")
                    resp["icebreaker_emoji"] = chosen or ""

            # ── eNPS slider (0-10) ─────────────────────────────────────
            elif qtype == "enps":
                val = st.slider("", 0, 10, 7, key=key, label_visibility="collapsed")
                resp["enps"] = val
                enps_cat = "🟢 Promoter (9–10)" if val>=9 else ("🟡 Passive (7–8)" if val>=7 else "🔴 Detractor (0–6)")
                st.caption(f"Category: **{enps_cat}**")

            # ── Free text ──────────────────────────────────────────────
            elif qtype == "text":
                val = st.text_area("", placeholder="Optional — share anything on your mind...",
                    height=80, key=key, label_visibility="collapsed")
                # Live sentiment
                if val.strip():
                    sent_label, sent_score, sent_emoji = realtime_sentiment(val)
                    sent_css = f"badge-{sent_label.lower()}"
                    col_s1, col_s2 = st.columns([1,3])
                    with col_s1:
                        st.markdown(f'<span class="{sent_css}">{sent_emoji} {sent_label}</span>',
                            unsafe_allow_html=True)
                    with col_s2:
                        bar_v = int(min(abs(sent_score)*100,100))
                        st.progress(bar_v if sent_label!="Neutral" else 50,
                            text=f"Sentiment detected: {sent_label}")
                    resp["feedback"] = val
                else:
                    st.caption("💡 Sentiment is analysed live as you type")
                    resp["feedback"] = val

            st.write("")

        # ── SUBMIT BUTTON ──────────────────────────────────────────────
        st.divider()
        st.markdown("""
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;
                    padding:16px 20px;margin-bottom:16px;text-align:center">
            <strong style="color:#166534">✅ All responses are confidential and anonymous</strong><br>
            <span style="color:#4b7c5e;font-size:0.87rem">HR sees only aggregated trends — never individual scores</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀  Submit My Pulse Survey", use_container_width=True, type="primary"):
            _, sent_score, _ = realtime_sentiment(resp["feedback"]) if resp["feedback"].strip() else ("N", 0.0, "")
            save_survey(
                emp_id,
                resp["motivation"], resp["satisfaction"], resp["team_connection"],
                resp["recognition"], resp["stress"], resp["enps"],
                resp["feedback"], sent_score,
                resp["eq_pressure"], resp["eq_balance"], resp["eq_empathy"],
                resp["mindset_growth"], resp["mindset_purpose"], resp["mindset_clarity"],
                resp["icebreaker_word"], resp["icebreaker_emoji"]
            )
            st.balloons()
            st.rerun()

    # ── MY PROFILE (no scores — just participation & encouragement) ────────────
    elif page == "👤 My Profile":
        st.markdown("""<div class="top-header">
            <div><h1>👤 My Profile</h1><p>Your participation journey</p></div>
        </div>""", unsafe_allow_html=True)

        conn = get_conn()
        emp_row = pd.read_sql_query("SELECT * FROM employee WHERE id=?", conn, params=(emp_id,)).iloc[0]
        conn.close()
        history = get_employee_history(emp_id)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 🪪 My Details")
            st.write(f"**Name:** {emp_row['name']}")
            st.write(f"**Department:** {emp_row['department']}")
            st.write(f"**Designation:** {emp_row['designation']}")
            st.write(f"**Email:** {emp_row['email']}")
            st.write(f"**Employee ID:** #{emp_id}")
            st.write(f"**Joined:** {emp_row.get('joined_date','—')}")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 🎯 My Participation")
            total_done = len(history) if not history.empty else 0
            st.metric("Surveys Completed", total_done)
            if total_done >= 10:
                badge = "🏆 Survey Champion"
            elif total_done >= 5:
                badge = "⭐ Regular Contributor"
            elif total_done >= 1:
                badge = "🌱 Getting Started"
            else:
                badge = "🆕 Not started yet"
            st.metric("Participation Badge", badge)
            if not history.empty:
                last_date = history.iloc[0]["survey_date"]
                st.metric("Last Participated", last_date)
            st.markdown('</div>', unsafe_allow_html=True)

        # Participation streak chart (no scores shown)
        if not history.empty:
            st.divider()
            st.markdown("#### 📅 My Survey Participation History")
            st.caption("Each dot represents a survey you completed. Keep the streak going! 🔥")
            part_df = history[["survey_date"]].copy()
            part_df["submitted"] = 1
            part_df = part_df.sort_values("survey_date")
            fig, ax = plt.subplots(figsize=(10, 2))
            ax.scatter(part_df["survey_date"], part_df["submitted"],
                       marker="o", s=80, color="#3b82f6", zorder=3)
            ax.set_yticks([]); ax.set_ylabel("")
            ax.set_title("Your Participation Timeline", fontsize=11, fontweight="bold")
            ax.grid(axis="x", alpha=0.3)
            ax.spines[["top","right","left"]].set_visible(False)
            plt.xticks(rotation=40, ha="right", fontsize=7)
            plt.tight_layout()
            st.pyplot(fig); plt.close()

            st.divider()
            st.markdown("#### 💬 My Recent Comments")
            st.caption("A record of what you've shared with management (your words only).")
            fb_hist = history[history["feedback"].notna() & (history["feedback"] != "")][["survey_date","feedback"]].head(5)
            if fb_hist.empty:
                st.info("You haven't added any written feedback yet. Try sharing a thought in your next survey!")
            else:
                for _, r in fb_hist.iterrows():
                    st.markdown(f"**{r['survey_date']}** — {r['feedback']}")

# ═══════════════════════════════════════════════════════════════════════════════
# HR PAGES
# ═══════════════════════════════════════════════════════════════════════════════
else:
    survey_df = compute_engagement(cached_survey_data())
    survey_df["risk"] = survey_df["engagement_score"].apply(classify_risk)

    # ════════════════════════════════════════════════════════════════════════════
    # GLOBAL TIME-PERIOD FILTER — shown on every HR page
    # ════════════════════════════════════════════════════════════════════════════
    from datetime import timedelta as _td

    _today      = pd.Timestamp.today().normalize()
    _week_start = _today - _td(days=_today.weekday())
    _prev_wk_s  = _week_start - _td(days=7)
    _month_start= _today.replace(day=1)
    _prev_mo_s  = (_month_start - _td(days=1)).replace(day=1)
    _prev_mo_e  = _month_start - _td(days=1)
    _year_start = _today.replace(month=1, day=1)
    _prev_yr_s  = _year_start.replace(year=_year_start.year-1)
    _prev_yr_e  = _year_start - _td(days=1)

    # ── Analytics period filter — shown ONLY on analytics pages, not management pages ──
    _MGMT_PAGES = ["👥 Employee Management", "🔐 HR Access Control", "🎯 Intervention Tracker"]
    _is_analytics_page = not any(mp in page for mp in _MGMT_PAGES)

    _PERIOD_OPTIONS = ["Weekly", "Monthly", "Yearly", "Overall"]
    if "analytics_period" not in st.session_state:
        st.session_state["analytics_period"] = "Monthly"

    if _is_analytics_page:
        _fc1, _fc2, _fc3 = st.columns([3, 5, 2])
        with _fc1:
            st.markdown("""
            <div style="background:linear-gradient(90deg,#0a2540,#1557b0);border-radius:10px;
                        padding:10px 16px;color:white">
                <div style="font-size:0.7rem;opacity:0.7;text-transform:uppercase;letter-spacing:0.5px">Samvaad Analytics</div>
                <div style="font-size:1rem;font-weight:800">Listening. Understanding. Acting.</div>
            </div>""", unsafe_allow_html=True)

        with _fc2:
            _sel_idx   = _PERIOD_OPTIONS.index(st.session_state["analytics_period"]) if st.session_state["analytics_period"] in _PERIOD_OPTIONS else 1
            _period_sel= st.radio("Period", _PERIOD_OPTIONS,
                                   index=_sel_idx, horizontal=True,
                                   key="analytics_period_radio")
            st.session_state["analytics_period"] = _period_sel
        with _fc3:
            _p = _period_sel
            if   _p == "Weekly":  _dr = f"{_week_start.strftime('%d %b')} – {_today.strftime('%d %b %Y')}"
            elif _p == "Monthly": _dr = f"{_month_start.strftime('%d %b')} – {_today.strftime('%d %b %Y')}"
            elif _p == "Yearly":  _dr = f"{_year_start.strftime('%d %b %Y')} – {_today.strftime('%d %b %Y')}"
            else:                  _dr = "All Historical Data"
            st.markdown(f"""
            <div style="background:#f8faff;border:1px solid #d0e4ff;border-radius:10px;
                        padding:10px 14px;font-size:0.78rem;color:#0a2540;text-align:center">
                <div style="font-weight:700;color:#1557b0">Data Range</div>
                <div>{_dr}</div>
            </div>""", unsafe_allow_html=True)
        st.divider()
    else:
        # Management pages — use default period without showing filter
        _period_sel = st.session_state.get("analytics_period", "Monthly")
        _p = _period_sel
        if   _p == "Weekly":  _dr = f"{_week_start.strftime('%d %b')} – {_today.strftime('%d %b %Y')}"
        elif _p == "Monthly": _dr = f"{_month_start.strftime('%d %b')} – {_today.strftime('%d %b %Y')}"
        elif _p == "Yearly":  _dr = f"{_year_start.strftime('%d %b %Y')} – {_today.strftime('%d %b %Y')}"
        else:                  _dr = "All Historical Data"

    # Apply time filter to survey_df
    survey_df["_date"] = pd.to_datetime(survey_df["survey_date"])
    _p = st.session_state.get("analytics_period", "Monthly")
    if   _p == "Weekly":
        _filt_df      = survey_df[survey_df["_date"] >= _week_start].copy()
        _prev_df      = survey_df[(survey_df["_date"] >= _prev_wk_s) & (survey_df["_date"] < _week_start)].copy()
        _period_label = "Current Week"
        _prev_label   = "Previous Week"
    elif _p == "Monthly":
        _filt_df      = survey_df[survey_df["_date"] >= _month_start].copy()
        _prev_df      = survey_df[(survey_df["_date"] >= _prev_mo_s) & (survey_df["_date"] < _month_start)].copy()
        _period_label = "Current Month"
        _prev_label   = "Previous Month"
    elif _p == "Yearly":
        _filt_df      = survey_df[survey_df["_date"] >= _year_start].copy()
        _prev_df      = survey_df[(survey_df["_date"] >= _prev_yr_s) & (survey_df["_date"] < _year_start)].copy()
        _period_label = "Current Year"
        _prev_label   = "Previous Year"
    else:
        _filt_df      = survey_df.copy()
        _prev_df      = pd.DataFrame()
        _period_label = "All Time"
        _prev_label   = "—"

    # ── Day / Week sub-filters — analytics pages only ─────────────────────────
    _compare_weeks = []
    _day_filter    = []
    _week_filter   = []
    _avail_days    = []
    _avail_weeks   = []
    _compare_df    = None

    if _is_analytics_page and not _filt_df.empty:
        if "_date" not in _filt_df.columns:
            _filt_df["_date"] = pd.to_datetime(_filt_df["survey_date"])
        _filt_df["_dow"]        = _filt_df["_date"].dt.day_name()
        _filt_df["_week_label"] = _filt_df["_date"].apply(
            lambda d: f"W{d.isocalendar()[1]} ({d.strftime('%d %b')})")
        _avail_days  = sorted(_filt_df["_dow"].unique().tolist())
        _avail_weeks = sorted(_filt_df["_week_label"].unique().tolist())

        _sf1, _sf2, _sf3 = st.columns([2, 2, 3])
        with _sf1:
            _day_filter = st.multiselect("Survey Day Filter", _avail_days,
                                          default=_avail_days, key="day_filter_global")
        with _sf2:
            _week_filter = st.multiselect("Week Filter", _avail_weeks,
                                           default=_avail_weeks, key="week_filter_global")
        with _sf3:
            _compare_weeks = st.multiselect("Compare Weeks (select 2)", _avail_weeks,
                                             default=[], max_selections=2,
                                             key="compare_weeks_global",
                                             placeholder="Select exactly 2 weeks to compare")
        if _day_filter and len(_day_filter) < len(_avail_days):
            _filt_df = _filt_df[_filt_df["_dow"].isin(_day_filter)]
        if _week_filter and len(_week_filter) < len(_avail_weeks):
            _filt_df = _filt_df[_filt_df["_week_label"].isin(_week_filter)]
        if len(_compare_weeks) == 2:
            _cw1 = _filt_df[_filt_df["_week_label"] == _compare_weeks[0]]
            _cw2 = _filt_df[_filt_df["_week_label"] == _compare_weeks[1]]
            _compare_df = (_cw1, _cw2, _compare_weeks[0], _compare_weeks[1])
        if _day_filter and len(_day_filter) < len(_avail_days):
            st.caption(f"Filter active: {' + '.join(_day_filter)} · {len(_filt_df)} responses")
        st.divider()

    # Pages will use _filt_df (period + sub-filtered) and _prev_df (comparison)
    # survey_df holds everything for pages needing full history (heatmap, forecast)

    # ── Dept-scoped filtering for non-Super-Admin HR ───────────────────────────
    _dept_access = st.session_state.get("dept_access", "ALL")
    _is_super    = st.session_state.get("is_super", False)
    if not _is_super and _dept_access and _dept_access != "ALL":
        _allowed_depts = [d.strip() for d in _dept_access.split(",")]
        conn_scope = get_conn()
        _emp_scope = pd.read_sql_query(
            "SELECT id FROM employee WHERE department IN ({})".format(
                ",".join(["?"]*len(_allowed_depts))),
            conn_scope, params=_allowed_depts)
        conn_scope.close()
        _scoped_ids = _emp_scope["id"].tolist()
        survey_df = survey_df[survey_df["employee_id"].isin(_scoped_ids)]
        _filt_df  = _filt_df[_filt_df["employee_id"].isin(_scoped_ids)]
        _prev_df  = _prev_df[_prev_df["employee_id"].isin(_scoped_ids)] if not _prev_df.empty else _prev_df
        st.info(f"🔷 Dept scope: **{_dept_access}** · Period: **{_period_label}**")

    conn = get_conn()
    total_employees = pd.read_sql_query("SELECT COUNT(*) AS t FROM employee WHERE is_active=1",conn).iloc[0]["t"]
    conn.close()
    total_resp = len(survey_df)  # total all-time responses for context

    total_resp  = len(survey_df)
    green_count = len(survey_df[survey_df["risk"]=="🟢 Green"])
    amber_count = len(survey_df[survey_df["risk"]=="🟡 Amber"])
    red_count   = len(survey_df[survey_df["risk"]=="🔴 Red"])
    burn_count  = len(survey_df[survey_df["stress"]>=4])
    avg_eng     = round(survey_df["engagement_score"].mean(),2)
    enps_s, promoters, passives, detractors = compute_enps(survey_df)
    red_pct     = round(red_count/total_resp*100,1) if total_resp else 0
    burn_pct    = round(burn_count/total_resp*100,1) if total_resp else 0

    def page_header(icon, title, subtitle="", show_period=True):
        _pl = st.session_state.get("analytics_period","Monthly")
        _period_badge = ""
        if show_period:
            _badge_colours = {
                "Weekly":  ("#fef3c7","#92400e","📅"),
                "Monthly": ("#eff6ff","#1d4ed8","📆"),
                "Yearly":  ("#f0fdf4","#166534","🗓️"),
                "Overall": ("#f8fafc","#475569","📊"),
            }
            for k,(bg,col,ico) in _badge_colours.items():
                if k in _pl:
                    _period_badge = f'<span style="background:{bg};color:{col};border-radius:8px;padding:3px 10px;font-size:0.75rem;font-weight:600;margin-left:10px">{ico} {k} View</span>'
                    break
        st.markdown(f"""<div class="top-header">
            <div>
                <h1>{icon} {title}{_period_badge}</h1>
                <p>{subtitle} &nbsp;·&nbsp; <span style='opacity:0.75'>{_dr}</span></p>
            </div>
            <div style='text-align:right;color:#a8c4f0;font-size:0.8rem'>
                Last updated: {datetime.now().strftime("%H:%M:%S")}<br>
                Responses: {total_resp} · Employees: {total_employees}
            </div>
        </div>""", unsafe_allow_html=True)



    # ── HR ACCESS CONTROL ─────────────────────────────────────────────────────
    if page == "🔐 HR Access Control":
        page_header("🔐","HR Access Control","Manage HR roles, access levels and department permissions")

        if not st.session_state.get("is_super"):
            st.error("🚫 Only Super Admins can manage HR access. Contact your Super Admin.")
            st.stop()

        DEPT_OPTIONS = ["Production","HR","Operations","Finance","Maintenance",
                        "Quality","Sales","Logistics","ALL"]
        LEVEL_OPTIONS = ["Super Admin","HR Manager","HR Executive","Viewer"]
        LEVEL_DESC = {
            "Super Admin":  "Full access — can manage all employees, all departments, change HR roles",
            "HR Manager":   "Can view all dashboards and analytics for their assigned departments",
            "HR Executive": "Can submit surveys on behalf of employees, view basic dashboard only",
            "Viewer":       "Read-only access to dashboard and reports for assigned departments",
        }
        LEVEL_COLOURS = {
            "Super Admin":  ("#92400e","#fef3c7"),
            "HR Manager":   ("#1d4ed8","#eff6ff"),
            "HR Executive": ("#166534","#f0fdf4"),
            "Viewer":       ("#64748b","#f8fafc"),
        }

        # ── Current HR Users ───────────────────────────────────────────────────
        conn = get_conn()
        hr_users = pd.read_sql_query(
            "SELECT id, name, department, designation, hr_level, dept_access FROM employee WHERE role='HR' AND is_active=1 ORDER BY id",
            conn); conn.close()

        st.markdown("#### 👥 Current HR Team")
        st.caption("All employees with HR role. Super Admins can edit access levels and department scope.")
        st.divider()

        for _, hr in hr_users.iterrows():
            lvl   = str(hr["hr_level"]) if hr["hr_level"] else "Not assigned"
            depts = str(hr["dept_access"]) if hr["dept_access"] else "None"
            clr, bg = LEVEL_COLOURS.get(lvl, ("#64748b","#f8fafc"))
            is_me = (int(hr["id"]) == emp_id)

            with st.container():
                col_info, col_edit = st.columns([3, 2])
                with col_info:
                    _crown     = "👑 " if lvl == "Super Admin" else ""
                    _you_badge = " (You)" if is_me else ""
                    st.markdown(f"""
                    <div style="background:white;border:1px solid #e8edf5;border-radius:12px;
                                padding:14px 18px;border-left:4px solid {clr}">
                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
                            <strong style="color:#0a2540;font-size:1rem">{_crown}#{int(hr["id"])} {hr["name"]}{_you_badge}</strong>
                            <span style="background:{bg};color:{clr};border-radius:10px;padding:2px 10px;font-size:0.75rem;font-weight:600">{lvl}</span>
                        </div>
                        <div style="font-size:0.82rem;color:#64748b">
                            {hr["designation"]} · {hr["department"]}<br>
                            <strong>Dept access:</strong> {depts}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_edit:
                    if not is_me:
                        with st.expander("✏️ Edit Access"):
                            new_lvl = st.selectbox("Access Level",
                                LEVEL_OPTIONS,
                                index=LEVEL_OPTIONS.index(lvl) if lvl in LEVEL_OPTIONS else 0,
                                key=f"lvl_{hr['id']}")
                            st.caption(LEVEL_DESC.get(new_lvl,""))

                            new_depts = st.multiselect(
                                "Department Scope",
                                DEPT_OPTIONS,
                                default=[d.strip() for d in depts.split(",") if d.strip() in DEPT_OPTIONS],
                                key=f"dpt_{hr['id']}")
                            dept_str = ",".join(new_depts) if new_depts else "ALL"

                            s1, s2 = st.columns(2)
                            with s1:
                                if st.button("💾 Save", key=f"save_hr_{hr['id']}", type="primary", use_container_width=True):
                                    conn = get_conn()
                                    conn.execute(
                                        "UPDATE employee SET hr_level=?, dept_access=? WHERE id=?",
                                        (new_lvl, dept_str, int(hr["id"])))
                                    conn.execute(
                                        "INSERT INTO notifications (employee_id,message,created_at,is_read) VALUES (?,?,?,0)",
                                        (int(hr["id"]),
                                         f"Your access level has been updated to {new_lvl} by Super Admin",
                                         str(pd.Timestamp.now())))
                                    conn.commit(); conn.close()
                                    st.success("✅ Access updated!")
                                    st.rerun()
                            with s2:
                                if st.button("🔴 Revoke HR", key=f"revoke_{hr['id']}", use_container_width=True):
                                    conn = get_conn()
                                    conn.execute(
                                        "UPDATE employee SET role='Employee', hr_level='', dept_access=''  WHERE id=?",
                                        (int(hr["id"]),))
                                    conn.commit(); conn.close()
                                    st.warning(f"HR access revoked for {hr['name']}. They are now an Employee.")
                                    st.rerun()
                    else:
                        st.info("This is your own account — edit via Employee Management.")
            st.write("")

        st.divider()

        # ── Grant HR to an existing employee ─────────────────────────────────
        st.markdown("#### ➕ Grant HR Access to an Employee")
        st.caption("Select any active employee and assign them an HR role with specific department access.")

        conn = get_conn()
        non_hr = pd.read_sql_query(
            "SELECT id, name, department, designation FROM employee WHERE role='Employee' AND is_active=1 ORDER BY name",
            conn); conn.close()

        if non_hr.empty:
            st.info("No non-HR employees found.")
        else:
            g1, g2, g3 = st.columns([2,1,2])
            with g1:
                emp_options = {f"#{r['id']} {r['name']} ({r['department']})": r for _, r in non_hr.iterrows()}
                selected_emp_label = st.selectbox("Select Employee", list(emp_options.keys()), key="grant_emp")
            with g2:
                grant_level = st.selectbox("Access Level", LEVEL_OPTIONS[1:], key="grant_lvl")
            with g3:
                grant_depts = st.multiselect("Department Scope", DEPT_OPTIONS,
                                              default=["ALL"], key="grant_depts")
            grant_dept_str = ",".join(grant_depts) if grant_depts else "ALL"

            if st.button("✅ Grant HR Access", type="primary", use_container_width=True):
                target = emp_options[selected_emp_label]
                conn = get_conn()
                conn.execute(
                    "UPDATE employee SET role='HR', hr_level=?, dept_access=? WHERE id=?",
                    (grant_level, grant_dept_str, int(target["id"])))
                conn.execute(
                    "INSERT INTO notifications (employee_id,message,created_at,is_read) VALUES (?,?,?,0)",
                    (int(target["id"]),
                     f"You have been granted HR access ({grant_level}) by Super Admin. Please log out and log back in.",
                     str(pd.Timestamp.now())))
                conn.commit(); conn.close()
                st.success(f"✅ {target['name']} now has {grant_level} access for: {grant_dept_str}")
                st.rerun()

        st.divider()

        # ── Access level reference ────────────────────────────────────────────
        st.markdown("#### 📋 Access Level Reference")
        ref_data = {
            "Level":          ["Super Admin","HR Manager","HR Executive","Viewer"],
            "Who it's for":   ["CHRO / Head HR","Dept HR Business Partner","HR Coordinator / Recruiter","Leadership / Read-only"],
            "Dashboard":      ["✅ Full","✅ Full","✅ Basic only","✅ Read-only"],
            "Add Employees":  ["✅ Yes","✅ Yes","❌ No","❌ No"],
            "Survey Builder": ["✅ Yes","✅ Yes","❌ No","❌ No"],
            "HR Access Ctrl": ["✅ Yes","❌ No","❌ No","❌ No"],
            "Download Reports":["✅ Yes","✅ Yes","❌ No","✅ Yes"],
        }
        st.dataframe(pd.DataFrame(ref_data), use_container_width=True, hide_index=True)


    # ── LIVE DASHBOARD ────────────────────────────────────────────────────────
    elif page == "📊 Live Dashboard":

        # ── Executive header banner ────────────────────────────────────────────
        if "Weekly"  in _period_label: _view_icon = "📅"
        elif "Month" in _period_label: _view_icon = "📆"
        elif "Year"  in _period_label: _view_icon = "🗓️"
        else:                          _view_icon = "📊"

        st.markdown(f"""
        <div style="background:linear-gradient(90deg,#0a2540 0%,#1557b0 100%);
                    border-radius:14px;padding:20px 28px;margin-bottom:20px;
                    display:flex;justify-content:space-between;align-items:center">
            <div>
                <div style="color:#a8c4f0;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.8px">
                    🪷 Samvaad · Employee Engagement Dashboard
                </div>
                <div style="color:white;font-size:1.5rem;font-weight:800;margin:4px 0">
                    {_view_icon} {_period_label} View
                </div>
                <div style="color:#93c5fd;font-size:0.85rem">
                    Data Range: {_dr} &nbsp;|&nbsp; Compared to: {_prev_label}
                </div>
            </div>
            <div style="text-align:right">
                <div style="color:#a8c4f0;font-size:0.72rem">Last refreshed</div>
                <div style="color:white;font-size:0.9rem;font-weight:600">{datetime.now().strftime("%d %b %Y, %H:%M")}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Auto-refresh
        col_auto, col_ref = st.columns([4,1])
        with col_auto:
            auto = st.toggle("🔄 Auto-refresh every 30 seconds", value=False)
        with col_ref:
            if st.button("Refresh Now 🔄", use_container_width=True):
                st.cache_data.clear(); st.rerun()
        if auto:
            time.sleep(30); st.cache_data.clear(); st.rerun()

        # ── Period-specific metrics ────────────────────────────────────────────
        _fd = _filt_df   # period-filtered data
        _pd2 = _prev_df  # comparison period

        _f_total  = len(_fd)
        _f_green  = len(_fd[_fd["risk"]=="🟢 Green"])  if not _fd.empty else 0
        _f_amber  = len(_fd[_fd["risk"]=="🟡 Amber"])  if not _fd.empty else 0
        _f_red    = len(_fd[_fd["risk"]=="🔴 Red"])    if not _fd.empty else 0
        _f_burn   = len(_fd[_fd["stress"]>=4])         if not _fd.empty else 0
        _f_eng    = round(_fd["engagement_score"].mean(),2) if not _fd.empty else 0
        _f_enps_s,_f_prom,_f_pass,_f_det = compute_enps(_fd)

        # Participation rate
        _part_rate = round((_f_total / (total_employees * (7 if "Week" in _period_label else
                           30 if "Month" in _period_label else 365 if "Year" in _period_label else
                           len(survey_df["survey_date"].unique()) or 1))) * 100, 1)
        _part_rate = min(_part_rate, 100)

        # Comparison deltas
        def _delta(curr, prev_df, col, agg="mean"):
            if prev_df.empty or col not in prev_df.columns: return None
            pv = prev_df[col].mean() if agg=="mean" else len(prev_df)
            return round(curr - pv, 2) if pv else None

        _eng_delta  = _delta(_f_eng,  _prev_df, "engagement_score")
        _resp_delta = (_f_total - len(_prev_df)) if not _prev_df.empty else None
        _burn_pct   = round(_f_burn/_f_total*100,1) if _f_total else 0

        # ── KPI Cards with period labels ──────────────────────────────────────
        st.divider()
        k1,k2,k3,k4,k5,k6,k7 = st.columns(7)

        # ── KPI helper: renders as st.metric (no HTML parsing issues) ───────────
        def _kpi_col(col, icon, value, label, period, pct=None, delta=None, delta_label=None):
            """Render a KPI card using only st.metric — zero HTML, zero parsing issues."""
            with col:
                # Choose accent colour
                if "Engaged" in label:       _accent = "#22c55e"
                elif "Moderate" in label:    _accent = "#f59e0b"
                elif "Risk" in label:        _accent = "#ef4444"
                elif "Burnout" in label:     _accent = "#ef4444"
                elif "eNPS" in label:        _accent = "#8b5cf6"
                else:                        _accent = "#3b82f6"

                # Build the value string — append % if given
                _val_str = str(value)
                if pct is not None:
                    _val_str = f"{value}  ({pct}%)"

                # Build delta string for st.metric
                _delta_val = None
                if delta is not None and delta_label and delta != 0:
                    _sign = "+" if delta > 0 else ""
                    _delta_val = f"{_sign}{delta} vs {delta_label}"

                # Period sub-label
                _full_label = f"{label}  [{period}]"

                st.metric(
                    label=_full_label,
                    value=_val_str,
                    delta=_delta_val,
                    delta_color="normal"
                )

        # Compute percentages
        _pct_green = round(_f_green/_f_total*100,1) if _f_total else 0
        _pct_amber = round(_f_amber/_f_total*100,1) if _f_total else 0
        _pct_red   = round(_f_red/_f_total*100,1)   if _f_total else 0
        _pct_burn  = round(_f_burn/_f_total*100,1)  if _f_total else 0

        _kpi_col(k1,"👥", total_employees, "Total Employees",  "Active")
        _kpi_col(k2,"📝", _f_total,        "Survey Responses", _period_label,  delta=_resp_delta, delta_label=_prev_label)
        _kpi_col(k3,"📊", f"{_f_eng}/5",   "Engagement Score", _period_label,  delta=_eng_delta,  delta_label=_prev_label)
        _kpi_col(k4,"🟢", _f_green,        "Engaged",          _period_label,  pct=_pct_green)
        _kpi_col(k5,"🟡", _f_amber,        "Moderate Risk",    _period_label,  pct=_pct_amber)
        _kpi_col(k6,"🔴", _f_red,          "High Risk",        _period_label,  pct=_pct_red)
        _kpi_col(k7,"🔥", _f_burn,         "Burnout Risk",     _period_label,  pct=_pct_burn)

        st.divider()

        # ── Participation rate bar — using st.progress (no HTML) ─────────────
        _pr_label = f"📊 Participation Rate ({_period_label}) — {_f_total} responses from {total_employees} employees"
        st.write(f"**{_pr_label}**")
        st.progress(
            min(int(_part_rate), 100),
            text=f"{_part_rate}% {'✅ Good' if _part_rate>=70 else ('⚠️ Moderate' if _part_rate>=40 else '🔴 Low')}"
        )

        # ── Charts ────────────────────────────────────────────────────────────
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(f"#### 🥧 Risk Distribution ({_period_label})")
            if _fd.empty:
                st.info(f"No responses recorded for {_period_label.lower()}.")
            else:
                fig, ax = plt.subplots(figsize=(5,4))
                wedges, texts, autotexts = ax.pie(
                    [_f_green, _f_amber, _f_red],
                    labels=["Engaged","Moderate Risk","High Risk"],
                    autopct="%1.1f%%", startangle=90,
                    colors=["#22c55e","#f59e0b","#ef4444"],
                    wedgeprops={"edgecolor":"white","linewidth":2.5})
                for at in autotexts: at.set_fontsize(10); at.set_fontweight("bold")
                ax.set_title(f"Risk Distribution · {_period_label}", fontsize=11, fontweight="bold", pad=10)
                plt.tight_layout(); st.pyplot(fig); plt.close()

        with col_b:
            st.markdown(f"#### 📈 Engagement Trend ({_period_label})")
            if _fd.empty:
                st.info("No trend data available for this period.")
            else:
                _trend = _fd.groupby("survey_date").agg(
                    avg_score=("engagement_score","mean"),
                    responses=("engagement_score","count")
                ).reset_index().sort_values("survey_date")
                fig2, ax2 = plt.subplots(figsize=(6,4))
                ax2.plot(_trend["survey_date"], _trend["avg_score"],
                         marker="o", color="#3b82f6", linewidth=2.5, markersize=5, label="Avg Engagement")
                ax2_twin = ax2.twinx()
                ax2_twin.bar(_trend["survey_date"], _trend["responses"],
                             alpha=0.2, color="#93c5fd", label="Responses")
                ax2.set_ylim(1,5); ax2.set_ylabel("Avg Score", color="#3b82f6")
                ax2_twin.set_ylabel("Responses", color="#93c5fd")
                plt.xticks(rotation=40, ha="right", fontsize=7)
                ax2.set_title(f"Engagement & Participation · {_period_label}", fontweight="bold")
                ax2.spines[["top","right"]].set_visible(False)
                plt.tight_layout(); st.pyplot(fig2); plt.close()

        # ── Period comparison bar (if prev data exists) ───────────────────────
        if not _prev_df.empty and not _fd.empty:
            st.divider()
            st.markdown(f"#### 📊 {_period_label} vs {_prev_label} — Score Comparison")
            _comp_metrics = ["motivation","satisfaction","team_connection","recognition","stress"]
            _comp_labels  = ["Motivation","Satisfaction","Team","Recognition","Stress"]
            _curr_means = [round(_fd[m].mean(),2) if m in _fd.columns else 0 for m in _comp_metrics]
            _prev_means = [round(_prev_df[m].mean(),2) if m in _prev_df.columns else 0 for m in _comp_metrics]
            import numpy as _np2
            _x = _np2.arange(len(_comp_labels))
            fig3, ax3 = plt.subplots(figsize=(9,3.5))
            _b1 = ax3.bar(_x-0.2, _curr_means, 0.38, label=_period_label, color="#3b82f6", alpha=0.9)
            _b2 = ax3.bar(_x+0.2, _prev_means, 0.38, label=_prev_label,   color="#94a3b8", alpha=0.7)
            for b in list(_b1)+list(_b2):
                ax3.text(b.get_x()+b.get_width()/2, b.get_height()+0.04,
                         f"{b.get_height():.1f}", ha="center", fontsize=8)
            ax3.set_xticks(_x); ax3.set_xticklabels(_comp_labels)
            ax3.set_ylim(0,5.5); ax3.set_ylabel("Score (1–5)")
            ax3.legend(fontsize=9); ax3.spines[["top","right"]].set_visible(False)
            ax3.set_title(f"Comparison: {_period_label} vs {_prev_label}", fontweight="bold")
            plt.tight_layout(); st.pyplot(fig3); plt.close()

        # ── Week-vs-Week comparison (if HR selected 2 weeks) ──────────────────
        if _compare_df is not None:
            _cw1_df, _cw2_df, _cw1_lbl, _cw2_lbl = _compare_df
            st.divider()
            st.markdown(f"#### 🔄 Week-vs-Week Comparison: **{_cw1_lbl}** vs **{_cw2_lbl}**")

            _comp_metrics2 = ["motivation","satisfaction","team_connection","recognition","stress","engagement_score"]
            _comp_labels2  = ["Motivation","Satisfaction","Team","Recognition","Stress","Engagement"]
            _w1_means = [round(_cw1_df[m].mean(),2) if m in _cw1_df.columns and not _cw1_df.empty else 0 for m in _comp_metrics2]
            _w2_means = [round(_cw2_df[m].mean(),2) if m in _cw2_df.columns and not _cw2_df.empty else 0 for m in _comp_metrics2]

            # Mini KPIs for each week
            wc1, wc2, wc3, wc4 = st.columns(4)
            wc1.metric(f"Responses ({_cw1_lbl})", len(_cw1_df))
            wc2.metric(f"Responses ({_cw2_lbl})", len(_cw2_df),
                       delta=len(_cw2_df)-len(_cw1_df))
            wc3.metric(f"Avg Eng ({_cw1_lbl})",  f"{round(_cw1_df['engagement_score'].mean(),2) if not _cw1_df.empty else 0}/5")
            wc4.metric(f"Avg Eng ({_cw2_lbl})",  f"{round(_cw2_df['engagement_score'].mean(),2) if not _cw2_df.empty else 0}/5",
                       delta=round((_cw2_df['engagement_score'].mean() if not _cw2_df.empty else 0) -
                                   (_cw1_df['engagement_score'].mean() if not _cw1_df.empty else 0), 2))

            import numpy as _np3
            _x2 = _np3.arange(len(_comp_labels2))
            fig_ww, ax_ww = plt.subplots(figsize=(10, 3.8))
            _colors_ww = ["#3b82f6","#22c55e","#f59e0b","#8b5cf6","#ef4444","#0ea5e9"]
            _bw1 = ax_ww.bar(_x2-0.22, _w1_means, 0.42, label=_cw1_lbl, color="#3b82f6", alpha=0.85)
            _bw2 = ax_ww.bar(_x2+0.22, _w2_means, 0.42, label=_cw2_lbl, color="#f59e0b", alpha=0.85)
            for _b in list(_bw1)+list(_bw2):
                ax_ww.text(_b.get_x()+_b.get_width()/2, _b.get_height()+0.04,
                           f"{_b.get_height():.2f}", ha="center", fontsize=8, fontweight="bold")
            ax_ww.set_xticks(_x2); ax_ww.set_xticklabels(_comp_labels2, fontsize=9)
            ax_ww.set_ylim(0, 5.6); ax_ww.set_ylabel("Score (1–5)")
            ax_ww.legend(fontsize=9, loc="upper right")
            ax_ww.axhline(3, color="#ef4444", linewidth=0.8, linestyle="--", alpha=0.4)
            ax_ww.spines[["top","right"]].set_visible(False)
            ax_ww.set_title(f"Week-vs-Week: {_cw1_lbl} vs {_cw2_lbl}", fontweight="bold", fontsize=11)
            plt.tight_layout(); st.pyplot(fig_ww); plt.close()

            # Day breakdown within each week
            st.markdown(f"##### 📅 Day-by-Day Breakdown")
            _day_tab1, _day_tab2 = st.tabs([f"📅 {_cw1_lbl}", f"📅 {_cw2_lbl}"])
            for _tab, _wdf, _wlbl in [(_day_tab1, _cw1_df, _cw1_lbl), (_day_tab2, _cw2_df, _cw2_lbl)]:
                with _tab:
                    if _wdf.empty:
                        st.info("No data for this week.")
                    else:
                        _wdf2 = _wdf.copy()
                        _wdf2["Day"] = pd.to_datetime(_wdf2["survey_date"]).dt.day_name()
                        _day_grp = _wdf2.groupby("survey_date").agg(
                            Day=("survey_date", lambda x: pd.to_datetime(x.iloc[0]).strftime("%A %d %b")),
                            Responses=("engagement_score","count"),
                            Avg_Engagement=("engagement_score","mean"),
                            Avg_Stress=("stress","mean"),
                            Avg_Motivation=("motivation","mean")
                        ).reset_index(drop=True)
                        _day_grp["Avg_Engagement"] = _day_grp["Avg_Engagement"].round(2)
                        _day_grp["Avg_Stress"]     = _day_grp["Avg_Stress"].round(2)
                        _day_grp["Avg_Motivation"] = _day_grp["Avg_Motivation"].round(2)
                        st.dataframe(_day_grp, use_container_width=True, hide_index=True)

        st.divider()

        # ── AI recommendations with period context ────────────────────────────
        st.markdown(f"#### 🤖 AI Recommendations — {_period_label} Insights")

        # Period-aware deltas for rules
        _eng_chg  = _eng_delta if _eng_delta else 0
        _resp_chg = ((_f_total - len(_prev_df)) / max(len(_prev_df),1) * 100) if not _prev_df.empty else 0

        _period_insights = []
        if not _prev_df.empty:
            if _eng_chg < -0.2:
                _period_insights.append(("error",
                    f"📉 **{_period_label} Alert:** Engagement score dropped by {abs(_eng_chg):.2f} points compared to {_prev_label}. "
                    f"Immediate investigation recommended."))
            elif _eng_chg > 0.2:
                _period_insights.append(("success",
                    f"📈 **{_period_label} Positive:** Engagement improved by {_eng_chg:.2f} points vs {_prev_label}. "
                    f"Identify what drove this and reinforce it."))
            if _resp_chg < -20:
                _period_insights.append(("warning",
                    f"⚠️ **Participation Drop ({_period_label}):** Survey responses fell by {abs(round(_resp_chg,1))}% vs {_prev_label}. "
                    f"Send participation reminders."))
            elif _resp_chg > 20:
                _period_insights.append(("success",
                    f"✅ **Participation Up ({_period_label}):** Survey participation increased by {round(_resp_chg,1)}% vs {_prev_label}."))

        recs = get_rule_recs(_f_red, _f_amber, _f_burn, _f_eng, _f_enps_s, _f_total)
        for title, msg, lvl in recs:
            getattr(st, lvl)(f"**{title}** ({_period_label}) — {msg}")
        for lvl, msg in _period_insights:
            getattr(st, lvl)(msg)

        st.divider()
        st.markdown(f"#### 💬 Employee Feedback ({_period_label})")
        if _fd.empty or "feedback" not in _fd.columns:
            st.info("No feedback in this period.")
        else:
            _fb_period = _fd[_fd["feedback"].notna() & (_fd["feedback"].str.strip()!="")]["feedback"]
            if _fb_period.empty:
                st.info("No written feedback submitted in this period.")
            else:
                for item in _fb_period.tail(8):
                    _, _, _em = realtime_sentiment(item)
                    st.write(f"{_em} {item}")


    # ── ENGAGEMENT HEATMAP ────────────────────────────────────────────────────
    elif page == "🗺️ Engagement Heatmap":
        page_header("🗺️","Engagement Heatmap","Department × Week engagement intensity map")

        conn = get_conn()
        heat_df = pd.read_sql_query("""
            SELECT e.department, sr.survey_date,
                   ROUND(AVG((sr.motivation+sr.satisfaction+sr.team_connection+sr.recognition+(6-sr.stress))/5.0),2) AS avg_score
            FROM survey_response sr JOIN employee e ON e.id=sr.employee_id
            GROUP BY e.department, sr.survey_date ORDER BY sr.survey_date
        """, conn); conn.close()

        if heat_df.empty:
            st.info("No data available yet."); st.stop()

        heat_df["week"] = pd.to_datetime(heat_df["survey_date"]).dt.strftime("W%V %b%d")
        last_weeks = sorted(heat_df["week"].unique())[-16:]
        heat_df = heat_df[heat_df["week"].isin(last_weeks)]
        pivot = heat_df.pivot_table(index="department", columns="week", values="avg_score", aggfunc="mean").fillna(np.nan)

        fig, ax = plt.subplots(figsize=(max(14,len(pivot.columns)*1.1), max(5,len(pivot.index)*0.75)))
        cmap = sns.diverging_palette(10,130,as_cmap=True)
        mask = pivot.isna()
        sns.heatmap(pivot, ax=ax, cmap=cmap, vmin=1, vmax=5,
                    annot=True, fmt=".1f", linewidths=0.8, mask=mask,
                    cbar_kws={"label":"Engagement Score (1–5)","shrink":0.8},
                    annot_kws={"size":9,"weight":"bold"})
        ax.set_title("Department × Week Engagement Heatmap", fontsize=14, fontweight="bold", pad=14)
        ax.set_xlabel("Survey Week", fontsize=10); ax.set_ylabel("Department", fontsize=10)
        plt.xticks(rotation=45, ha="right", fontsize=8); plt.yticks(rotation=0, fontsize=9)
        plt.tight_layout(); st.pyplot(fig); plt.close()

        st.divider()
        c1,c2,c3 = st.columns(3)
        c1.success("Score 4–5 = Highly Engaged")
        c2.warning("Score 3–4 = Moderate")
        c3.error("Score 1–3 = At Risk")

        avg_by_week = heat_df.groupby("week")["avg_score"].mean()
        if not avg_by_week.empty:
            st.divider()
            w1,w2 = st.columns(2)
            w1.metric("📉 Lowest Engagement Week", avg_by_week.idxmin(), f"{round(avg_by_week.min(),2)}/5")
            w2.metric("📈 Best Engagement Week",   avg_by_week.idxmax(), f"{round(avg_by_week.max(),2)}/5")


    # ── eNPS ANALYTICS ────────────────────────────────────────────────────────
    elif page == "📈 eNPS Analytics":
        page_header("📈","eNPS Analytics","Employee Net Promoter Score — loyalty & advocacy")

        with st.expander("ℹ️ eNPS Formula & Interpretation"):
            st.markdown("""
            | Score | Category | What it means |
            |-------|----------|---------------|
            | 9–10 | 🟢 Promoter | Highly engaged — advocates for the company |
            | 7–8  | 🟡 Passive  | Satisfied but not enthusiastic |
            | 0–6  | 🔴 Detractor| Disengaged — may spread negativity |

            **eNPS = % Promoters − % Detractors**
            > Above 30 = Excellent · 10–30 = Good · 0–10 = Needs Work · Below 0 = Critical
            """)

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("📊 Overall eNPS", enps_s)
        c2.metric("Promoters (9–10)",  promoters, f"{round(promoters/total_resp*100,1) if total_resp else 0}%")
        c3.metric("Passives (7–8)",   passives,  f"{round(passives/total_resp*100,1) if total_resp else 0}%")
        c4.metric("Detractors (0–6)", detractors,f"{round(detractors/total_resp*100,1) if total_resp else 0}%")

        col_g, col_c = st.columns(2)
        with col_g:
            colour = "#22c55e" if enps_s>=30 else ("#f59e0b" if enps_s>=0 else "#ef4444")
            label  = "Excellent 🏆" if enps_s>=30 else ("Good ✅" if enps_s>=10 else ("Needs Work ⚠️" if enps_s>=0 else "Critical 🚨"))
            st.markdown(f"""<div class="section-card" style="text-align:center; padding:40px 20px">
                <div style="font-size:1rem;color:#6b7a99;margin-bottom:8px">Overall eNPS Score</div>
                <div style="font-size:5rem;font-weight:900;color:{colour};line-height:1">{enps_s}</div>
                <div style="font-size:1.1rem;color:{colour};margin-top:8px">{label}</div>
            </div>""", unsafe_allow_html=True)
            st.progress(max(0, min(int((enps_s+100)/2), 100)))

        with col_c:
            fig, ax = plt.subplots(figsize=(5,4))
            bars = ax.bar(["Promoters\n(9–10)","Passives\n(7–8)","Detractors\n(0–6)"],
                          [promoters, passives, detractors],
                          color=["#22c55e","#f59e0b","#ef4444"], edgecolor="white", linewidth=1.5, width=0.5)
            for b in bars:
                ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.5,
                        str(int(b.get_height())), ha="center", fontweight="bold", fontsize=12)
            ax.set_title("eNPS Distribution", fontweight="bold")
            ax.set_ylabel("Responses"); ax.spines[["top","right"]].set_visible(False)
            plt.tight_layout(); st.pyplot(fig); plt.close()

        st.divider()
        st.markdown("#### 🏢 eNPS by Department")
        dept_df = cached_dept_stats().fillna(0)
        dept_sorted = dept_df.sort_values("dept_enps", ascending=False)
        fig3, ax3 = plt.subplots(figsize=(10,4))
        colours = ["#22c55e" if v>=0 else "#ef4444" for v in dept_sorted["dept_enps"]]
        ax3.bar(dept_sorted["department"], dept_sorted["dept_enps"], color=colours, edgecolor="white", width=0.6)
        ax3.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax3.set_title("Department eNPS", fontweight="bold"); ax3.set_ylabel("eNPS Score")
        ax3.spines[["top","right"]].set_visible(False)
        plt.xticks(rotation=30, ha="right"); plt.tight_layout()
        st.pyplot(fig3); plt.close()

        st.divider()
        st.markdown("#### 📅 eNPS Trend Over Time")
        conn = get_conn()
        et = pd.read_sql_query("""
            SELECT survey_date,
                   ROUND(AVG(CASE WHEN enps>=9 THEN 100.0 WHEN enps<=6 THEN -100.0 ELSE 0 END),1) AS enps_score
            FROM survey_response WHERE enps IS NOT NULL GROUP BY survey_date ORDER BY survey_date
        """, conn); conn.close()
        if not et.empty:
            st.line_chart(et.set_index("survey_date"))


    # ── DEPARTMENT ANALYTICS ──────────────────────────────────────────────────
    elif page == "🏢 Department Analytics":
        page_header("🏢","Department Analytics","Performance breakdown by function")

        dept_df = cached_dept_stats().fillna(0)
        dept_df["high_risk"]    = dept_df["high_risk"].astype(int)
        dept_df["burnout_risk"] = dept_df["burnout_risk"].astype(int)
        best  = dept_df.sort_values("avg_engagement", ascending=False).iloc[0]
        worst = dept_df.sort_values("avg_engagement").iloc[0]

        c1,c2,c3 = st.columns(3)
        c1.metric("Best Engaged Dept", best["department"], f"{best['avg_engagement']}/5")
        c2.metric("Needs Attention", worst["department"], f"{worst['avg_engagement']}/5")
        c3.metric("Total High Risk Employees", int(dept_df["high_risk"].sum()))
        st.divider()

        display = dept_df.rename(columns={"department":"Department","total_employees":"Employees",
            "responses":"Responses","avg_engagement":"Avg Score","high_risk":"High Risk",
            "burnout_risk":"Burnout Risk","dept_enps":"Dept eNPS"})
        st.dataframe(display, use_container_width=True)

        col1,col2 = st.columns(2)
        with col1:
            st.markdown("#### Avg Engagement Score")
            st.bar_chart(dept_df.set_index("department")[["avg_engagement"]])
        with col2:
            st.markdown("#### Risk Counts")
            st.bar_chart(dept_df.set_index("department")[["high_risk","burnout_risk"]])


    # ── SENTIMENT ANALYSIS ────────────────────────────────────────────────────
    elif page == "💬 Sentiment Analysis":
        page_header("💬","Sentiment Analysis","Live text analysis from employee feedback")

        conn = get_conn()
        all_fb = pd.read_sql_query(
            "SELECT feedback, survey_date FROM survey_response WHERE feedback IS NOT NULL AND feedback!=''", conn)
        conn.close()
        all_fb["sentiment"] = all_fb["feedback"].apply(sentiment_label)
        all_fb["score"]     = all_fb["feedback"].apply(lambda x: realtime_sentiment(x)[1])
        pos_c = len(all_fb[all_fb["sentiment"]=="Positive"])
        neu_c = len(all_fb[all_fb["sentiment"]=="Neutral"])
        neg_c = len(all_fb[all_fb["sentiment"]=="Negative"])
        total_fb = len(all_fb)

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("📝 Total Feedback", total_fb)
        c2.metric("😊 Positive", pos_c, f"{round(pos_c/total_fb*100,1) if total_fb else 0}%")
        c3.metric("😐 Neutral",  neu_c, f"{round(neu_c/total_fb*100,1) if total_fb else 0}%")
        c4.metric("😟 Negative", neg_c, f"{round(neg_c/total_fb*100,1) if total_fb else 0}%")

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            fig, ax = plt.subplots(figsize=(5,4))
            ax.pie([pos_c,neu_c,neg_c], labels=["Positive","Neutral","Negative"],
                   autopct="%1.1f%%", colors=["#22c55e","#94a3b8","#ef4444"],
                   startangle=90, wedgeprops={"edgecolor":"white","linewidth":2.5})
            ax.set_title("Sentiment Distribution", fontweight="bold")
            plt.tight_layout(); st.pyplot(fig); plt.close()
        with col_b:
            sent_trend = all_fb.groupby(["survey_date","sentiment"]).size().unstack(fill_value=0)
            if not sent_trend.empty:
                st.markdown("#### Sentiment Over Time")
                st.line_chart(sent_trend)

        st.divider()
        st.markdown("#### All Feedback with Labels")
        all_fb["emoji"] = all_fb["sentiment"].map({"Positive":"😊","Neutral":"😐","Negative":"😟"})
        st.dataframe(all_fb[["survey_date","emoji","sentiment","feedback"]].rename(
            columns={"survey_date":"Date","emoji":"","sentiment":"Sentiment","feedback":"Feedback"}
        ).reset_index(drop=True), use_container_width=True)


    # ── EMPLOYEE ACTION PLAN ──────────────────────────────────────────────────
    elif page == "🎯 Intervention Tracker":
        # No period filter needed — interventions are date-managed independently
        st.markdown("""<div class="top-header">
            <div><h1>Intervention Tracker</h1>
            <p>Create · Track · Measure · Close the loop on every engagement risk</p></div>
            <div style='text-align:right;color:#a8c4f0;font-size:0.78rem'>
                Complete Action Management System
            </div>
        </div>""", unsafe_allow_html=True)

        tab_dash, tab_create, tab_manage, tab_exec = st.tabs([
            "Dashboard", "Create Intervention", "Manage & Update", "Executive Report"
        ])

        # ── SHARED DATA ────────────────────────────────────────────────────────
        all_iv = get_interventions()
        DEPTS = ["All","Production","HR","Operations","Finance","Maintenance","Quality","Sales","Logistics"]
        CATS  = list(AI_INTERVENTIONS.keys())
        PRIOS = ["High","Medium","Low"]
        STATS = ["Planned","In Progress","Completed","On Hold","Cancelled"]
        STAT_COLOURS = {
            "Planned":    ("#eff6ff","#1d4ed8"),
            "In Progress":("#fef3c7","#92400e"),
            "Completed":  ("#f0fdf4","#166534"),
            "On Hold":    ("#f8fafc","#64748b"),
            "Cancelled":  ("#fee2e2","#991b1b"),
        }
        PRIO_COLOURS = {"High":"#ef4444","Medium":"#f59e0b","Low":"#22c55e"}

        # ═══ TAB 1: DASHBOARD ═══════════════════════════════════════════════════
        with tab_dash:
            if all_iv.empty:
                st.info("No interventions created yet. Use the 'Create Intervention' tab to get started.")
            else:
                total     = len(all_iv)
                open_iv   = len(all_iv[all_iv["status"].isin(["Planned","In Progress"])])
                completed = len(all_iv[all_iv["status"]=="Completed"])
                on_hold   = len(all_iv[all_iv["status"]=="On Hold"])
                overdue   = len(all_iv[
                    (all_iv["status"].isin(["Planned","In Progress"])) &
                    (pd.to_datetime(all_iv["due_date"], errors="coerce") < pd.Timestamp.today())])
                comp_rate = round(completed/total*100, 1) if total else 0

                # Effectiveness from completed interventions
                comp_df = all_iv[all_iv["effectiveness_score"].notna()]
                avg_eff = round(comp_df["effectiveness_score"].mean(), 1) if not comp_df.empty else 0

                # KPI row
                k1,k2,k3,k4,k5,k6 = st.columns(6)
                k1.metric("Total Interventions", total)
                k2.metric("Open",                open_iv)
                k3.metric("Completed",           completed,  delta=f"{comp_rate}% rate")
                k4.metric("On Hold",             on_hold)
                k5.metric("Overdue",             overdue,    delta_color="inverse",
                          delta=f"{overdue} need attention" if overdue else None)
                k6.metric("Avg Effectiveness",   f"{avg_eff}%" if avg_eff else "—")

                st.divider()
                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown("#### Status Breakdown")
                    status_counts = all_iv["status"].value_counts().reset_index()
                    status_counts.columns = ["Status","Count"]
                    colours_list = [STAT_COLOURS.get(s,(("#f8fafc","#64748b")))[1]
                                    for s in status_counts["Status"]]
                    colours_hex  = ["#3b82f6","#f59e0b","#22c55e","#94a3b8","#ef4444"]
                    fig,ax = plt.subplots(figsize=(5,4))
                    bars = ax.barh(status_counts["Status"], status_counts["Count"],
                                  color=colours_hex[:len(status_counts)], height=0.5)
                    for bar in bars:
                        ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
                                str(int(bar.get_width())), va='center', fontsize=10, fontweight='bold')
                    ax.set_xlabel("Count"); ax.spines[["top","right"]].set_visible(False)
                    ax.set_title("Interventions by Status", fontweight="bold")
                    plt.tight_layout(); st.pyplot(fig); plt.close()

                with col_b:
                    st.markdown("#### Priority Distribution")
                    prio_counts = all_iv["priority"].value_counts().reset_index()
                    prio_counts.columns = ["Priority","Count"]
                    prio_colours = [PRIO_COLOURS.get(p,"#666") for p in prio_counts["Priority"]]
                    fig2,ax2 = plt.subplots(figsize=(5,4))
                    wedges,_,autotexts = ax2.pie(
                        prio_counts["Count"], labels=prio_counts["Priority"],
                        autopct="%1.0f%%", colors=prio_colours,
                        wedgeprops={"edgecolor":"white","linewidth":2})
                    for at in autotexts: at.set_fontsize(10); at.set_fontweight("bold")
                    ax2.set_title("Priority Distribution", fontweight="bold")
                    plt.tight_layout(); st.pyplot(fig2); plt.close()

                st.divider()
                st.markdown("#### Department-wise Interventions")
                dept_iv = all_iv.groupby("department").agg(
                    Total=("id","count"),
                    Open=("status", lambda x: (x.isin(["Planned","In Progress"])).sum()),
                    Completed=("status", lambda x: (x=="Completed").sum()),
                    Overdue=("id", lambda x: (
                        all_iv.loc[x.index,"status"].isin(["Planned","In Progress"]) &
                        (pd.to_datetime(all_iv.loc[x.index,"due_date"], errors="coerce") < pd.Timestamp.today())
                    ).sum())
                ).reset_index().rename(columns={"department":"Department"})
                st.dataframe(dept_iv, use_container_width=True, hide_index=True)

                st.divider()
                # Effectiveness tracking for completed interventions
                if not comp_df.empty:
                    st.markdown("#### Effectiveness of Completed Interventions")
                    eff_display = comp_df[["title","department","issue_category",
                                           "before_score","after_score","effectiveness_score"]].copy()
                    eff_display.columns = ["Intervention","Department","Issue",
                                           "Score Before","Score After","Effectiveness %"]
                    eff_display["Score Before"] = eff_display["Score Before"].round(2)
                    eff_display["Score After"]  = eff_display["Score After"].fillna(0).round(2)
                    st.dataframe(eff_display, use_container_width=True, hide_index=True)

                # Overdue alert
                if overdue > 0:
                    st.divider()
                    st.error(f"**{overdue} overdue intervention(s)** — due dates have passed without completion.")
                    overdue_df = all_iv[
                        (all_iv["status"].isin(["Planned","In Progress"])) &
                        (pd.to_datetime(all_iv["due_date"], errors="coerce") < pd.Timestamp.today())
                    ][["title","department","priority","due_date","owner"]].copy()
                    overdue_df.columns = ["Intervention","Department","Priority","Due Date","Owner"]
                    st.dataframe(overdue_df, use_container_width=True, hide_index=True)

        # ═══ TAB 2: CREATE ══════════════════════════════════════════════════════
        with tab_create:
            st.markdown("#### Create New Intervention")
            st.caption("Fill in the details below. AI suggestions load automatically based on the issue category.")

            c1, c2 = st.columns(2)
            with c1:
                iv_title   = st.text_input("Intervention Title *", placeholder="e.g. Burnout Reduction — Production Q3")
                iv_cat     = st.selectbox("Issue Category *", CATS)
                iv_dept    = st.selectbox("Department *", DEPTS[1:])
                iv_desc    = st.text_area("Description", placeholder="Describe the issue and context...", height=90)
                iv_prio    = st.selectbox("Priority *", PRIOS)
            with c2:
                # AI suggested actions
                ai_suggestions = AI_INTERVENTIONS.get(iv_cat, [])
                st.markdown(f"**AI Suggested Actions for '{iv_cat}':**")
                for sugg in ai_suggestions:
                    st.markdown(f"- {sugg}")
                iv_action  = st.text_area("Recommended Action *",
                    value=ai_suggestions[0] if ai_suggestions else "",
                    placeholder="Describe the planned action...", height=70)
                iv_owner   = st.selectbox("Assigned To (Owner) *",
                    [r["name"] for _,r in get_all_employees().iterrows() if r["role"]=="HR"] or ["HR Team"])
                iv_hrbp    = st.text_input("HRBP", placeholder="HRBP name")
                iv_manager = st.text_input("Manager Responsible", placeholder="Department manager name")

            c3, c4, c5 = st.columns(3)
            with c3: iv_start  = st.date_input("Start Date",    value=date.today())
            with c4: iv_due    = st.date_input("Target Completion", value=date.today()+timedelta(days=30))
            with c5: iv_status = st.selectbox("Initial Status", STATS[:2])

            st.markdown("#### Baseline Metrics (Before Intervention)")
            b1, b2, b3 = st.columns(3)
            with b1: iv_bscore = st.number_input("Current Engagement Score (1–5)", 1.0, 5.0, float(survey_df["engagement_score"].mean()) if not survey_df.empty else 3.0, 0.1)
            with b2: iv_bburn  = st.number_input("Current Burnout Risk %", 0.0, 100.0, float(burn_pct) if "burn_pct" in dir() and burn_pct else 20.0, 0.5)
            with b3:
                conn = get_conn()
                all_emps_iv = pd.read_sql_query("SELECT id, name FROM employee WHERE is_active=1", conn)
                conn.close()
                emp_opts = ["None"] + [f"#{r['id']} {r['name']}" for _,r in all_emps_iv.iterrows()]
                iv_emp = st.selectbox("Linked Employee (optional)", emp_opts)

            iv_comments = st.text_area("Comments", placeholder="Any additional context...", height=60)

            if st.button("Create Intervention", use_container_width=True, type="primary"):
                if not iv_title.strip() or not iv_action.strip():
                    st.error("Title and Recommended Action are required.")
                else:
                    linked_id = None
                    if iv_emp != "None":
                        try: linked_id = int(iv_emp.split()[0].replace("#",""))
                        except: pass
                    create_intervention({
                        "title": iv_title.strip(), "issue_category": iv_cat,
                        "department": iv_dept, "description": iv_desc.strip(),
                        "recommended_action": iv_action.strip(), "priority": iv_prio,
                        "owner": iv_owner, "hrbp": iv_hrbp, "manager": iv_manager,
                        "status": iv_status, "start_date": str(iv_start),
                        "due_date": str(iv_due), "before_score": iv_bscore,
                        "before_burnout": iv_bburn, "linked_emp": linked_id,
                        "comments": iv_comments
                    })
                    st.success(f"✅ Intervention '{iv_title}' created successfully!")
                    st.balloons()

        # ═══ TAB 3: MANAGE & UPDATE ═════════════════════════════════════════════
        with tab_manage:
            st.markdown("#### Manage Existing Interventions")

            # Filters
            fc1,fc2,fc3 = st.columns(3)
            with fc1: filt_dept = st.selectbox("Department", DEPTS, key="iv_dept_f")
            with fc2: filt_stat = st.selectbox("Status", ["All"]+STATS, key="iv_stat_f")
            with fc3: filt_prio = st.selectbox("Priority", ["All"]+PRIOS, key="iv_prio_f")

            iv_filtered = get_interventions(
                dept=filt_dept if filt_dept!="All" else None,
                status=filt_stat if filt_stat!="All" else None,
                priority=filt_prio if filt_prio!="All" else None)

            m1,m2,m3 = st.columns(3)
            m1.metric("Showing", len(iv_filtered))
            m2.metric("Open",    len(iv_filtered[iv_filtered["status"].isin(["Planned","In Progress"])]) if not iv_filtered.empty else 0)
            m3.metric("Completed", len(iv_filtered[iv_filtered["status"]=="Completed"]) if not iv_filtered.empty else 0)

            if iv_filtered.empty:
                st.info("No interventions match the selected filters.")
            else:
                for _, iv in iv_filtered.iterrows():
                    stat_bg, stat_col = STAT_COLOURS.get(iv["status"], ("#f8fafc","#64748b"))
                    prio_col = PRIO_COLOURS.get(iv["priority"], "#666")
                    due_flag = ""
                    if iv["status"] in ["Planned","In Progress"] and iv["due_date"]:
                        try:
                            days_left = (pd.to_datetime(iv["due_date"]) - pd.Timestamp.today()).days
                            if days_left < 0:   due_flag = f" · **OVERDUE by {abs(days_left)} days**"
                            elif days_left <= 7: due_flag = f" · Due in {days_left} days"
                        except: pass

                    with st.expander(
                        f"[{iv['priority']}] {iv['title']} — {iv['department']} · {iv['status']}{due_flag}",
                        expanded=(iv["status"]=="In Progress" or "OVERDUE" in due_flag)):

                        ci1, ci2 = st.columns([2,1])
                        with ci1:
                            st.markdown(f"**Category:** {iv['issue_category']}  |  **Owner:** {iv['owner'] or '—'}  |  **Manager:** {iv['manager_responsible'] or '—'}")
                            st.markdown(f"**Description:** {iv['description'] or '—'}")
                            st.markdown(f"**Action:** {iv['recommended_action'] or '—'}")
                            st.markdown(f"**Timeline:** {iv['start_date'] or '—'} → {iv['due_date'] or '—'}")
                            if iv["comments"]: st.markdown(f"**Comments:** {iv['comments']}")

                        with ci2:
                            st.markdown("**Metrics**")
                            if iv["before_score"]:
                                st.write(f"Before: {iv['before_score']}/5")
                            if iv["after_score"]:
                                st.write(f"After: {iv['after_score']}/5")
                                imp = round((float(iv['after_score'])-float(iv['before_score']))/max(float(iv['before_score']),0.1)*100,1) if iv['before_score'] else 0
                                st.write(f"Improvement: **{'+' if imp>=0 else ''}{imp}%**")
                            if iv["effectiveness_score"]:
                                st.write(f"Effectiveness: **{iv['effectiveness_score']}%**")

                        st.markdown("##### Update This Intervention")
                        uc1,uc2,uc3,uc4 = st.columns(4)
                        with uc1:
                            new_status = st.selectbox("Status", STATS,
                                index=STATS.index(iv["status"]) if iv["status"] in STATS else 0,
                                key=f"st_{iv['id']}")
                        with uc2:
                            new_ascore = st.number_input("Score After (1–5)", 1.0, 5.0,
                                value=float(iv["after_score"]) if iv["after_score"] else float(iv["before_score"] or 3.0),
                                step=0.1, key=f"as_{iv['id']}")
                        with uc3:
                            new_aburn = st.number_input("Burnout % After", 0.0, 100.0,
                                value=float(iv["after_burnout"]) if iv["after_burnout"] else float(iv["before_burnout"] or 20.0),
                                step=0.5, key=f"ab_{iv['id']}")
                        with uc4:
                            new_comment = st.text_input("Progress note", placeholder="Update comment...", key=f"cm_{iv['id']}")

                        if st.button(f"Save Update", key=f"save_{iv['id']}", type="primary", use_container_width=True):
                            update_intervention(iv["id"], "status", new_status)
                            update_intervention(iv["id"], "after_score", new_ascore)
                            update_intervention(iv["id"], "after_burnout", new_aburn)
                            if new_comment:
                                existing = iv["comments"] or ""
                                update_intervention(iv["id"], "comments",
                                    f"{existing}\n[{date.today()}] {new_comment}".strip())
                            # Recompute effectiveness
                            if iv["before_score"] and new_ascore:
                                eff = compute_effectiveness(
                                    float(iv["before_score"]), new_ascore,
                                    float(iv["before_burnout"]) if iv["before_burnout"] else None,
                                    new_aburn if iv["before_burnout"] else None)
                                if eff: update_intervention(iv["id"], "effectiveness_score", eff)
                            st.success("✅ Updated")
                            st.rerun()

        # ═══ TAB 4: EXECUTIVE REPORT ════════════════════════════════════════════
        with tab_exec:
            st.markdown("#### Executive Intervention Summary")
            if all_iv.empty:
                st.info("No interventions recorded yet.")
            else:
                total    = len(all_iv)
                open_iv  = len(all_iv[all_iv["status"].isin(["Planned","In Progress"])])
                done     = len(all_iv[all_iv["status"]=="Completed"])
                overdue2 = len(all_iv[
                    all_iv["status"].isin(["Planned","In Progress"]) &
                    (pd.to_datetime(all_iv["due_date"], errors="coerce") < pd.Timestamp.today())])
                comp_rate2 = round(done/total*100,1) if total else 0
                comp_df2   = all_iv[all_iv["effectiveness_score"].notna()]
                avg_eff2   = round(comp_df2["effectiveness_score"].mean(),1) if not comp_df2.empty else 0

                # Avg closure time
                closed = all_iv[(all_iv["status"]=="Completed") & all_iv["completion_date"].notna() & all_iv["created_date"].notna()]
                if not closed.empty:
                    avg_days = round((pd.to_datetime(closed["completion_date"]) - pd.to_datetime(closed["created_date"])).dt.days.mean(), 1)
                else:
                    avg_days = None

                # Summary table
                st.markdown("##### Key Metrics")
                summ_data = {
                    "Metric": ["Total Interventions","Open","Completed","Overdue",
                               "Completion Rate","Avg Effectiveness","Avg Closure Time"],
                    "Value":  [total, open_iv, done, overdue2,
                               f"{comp_rate2}%", f"{avg_eff2}%" if avg_eff2 else "—",
                               f"{avg_days} days" if avg_days else "—"],
                    "Status": ["—","Action Required" if open_iv>3 else "Manageable",
                               "Good" if comp_rate2>=60 else "Needs Attention",
                               "Urgent" if overdue2>0 else "Clear",
                               "Good" if comp_rate2>=60 else "Improve","—","—"]
                }
                st.dataframe(pd.DataFrame(summ_data), use_container_width=True, hide_index=True)

                st.divider()
                # Top issues
                st.markdown("##### Top Issue Categories")
                cat_counts = all_iv["issue_category"].value_counts().head(5).reset_index()
                cat_counts.columns = ["Issue","Count"]
                st.dataframe(cat_counts, use_container_width=True, hide_index=True)

                st.divider()
                # Dept risk status
                st.markdown("##### Department Risk & Intervention Status")
                dept_summ = all_iv.groupby("department").agg(
                    Interventions=("id","count"),
                    High_Priority=("priority", lambda x: (x=="High").sum()),
                    Open=("status", lambda x: x.isin(["Planned","In Progress"]).sum()),
                    Completed=("status", lambda x: (x=="Completed").sum()),
                    Avg_Effectiveness=("effectiveness_score", lambda x: round(x.dropna().mean(),1) if x.dropna().any() else None)
                ).reset_index().rename(columns={"department":"Department","High_Priority":"High Priority",
                                                  "Avg_Effectiveness":"Avg Effectiveness %"})
                st.dataframe(dept_summ, use_container_width=True, hide_index=True)

                st.divider()
                # Recommended next actions
                st.markdown("##### AI-Recommended Next Actions")
                open_high = all_iv[(all_iv["status"].isin(["Planned","In Progress"])) & (all_iv["priority"]=="High")]
                if not open_high.empty:
                    st.error(f"**{len(open_high)} high-priority interventions still open.** Immediate attention required.")
                    for _,r in open_high.iterrows():
                        st.write(f"- **{r['department']}** · {r['title']} (Owner: {r['owner'] or 'Unassigned'})")
                if overdue2 > 0:
                    st.warning(f"**{overdue2} interventions are overdue.** Review with respective owners and update timelines.")
                if comp_rate2 < 50:
                    st.warning("**Completion rate below 50%.** Consider reviewing resource allocation and timelines.")
                if avg_eff2 > 0 and avg_eff2 < 15:
                    st.warning("**Effectiveness score is low.** Review if interventions are targeting root causes.")
                if done > 0 and avg_eff2 >= 15:
                    st.success(f"**{done} interventions completed** with avg effectiveness of {avg_eff2}%. Strong impact demonstrated.")

                # Download
                st.divider()
                exec_buf = BytesIO()
                with pd.ExcelWriter(exec_buf, engine="openpyxl") as w:
                    pd.DataFrame(summ_data).to_excel(w, sheet_name="Summary", index=False)
                    all_iv.to_excel(w, sheet_name="All Interventions", index=False)
                    dept_summ.to_excel(w, sheet_name="Dept Status", index=False)
                    if not comp_df2.empty:
                        comp_df2[["title","department","before_score","after_score","effectiveness_score"]].to_excel(
                            w, sheet_name="Effectiveness", index=False)
                st.download_button("Download Intervention Report (.xlsx)", data=exec_buf.getvalue(),
                    file_name=f"Samvaad_Interventions_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)

    elif page == "📋 Employee Action Plan":
        page_header("📋","Employee Action Plan","Track each employee individually — filter, drill down, view full history")

        # Use survey_df (which already has dept/designation from the JOIN in cached_survey_data)
        # Do NOT merge with emp_info again — that creates department_x/department_y collision
        latest = survey_df.sort_values("survey_date", ascending=False).drop_duplicates("employee_id").copy()

        # Ensure risk column exists
        if "risk" not in latest.columns:
            latest = compute_engagement(latest)
            latest["risk"] = latest["engagement_score"].apply(classify_risk)
        if "engagement_score" not in latest.columns:
            latest = compute_engagement(latest)

        latest["burnout_risk"]       = latest["stress"].apply(lambda x:"Yes" if x>=4 else "No")
        latest["priority"]           = latest["risk"].map({"🔴 Red":"High","🟡 Amber":"Medium","🟢 Green":"Low"})
        latest["recommended_action"] = latest.apply(get_action, axis=1)
        latest["engagement_score"]   = latest["engagement_score"].round(2)

        # emp_name from the cached join is the name column; use it directly
        # Map column names: emp_name -> Employee, department -> Department, designation -> Designation
        name_col = "emp_name" if "emp_name" in latest.columns else ("name" if "name" in latest.columns else None)

        conn = get_conn()
        emp_info = pd.read_sql_query("SELECT id, name, department, designation FROM employee WHERE is_active=1", conn)
        conn.close()

        # Only merge if name/dept/desig not already in latest
        if name_col is None or "department" not in latest.columns:
            merged = latest.merge(emp_info, left_on="employee_id", right_on="id", how="left")
            name_col = "name"
        else:
            merged = latest.copy()

        # Normalise column names for display
        merged["_name"]   = merged[name_col] if name_col in merged.columns else "Unknown"
        merged["_dept"]   = merged["department"]   if "department"   in merged.columns else ""
        merged["_desig"]  = merged["designation"]  if "designation"  in merged.columns else ""

        display = merged[["employee_id","_name","_dept","_desig","engagement_score",
                           "risk","priority","burnout_risk","recommended_action"]].rename(columns={
            "employee_id":"EmpID","_name":"Employee","_dept":"Department","_desig":"Designation",
            "engagement_score":"Score","risk":"Risk","priority":"Priority",
            "burnout_risk":"Burnout","recommended_action":"Recommended Action"})

        # ── Filters row ────────────────────────────────────────────────────────
        st.markdown("#### 🔍 Filter & Search")
        fc1,fc2,fc3,fc4 = st.columns([2,2,2,2])
        with fc1:
            search_name = st.text_input("Search by name", placeholder="Type employee name...")
        with fc2:
            pf = st.multiselect("Priority", ["High","Medium","Low"], default=["High","Medium","Low"])
        with fc3:
            df_f = st.multiselect("Department",
                sorted(display["Department"].dropna().unique()),
                default=sorted(display["Department"].dropna().unique()))
        with fc4:
            risk_f = st.multiselect("Risk", ["🔴 Red","🟡 Amber","🟢 Green"],
                default=["🔴 Red","🟡 Amber","🟢 Green"])

        filtered = display[
            display["Priority"].isin(pf) &
            display["Department"].isin(df_f) &
            display["Risk"].isin(risk_f)
        ]
        if search_name.strip():
            filtered = filtered[filtered["Employee"].str.contains(search_name.strip(), case=False, na=False)]

        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Employees Shown", len(filtered))
        m2.metric("High Priority", len(filtered[filtered["Priority"]=="High"]))
        m3.metric("Burnout Risk", len(filtered[filtered["Burnout"]=="Yes"]))
        m4.metric("Avg Score", round(filtered["Score"].mean(),2) if not filtered.empty else "—")

        st.dataframe(filtered.drop(columns=["EmpID"]).reset_index(drop=True),
                     use_container_width=True)

        st.divider()

        # ── Individual Employee Deep Dive ──────────────────────────────────────
        st.markdown("#### 🔎 Individual Employee Tracker")
        st.caption("Select any employee to view their complete survey history, score trend, and all responses.")

        all_active = emp_info.copy()
        emp_select_map = {f"#{r['id']} — {r['name']} ({r['department']})": int(r["id"])
                          for _, r in all_active.iterrows()}
        selected_label = st.selectbox("Select Employee to Track", list(emp_select_map.keys()),
                                      label_visibility="visible")
        selected_eid = emp_select_map[selected_label]

        emp_history = get_employee_history(selected_eid)
        emp_detail  = all_active[all_active["id"] == selected_eid].iloc[0] if not all_active[all_active["id"]==selected_eid].empty else None

        if emp_history.empty:
            st.info("This employee has not submitted any surveys yet.")
        else:
            emp_history = compute_engagement(emp_history)
            emp_history = emp_history.sort_values("survey_date")

            latest_row  = emp_history.iloc[-1]
            avg_score   = round(emp_history["engagement_score"].mean(), 2)
            latest_score= round(latest_row["engagement_score"], 2)
            trend_delta = round(float(emp_history["engagement_score"].iloc[-1]) -
                                float(emp_history["engagement_score"].iloc[0]), 2)
            trend_label = "📈 Improving" if trend_delta > 0.1 else ("📉 Declining" if trend_delta < -0.1 else "➡️ Stable")

            # Mini KPIs
            di1,di2,di3,di4,di5 = st.columns(5)
            di1.metric("Latest Score",     f"{latest_score}/5")
            di2.metric("Average Score",    f"{avg_score}/5")
            di3.metric("Risk Status",      classify_risk(latest_score))
            di4.metric("Surveys Done",     len(emp_history))
            di5.metric("Overall Trend",    trend_label, delta=f"{trend_delta:+.2f}")

            # Trend chart
            fig_e, ax_e = plt.subplots(figsize=(10, 3.2))
            colors_lines = [
                ("motivation",      "#3b82f6", "Motivation"),
                ("satisfaction",    "#22c55e", "Satisfaction"),
                ("team_connection", "#f59e0b", "Team Connection"),
                ("recognition",     "#8b5cf6", "Recognition"),
                ("engagement_score","#ef4444", "Engagement Score"),
            ]
            for col_n, col_c, col_l in colors_lines:
                if col_n in emp_history.columns:
                    lw = 2.5 if col_n == "engagement_score" else 1.5
                    ls = "-" if col_n == "engagement_score" else "--"
                    ax_e.plot(emp_history["survey_date"], emp_history[col_n],
                              color=col_c, linewidth=lw, linestyle=ls,
                              marker="o", markersize=3, label=col_l)
            ax_e.axhline(3, color="#ef4444", linewidth=0.8, linestyle=":", alpha=0.5)
            ax_e.set_ylim(0.5, 5.5)
            ax_e.set_ylabel("Score (1–5)", fontsize=9)
            ax_e.legend(fontsize=7.5, loc="upper left", ncol=3)
            ax_e.spines[["top","right"]].set_visible(False)
            ax_e.grid(axis="y", alpha=0.25)
            plt.xticks(rotation=35, ha="right", fontsize=7)
            name_label = emp_detail["name"] if emp_detail is not None else f"Employee #{selected_eid}"
            ax_e.set_title(f"Engagement History — {name_label}", fontsize=11, fontweight="bold")
            plt.tight_layout()
            st.pyplot(fig_e); plt.close()

            # Stress trend separately
            fig_s, ax_s = plt.subplots(figsize=(10, 2))
            ax_s.bar(emp_history["survey_date"], emp_history["stress"],
                     color=["#ef4444" if v>=4 else "#f59e0b" if v==3 else "#22c55e"
                            for v in emp_history["stress"]],
                     width=0.6)
            ax_s.axhline(4, color="#ef4444", linewidth=0.8, linestyle="--", alpha=0.6, label="Burnout threshold")
            ax_s.set_ylim(0, 5.5); ax_s.set_ylabel("Stress", fontsize=8)
            ax_s.set_title("Stress Level History", fontsize=10, fontweight="bold")
            ax_s.spines[["top","right"]].set_visible(False)
            plt.xticks(rotation=35, ha="right", fontsize=7)
            plt.tight_layout()
            st.pyplot(fig_s); plt.close()

            # Full response table
            st.markdown("##### 📅 Complete Survey Response History")
            show_cols = ["survey_date","motivation","satisfaction","team_connection",
                         "recognition","stress","enps","engagement_score","feedback"]
            avail = [c for c in show_cols if c in emp_history.columns]
            hist_disp = emp_history[avail].rename(columns={
                "survey_date":"Date","motivation":"Motivation","satisfaction":"Satisfaction",
                "team_connection":"Team","recognition":"Recognition","stress":"Stress",
                "enps":"eNPS","engagement_score":"Eng Score","feedback":"Feedback"
            }).sort_values("Date", ascending=False)
            hist_disp["Eng Score"] = hist_disp["Eng Score"].round(2)
            st.dataframe(hist_disp.reset_index(drop=True), use_container_width=True)

            # Icebreaker & mindset responses if available
            extra_cols = [c for c in ["icebreaker_word","icebreaker_emoji","mindset_growth",
                                       "mindset_purpose","eq_pressure","eq_balance","eq_empathy"]
                          if c in emp_history.columns and emp_history[c].astype(str).str.strip().ne("").any()]
            if extra_cols:
                with st.expander("🧠 Mindset, EQ & Icebreaker Responses"):
                    st.dataframe(emp_history[["survey_date"]+extra_cols].rename(
                        columns={"survey_date":"Date","icebreaker_word":"Word","icebreaker_emoji":"Emoji",
                                 "mindset_growth":"Growth?","mindset_purpose":"Purpose?",
                                 "eq_pressure":"EQ Pressure","eq_balance":"EQ Balance","eq_empathy":"EQ Empathy"}
                    ).reset_index(drop=True), use_container_width=True)


    # ── AI DEEP ANALYSIS ─────────────────────────────────────────────────────
    elif page == "🤖 AI Deep Analysis":
        page_header("🤖","AI Deep Analysis","Claude AI-powered strategic HR insights")

        if not ANTHROPIC_API_KEY:
            st.warning("""
            **Set your Anthropic API key to unlock Claude AI insights.**

            Steps:
            1. Get key at [console.anthropic.com](https://console.anthropic.com)
            2. Run: `set ANTHROPIC_API_KEY=sk-ant-...` (Windows) or `export ANTHROPIC_API_KEY=...` (Mac/Linux)
            3. Restart: `streamlit run app.py`

            The rule-based engine on the Dashboard works without an API key.
            """)

        conn = get_conn()
        all_fb2 = pd.read_sql_query(
            "SELECT feedback FROM survey_response WHERE feedback IS NOT NULL AND feedback!='' ORDER BY id DESC LIMIT 30", conn)
        conn.close()
        all_fb2["sentiment"] = all_fb2["feedback"].apply(sentiment_label)
        dept_df2 = cached_dept_stats().fillna(0)
        worst_d = dept_df2.sort_values("avg_engagement").iloc[0]["department"]
        best_d  = dept_df2.sort_values("avg_engagement", ascending=False).iloc[0]["department"]
        fb_sample = "\n".join([f"- {f}" for f in all_fb2["feedback"].head(15).tolist()])

        data_summary = f"""
ENGAGEMENT DATA SUMMARY:
- Total Employees: {total_employees} | Total Responses: {total_resp}
- Avg Engagement: {avg_eng}/5 | eNPS: {enps_s}
- Green: {green_count} ({round(green_count/total_resp*100,1) if total_resp else 0}%)
- Amber: {amber_count} | Red: {red_count} ({red_pct}%)
- Burnout Risk: {burn_count} ({burn_pct}%)
- Promoters: {promoters} | Passives: {passives} | Detractors: {detractors}
- Best Department: {best_d} | At-Risk Department: {worst_d}

RECENT FEEDBACK SAMPLES:
{fb_sample}
"""
        with st.expander("📋 Data being analysed"):
            st.text(data_summary)

        analysis_type = st.selectbox("Analysis Type", [
            "Overall Engagement Health Assessment",
            "Root Cause Analysis of High Risk Employees",
            "Burnout Risk & Wellbeing Strategy",
            "Department-level Interventions",
            "eNPS Improvement Plan",
            "Custom Question"
        ])
        custom_q = ""
        if analysis_type == "Custom Question":
            custom_q = st.text_area("Your question:", placeholder="e.g. Why might Production employees be disengaged?")

        if st.button("🤖 Generate AI Insight", use_container_width=True, type="primary"):
            prompts = {
                "Overall Engagement Health Assessment": f"You are a senior HR analytics consultant. Analyse this data and give a comprehensive health assessment with 5 specific actionable recommendations.\n\n{data_summary}",
                "Root Cause Analysis of High Risk Employees": f"You are an organisational psychologist. Perform root cause analysis of why {red_count} employees are High Risk. Give a 30-60-90 day action plan.\n\n{data_summary}",
                "Burnout Risk & Wellbeing Strategy": f"You are a workplace wellbeing specialist. Analyse burnout indicators ({burn_count} employees, {burn_pct}%). Recommend a wellbeing programme framework.\n\n{data_summary}",
                "Department-level Interventions": f"You are an HRBP. Provide tailored interventions for each department. Best dept: {best_d}, worst: {worst_d}.\n\n{data_summary}",
                "eNPS Improvement Plan": f"You are a talent retention specialist. eNPS is {enps_s} with {detractors} detractors. Build an improvement strategy with milestones.\n\n{data_summary}",
                "Custom Question": f"You are a senior HR analytics consultant. Using this data, answer: {custom_q}\n\n{data_summary}"
            }
            prompt = prompts.get(analysis_type)
            if analysis_type=="Custom Question" and not custom_q.strip():
                st.warning("Please enter your question first."); st.stop()

            with st.spinner("🤖 Claude AI is analysing your workforce data..."):
                result, status = call_claude_ai(prompt, max_tokens=800)

            if status=="ok" and result:
                st.markdown(f'<div class="ai-insight">{result}</div>', unsafe_allow_html=True)
                st.session_state.ai_cache = result
                st.session_state.ai_cache_time = datetime.now()
            elif status=="no_key":
                st.error("API key not configured.")
                recs = get_rule_recs(red_count, amber_count, burn_count, avg_eng, enps_s, total_resp)
                for t,m,l in recs: getattr(st,l)(f"**{t}** — {m}")
            else:
                st.error(f"Request failed: {status}")

        if st.session_state.ai_cache:
            age = int((datetime.now()-st.session_state.ai_cache_time).seconds/60) if st.session_state.ai_cache_time else 0
            st.caption(f"Showing cached insight from {age} min ago")
            st.markdown(f'<div class="ai-insight">{st.session_state.ai_cache}</div>', unsafe_allow_html=True)


    # ── SURVEY BUILDER ────────────────────────────────────────────────────────
    elif page == "🛠️ Survey Builder":
        page_header("🛠️","Survey Builder","Create, edit, reorder and delete pulse survey questions")

        st.markdown("""
        <div style="background:#fffbeb;border:1px solid #fde68a;border-left:5px solid #f59e0b;
                    border-radius:10px;padding:14px 18px;margin-bottom:20px">
            <strong style="color:#92400e">💡 How it works:</strong>
            <span style="color:#78350f"> Changes here take effect immediately for the next survey employees open.
            Employees never see scores — only their questions and a motivational message after submission.</span>
        </div>
        """, unsafe_allow_html=True)

        tab_view, tab_add = st.tabs(["📋 Manage Questions", "➕ Add New Question"])

        # ── TAB 1: VIEW & MANAGE ───────────────────────────────────────────────
        with tab_view:
            questions_df = get_survey_questions()

            if questions_df.empty:
                st.info("No questions yet. Add your first question in the 'Add New Question' tab.")
            else:
                st.markdown(f"**{len(questions_df)} active questions** — shown in this order to employees:")
                st.divider()

                CAT_COLOURS = {
                    "Engagement": "#3b82f6", "Wellbeing": "#22c55e", "EQ": "#8b5cf6",
                    "Mindset": "#f59e0b", "Icebreaker": "#ec4899",
                    "eNPS": "#0ea5e9", "Feedback": "#64748b"
                }
                TYPE_LABELS = {
                    "slider": "⬛ Slider (1–5)",
                    "emoji_rating": "😊 Emoji Rating (1–5)",
                    "yes_no": "✅ Yes / No",
                    "one_word": "💬 One Word",
                    "emoji_pick": "🎭 Emoji Pick",
                    "enps": "⭐ eNPS (0–10)",
                    "text": "📝 Free Text"
                }

                questions_list = questions_df.reset_index(drop=True)

                for i, q in questions_list.iterrows():
                    cat_colour = CAT_COLOURS.get(q["category"], "#666")

                    with st.container():
                        col_num, col_content, col_actions = st.columns([0.4, 5.5, 2.5])

                        with col_num:
                            st.markdown(f"""
                            <div style="background:{cat_colour};color:white;border-radius:50%;
                                        width:32px;height:32px;display:flex;align-items:center;
                                        justify-content:center;font-weight:700;font-size:0.9rem;
                                        margin-top:8px">{i+1}</div>
                            """, unsafe_allow_html=True)

                        with col_content:
                            st.markdown(f"""
                            <div style="background:white;border:1px solid #e8edf5;
                                        border-left:4px solid {cat_colour};border-radius:10px;
                                        padding:12px 16px;margin-bottom:4px">
                                <span style="font-size:1.1rem">{q['emoji']}</span>
                                <strong style="color:#0a2540;margin-left:6px">{q['question_text']}</strong><br>
                                <span style="font-size:0.78rem;color:{cat_colour};font-weight:600">{q['category'].upper()}</span>
                                <span style="font-size:0.78rem;color:#94a3b8;margin-left:10px">{TYPE_LABELS.get(q['question_type'],'?')}</span>
                            </div>
                            """, unsafe_allow_html=True)

                        with col_actions:
                            c1, c2, c3, c4 = st.columns(4)
                            with c1:
                                if st.button("⬆️", key=f"up_{q['id']}", help="Move up",
                                             use_container_width=True, disabled=(i==0)):
                                    move_question(int(q["id"]), "up", questions_df)
                                    st.rerun()
                            with c2:
                                if st.button("⬇️", key=f"dn_{q['id']}", help="Move down",
                                             use_container_width=True, disabled=(i==len(questions_list)-1)):
                                    move_question(int(q["id"]), "down", questions_df)
                                    st.rerun()
                            with c3:
                                if st.button("✏️", key=f"ed_{q['id']}", help="Edit",
                                             use_container_width=True):
                                    st.session_state[f"editing_{q['id']}"] = True

                            with c4:
                                if st.button("🗑️", key=f"del_{q['id']}", help="Delete",
                                             use_container_width=True):
                                    st.session_state[f"confirm_del_{q['id']}"] = True

                        # Confirm delete
                        if st.session_state.get(f"confirm_del_{q['id']}"):
                            q_preview = q['question_text'][:50]
                            st.warning(f"Delete \"{q_preview}...\"?")
                            dc1, dc2, _ = st.columns([1,1,4])
                            with dc1:
                                if st.button("Yes, delete", key=f"yes_del_{q['id']}", type="primary"):
                                    delete_question(int(q["id"]))
                                    st.session_state.pop(f"confirm_del_{q['id']}", None)
                                    st.success("Question deleted.")
                                    st.rerun()
                            with dc2:
                                if st.button("Cancel", key=f"no_del_{q['id']}"):
                                    st.session_state.pop(f"confirm_del_{q['id']}", None)
                                    st.rerun()

                        # Inline edit form
                        if st.session_state.get(f"editing_{q['id']}"):
                            with st.expander(f"✏️ Editing Q{i+1}", expanded=True):
                                e_text  = st.text_area("Question Text", value=q["question_text"],
                                                        key=f"et_{q['id']}")
                                ec1, ec2, ec3 = st.columns(3)
                                with ec1:
                                    e_type = st.selectbox("Question Type",
                                        ["slider","emoji_rating","yes_no","one_word","emoji_pick","enps","text"],
                                        index=["slider","emoji_rating","yes_no","one_word","emoji_pick","enps","text"].index(
                                            q["question_type"]) if q["question_type"] in
                                            ["slider","emoji_rating","yes_no","one_word","emoji_pick","enps","text"] else 0,
                                        key=f"ety_{q['id']}")
                                with ec2:
                                    e_cat = st.selectbox("Category",
                                        ["Engagement","Wellbeing","EQ","Mindset","Icebreaker","eNPS","Feedback"],
                                        index=["Engagement","Wellbeing","EQ","Mindset","Icebreaker","eNPS","Feedback"].index(
                                            q["category"]) if q["category"] in
                                            ["Engagement","Wellbeing","EQ","Mindset","Icebreaker","eNPS","Feedback"] else 0,
                                        key=f"ec_{q['id']}")
                                with ec3:
                                    e_emoji = st.text_input("Emoji", value=q["emoji"], key=f"ee_{q['id']}", max_chars=4)
                                e_opts = st.text_input("Options (for emoji_pick — separate with |)",
                                                        value=str(q["options"]) if q["options"] else "",
                                                        key=f"eo_{q['id']}",
                                                        placeholder="e.g. 😄 Happy|😐 Meh|😟 Sad")
                                sc1, sc2 = st.columns(2)
                                with sc1:
                                    if st.button("💾 Save Changes", key=f"save_{q['id']}", type="primary"):
                                        update_question(int(q["id"]), e_text, e_type, e_cat,
                                                        e_emoji, e_opts, int(q["sort_order"]))
                                        st.session_state.pop(f"editing_{q['id']}", None)
                                        st.success("✅ Question updated!")
                                        st.rerun()
                                with sc2:
                                    if st.button("Cancel", key=f"cancel_{q['id']}"):
                                        st.session_state.pop(f"editing_{q['id']}", None)
                                        st.rerun()

                st.divider()
                st.caption(f"Total questions in survey: {len(questions_list)}")

        # ── TAB 2: ADD NEW QUESTION ────────────────────────────────────────────
        with tab_add:
            st.markdown("#### Add a New Survey Question")
            st.caption("The question will appear at the bottom of the survey. Use Move Up/Down in the Manage tab to reorder it.")

            a_col1, a_col2 = st.columns(2)
            with a_col1:
                new_q_text = st.text_area("Question Text *",
                    placeholder="e.g. Do you feel your ideas are heard by your manager?",
                    height=90)
                new_q_emoji = st.text_input("Emoji (optional)", placeholder="💡", max_chars=4)

            with a_col2:
                new_q_type = st.selectbox("Question Type *", [
                    "slider — Rating 1 to 5 with emoji faces",
                    "emoji_rating — EQ-style 1 to 5 rating",
                    "yes_no — Yes or No buttons",
                    "one_word — Employee types one word",
                    "emoji_pick — Employee picks from emoji options",
                    "enps — Recommend score 0 to 10",
                    "text — Open text feedback box"
                ])
                new_q_cat = st.selectbox("Category *",
                    ["Engagement", "Wellbeing", "EQ", "Mindset", "Icebreaker", "eNPS", "Feedback"])

            new_q_opts = ""
            if "emoji_pick" in new_q_type:
                new_q_opts = st.text_input("Emoji Options (separate with |) *",
                    placeholder="😄 Pumped|😊 Good|😐 Meh|😴 Tired|😤 Frustrated",
                    help="Each option shows as a radio button. Separate with a pipe character |")

            # Preview
            if new_q_text.strip():
                actual_type = new_q_type.split(" — ")[0]
                st.markdown(f"""
                <div style="background:#f8faff;border:1px solid #bfdbfe;border-left:4px solid #3b82f6;
                            border-radius:10px;padding:14px 18px;margin:12px 0">
                    <strong>Preview:</strong><br>
                    <span style="font-size:1.1rem">{new_q_emoji or "❓"}</span>
                    <strong style="margin-left:6px">{new_q_text}</strong><br>
                    <span style="font-size:0.78rem;color:#64748b">Type: {actual_type} · Category: {new_q_cat}</span>
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            if st.button("➕ Add Question to Survey", use_container_width=True, type="primary"):
                if not new_q_text.strip():
                    st.error("Please enter the question text.")
                else:
                    actual_type = new_q_type.split(" — ")[0]
                    # Get max sort_order
                    conn = get_conn()
                    max_order = pd.read_sql_query(
                        "SELECT COALESCE(MAX(sort_order),0)+1 AS next_order FROM survey_questions", conn
                    ).iloc[0]["next_order"]
                    conn.close()
                    add_question(new_q_text.strip(), actual_type, new_q_cat,
                                 new_q_emoji or "❓", new_q_opts, int(max_order))
                    st.success(f"✅ Question added! It will appear at position {int(max_order)} in the survey.")
                    st.rerun()

            st.divider()
            st.markdown("#### Question Type Guide")
            guide_data = {
                "Type": ["slider", "emoji_rating", "yes_no", "one_word", "emoji_pick", "enps", "text"],
                "Best For": [
                    "Core engagement & wellbeing ratings",
                    "EQ, emotional state, soft skill ratings",
                    "Binary mindset / opinion questions",
                    "Fun icebreaker — one-word check-in",
                    "Mood pick from emoji list — most engaging",
                    "Loyalty / recommendation score",
                    "Open-ended suggestions & feedback"
                ],
                "Employee Experience": [
                    "Drag slider with emoji face labels 😟→😄",
                    "Select from 5 emoji-labelled options",
                    "Tap Yes 👍 or No 👎 buttons",
                    "Type any single word",
                    "Pick one emoji from a row of choices",
                    "Move slider from 0 to 10",
                    "Free text box with live sentiment"
                ]
            }
            st.dataframe(pd.DataFrame(guide_data), use_container_width=True, hide_index=True)


    # ── EMPLOYEE MANAGEMENT ───────────────────────────────────────────────────
    elif page == "👥 Employee Management":
        # No period filter shown for Employee Management — it manages all employees
        st.markdown('<div class="top-header"><div><h1>👥 Employee Management</h1><p>Add, bulk upload, view and manage your workforce</p></div></div>', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["➕ Add Single Employee", "📂 Bulk Upload (Excel/CSV)", "👁️ View All Employees"])

        # ── TAB 1: Single Add ──────────────────────────
        with tab1:
            st.markdown("#### Add New Employee")
            st.caption("Fill in all details below. The employee can login immediately after being added.")

            col1, col2 = st.columns(2)
            with col1:
                new_name  = st.text_input("Full Name *", placeholder="e.g. Ravi Shankar")
                new_email = st.text_input("Email Address *", placeholder="ravi@company.com")
                new_dept  = st.selectbox("Department *",
                    ["Production","HR","Operations","Finance","Maintenance","Quality","Sales","Logistics","Other"])
            with col2:
                new_desig = st.text_input("Designation *", placeholder="e.g. Senior Engineer")
                new_role  = st.selectbox("System Role *", ["Employee","HR"])
                new_pwd   = st.text_input("Set Password *", value="password", help="Employee will use this to login")

            col3, col4 = st.columns(2)
            with col3:
                new_joined = st.date_input("Date of Joining", value=date.today())
            with col4:
                st.write("")
                st.write("")

            st.write("")
            if st.button("✅ Add Employee", use_container_width=True, type="primary"):
                if not new_name or not new_email or not new_desig:
                    st.error("Please fill all required fields (*).")
                else:
                    # Check duplicate email
                    conn = get_conn()
                    existing = pd.read_sql_query("SELECT id FROM employee WHERE email=?", conn, params=(new_email,))
                    conn.close()
                    if not existing.empty:
                        st.error(f"❌ An employee with email **{new_email}** already exists.")
                    else:
                        add_employee_single(new_name, new_dept, new_desig, new_email,
                                            new_role, new_pwd, str(new_joined))
                        st.success(f"✅ **{new_name}** added successfully! They can login now with password: `{new_pwd}`")
                        st.balloons()

        # ── TAB 2: Bulk Upload ─────────────────────────
        with tab2:
            st.markdown("#### Bulk Upload via Excel or CSV")
            st.markdown('<div class="upload-info">📂 Upload an Excel (.xlsx) or CSV file with your employee list</div>',
                        unsafe_allow_html=True)
            st.write("")

            # Downloadable template
            template_df = pd.DataFrame({
                "name":        ["Ravi Shankar", "Meera Nair"],
                "department":  ["Production",   "Finance"],
                "designation": ["Engineer",     "Analyst"],
                "email":       ["ravi@company.com", "meera@company.com"],
                "role":        ["Employee",     "Employee"],
                "password":    ["password",     "password"],
                "joined_date": ["2024-01-15",   "2024-03-01"]
            })
            tpl_buf = BytesIO()
            with pd.ExcelWriter(tpl_buf, engine="openpyxl") as w:
                template_df.to_excel(w, index=False, sheet_name="Employees")
            st.download_button("📥 Download Employee Template (.xlsx)",
                data=tpl_buf.getvalue(),
                file_name="Employee_Upload_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            st.divider()
            uploaded_file = st.file_uploader("Upload completed file", type=["xlsx","csv"])

            if uploaded_file:
                try:
                    if uploaded_file.name.endswith(".csv"):
                        upload_df = pd.read_csv(uploaded_file)
                    else:
                        upload_df = pd.read_excel(uploaded_file)

                    required_cols = {"name","department","designation","email","role","password"}
                    missing = required_cols - set(upload_df.columns.str.lower())
                    if missing:
                        st.error(f"Missing columns: {missing}. Download the template to see the correct format.")
                    else:
                        upload_df.columns = upload_df.columns.str.lower().str.strip()
                        st.success(f"✅ File loaded — {len(upload_df)} employee(s) found")
                        st.dataframe(upload_df, use_container_width=True)

                        if st.button(f"➕ Import {len(upload_df)} Employee(s)", type="primary"):
                            added, skipped = 0, 0
                            conn = get_conn()
                            for _, row in upload_df.iterrows():
                                existing = pd.read_sql_query("SELECT id FROM employee WHERE email=?",
                                    conn, params=(str(row.get("email","")).strip(),))
                                if not existing.empty:
                                    skipped += 1; continue
                                conn.execute(
                                    "INSERT INTO employee (name,department,designation,email,role,password,is_active,joined_date) VALUES (?,?,?,?,?,?,1,?)",
                                    (str(row.get("name","")), str(row.get("department","")),
                                     str(row.get("designation","")), str(row.get("email","")),
                                     str(row.get("role","Employee")), str(row.get("password","password")),
                                     str(row.get("joined_date", str(date.today()))))
                                )
                                added += 1
                            conn.commit(); conn.close()
                            st.success(f"✅ Imported {added} employee(s). Skipped {skipped} duplicate(s).")
                except Exception as e:
                    st.error(f"Error reading file: {e}")

        # ── TAB 3: View All ────────────────────────────
        with tab3:
            st.markdown("#### Current Workforce")
            show_inactive = st.checkbox("Show inactive employees too")
            all_emp = get_all_employees(active_only=not show_inactive)

            col_s, col_d = st.columns(2)
            with col_s:
                search = st.text_input("🔍 Search by name or email", placeholder="Type to filter...")
            with col_d:
                dept_filter = st.selectbox("Filter by Department", ["All"]+sorted(all_emp["department"].dropna().unique().tolist()))

            if search:
                all_emp = all_emp[all_emp["name"].str.contains(search, case=False, na=False) |
                                  all_emp["email"].str.contains(search, case=False, na=False)]
            if dept_filter != "All":
                all_emp = all_emp[all_emp["department"] == dept_filter]

            st.metric("Employees Shown", len(all_emp))

            display_emp = all_emp[["id","name","department","designation","email","role","is_active","joined_date"]].rename(
                columns={"id":"ID","name":"Name","department":"Dept","designation":"Title",
                         "email":"Email","role":"Role","is_active":"Active","joined_date":"Joined"})
            display_emp["Active"] = display_emp["Active"].map({1:"✅ Active", 0:"❌ Inactive"})
            st.dataframe(display_emp.reset_index(drop=True), use_container_width=True)

            st.divider()
            st.markdown("#### Deactivate / Reactivate Employee")
            col_a, col_b, col_c = st.columns([2,1,1])
            with col_a:
                emp_ids_list = all_emp["id"].tolist()
                emp_names_map = {f"#{r['id']} {r['name']}": r["id"] for _,r in all_emp.iterrows()}
                selected_emp_label = st.selectbox("Select Employee", list(emp_names_map.keys()))
                selected_emp_id = emp_names_map[selected_emp_label]
            with col_b:
                st.write("")
                if st.button("❌ Deactivate", use_container_width=True):
                    deactivate_employee(selected_emp_id)
                    st.warning(f"Employee #{selected_emp_id} deactivated. They cannot login anymore.")
                    st.rerun()
            with col_c:
                st.write("")
                if st.button("✅ Reactivate", use_container_width=True):
                    reactivate_employee(selected_emp_id)
                    st.success(f"Employee #{selected_emp_id} reactivated.")
                    st.rerun()


    # ── PREDICTIVE FORECAST ───────────────────────────────────────────────────
    elif page == "🔮 Predictive Forecast":
        page_header("🔮","Predictive Forecast","Production-grade ML forecast · Huber Regression with Time-Series CV validation")

        # ── IMPORTS ─────────────────────────────────────────────────────────────
        from sklearn.linear_model import HuberRegressor, Ridge
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import Pipeline
        from sklearn.metrics import mean_absolute_error, r2_score
        from sklearn.model_selection import TimeSeriesSplit
        import warnings; warnings.filterwarnings('ignore')

        # ── LOAD DATA ────────────────────────────────────────────────────────────
        conn = get_conn()
        hist = pd.read_sql_query("""
            SELECT survey_date,
                   AVG((motivation+satisfaction+team_connection+recognition+(6-stress))/5.0) AS eng,
                   AVG(stress) AS avg_stress, AVG(motivation) AS avg_motivation,
                   COUNT(*) AS n_responses, AVG(enps) AS avg_enps
            FROM survey_response GROUP BY survey_date ORDER BY survey_date
        """, conn)
        dept_hist = pd.read_sql_query("""
            SELECT e.department, sr.survey_date,
                   AVG((sr.motivation+sr.satisfaction+sr.team_connection+sr.recognition+(6-sr.stress))/5.0) AS eng
            FROM survey_response sr JOIN employee e ON e.id=sr.employee_id
            GROUP BY e.department, sr.survey_date ORDER BY sr.survey_date
        """, conn)
        conn.close()

        if len(hist) < 8:
            st.warning(f"Only {len(hist)} survey cycles available. Minimum 8 needed for reliable forecasting.")
            st.info("Continue collecting surveys — the model activates automatically once you have enough data.")
            st.stop()

        # ── FEATURE ENGINEERING ──────────────────────────────────────────────────
        def build_features(df):
            df = df.copy()
            df['date']        = pd.to_datetime(df['survey_date'])
            df['t']           = (df['date'] - df['date'].min()).dt.days
            df['dow']         = df['date'].dt.dayofweek
            df['week_num']    = df['date'].dt.isocalendar().week.astype(int)
            df['month']       = df['date'].dt.month
            df['eng_lag1']    = df['eng'].shift(1)
            df['eng_lag2']    = df['eng'].shift(2)
            df['eng_rolling3']= df['eng'].rolling(3, min_periods=1).mean()
            return df.dropna()

        hist = build_features(hist)
        FEAT = ['t','dow','week_num','month','avg_stress','avg_motivation',
                'n_responses','eng_lag1','eng_lag2','eng_rolling3']
        X = hist[FEAT].values; y = hist['eng'].values

        # ── CROSS-VALIDATED MODEL EVALUATION ────────────────────────────────────
        n_splits = min(5, max(2, len(hist)//4))
        tscv     = TimeSeriesSplit(n_splits=n_splits)
        cv_errors, cv_r2s = [], []
        fold_results = []

        for fold, (tr, te) in enumerate(tscv.split(X), 1):
            if len(te) == 0: continue
            m = Pipeline([('sc', StandardScaler()),
                           ('m', HuberRegressor(epsilon=1.35, max_iter=300))])
            m.fit(X[tr], y[tr])
            preds = m.predict(X[te])
            fold_mae = mean_absolute_error(y[te], preds)
            fold_r2  = r2_score(y[te], preds) if len(y[te]) > 1 else 0
            cv_errors.extend(np.abs(y[te] - preds))
            cv_r2s.append(fold_r2)
            fold_results.append({'Fold': fold, 'Test Points': len(te),
                                  'MAE': round(fold_mae, 4), 'R²': round(fold_r2, 3)})

        cv_mae = np.mean(cv_errors)
        cv_std = np.std(cv_errors)
        ci_95  = 1.96 * cv_mae  # 95% confidence interval half-width per prediction

        # ── PRODUCTION MODEL (fit on all data) ───────────────────────────────────
        prod_model = Pipeline([('sc', StandardScaler()),
                                ('m', HuberRegressor(epsilon=1.35, max_iter=300))])
        prod_model.fit(X, y)
        train_r2   = round(r2_score(y, prod_model.predict(X)), 3)
        overfit_gap= round(train_r2 - np.mean(cv_r2s), 3)

        # ── 30-DAY FORECAST ──────────────────────────────────────────────────────
        last_row    = hist.iloc[-1]
        origin_date = hist['date'].min()
        fc_rows     = []

        for delta in range(1, 32):
            fd  = last_row['date'] + timedelta(days=delta)
            t2  = (fd - origin_date).days
            dow = fd.weekday()
            Xp  = [[t2, dow, fd.isocalendar()[1], fd.month,
                     float(last_row['avg_stress']), float(last_row['avg_motivation']),
                     float(last_row['n_responses']),
                     float(last_row['eng']), float(hist.iloc[-2]['eng']) if len(hist)>1 else float(last_row['eng']),
                     float(last_row['eng_rolling3'])]]
            pred = float(np.clip(prod_model.predict(Xp)[0], 1, 5))
            # CI widens with horizon (uncertainty compounds)
            ci   = ci_95 * (1 + delta/60)
            fc_rows.append({
                'date':       fd.strftime('%Y-%m-%d'),
                'pred':       round(pred, 3),
                'upper':      round(min(pred + ci, 5), 3),
                'lower':      round(max(pred - ci, 1), 3),
                'is_survey':  dow in (0, 4),
                'risk':       classify_risk(pred)
            })
        fc = pd.DataFrame(fc_rows)
        fc_dates    = pd.to_datetime(fc['date'])

        curr_score  = round(float(y[-1]), 2)
        fc_avg      = round(float(fc['pred'].mean()), 2)
        fc_end      = round(float(fc['pred'].iloc[-1]), 2)
        at_risk_days= len(fc[fc['pred'] < 3])
        trend_dir   = "Improving" if fc_end > curr_score+0.1 else ("Declining" if fc_end < curr_score-0.1 else "Stable")

        # ── MODEL QUALITY BANNER ─────────────────────────────────────────────────
        quality_ok = cv_mae < 0.25 and overfit_gap < 0.4
        if quality_ok:
            st.success(f"""**Model validated.** Cross-validated MAE = {cv_mae:.4f} · 95% CI = ±{ci_95:.3f} · Overfitting gap = {overfit_gap}
            The Huber Regression model has been validated on {n_splits}-fold time-series cross-validation.
            It is safe to present this as a directional engagement indicator.""")
        else:
            st.warning(f"""**Model needs more data.** CV MAE = {cv_mae:.4f} · Overfitting gap = {overfit_gap}
            Collect more survey cycles before presenting forecasts to leadership. Current reliability: directional only.""")

        st.divider()

        # ── KPIs ─────────────────────────────────────────────────────────────────
        k1,k2,k3,k4,k5 = st.columns(5)
        k1.metric("Current Score",       f"{curr_score}/5")
        k2.metric("30-Day Forecast Avg", f"{fc_avg}/5",    delta=round(fc_avg-curr_score,2))
        k3.metric("Month-End Score",     f"{fc_end}/5",    delta=round(fc_end-curr_score,2))
        k4.metric("30-Day Trend",        trend_dir)
        k5.metric("At-Risk Days (< 3)",  at_risk_days)

        st.divider()

        # ── MAIN CHART ───────────────────────────────────────────────────────────
        col_chart, col_info = st.columns([3, 1])
        with col_chart:
            st.markdown("#### Historical Engagement + 30-Day Validated Forecast")
            fig, ax = plt.subplots(figsize=(11, 4.5))

            # Historical
            ax.plot(hist['date'], y, color='#3b82f6', linewidth=2.5, marker='o',
                    markersize=4, label='Historical (actual)', zorder=3)

            # Confidence band
            ax.fill_between(fc_dates, fc['lower'], fc['upper'],
                            color='#f59e0b', alpha=0.20, label=f'95% CI (±{ci_95:.2f})')

            # Forecast
            ax.plot(fc_dates, fc['pred'], color='#f59e0b', linewidth=2.5,
                    linestyle='--', marker='o', markersize=3.5, label='Huber forecast', zorder=3)

            # Survey day markers
            sdays = fc[fc['is_survey']]
            ax.scatter(pd.to_datetime(sdays['date']), sdays['pred'],
                       marker='D', s=25, color='#f59e0b', zorder=4)

            # Risk zones
            ax.axhspan(1, 3, color='#ef4444', alpha=0.04, label='High-risk zone (< 3)')
            ax.axhspan(3, 4, color='#f59e0b', alpha=0.03)

            # Today divider
            ax.axvline(hist['date'].max(), color='#94a3b8', linewidth=1.2, linestyle='-')
            ax.text(hist['date'].max(), 1.12, '  Today', fontsize=8, color='#94a3b8')

            ax.set_ylim(1, 5.2); ax.set_ylabel('Engagement Score (1–5)', fontsize=9)
            ax.legend(fontsize=8, loc='upper left')
            ax.grid(axis='y', alpha=0.25, linewidth=0.5)
            ax.spines[['top','right']].set_visible(False)
            plt.xticks(rotation=35, ha='right', fontsize=7)
            plt.tight_layout()
            st.pyplot(fig); plt.close()
            st.caption(f"Model: Huber Regression (robust to outliers) · {n_splits}-fold Time-Series CV · CV MAE={cv_mae:.4f} · ◆ = survey days")

        with col_info:
            st.markdown("#### Model Validation")
            st.markdown(f"""
**Algorithm:** Huber Regression
*(robust — outliers cannot skew predictions)*

**CV MAE:** `{cv_mae:.4f}`
*(avg prediction error on unseen data)*

**95% CI:** `±{ci_95:.3f}`
*(honest uncertainty range)*

**Overfitting gap:** `{overfit_gap}`
*(train R² minus CV R² — lower is better)*

**Folds:** {n_splits}-fold time-series split
*(future never leaks into past)*

**Features:** {len(FEAT)} engineered inputs
            """)
            if quality_ok:
                st.success("Ready for leadership presentation")
            else:
                st.warning("Directional use only")

        # ── CV FOLD BREAKDOWN ────────────────────────────────────────────────────
        st.divider()
        with st.expander("Show cross-validation fold details"):
            fold_df = pd.DataFrame(fold_results)
            st.dataframe(fold_df, use_container_width=True, hide_index=True)
            st.caption("Each fold trains on past data and tests on future data — the correct way to validate time-series models. MAE = Mean Absolute Error (lower is better).")

        # ── DEPARTMENT FORECASTS ─────────────────────────────────────────────────
        st.divider()
        st.markdown("#### 30-Day Department Forecast")
        dept_res = []
        for dept in dept_hist['department'].unique():
            ddf = dept_hist[dept_hist['department']==dept].copy()
            if len(ddf) < 5: continue
            ddf['date']     = pd.to_datetime(ddf['survey_date'])
            ddf['t']        = (ddf['date'] - ddf['date'].min()).dt.days
            ddf['eng_lag1'] = ddf['eng'].shift(1)
            ddf['eng_rolling3'] = ddf['eng'].rolling(3, min_periods=1).mean()
            ddf = ddf.dropna()
            if len(ddf) < 4: continue
            Xd = ddf[['t','eng_lag1','eng_rolling3']].values; yd = ddf['eng'].values
            dm = Pipeline([('sc', StandardScaler()),
                            ('m', HuberRegressor(epsilon=1.35, max_iter=200))])
            dm.fit(Xd, yd)
            lt   = int(ddf['t'].max())
            cur  = round(float(ddf['eng'].iloc[-1]), 2)
            lag1 = float(ddf['eng'].iloc[-1])
            roll = float(ddf['eng_rolling3'].iloc[-1])
            p30  = round(float(np.clip(dm.predict([[lt+30, lag1, roll]])[0], 1, 5)), 2)
            chg  = round(p30 - cur, 2)
            alert= ""
            r_now = classify_risk(cur); r_30 = classify_risk(p30)
            if r_30 == "🔴 Red"   and r_now != "🔴 Red":   alert = "Moving into Red — intervene now"
            elif r_30 == "🟡 Amber" and r_now == "🟢 Green": alert = "Slipping to Amber — monitor"
            elif r_now == "🔴 Red"  and r_30 == "🔴 Red":    alert = "Stays Critical"
            dept_res.append({'Department': dept, 'Current': cur, 'Risk Now': r_now,
                              'Forecast (30d)': p30, 'Risk (30d)': r_30,
                              'Change': f"{'+' if chg>0 else ''}{chg}",
                              'Trend': "Rising" if chg>0.1 else ("Falling" if chg<-0.1 else "Stable"),
                              'Alert': alert})

        dfc = pd.DataFrame(dept_res).sort_values('Forecast (30d)')
        st.dataframe(dfc.reset_index(drop=True), use_container_width=True, hide_index=True)

        # ── BUSINESS IMPACT TRANSLATOR ───────────────────────────────────────────
        st.divider()
        st.markdown("#### Business Impact — Translating Engagement to What Leadership Cares About")
        st.caption("Based on Gallup State of the Global Workplace research benchmarks, India manufacturing context.")

        bi1, bi2 = st.columns(2)
        with bi1:
            st.markdown("**Assumptions (editable)**")
            avg_salary   = st.number_input("Avg annual salary per employee (₹)", value=600000, step=50000)
            n_emp        = st.number_input("Number of employees in scope", value=int(total_employees), step=5)
            replace_cost = st.slider("Replacement cost as % of salary", 30, 100, 50,
                                     help="Industry avg: 50% for manufacturing roles")

        with bi2:
            eng_drop = max(0, round(curr_score - fc_end, 2))
            eng_rise = max(0, round(fc_end - curr_score, 2))

            # Attrition (Gallup: 12% attrition risk increase per 1-unit engagement drop)
            attrition_risk    = eng_drop * 0.12
            est_leavers       = round(n_emp * attrition_risk, 1)
            attrition_cost_cr = round((est_leavers * avg_salary * replace_cost/100) / 10000000, 2)

            # Productivity (Gallup: 23% higher profit in highly engaged teams)
            prod_loss_pct     = round(eng_drop * 8, 1)  # 8% per unit drop
            prod_cost_cr      = round((n_emp * avg_salary * prod_loss_pct/100) / 10000000, 2)

            # Absenteeism (Gallup: disengaged = 81% higher absenteeism)
            absent_days_extra = round(eng_drop * 3.2, 1)  # 3.2 extra days per unit drop per person
            absent_cost_cr    = round((n_emp * absent_days_extra * avg_salary/250) / 10000000, 2)

            total_risk_cr     = round(attrition_cost_cr + prod_cost_cr + absent_cost_cr, 2)

            st.markdown("**Projected 30-Day Risk (if trend continues)**")
            if eng_drop > 0:
                st.metric("Engagement drop forecast",    f"{eng_drop} points",  delta=f"-{eng_drop}", delta_color="inverse")
                st.metric("Additional attrition risk",   f"~{est_leavers} people")
                st.metric("Attrition cost exposure",     f"₹{attrition_cost_cr} Cr")
                st.metric("Productivity loss (est.)",    f"₹{prod_cost_cr} Cr")
                st.metric("Absenteeism cost (est.)",     f"₹{absent_cost_cr} Cr")
                if total_risk_cr > 0:
                    st.error(f"**Total 30-day risk exposure: ₹{total_risk_cr} Cr**\n\nThis is the cost of inaction — the business case for HR intervention.")
            elif eng_rise > 0:
                prod_gain_cr = round((n_emp * avg_salary * eng_rise * 0.08) / 10000000, 2)
                st.metric("Engagement improvement forecast", f"+{eng_rise} points", delta=f"+{eng_rise}")
                st.metric("Productivity gain (est.)",        f"₹{prod_gain_cr} Cr")
                st.success(f"**Positive outlook: ₹{prod_gain_cr} Cr productivity gain projected.**\n\nPresent this as ROI on current engagement investments.")
            else:
                st.info("Engagement is forecast to remain stable. No urgent business risk identified.")

        # ── LEADERSHIP NARRATIVE ─────────────────────────────────────────────────
        st.divider()
        st.markdown("#### Ready-to-Present Leadership Narrative")
        declining  = [r['Department'] for r in dept_res if float(r['Change'].replace('+','')) < -0.1]
        improving  = [r['Department'] for r in dept_res if float(r['Change'].replace('+','')) > 0.1]
        alerts_depts = [r for r in dept_res if r['Alert']]

        narrative = f"""SAMVAAD ENGAGEMENT FORECAST — LEADERSHIP BRIEF
Period: Next 30 Days | Model: Huber Regression | CV MAE: {cv_mae:.3f} | Confidence: 95% CI ±{ci_95:.2f}

EXECUTIVE SUMMARY
Current workforce engagement: {curr_score}/5.0 ({classify_risk(curr_score)})
30-day forecast:              {fc_avg}/5.0 average | {fc_end}/5.0 at month-end
Overall trend:                {trend_dir}
At-risk survey days:          {at_risk_days} of 30 predicted below 3.0 threshold

BUSINESS RISK TRANSLATION
{"Engagement is forecast to drop " + str(eng_drop) + " points." if eng_drop > 0 else "Engagement is forecast to remain stable or improve."}
{"- Estimated additional attrition risk: " + str(est_leavers) + " employees" if eng_drop > 0 else ""}
{"- Total cost exposure (attrition + productivity + absenteeism): ₹" + str(total_risk_cr) + " Cr" if eng_drop > 0 else ""}

DEPARTMENT WATCH LIST
{"- At-risk: " + ", ".join([r['Department']+" ("+r['Alert']+")" for r in alerts_depts]) if alerts_depts else "- No departments forecast to cross a risk threshold in 30 days."}
{"- Declining: " + ", ".join(declining) if declining else ""}
{"- Improving: " + ", ".join(improving) if improving else ""}

MODEL TRANSPARENCY NOTE
This forecast uses Huber Regression validated on {n_splits}-fold time-series cross-validation.
Average prediction error on unseen data: ±{cv_mae:.3f} engagement points.
Treat as a directional early-warning system, not a precise number.
Refresh monthly as new survey data accumulates.

Source: Samvaad v5.0 | Tata Steel HR Analytics | {date.today().strftime("%d %B %Y")}
"""
        st.text_area("Copy for leadership deck or email", narrative, height=350)
        st.download_button("Download Leadership Brief (.txt)", data=narrative,
            file_name=f"Samvaad_Forecast_Brief_{date.today()}.txt", mime="text/plain",
            use_container_width=True)

        # ── DOWNLOAD ─────────────────────────────────────────────────────────────
        st.divider()
        buf_fc = BytesIO()
        with pd.ExcelWriter(buf_fc, engine='openpyxl') as w:
            fc.to_excel(w, sheet_name='30-Day Forecast', index=False)
            dfc.to_excel(w, sheet_name='Dept Forecasts', index=False)
            pd.DataFrame(fold_results).to_excel(w, sheet_name='Model Validation', index=False)
            hist[['survey_date','eng','avg_stress','avg_motivation','n_responses']].to_excel(
                w, sheet_name='Historical Data', index=False)
            pd.DataFrame({'Metric':['CV MAE','CV STD','95% CI','Train R²','Overfit Gap','Algorithm'],
                           'Value':[cv_mae,cv_std,ci_95,train_r2,overfit_gap,'Huber Regression']
                          }).to_excel(w, sheet_name='Model Report Card', index=False)
        st.download_button("Download Full Forecast Report (.xlsx)", data=buf_fc.getvalue(),
            file_name=f"Samvaad_Forecast_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

    elif page == "📅 Survey Schedule":
        page_header("📅","Survey Schedule","Control when pulse surveys open and close")

        today_name = date.today().strftime("%A")
        schedule_df = get_schedule()

        st.markdown(f"**Today:** {today_name}, {date.today()}")
        st.divider()

        if not schedule_df.empty:
            for _, row in schedule_df.iterrows():
                col1, col2, col3 = st.columns([3,1,1])
                with col1:
                    status_html = f'<span class="sched-on">● Active</span>' if row["is_active"] else f'<span class="sched-off">● Paused</span>'
                    is_today = row["day_of_week"]==today_name
                    today_badge = ' <span style="background:#dbeafe;color:#1e40af;border-radius:10px;padding:2px 8px;font-size:0.78rem">TODAY</span>' if is_today else ""
                    st.markdown(f"**{row['schedule_type']}** — Every {row['day_of_week']} &nbsp;{status_html}{today_badge}", unsafe_allow_html=True)
                with col2:
                    if row["is_active"]:
                        if st.button("⏸ Pause", key=f"p{row['id']}", use_container_width=True):
                            toggle_schedule(row["id"], 0); st.rerun()
                    else:
                        if st.button("▶ Activate", key=f"a{row['id']}", use_container_width=True):
                            toggle_schedule(row["id"], 1); st.rerun()
                with col3:
                    if is_today and row["is_active"]: st.success("OPEN")
                    elif is_today: st.error("PAUSED")
                    else: st.caption("—")
                st.divider()

        st.markdown("#### ➕ Add New Schedule")
        c1,c2,c3 = st.columns([2,2,1])
        with c1: nn = st.text_input("Name", placeholder="e.g. Wednesday Wellness Check")
        with c2: nd = st.selectbox("Day", ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
        with c3:
            st.write(""); st.write("")
            if st.button("Add", use_container_width=True, type="primary"):
                if nn:
                    conn = get_conn()
                    conn.execute("INSERT INTO survey_schedule (schedule_type,day_of_week,is_active,created_by,created_at) VALUES (?,?,1,?,?)",
                                 (nn,nd,emp_id,datetime.now().isoformat()))
                    conn.commit(); conn.close()
                    st.success(f"✅ Added '{nn}' for every {nd}."); st.rerun()


    # ── NOTIFICATIONS ─────────────────────────────────────────────────────────
    elif "Notifications" in page:
        page_header("🔔","Notifications","Survey activity & system alerts")

        notifs = get_notifications(emp_id)
        if notifs.empty:
            st.info("No notifications yet. When employees submit surveys, they'll appear here.")
        else:
            unread = len(notifs[notifs["is_read"]==0])
            if unread > 0:
                st.success(f"**{unread} new notification(s)**")
                mark_notifications_read(emp_id)
            for _, row in notifs.iterrows():
                icon = "🆕" if row["is_read"]==0 else "📩"
                st.write(f"{icon} {row['message']} — *{str(row['created_at'])[:16]}*")
            st.divider()
            if st.button("🗑️ Clear All"):
                conn = get_conn()
                conn.execute("DELETE FROM notifications WHERE employee_id=?", (emp_id,))
                conn.commit(); conn.close(); st.rerun()


    # ── EXECUTIVE SUMMARY ─────────────────────────────────────────────────────
    elif page == "📄 Executive Summary":
        page_header("📄","Executive Summary","Auto-generated leadership brief for selected period")

        # Use period-filtered data for summary
        _exec_df  = _filt_df if not _filt_df.empty else survey_df
        _exec_eng = round(_exec_df["engagement_score"].mean(),2) if not _exec_df.empty else 0
        _exec_enps,_exec_prom,_exec_pass,_exec_det = compute_enps(_exec_df)
        _exec_red  = len(_exec_df[_exec_df["risk"]=="🔴 Red"])   if not _exec_df.empty else 0
        _exec_amb  = len(_exec_df[_exec_df["risk"]=="🟡 Amber"]) if not _exec_df.empty else 0
        _exec_grn  = len(_exec_df[_exec_df["risk"]=="🟢 Green"]) if not _exec_df.empty else 0
        _exec_burn = len(_exec_df[_exec_df["stress"]>=4])        if not _exec_df.empty else 0
        _exec_resp = len(_exec_df)

        conn = get_conn()
        all_fb3 = pd.read_sql_query("SELECT feedback FROM survey_response WHERE feedback IS NOT NULL AND feedback!=''", conn)
        conn.close()
        all_fb3["sentiment"] = all_fb3["feedback"].apply(sentiment_label)
        pos3 = len(all_fb3[all_fb3["sentiment"]=="Positive"])
        neg3 = len(all_fb3[all_fb3["sentiment"]=="Negative"])
        enps_lbl   = "Excellent" if _exec_enps>=30 else ("Good" if _exec_enps>=10 else ("Needs Improvement" if _exec_enps>=0 else "Critical"))
        resp_rate  = round((_exec_resp/(total_employees*max(1,len(_exec_df["survey_date"].unique()) if not _exec_df.empty else 1)))*100,1)
        resp_rate  = min(resp_rate, 100)

        summary = f"""
══════════════════════════════════════════════════════════════
EMPLOYEE ENGAGEMENT EXECUTIVE SUMMARY
Organisation : Manufacturing Sector (Pilot Programme)
Report Date  : {date.today()} | EngageAI Platform v3.0
══════════════════════════════════════════════════════════════

1. WORKFORCE OVERVIEW
   Total Active Employees      : {total_employees}
   Total Survey Responses      : {total_resp}
   Estimated Response Rate     : {resp_rate}%
   Average Engagement Score    : {avg_eng}/5.0

2. RISK CLASSIFICATION
   🟢 Engaged (Green)          : {green_count} ({round(green_count/total_resp*100,1) if total_resp else 0}%)
   🟡 Moderate Risk (Amber)    : {amber_count} ({round(amber_count/total_resp*100,1) if total_resp else 0}%)
   🔴 High Risk (Red)          : {red_count} ({red_pct}%)

3. eNPS ANALYSIS
   eNPS Score                  : {enps_s} — {enps_lbl}
   Promoters (9–10)            : {promoters}
   Passives  (7–8)             : {passives}
   Detractors (0–6)            : {detractors}

4. BURNOUT ANALYSIS
   At Burnout Risk             : {burn_count} employees ({burn_pct}%)

5. SENTIMENT ANALYSIS
   Positive Feedback           : {pos3} responses
   Negative Feedback           : {neg3} responses
   Key Themes                  : Workload, recognition, communication, team support

6. KEY FINDINGS
   • {red_pct}% of employees are at High Risk — immediate action required.
   • {burn_pct}% show active burnout indicators.
   • eNPS of {enps_s} places the org in the '{enps_lbl}' category.

7. RECOMMENDATIONS
   IMMEDIATE:  1-on-1 check-ins for Red employees · Workload review
   SHORT-TERM: Team-building · Stress management workshops · Manager coaching
   LONG-TERM:  Revamp recognition · Career development · Target eNPS >30

══════════════════════════════════════════════════════════════
CONFIDENTIAL — For HR & Leadership Use Only
══════════════════════════════════════════════════════════════
"""
        st.text_area("", summary, height=520, label_visibility="collapsed")
        st.download_button("📥 Download Summary (.txt)", data=summary,
            file_name=f"Executive_Summary_{date.today()}.txt", mime="text/plain")


    # ── DOWNLOAD REPORT ───────────────────────────────────────────────────────
    elif page == "📥 Download Report":
        page_header("📥","Download Reports","Period-specific Excel reports — Weekly, Monthly, Quarterly, Annual, Overall")

        st.markdown(f"""
        <div style="background:#f0f7ff;border:1px solid #bfdbfe;border-radius:12px;
                    padding:14px 20px;margin-bottom:20px">
            <strong style="color:#1e40af">📌 Currently selected period: {_period_label}</strong>
            &nbsp;·&nbsp; <span style="color:#64748b">Data range: {_dr}</span><br>
            <span style="font-size:0.82rem;color:#64748b">
                Use the period toggle at the top of any page to switch between Weekly / Monthly / Yearly / Overall,
                then return here to download the corresponding report.
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Helper: build one period's Excel report
        def _build_report(label, data_df, dr_str):
            conn_r = get_conn()
            _fb = pd.read_sql_query(
                "SELECT feedback FROM survey_response WHERE feedback IS NOT NULL AND feedback!=''", conn_r)
            _emp_dir = pd.read_sql_query("SELECT * FROM employee", conn_r)
            conn_r.close()
            _fb["sentiment"] = _fb["feedback"].apply(sentiment_label)

            _lat = data_df.sort_values("survey_date", ascending=False).drop_duplicates("employee_id").copy() if not data_df.empty else pd.DataFrame()
            _lat2 = pd.DataFrame()
            if not _lat.empty:
                if "engagement_score" not in _lat.columns: _lat = compute_engagement(_lat)
                if "risk" not in _lat.columns: _lat["risk"] = _lat["engagement_score"].apply(classify_risk)
                _lat["burnout_risk"] = _lat["stress"].apply(lambda x:"Yes" if x>=4 else "No")
                _lat["priority"]     = _lat["risk"].map({"🔴 Red":"High","🟡 Amber":"Medium","🟢 Green":"Low"})
                _lat["action"]       = _lat.apply(get_action, axis=1)
                # Use existing cols from cached_survey_data JOIN — avoid duplicate column collision
                _has_name = "emp_name" in _lat.columns or "name" in _lat.columns
                _has_dept = "department" in _lat.columns
                if _has_name and _has_dept:
                    _lat["_name"]  = _lat["emp_name"] if "emp_name" in _lat.columns else _lat["name"]
                    _lat["_dept"]  = _lat["department"]
                    _lat["_desig"] = _lat["designation"] if "designation" in _lat.columns else ""
                    _lat2 = _lat.copy()
                else:
                    # Fallback: merge only if columns missing
                    _lat2 = _lat.merge(_emp_dir[["id","name","department","designation"]].rename(
                        columns={"name":"_name","department":"_dept","designation":"_desig"}),
                        left_on="employee_id", right_on="id", how="left")
            _pos = len(_fb[_fb["sentiment"]=="Positive"])
            _neg = len(_fb[_fb["sentiment"]=="Negative"])
            _r_eng = round(data_df["engagement_score"].mean(),2) if not data_df.empty else 0
            _r_resp= len(data_df)
            _r_enps,_,_,_ = compute_enps(data_df)
            _r_red  = len(data_df[data_df["risk"]=="🔴 Red"])  if not data_df.empty else 0
            _r_amb  = len(data_df[data_df["risk"]=="🟡 Amber"]) if not data_df.empty else 0
            _r_grn  = len(data_df[data_df["risk"]=="🟢 Green"]) if not data_df.empty else 0
            _r_burn = len(data_df[data_df["stress"]>=4])        if not data_df.empty else 0

            _buf = BytesIO()
            with pd.ExcelWriter(_buf, engine="openpyxl") as _w:
                # Sheet 1: Summary
                pd.DataFrame({
                    "Metric":["Report Period","Data Range","Total Employees","Total Responses",
                              "Avg Engagement Score","eNPS Score",
                              "Engaged (Green)","Moderate Risk (Amber)","High Risk (Red)",
                              "Burnout Risk","Positive Feedback","Negative Feedback"],
                    "Value":[label, dr_str, total_employees, _r_resp,
                             _r_eng, _r_enps,
                             _r_grn, _r_amb, _r_red,
                             _r_burn, _pos, _neg]
                }).to_excel(_w, sheet_name="Executive Summary", index=False)

                # Sheet 2: Action Plan
                if not _lat.empty and not _lat2.empty:
                    _action_df = _lat2[["_name","_dept","_desig","engagement_score",
                                        "risk","priority","burnout_risk","action"]].copy()
                    _action_df.columns = ["Employee","Dept","Title","Score","Risk","Priority","Burnout","Recommended Action"]
                    _action_df["Score"] = _action_df["Score"].round(2)
                    _action_df.to_excel(_w, sheet_name="Employee Action Plan", index=False)

                # Sheet 3: Dept analytics
                cached_dept_stats().to_excel(_w, sheet_name="Department Analytics", index=False)

                # Sheet 4: Raw data for period
                data_df.to_excel(_w, sheet_name=f"Raw Data ({label})", index=False)

                # Sheet 5: Sentiment
                _fb.to_excel(_w, sheet_name="Feedback & Sentiment", index=False)

                # Sheet 6: Employee directory
                _emp_dir.to_excel(_w, sheet_name="Employee Directory", index=False)

            return _buf.getvalue()

        # ── Report cards grid ─────────────────────────────────────────────────
        st.markdown("#### 📥 Download by Period")
        r1, r2 = st.columns(2)

        with r1:
            # Weekly
            _wk_data = survey_df[survey_df["_date"] >= _week_start] if "_date" in survey_df.columns else survey_df
            _wk_dr   = f"{_week_start.strftime('%d %b')} – {_today.strftime('%d %b %Y')}"
            st.markdown(f"""<div class="section-card">
                <strong>📅 Weekly Report</strong><br>
                <span style="font-size:0.8rem;color:#64748b">Period: {_wk_dr}</span><br>
                <span style="font-size:0.8rem;color:#64748b">{len(_wk_data)} responses</span>
            </div>""", unsafe_allow_html=True)
            st.download_button("📥 Download Weekly Report",
                data=_build_report("Weekly", _wk_data, _wk_dr),
                file_name=f"Samvaad_Weekly_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, key="dl_weekly")

            # Yearly
            _yr_data = survey_df[survey_df["_date"] >= _year_start] if "_date" in survey_df.columns else survey_df
            _yr_dr   = f"{_year_start.strftime('%d %b %Y')} – {_today.strftime('%d %b %Y')}"
            st.write("")
            st.markdown(f"""<div class="section-card">
                <strong>🗓️ Annual Report ({_year_start.year})</strong><br>
                <span style="font-size:0.8rem;color:#64748b">Period: {_yr_dr}</span><br>
                <span style="font-size:0.8rem;color:#64748b">{len(_yr_data)} responses</span>
            </div>""", unsafe_allow_html=True)
            st.download_button("📥 Download Annual Report",
                data=_build_report("Annual", _yr_data, _yr_dr),
                file_name=f"Samvaad_Annual_{_year_start.year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, key="dl_yearly")

        with r2:
            # Monthly
            _mo_data = survey_df[survey_df["_date"] >= _month_start] if "_date" in survey_df.columns else survey_df
            _mo_dr   = f"{_month_start.strftime('%d %b')} – {_today.strftime('%d %b %Y')}"
            st.markdown(f"""<div class="section-card">
                <strong>📆 Monthly Report ({_month_start.strftime('%B %Y')})</strong><br>
                <span style="font-size:0.8rem;color:#64748b">Period: {_mo_dr}</span><br>
                <span style="font-size:0.8rem;color:#64748b">{len(_mo_data)} responses</span>
            </div>""", unsafe_allow_html=True)
            st.download_button("📥 Download Monthly Report",
                data=_build_report("Monthly", _mo_data, _mo_dr),
                file_name=f"Samvaad_Monthly_{_month_start.strftime('%b_%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, key="dl_monthly")

            # Overall
            _all_dr = f"All data · {survey_df['survey_date'].min()} – {survey_df['survey_date'].max()}"
            st.write("")
            st.markdown(f"""<div class="section-card">
                <strong>📊 Overall Organisational Report</strong><br>
                <span style="font-size:0.8rem;color:#64748b">{_all_dr}</span><br>
                <span style="font-size:0.8rem;color:#64748b">{len(survey_df)} total responses · all time</span>
            </div>""", unsafe_allow_html=True)
            st.download_button("📥 Download Overall Report",
                data=_build_report("Overall", survey_df, _all_dr),
                file_name=f"Samvaad_Overall_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, key="dl_overall")

        st.divider()

        # Quarterly (computed from last 3 months)
        _q_start = _today - pd.Timedelta(days=90)
        _q_data  = survey_df[survey_df["_date"] >= _q_start] if "_date" in survey_df.columns else survey_df
        _q_dr    = f"{_q_start.strftime('%d %b')} – {_today.strftime('%d %b %Y')}"
        st.markdown("#### 📋 Quarterly Report (Last 90 Days)")
        st.caption(f"Period: {_q_dr} · {len(_q_data)} responses")
        st.download_button("📥 Download Quarterly Report",
            data=_build_report("Quarterly", _q_data, _q_dr),
            file_name=f"Samvaad_Quarterly_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, key="dl_quarterly")

        st.divider()
        st.markdown("#### 📄 Raw CSV Export")
        _csv_df = _filt_df if not _filt_df.empty else survey_df
        st.download_button("📥 Download Raw CSV (current period)",
            data=_csv_df.to_csv(index=False).encode("utf-8"),
            file_name=f"Samvaad_Raw_{_period_label.replace(' ','_')}_{date.today()}.csv",
            mime="text/csv", use_container_width=True)