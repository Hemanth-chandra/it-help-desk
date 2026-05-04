import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(page_title="IT Help Desk", page_icon="🎫", layout="wide", initial_sidebar_state="expanded")

# ── Data helpers ──────────────────────────────────────────────────────────────
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {
        "tickets": [
            {"id":"TKT-001","employee":"Ravi Kumar",  "dept":"HR",     "category":"Hardware","description":"Laptop not starting up after Windows update","priority":"High",    "status":"Resolved",   "technician":"Arjun Sharma","created":"2025-04-25 09:10","resolved":"2025-04-25 13:00","notes":"Replaced faulty RAM module"},
            {"id":"TKT-002","employee":"Priya Nair",  "dept":"Finance","category":"Software","description":"MS Excel crashing when opening large files",  "priority":"High",    "status":"In Progress","technician":"Meena Raj",   "created":"2025-04-26 10:30","resolved":"","notes":""},
            {"id":"TKT-003","employee":"Amit Singh",  "dept":"Sales",  "category":"Network", "description":"Unable to connect to office WiFi",            "priority":"High",    "status":"Open",       "technician":"",            "created":"2025-04-27 08:45","resolved":"","notes":""},
            {"id":"TKT-004","employee":"Sneha Patel", "dept":"IT",     "category":"Software","description":"Need Python 3.11 installed on workstation",   "priority":"Low",     "status":"Closed",     "technician":"Arjun Sharma","created":"2025-04-23 14:00","resolved":"2025-04-23 14:45","notes":"Installed via company software portal"},
            {"id":"TKT-005","employee":"Karan Mehta", "dept":"Admin",  "category":"Hardware","description":"Printer not responding on 3rd floor",         "priority":"Critical","status":"In Progress","technician":"Meena Raj",   "created":"2025-04-28 08:00","resolved":"","notes":""},
        ],
        "next_id": 6
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_next_id(data):
    nid = data["next_id"]
    data["next_id"] += 1
    return f"TKT-{nid:03d}"

# ── Constants ─────────────────────────────────────────────────────────────────
SLA            = {"Critical": 2, "High": 4, "Medium": 24, "Low": 72}
PRIORITY_COLOR = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
STATUS_COLOR   = {"Open": "🔵", "In Progress": "🟣", "Resolved": "🟢", "Closed": "⚫"}
TECHNICIANS    = ["Arjun Sharma", "Meena Raj", "Vikram Das", "Lakshmi Iyer"]
DEPARTMENTS    = ["HR", "Finance", "Sales", "IT", "Admin", "Operations", "Marketing"]
CATEGORIES     = ["Hardware", "Software", "Network", "Other"]

# ── Auto Priority Engine ──────────────────────────────────────────────────────
# Logic:
#   Step 1 → Scan description keywords top-down (Critical first, Low last). First match wins.
#   Step 2 → Category risk escalation: high-risk category + risky word → bump up 1 level
#   Step 3 → Department escalation: Finance/IT/Operations Medium → bumped to High
#   Default → Low (routine request if no keywords matched)
#
# Why not let users choose?
#   Users always think their issue is Critical. The engine decides based on
#   IMPACT (is work stopped?) not URGENCY (how annoyed am I?).

import urllib.request

# ── AI Priority Detection (Anthropic API) ────────────────────────────────────
# Primary: AI understands context, urgency cues, and business impact naturally.
# Fallback: keyword engine runs if API key is missing or API call fails.

PRIORITY_RULES = """
You are an IT Help Desk triage engine. Your job is to assign priority to IT issues.

Priority definitions (based on BUSINESS IMPACT, not how annoyed the user is):
- Critical: Work is completely stopped OR data loss / security breach is involved.
  Examples: server down, system won't boot, locked out of all systems, ransomware, data deleted.
- High: Work is heavily impacted — major function broken, but not total stoppage.
  Examples: application keeps crashing, wifi not connecting, email not working, printer offline.
- Medium: Work is partially affected — can continue with workarounds.
  Examples: software running slow, sync issues, webcam not working, VPN issue.
- Low: Routine request — no immediate impact on work.
  Examples: install new software, need a cable, change settings, how-to question.

Rules:
1. Judge by IMPACT on work, not how urgently the user phrases it.
2. "Urgent" or "ASAP" alone does not change priority.
3. Finance/IT/Operations departments get bumped up one level if Medium.
4. Hardware failures (smoke, dead device) and security issues (virus, hack) are always Critical.

Respond ONLY with valid JSON in this exact format, nothing else:
{"priority": "High", "reason": "Application keeps crashing — work heavily impacted", "confidence": "high"}

Priority must be one of: Critical, High, Medium, Low
Confidence must be one of: high, medium, low
"""

def ai_detect_priority(description, category, department):
    """Call Anthropic API to detect priority. Returns (priority, reason) or raises."""
    import os, json as _json

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("No API key")

    prompt = f"""Issue details:
- Description: {description}
- Category: {category}
- Department: {department}

Assign the correct priority based on the rules."""

    payload = _json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 150,
        "system": PRIORITY_RULES,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        result = _json.loads(resp.read())

    text = result["content"][0]["text"].strip()
    parsed = _json.loads(text)
    priority = parsed["priority"]
    reason   = parsed["reason"]
    assert priority in ["Critical", "High", "Medium", "Low"]
    return priority, f"🤖 AI analysis: {reason}"


# ── Keyword Fallback Engine ───────────────────────────────────────────────────
PRIORITY_KEYWORDS = {
    "Critical": [
        "server down","system down","network down","completely down","not working at all",
        "website down","database down","cannot login","can't login","locked out",
        "not booting","won't start","not starting","dead","blank screen",
        "data loss","data lost","deleted by mistake","ransomware","virus","malware",
        "hacked","security breach","breach","power failure","not turning on","smoke","burnt",
    ],
    "High": [
        "not responding","keeps crashing","crashing","freezing","frozen","hanging",
        "blue screen","bsod","wifi not connecting","can't connect to wifi",
        "cannot connect","email not sending","email not receiving",
        "printer not working","printer offline","password reset","forgot password",
        "access denied","permission denied","software not opening","application crashing",
        "keyboard not working","mouse not working","monitor not working",
        "unable to access","cannot access","not loading","error message",
    ],
    "Medium": [
        "slow","lagging","running slow","low storage","disk full",
        "not syncing","sync issue","audio issue","sound issue","mic not working",
        "webcam not working","camera not working","zoom issue","teams not working",
        "vpn issue","driver issue","outlook issue","excel issue","word issue",
        "file corrupted","need access to","request access","install software","scanner not working",
    ],
    "Low": [
        "need","request","setup","configure","change settings","new device",
        "new laptop","cable needed","need a charger","headset","headphone",
        "docking station","how to","help with","query about","install chrome","install zoom",
    ]
}

CATEGORY_ESCALATE = {
    "Network":  ["down","outage","failure","no internet","disconnected completely"],
    "Hardware": ["dead","broken","not starting","won't turn on","smoke","damaged","burnt"],
    "Software": ["ransomware","virus","malware","hacked","breach","data loss"],
}
DEPT_ESCALATE = ["Finance", "IT", "Operations"]

def keyword_detect_priority(description, category, department):
    text  = description.lower().strip()
    order = ["Low", "Medium", "High", "Critical"]
    detected, matched_kw, escalation_notes = "Low", "", []

    for level in ["Critical", "High", "Medium", "Low"]:
        for kw in PRIORITY_KEYWORDS[level]:
            if kw in text:
                detected, matched_kw = level, kw
                break
        if matched_kw:
            break

    if category in CATEGORY_ESCALATE:
        for kw in CATEGORY_ESCALATE[category]:
            if kw in text:
                idx = order.index(detected)
                if idx < 3:
                    old = detected; detected = order[idx + 1]
                    escalation_notes.append(f"Category risk ({category}: '{kw}') escalated {old} → {detected}")
                break

    if department in DEPT_ESCALATE and detected == "Medium":
        detected = "High"
        escalation_notes.append(f"Department ({department}) escalated Medium → High")

    reason = f'📋 Keyword matched: **"{matched_kw}"**' if matched_kw else "📋 No impact keywords found → defaulted to **Low**"
    if escalation_notes:
        reason += "  \n" + "  \n".join(f"↑ {n}" for n in escalation_notes)
    return detected, reason


def auto_detect_priority(description, category, department):
    """Try AI first, fall back to keyword engine."""
    explain_map = {
        "Critical": "Work is **completely stopped** or data/security is at risk.",
        "High":     "Work is **heavily impacted** — major disruption.",
        "Medium":   "Work is **partially affected** — tasks can still continue.",
        "Low":      "**Routine request** — no immediate impact on work.",
    }
    try:
        priority, reason = ai_detect_priority(description, category, department)
        source = "ai"
    except Exception:
        priority, reason = keyword_detect_priority(description, category, department)
        source = "keyword"
    return priority, reason, explain_map[priority], source


# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #1F3864; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    [data-testid="stMetric"] {
        background: #f8f9fa; border: 1px solid #dee2e6;
        border-radius: 8px; padding: 12px; border-left: 4px solid #2E75B6;
    }
    [data-testid="stMetricValue"] { font-size: 2rem !important; color: #1F3864 !important; }
    [data-testid="stMetricLabel"] { color: #595959 !important; font-weight: 600; }
    .ticket-card {
        background: #fff; border: 1px solid #dee2e6;
        border-left: 5px solid #2E75B6; border-radius: 6px;
        padding: 14px 18px; margin-bottom: 10px;
    }
    .ticket-card.critical { border-left-color: #C00000; }
    .ticket-card.high     { border-left-color: #FF6B35; }
    .ticket-card.medium   { border-left-color: #F39C12; }
    .ticket-card.low      { border-left-color: #2ECC71; }
    .ticket-id    { font-size: 0.8rem; color: #595959; font-weight: 600; }
    .ticket-title { font-size: 1rem; font-weight: 700; color: #1F3864; margin: 2px 0; }
    .ticket-meta  { font-size: 0.82rem; color: #888; }
    .badge { display:inline-block; padding:2px 10px; border-radius:12px; font-size:0.78rem; font-weight:600; margin-right:4px; }
    .badge-open       { background:#DBEAFE; color:#1D4ED8; }
    .badge-inprogress { background:#EDE9FE; color:#5B21B6; }
    .badge-resolved   { background:#DCFCE7; color:#166534; }
    .badge-closed     { background:#F3F4F6; color:#374151; }
    .badge-critical   { background:#FEE2E2; color:#991B1B; }
    .badge-high       { background:#FFEDD5; color:#9A3412; }
    .badge-medium     { background:#FEF9C3; color:#713F12; }
    .badge-low        { background:#DCFCE7; color:#166534; }
    .section-header {
        background: #1F3864; color: white; padding: 8px 16px;
        border-radius: 6px; font-size: 1rem; font-weight: 700; margin-bottom: 14px;
    }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Load ──────────────────────────────────────────────────────────────────────
data    = load_data()
tickets = data["tickets"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎫 IT Help Desk")
    st.markdown("---")
    page = st.radio("Navigation", [
        "📊 Dashboard", "🎫 All Tickets", "➕ Raise Ticket",
        "🔧 Technician View", "👤 My Tickets"
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**Role:**")
    role = st.selectbox("Role", ["Employee", "IT Technician", "IT Manager"], label_visibility="collapsed")
    st.markdown("**Name:**")
    if role in ["IT Technician", "IT Manager"]:
        user_name = st.selectbox("Name", TECHNICIANS, label_visibility="collapsed")
    else:
        user_name = st.text_input("Name", value="Ravi Kumar", label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**🤖 AI Priority Detection**")
    api_key_input = st.text_input(
        "Anthropic API Key (optional)",
        type="password",
        placeholder="sk-ant-...",
        label_visibility="collapsed",
        help="If provided, AI will detect ticket priority. Otherwise keyword engine is used."
    )
    if api_key_input:
        os.environ["ANTHROPIC_API_KEY"] = api_key_input
        st.markdown("<small style='color:#90EE90'>✓ AI mode active</small>", unsafe_allow_html=True)
    else:
        st.markdown("<small style='color:#aaa'>Keyword mode (no key needed)</small>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<small style='color:#aaa'>SAD Project · IIITM Gwalior</small>", unsafe_allow_html=True)

page_name = page.split(" ", 1)[1]

def status_badge(s):
    cls = {"Open":"open","In Progress":"inprogress","Resolved":"resolved","Closed":"closed"}.get(s,"open")
    return f'<span class="badge badge-{cls}">{s}</span>'

def priority_badge(p):
    return f'<span class="badge badge-{p.lower()}">{PRIORITY_COLOR.get(p,"")} {p}</span>'

# ═══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
if page_name == "Dashboard":
    st.markdown("## 📊 Dashboard")
    st.markdown("---")

    total    = len(tickets)
    open_t   = sum(1 for t in tickets if t["status"] == "Open")
    inprog   = sum(1 for t in tickets if t["status"] == "In Progress")
    resolved = sum(1 for t in tickets if t["status"] in ["Resolved","Closed"])
    critical = sum(1 for t in tickets if t["priority"] == "Critical" and t["status"] not in ["Resolved","Closed"])

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Tickets",    total)
    c2.metric("Open",             open_t,   delta=f"+{open_t} pending", delta_color="inverse")
    c3.metric("In Progress",      inprog)
    c4.metric("Resolved/Closed",  resolved)
    c5.metric("🔴 Critical Open", critical, delta_color="inverse")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Recent Tickets</div>', unsafe_allow_html=True)
        for t in sorted(tickets, key=lambda x: x["created"], reverse=True)[:5]:
            st.markdown(f"""
            <div class="ticket-card {t['priority'].lower()}">
                <div class="ticket-id">{t['id']} · {t['created']}</div>
                <div class="ticket-title">{t['description'][:65]}{'...' if len(t['description'])>65 else ''}</div>
                <div class="ticket-meta">{priority_badge(t['priority'])} {status_badge(t['status'])} · {t['employee']} ({t['dept']})</div>
            </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">Status Breakdown</div>', unsafe_allow_html=True)
        sc = {}
        for t in tickets: sc[t["status"]] = sc.get(t["status"],0)+1
        st.bar_chart(pd.DataFrame(list(sc.items()), columns=["Status","Count"]).set_index("Status"))
        st.markdown('<div class="section-header" style="margin-top:10px">Priority Breakdown</div>', unsafe_allow_html=True)
        pc = {}
        for t in tickets: pc[t["priority"]] = pc.get(t["priority"],0)+1
        st.bar_chart(pd.DataFrame(list(pc.items()), columns=["Priority","Count"]).set_index("Priority"))

    st.markdown("---")
    st.markdown('<div class="section-header">Technician Performance</div>', unsafe_allow_html=True)
    ts = {}
    for t in tickets:
        tech = t["technician"] or "Unassigned"
        ts.setdefault(tech, {"Assigned":0,"Resolved":0})
        ts[tech]["Assigned"] += 1
        if t["status"] in ["Resolved","Closed"]: ts[tech]["Resolved"] += 1
    df = pd.DataFrame([{"Technician":k,"Assigned":v["Assigned"],"Resolved":v["Resolved"]} for k,v in ts.items() if k!="Unassigned"])
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════
# ALL TICKETS
# ═══════════════════════════════════════════════════════════════════════
elif page_name == "All Tickets":
    st.markdown("## 🎫 All Tickets")
    st.markdown("---")
    col1,col2,col3,col4 = st.columns(4)
    f_s = col1.selectbox("Status",   ["All","Open","In Progress","Resolved","Closed"])
    f_p = col2.selectbox("Priority", ["All","Critical","High","Medium","Low"])
    f_c = col3.selectbox("Category", ["All"]+CATEGORIES)
    f_q = col4.text_input("Search",  placeholder="Keyword...")

    filtered = tickets
    if f_s != "All": filtered = [t for t in filtered if t["status"]   == f_s]
    if f_p != "All": filtered = [t for t in filtered if t["priority"] == f_p]
    if f_c != "All": filtered = [t for t in filtered if t["category"] == f_c]
    if f_q:          filtered = [t for t in filtered if f_q.lower() in t["description"].lower() or f_q.lower() in t["employee"].lower()]

    st.markdown(f"**{len(filtered)} ticket(s) found**")
    st.markdown("---")

    if not filtered:
        st.info("No tickets match the selected filters.")
    else:
        for t in sorted(filtered, key=lambda x: x["created"], reverse=True):
            tech_txt = f"👨‍🔧 {t['technician']}" if t["technician"] else "👨‍🔧 Unassigned"
            st.markdown(f"""
            <div class="ticket-card {t['priority'].lower()}">
                <div class="ticket-id">{t['id']} · {t['created']}</div>
                <div class="ticket-title">{t['description']}</div>
                <div class="ticket-meta">
                    {priority_badge(t['priority'])} {status_badge(t['status'])}
                    &nbsp;· <b>{t['employee']}</b> ({t['dept']}) · {t['category']} · {tech_txt}
                </div>
                {'<div class="ticket-meta" style="margin-top:4px">📝 <i>'+t["notes"]+'</i></div>' if t["notes"] else ''}
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# RAISE TICKET  ← Auto-priority engine
# ═══════════════════════════════════════════════════════════════════════
elif page_name == "Raise Ticket":
    st.markdown("## ➕ Raise a New Ticket")
    st.markdown("Describe your issue — the system **automatically assigns priority** based on the impact on your work.")
    st.markdown("---")

    col_form, col_guide = st.columns([2, 1])

    with col_form:
        with st.form("ticket_form"):
            fc1, fc2 = st.columns(2)
            emp_name = fc1.text_input("Your Name *", value=user_name)
            emp_dept = fc2.selectbox("Department *", DEPARTMENTS)
            category = st.selectbox("Issue Category *", CATEGORIES)
            description = st.text_area(
                "Describe your issue in detail *", height=130,
                placeholder="Example: My laptop is not starting up since morning. I have an urgent client presentation today.",
                help="Be specific — mention what is happening and how it is affecting your work."
            )
            submitted = st.form_submit_button("🎫 Submit Ticket", use_container_width=True)

        if submitted:
            if not emp_name.strip() or not description.strip():
                st.error("Please fill in all required fields.")
            else:
                with st.spinner("🤖 Analysing your issue..."):
                    priority, reason, explanation, source = auto_detect_priority(description, category, emp_dept)
                new_ticket = {
                    "id":          get_next_id(data),
                    "employee":    emp_name.strip(),
                    "dept":        emp_dept,
                    "category":    category,
                    "description": description.strip(),
                    "priority":    priority,
                    "status":      "Open",
                    "technician":  "",
                    "created":     datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "resolved":    "",
                    "notes":       ""
                }
                data["tickets"].append(new_ticket)
                save_data(data)

                color_map = {"Critical":"#C00000","High":"#FF6B35","Medium":"#F39C12","Low":"#2ECC71"}
                source_badge = "🤖 Detected by AI" if source == "ai" else "📋 Detected by keyword engine"
                st.success(f"✅ Ticket **{new_ticket['id']}** submitted successfully!")
                st.markdown(f"""
                <div style="background:#f0f4ff;border-left:4px solid {color_map[priority]};
                            border-radius:6px;padding:14px 18px;margin-top:8px;">
                    <b>Priority assigned: {PRIORITY_COLOR[priority]} {priority}</b>
                    &nbsp;&nbsp;<small style="color:#888">{source_badge}</small><br><br>
                    <span style="font-size:0.9rem">{reason}</span><br>
                    <span style="color:#555;font-size:0.88rem">{explanation}</span><br><br>
                    ⏱️ Expected resolution: <b>{SLA[priority]} hour(s)</b>
                </div>""", unsafe_allow_html=True)

    with col_guide:
        st.markdown("#### 🤖 How Priority is Decided")
        st.caption("You don't choose — the system detects it from your description based on work impact.")
        st.markdown("---")
        rules = [
            ("🔴 Critical", "#FEE2E2", "#991B1B", "Work completely stopped", "server down, data loss, locked out, not booting"),
            ("🟠 High",     "#FFEDD5", "#9A3412", "Work heavily impacted",   "crashing, access denied, wifi not connecting"),
            ("🟡 Medium",   "#FEF9C3", "#713F12", "Work partially affected", "slow, sync issue, install software, vpn issue"),
            ("🟢 Low",      "#DCFCE7", "#166534", "Routine request",         "need, request, setup, cable, headset, how to"),
        ]
        for label, bg, fg, impact, kws in rules:
            st.markdown(f"""
            <div style="background:{bg};border-radius:6px;padding:10px 14px;margin-bottom:8px;">
                <b style="color:{fg}">{label}</b> — {impact}<br>
                <span style="font-size:0.78rem;color:#666">e.g. {kws}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.info("💡 **Tip:** Describe what happened and how it affects your work. More detail = more accurate priority.")

    st.markdown("---")
    st.markdown("#### 🔍 Try These Examples")
    eg_cols = st.columns(4)
    examples = [
        ("Server is completely down, all work stopped", "Network", "IT"),
        ("My laptop keeps crashing and freezing", "Hardware", "HR"),
        ("Excel is running very slow", "Software", "Finance"),
        ("Need a new charging cable", "Hardware", "Admin"),
    ]
    color_map = {"Critical":"#C00000","High":"#FF6B35","Medium":"#F39C12","Low":"#2ECC71"}
    for i, (desc, cat, dept) in enumerate(examples):
        p, r, e, src = auto_detect_priority(desc, cat, dept)
        kw = r.split('"')[1] if '"' in r else desc.split()[0]
        with eg_cols[i]:
            st.markdown(f"""
            <div style="border:1.5px solid {color_map[p]};border-radius:6px;padding:10px;font-size:0.82rem;min-height:90px;">
                <i style="color:#333">"{desc}"</i><br><br>
                <b style="color:{color_map[p]}">{PRIORITY_COLOR[p]} {p}</b><br>
                <span style="color:#666;font-size:0.76rem">matched: "{kw}"</span>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# TECHNICIAN VIEW
# ═══════════════════════════════════════════════════════════════════════
elif page_name == "Technician View":
    st.markdown("## 🔧 Technician View")
    st.markdown(f"Logged in as: **{user_name}** ({role})")
    st.markdown("---")

    if role == "IT Manager":
        view_tickets = [t for t in tickets if t["status"] != "Closed"]
    else:
        view_tickets = [t for t in tickets if t["technician"] == user_name or t["status"] == "Open"]

    if not view_tickets:
        st.info("No tickets to display.")
    else:
        for t in sorted(view_tickets, key=lambda x: ["Critical","High","Medium","Low"].index(x["priority"])):
            with st.expander(f"{PRIORITY_COLOR[t['priority']]}  {t['id']}  —  {t['description'][:65]}  |  {STATUS_COLOR.get(t['status'],'')} {t['status']}"):
                c1,c2 = st.columns(2)
                c1.markdown(f"**Employee:** {t['employee']} ({t['dept']})")
                c1.markdown(f"**Category:** {t['category']}")
                c1.markdown(f"**Created:** {t['created']}")
                c2.markdown(f"**Priority:** {priority_badge(t['priority'])}", unsafe_allow_html=True)
                c2.markdown(f"**Status:** {status_badge(t['status'])}", unsafe_allow_html=True)
                c2.markdown(f"**Technician:** {t['technician'] or 'Unassigned'}")
                st.markdown(f"**Description:** {t['description']}")
                if t["notes"]: st.markdown(f"**Notes:** {t['notes']}")
                st.markdown("---")

                a1,a2,a3 = st.columns(3)
                if role == "IT Manager" and not t["technician"]:
                    with a1:
                        sel = st.selectbox("Assign to", TECHNICIANS, key=f"tech_{t['id']}")
                        if st.button("Assign", key=f"assign_{t['id']}"):
                            for tk in data["tickets"]:
                                if tk["id"] == t["id"]:
                                    tk["technician"] = sel
                                    tk["status"] = "In Progress"
                            save_data(data)
                            st.success(f"Assigned to {sel}")
                            st.rerun()

                with a2:
                    ns = st.selectbox("Update Status",
                        ["Open","In Progress","Resolved","Closed"],
                        index=["Open","In Progress","Resolved","Closed"].index(t["status"]),
                        key=f"status_{t['id']}")
                    if st.button("Update", key=f"upd_{t['id']}"):
                        for tk in data["tickets"]:
                            if tk["id"] == t["id"]:
                                tk["status"] = ns
                                if ns in ["Resolved","Closed"]:
                                    tk["resolved"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        save_data(data)
                        st.success("Updated.")
                        st.rerun()

                with a3:
                    ni = st.text_area("Resolution Notes", value=t["notes"], height=80, key=f"notes_{t['id']}")
                    if st.button("Save Notes", key=f"save_{t['id']}"):
                        for tk in data["tickets"]:
                            if tk["id"] == t["id"]: tk["notes"] = ni
                        save_data(data)
                        st.success("Saved.")
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# MY TICKETS
# ═══════════════════════════════════════════════════════════════════════
elif page_name == "My Tickets":
    st.markdown("## 👤 My Tickets")
    st.markdown(f"Showing tickets raised by **{user_name}**")
    st.markdown("---")

    my = [t for t in tickets if t["employee"].lower() == user_name.lower()]

    if not my:
        st.info(f"No tickets found for '{user_name}'. Go to **Raise Ticket** to submit one.")
    else:
        for t in sorted(my, key=lambda x: x["created"], reverse=True):
            tech_txt = f"Assigned to: **{t['technician']}**" if t["technician"] else "⏳ Awaiting assignment"
            st.markdown(f"""
            <div class="ticket-card {t['priority'].lower()}">
                <div class="ticket-id">{t['id']} · {t['created']}</div>
                <div class="ticket-title">{t['description']}</div>
                <div class="ticket-meta">
                    {priority_badge(t['priority'])} {status_badge(t['status'])}
                    &nbsp;· {t['category']} · {tech_txt}
                </div>
                {'<div class="ticket-meta" style="margin-top:4px;color:#166534">✅ <i>'+t["notes"]+'</i></div>' if t["notes"] else ''}
            </div>""", unsafe_allow_html=True)
