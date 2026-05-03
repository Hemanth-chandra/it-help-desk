import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import random

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IT Help Desk",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Data helpers (JSON file as lightweight DB) ────────────────────────────────
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    # Default seed data
    return {
        "tickets": [
            {"id": "TKT-001", "employee": "Ravi Kumar",   "dept": "HR",      "category": "Hardware",  "description": "Laptop not starting up after Windows update", "priority": "High",     "status": "Resolved",     "technician": "Arjun Sharma",  "created": "2025-04-25 09:10", "resolved": "2025-04-25 13:00", "notes": "Replaced faulty RAM module"},
            {"id": "TKT-002", "employee": "Priya Nair",   "dept": "Finance", "category": "Software",  "description": "MS Excel crashing when opening large files",  "priority": "Medium",   "status": "In Progress",  "technician": "Meena Raj",     "created": "2025-04-26 10:30", "resolved": "",               "notes": ""},
            {"id": "TKT-003", "employee": "Amit Singh",   "dept": "Sales",   "category": "Network",   "description": "Unable to connect to office WiFi",            "priority": "High",     "status": "Open",         "technician": "",              "created": "2025-04-27 08:45", "resolved": "",               "notes": ""},
            {"id": "TKT-004", "employee": "Sneha Patel",  "dept": "IT",      "category": "Software",  "description": "Need Python 3.11 installed on workstation",   "priority": "Low",      "status": "Closed",       "technician": "Arjun Sharma",  "created": "2025-04-23 14:00", "resolved": "2025-04-23 14:45","notes": "Installed via company software portal"},
            {"id": "TKT-005", "employee": "Karan Mehta",  "dept": "Admin",   "category": "Hardware",  "description": "Printer not responding on 3rd floor",         "priority": "Critical", "status": "In Progress",  "technician": "Meena Raj",     "created": "2025-04-28 08:00", "resolved": "",               "notes": ""},
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

# ── SLA config ────────────────────────────────────────────────────────────────
SLA = {"Critical": 2, "High": 4, "Medium": 24, "Low": 72}
PRIORITY_COLOR = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
STATUS_COLOR   = {"Open": "🔵", "In Progress": "🟣", "Resolved": "🟢", "Closed": "⚫"}
TECHNICIANS    = ["Arjun Sharma", "Meena Raj", "Vikram Das", "Lakshmi Iyer"]
DEPARTMENTS    = ["HR", "Finance", "Sales", "IT", "Admin", "Operations", "Marketing"]
CATEGORIES     = ["Hardware", "Software", "Network", "Other"]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1F3864; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    [data-testid="stSidebar"] .stRadio label { color: #ffffff !important; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #2E75B6;
    }
    [data-testid="stMetricValue"] { font-size: 2rem !important; color: #1F3864 !important; }
    [data-testid="stMetricLabel"] { color: #595959 !important; font-weight: 600; }

    /* Ticket cards */
    .ticket-card {
        background: #ffffff;
        border: 1px solid #dee2e6;
        border-left: 5px solid #2E75B6;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .ticket-card.critical { border-left-color: #C00000; }
    .ticket-card.high     { border-left-color: #FF6B35; }
    .ticket-card.medium   { border-left-color: #F39C12; }
    .ticket-card.low      { border-left-color: #2ECC71; }
    .ticket-id   { font-size: 0.8rem; color: #595959; font-weight: 600; }
    .ticket-title{ font-size: 1rem; font-weight: 700; color: #1F3864; margin: 2px 0; }
    .ticket-meta { font-size: 0.82rem; color: #888; }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 4px;
    }
    .badge-open       { background:#DBEAFE; color:#1D4ED8; }
    .badge-inprogress { background:#EDE9FE; color:#5B21B6; }
    .badge-resolved   { background:#DCFCE7; color:#166534; }
    .badge-closed     { background:#F3F4F6; color:#374151; }
    .badge-critical   { background:#FEE2E2; color:#991B1B; }
    .badge-high       { background:#FFEDD5; color:#9A3412; }
    .badge-medium     { background:#FEF9C3; color:#713F12; }
    .badge-low        { background:#DCFCE7; color:#166534; }

    /* Section headers */
    .section-header {
        background: #1F3864;
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 14px;
    }
    /* Form */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border: 1px solid #dee2e6 !important;
        border-radius: 6px !important;
    }
    div[data-testid="stForm"] {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 20px;
        background: #f8f9fa;
    }
    /* Hide streamlit branding */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
data = load_data()
tickets = data["tickets"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎫 IT Help Desk")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "🎫 All Tickets", "➕ Raise Ticket", "🔧 Technician View", "👤 My Tickets"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**Logged in as:**")
    role = st.selectbox("Role", ["Employee", "IT Technician", "IT Manager"], label_visibility="collapsed")
    if role in ["IT Technician", "IT Manager"]:
        user_name = st.selectbox("Select Technician", TECHNICIANS, label_visibility="collapsed")
    else:
        user_name = st.text_input("Your Name", value="Ravi Kumar", label_visibility="collapsed")
    st.markdown("---")
    st.markdown("<small style='color:#aaa'>SAD Project · IIITM Gwalior</small>", unsafe_allow_html=True)

page_name = page.split(" ", 1)[1]  # strip emoji

# ── Helper: status badge HTML ──────────────────────────────────────────────────
def status_badge(status):
    cls = {"Open":"open","In Progress":"inprogress","Resolved":"resolved","Closed":"closed"}.get(status,"open")
    return f'<span class="badge badge-{cls}">{status}</span>'

def priority_badge(priority):
    cls = priority.lower()
    return f'<span class="badge badge-{cls}">{PRIORITY_COLOR.get(priority,"")} {priority}</span>'

# ═══════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
if page_name == "Dashboard":
    st.markdown("## 📊 Dashboard")
    st.markdown("Overview of all IT support activity")
    st.markdown("---")

    total    = len(tickets)
    open_t   = sum(1 for t in tickets if t["status"] == "Open")
    inprog_t = sum(1 for t in tickets if t["status"] == "In Progress")
    resolved = sum(1 for t in tickets if t["status"] in ["Resolved", "Closed"])
    critical = sum(1 for t in tickets if t["priority"] == "Critical" and t["status"] not in ["Resolved","Closed"])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Tickets",   total)
    c2.metric("Open",            open_t,   delta=f"+{open_t} pending", delta_color="inverse")
    c3.metric("In Progress",     inprog_t)
    c4.metric("Resolved/Closed", resolved)
    c5.metric("🔴 Critical Open", critical, delta_color="inverse")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Recent Tickets</div>', unsafe_allow_html=True)
        recent = sorted(tickets, key=lambda x: x["created"], reverse=True)[:5]
        for t in recent:
            pri_cls = t["priority"].lower()
            st.markdown(f"""
            <div class="ticket-card {pri_cls}">
                <div class="ticket-id">{t['id']} · {t['created']}</div>
                <div class="ticket-title">{t['description'][:60]}{'...' if len(t['description'])>60 else ''}</div>
                <div class="ticket-meta">
                    {priority_badge(t['priority'])} {status_badge(t['status'])}
                    &nbsp;· {t['employee']} ({t['dept']}) · {t['category']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">Status Breakdown</div>', unsafe_allow_html=True)
        status_counts = {}
        for t in tickets:
            status_counts[t["status"]] = status_counts.get(t["status"], 0) + 1
        df_status = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])
        st.bar_chart(df_status.set_index("Status"))

        st.markdown('<div class="section-header" style="margin-top:12px">Priority Breakdown</div>', unsafe_allow_html=True)
        pri_counts = {}
        for t in tickets:
            pri_counts[t["priority"]] = pri_counts.get(t["priority"], 0) + 1
        df_pri = pd.DataFrame(list(pri_counts.items()), columns=["Priority", "Count"])
        st.bar_chart(df_pri.set_index("Priority"))

    st.markdown("---")
    st.markdown('<div class="section-header">Technician Performance</div>', unsafe_allow_html=True)
    tech_stats = {}
    for t in tickets:
        tech = t["technician"] or "Unassigned"
        if tech not in tech_stats:
            tech_stats[tech] = {"assigned": 0, "resolved": 0}
        tech_stats[tech]["assigned"] += 1
        if t["status"] in ["Resolved", "Closed"]:
            tech_stats[tech]["resolved"] += 1
    df_tech = pd.DataFrame([
        {"Technician": k, "Assigned": v["assigned"], "Resolved": v["resolved"]}
        for k, v in tech_stats.items() if k != "Unassigned"
    ])
    if not df_tech.empty:
        st.dataframe(df_tech, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGE: ALL TICKETS
# ═══════════════════════════════════════════════════════════════════════
elif page_name == "All Tickets":
    st.markdown("## 🎫 All Tickets")
    st.markdown("---")

    # Filters
    col1, col2, col3, col4 = st.columns(4)
    f_status   = col1.selectbox("Status",   ["All", "Open", "In Progress", "Resolved", "Closed"])
    f_priority = col2.selectbox("Priority", ["All", "Critical", "High", "Medium", "Low"])
    f_category = col3.selectbox("Category", ["All"] + CATEGORIES)
    f_search   = col4.text_input("Search", placeholder="Keyword...")

    filtered = tickets
    if f_status   != "All": filtered = [t for t in filtered if t["status"]   == f_status]
    if f_priority != "All": filtered = [t for t in filtered if t["priority"] == f_priority]
    if f_category != "All": filtered = [t for t in filtered if t["category"] == f_category]
    if f_search:            filtered = [t for t in filtered if f_search.lower() in t["description"].lower() or f_search.lower() in t["employee"].lower()]

    st.markdown(f"**{len(filtered)} ticket(s) found**")
    st.markdown("---")

    if not filtered:
        st.info("No tickets match the selected filters.")
    else:
        for t in sorted(filtered, key=lambda x: x["created"], reverse=True):
            pri_cls = t["priority"].lower()
            tech_txt = f"👨‍🔧 {t['technician']}" if t["technician"] else "👨‍🔧 Unassigned"
            st.markdown(f"""
            <div class="ticket-card {pri_cls}">
                <div class="ticket-id">{t['id']} · {t['created']}</div>
                <div class="ticket-title">{t['description']}</div>
                <div class="ticket-meta">
                    {priority_badge(t['priority'])} {status_badge(t['status'])}
                    &nbsp;· <b>{t['employee']}</b> ({t['dept']}) · {t['category']} · {tech_txt}
                </div>
                {'<div class="ticket-meta" style="margin-top:4px">📝 <i>'+t["notes"]+'</i></div>' if t["notes"] else ''}
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGE: RAISE TICKET
# ═══════════════════════════════════════════════════════════════════════
elif page_name == "Raise Ticket":
    st.markdown("## ➕ Raise a New Ticket")
    st.markdown("Fill in the details below to submit an IT support request.")
    st.markdown("---")

    with st.form("ticket_form"):
        col1, col2 = st.columns(2)
        emp_name = col1.text_input("Your Name *", value=user_name)
        emp_dept = col2.selectbox("Department *", DEPARTMENTS)

        col3, col4 = st.columns(2)
        category = col3.selectbox("Issue Category *", CATEGORIES)
        priority = col4.selectbox("Priority *", ["Low", "Medium", "High", "Critical"],
                                   help="Critical = system down, High = major impact, Medium = moderate, Low = minor")

        description = st.text_area("Issue Description *", height=120,
                                    placeholder="Describe your issue in detail...")

        st.markdown(f"⏱️ **Expected resolution time:** {SLA[priority]} hour(s) based on selected priority")

        submitted = st.form_submit_button("🎫 Submit Ticket", use_container_width=True)

        if submitted:
            if not emp_name.strip() or not description.strip():
                st.error("Please fill in all required fields.")
            else:
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
                st.success(f"✅ Ticket submitted successfully! Your Ticket ID is **{new_ticket['id']}**")
                st.info(f"📧 A confirmation has been sent. Expected resolution within **{SLA[priority]} hour(s)**.")
                st.balloons()

    st.markdown("---")
    st.markdown("#### Priority Guide")
    guide = {
        "🔴 Critical": "System completely down, blocking all work. Escalates in 30 min.",
        "🟠 High":     "Major impact on productivity. Escalates in 1 hour.",
        "🟡 Medium":   "Moderate impact. Resolved within 1 working day.",
        "🟢 Low":      "Minor issue, no immediate impact. Resolved within 3 days."
    }
    cols = st.columns(4)
    for i, (k, v) in enumerate(guide.items()):
        with cols[i]:
            st.markdown(f"**{k}**")
            st.caption(v)

# ═══════════════════════════════════════════════════════════════════════
# PAGE: TECHNICIAN VIEW
# ═══════════════════════════════════════════════════════════════════════
elif page_name == "Technician View":
    st.markdown("## 🔧 Technician View")
    st.markdown(f"Logged in as: **{user_name if role == 'IT Technician' else 'IT Manager (Admin)'}**")
    st.markdown("---")

    if role == "IT Manager":
        view_tickets = [t for t in tickets if t["status"] not in ["Closed"]]
    else:
        view_tickets = [t for t in tickets if t["technician"] == user_name or t["status"] == "Open"]

    if not view_tickets:
        st.info("No tickets to display.")
    else:
        for idx, t in enumerate(sorted(view_tickets, key=lambda x: ["Critical","High","Medium","Low"].index(x["priority"]))):
            pri_cls = t["priority"].lower()
            with st.expander(f"{PRIORITY_COLOR[t['priority']]}  {t['id']}  —  {t['description'][:65]}  |  {STATUS_COLOR.get(t['status'],'')} {t['status']}"):
                col1, col2 = st.columns(2)
                col1.markdown(f"**Employee:** {t['employee']} ({t['dept']})")
                col1.markdown(f"**Category:** {t['category']}")
                col1.markdown(f"**Created:** {t['created']}")
                col2.markdown(f"**Priority:** {priority_badge(t['priority'])}", unsafe_allow_html=True)
                col2.markdown(f"**Status:** {status_badge(t['status'])}", unsafe_allow_html=True)
                col2.markdown(f"**Technician:** {t['technician'] or 'Unassigned'}")

                st.markdown("**Description:**")
                st.info(t["description"])

                if t["notes"]:
                    st.markdown(f"**Resolution Notes:** {t['notes']}")

                st.markdown("---")
                c1, c2, c3 = st.columns(3)

                # Assign technician
                if role == "IT Manager" and not t["technician"]:
                    with c1:
                        sel_tech = st.selectbox(f"Assign Technician", TECHNICIANS, key=f"tech_{t['id']}")
                        if st.button("Assign", key=f"assign_{t['id']}"):
                            for tk in data["tickets"]:
                                if tk["id"] == t["id"]:
                                    tk["technician"] = sel_tech
                                    tk["status"] = "In Progress"
                            save_data(data)
                            st.success(f"Assigned to {sel_tech}")
                            st.rerun()

                # Update status
                with c2:
                    new_status = st.selectbox("Update Status", ["Open","In Progress","Resolved","Closed"], key=f"status_{t['id']}",
                                               index=["Open","In Progress","Resolved","Closed"].index(t["status"]))
                    if st.button("Update", key=f"update_{t['id']}"):
                        for tk in data["tickets"]:
                            if tk["id"] == t["id"]:
                                tk["status"] = new_status
                                if new_status in ["Resolved","Closed"]:
                                    tk["resolved"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        save_data(data)
                        st.success("Status updated.")
                        st.rerun()

                # Add notes
                with c3:
                    notes_input = st.text_area("Resolution Notes", value=t["notes"], key=f"notes_{t['id']}", height=80)
                    if st.button("Save Notes", key=f"savenotes_{t['id']}"):
                        for tk in data["tickets"]:
                            if tk["id"] == t["id"]:
                                tk["notes"] = notes_input
                        save_data(data)
                        st.success("Notes saved.")
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# PAGE: MY TICKETS
# ═══════════════════════════════════════════════════════════════════════
elif page_name == "My Tickets":
    st.markdown("## 👤 My Tickets")
    st.markdown(f"Showing tickets raised by **{user_name}**")
    st.markdown("---")

    my_tickets = [t for t in tickets if t["employee"].lower() == user_name.lower()]

    if not my_tickets:
        st.info(f"No tickets found for '{user_name}'. Try raising one from the **Raise Ticket** page.")
    else:
        for t in sorted(my_tickets, key=lambda x: x["created"], reverse=True):
            pri_cls = t["priority"].lower()
            tech_txt = f"Assigned to: **{t['technician']}**" if t["technician"] else "⏳ Awaiting assignment"
            resolved_txt = f"Resolved: {t['resolved']}" if t["resolved"] else ""
            st.markdown(f"""
            <div class="ticket-card {pri_cls}">
                <div class="ticket-id">{t['id']} · Raised: {t['created']} {'· '+resolved_txt if resolved_txt else ''}</div>
                <div class="ticket-title">{t['description']}</div>
                <div class="ticket-meta">
                    {priority_badge(t['priority'])} {status_badge(t['status'])}
                    &nbsp;· {t['category']} · {tech_txt}
                </div>
                {'<div class="ticket-meta" style="margin-top:4px; color:#166534">✅ <i>'+t["notes"]+'</i></div>' if t["notes"] else ''}
            </div>
            """, unsafe_allow_html=True)
