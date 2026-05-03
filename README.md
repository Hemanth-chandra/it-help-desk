# 🎫 IT Help Desk Ticketing System

A simple, clean IT Help Desk web application built with **Streamlit** as part of a System Analysis and Design project.

---

## 📋 Features

| Feature | Description |
|---|---|
| **Dashboard** | Live overview of all tickets — counts, charts, technician performance |
| **All Tickets** | Filter and search tickets by status, priority, category |
| **Raise Ticket** | Employee form to submit a new IT support request |
| **Technician View** | Assign technicians, update status, add resolution notes |
| **My Tickets** | Employee view of their own submitted tickets |

---

## 🚀 Deploy on Streamlit Cloud (Step by Step)

### Step 1 — Push to GitHub

```bash
# Clone or create your repo
git init
git add .
git commit -m "Initial commit — IT Help Desk app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/it-helpdesk.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repository and branch (`main`)
5. Set **Main file path** to `app.py`
6. Click **Deploy**

Your app will be live at:
```
https://YOUR_USERNAME-it-helpdesk-app-XXXX.streamlit.app
```

---

## 💻 Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
it-helpdesk/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .gitignore          # Files to ignore in git
├── README.md           # This file
└── data.json           # Auto-created on first run (ticket storage)
```

---

## 🎭 User Roles

| Role | Access |
|---|---|
| **Employee** | Raise tickets, view own tickets |
| **IT Technician** | View assigned tickets, update status, add notes |
| **IT Manager** | Full access — assign technicians, view all tickets, dashboard |

---

## 📚 Academic Context

- **Subject:** System Analysis and Design
- **Institute:** Atal Bihari Vajpai IIITM, Gwalior
- **Covers:** SDLC, DFD, ER Diagram, Process Specifications, Decision Tables, I/O Design

---

## 🛠️ Tech Stack

- **Frontend + Backend:** Python, Streamlit
- **Data Storage:** JSON file (lightweight, no database needed)
- **Deployment:** Streamlit Cloud (free)
