# 🎓 CareerDock - Placement Portal Application

A comprehensive Flask-based web application for managing campus recruitment operations, including placement drives, student applications, company management, and administrative oversight with role-based access control.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)](https://www.sqlite.org/)
---

## ✨ Features

### 🔐 Role-Based Access Control
Three distinct user portals with specific permissions:

#### Admin Portal
- Comprehensive dashboard with system-wide statistics
- Complete user management for students and companies
  - View all registered students and companies
  - Search functionality across students and companies
  - Enable or disable user accounts
  - Blacklist/remove students and companies
- Company registration approval and rejection workflow
- Placement drive management
  - Approve or close active drives
- View all applications and placements across the system
- Department-level reporting and oversight

#### Company Portal
- Company dashboard with drive and applicant overview
- Create and manage placement drives
  - Add eligibility criteria, deadlines, and descriptions
  - Edit, close, or delete existing drives
- Applicant management
  - View all applicants per drive with applicant count per drive
  - Update application status (Shortlisted / Selected / Rejected)
  - Mark students as officially placed with CTC/package
- View complete placement records

#### Student Portal
- User-friendly dashboard with drive and application overview
- View and update personal profile
  - Upload resume link
  - Update branch and skills
- Browse available placement drives
- Smart application flow
  - Apply to open drives with a single click
  - View application history with real-time status tracking
- Access personal placement history with package details

---

## 🛠 Technology Stack

### Backend
- **Flask** — Lightweight Python web framework
- **Flask-SQLAlchemy** — ORM for database operations
- **Flask-Login** — User session management
- **Werkzeug** — Password hashing and security utilities

### Frontend
- **HTML5 / CSS3** — Structure and styling
- **Jinja2** — Template engine
- **Bootstrap 5** — Responsive UI framework
- **Chart.js** — Interactive dashboard charts

### Database
- **SQLite** — Lightweight relational database

---

## 🗄 Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│      USER       │
│─────────────────│
│ id (PK)         │
│ name            │
│ email (UNIQUE)  │
│ password        │
│ role            │
│ is_active       │
└─────────────────┘
        │
   ─────┴─────
   │         │
   │ 1:1     │ 1:1
   ▼         ▼
┌──────────────┐    ┌──────────────────┐
│   STUDENT    │    │    COMPANY       │
│──────────────│    │──────────────────│
│ id (PK)      │    │ id (PK)          │
│ user_id (FK) │    │ user_id (FK)     │
│ branch       │    │ company_name     │
│ skills       │    │ hr_contact       │
│ resume_link  │    │ website          │
└──────────────┘    │ description      │
        │           │ status           │
        │ 1:N       └──────────────────┘
        │                   │ 1:N
        ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│   APPLICATION    │  │      DRIVE       │
│──────────────────│  │──────────────────│
│ id (PK)          │  │ id (PK)          │
│ student_id (FK)  │  │ company_id (FK)  │
│ drive_id (FK)    │  │ title            │
│ applied_on       │  │ description      │
│ status           │  │ eligibility      │
└──────────────────┘  │ deadline         │
        │             │ status           │
        │             └──────────────────┘
        │                     │
        └──────────┬──────────┘
                   │
                   ▼
          ┌──────────────────┐
          │    PLACEMENT     │
          │──────────────────│
          │ id (PK)          │
          │ student_id (FK)  │
          │ drive_id (FK)    │
          │ company_id (FK)  │
          │ package          │
          │ placed_on        │
          │ status           │
          └──────────────────┘
```

---

## 📡 Route Design

### Authentication

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/login` | Render login page | Public |
| POST | `/login` | Authenticate user | Public |
| GET | `/register/student` | Render student registration page | Public |
| POST | `/register/student` | Create student account | Public |
| GET | `/register/company` | Render company registration page | Public |
| POST | `/register/company` | Create company account | Public |
| GET | `/logout` | Log out user | Authenticated |

### Admin Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/admin/dashboard` | Admin dashboard | Admin |
| GET | `/admin/students` | View all students | Admin |
| GET | `/admin/companies` | View all companies | Admin |
| GET | `/admin/toggle_user/<id>/<source>` | Enable/disable user | Admin |
| GET | `/admin/company/approve/<id>` | Approve company | Admin |
| GET | `/admin/company/reject/<id>` | Reject company | Admin |
| GET | `/admin/drives` | View all drives | Admin |
| GET | `/admin/drive/approve/<id>` | Approve a drive | Admin |
| GET | `/admin/drive/close/<id>` | Close a drive | Admin |
| GET | `/admin/applications` | View all applications | Admin |
| GET | `/admin/placements` | View all placements | Admin |
| GET | `/admin/search` | Render search page | Admin |
| POST | `/admin/search` | Search students/companies | Admin |
| POST | `/admin/company/blacklist/<id>` | Remove company | Admin |
| POST | `/admin/student/blacklist/<id>` | Remove student | Admin |

### Student Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/student/dashboard` | Student dashboard | Student |
| GET | `/student/drives` | View available drives | Student |
| GET | `/student/apply/<drive_id>` | Apply for a drive | Student |
| GET | `/student/applications` | View applied drives | Student |
| GET | `/student/placements` | View placement history | Student |
| GET | `/student/profile` | View profile | Student |
| POST | `/student/profile` | Update profile | Student |

### Company Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/company/dashboard` | Company dashboard | Company |
| GET | `/company/create_drive` | Render create drive page | Company |
| POST | `/company/create_drive` | Create new drive | Company |
| GET | `/company/drives` | View created drives | Company |
| GET | `/company/drive/edit/<id>` | Render edit drive page | Company |
| POST | `/company/drive/edit/<id>` | Update drive | Company |
| GET | `/company/drive/close/<id>` | Close a drive | Company |
| GET | `/company/drive/delete/<id>` | Delete a drive | Company |
| GET | `/company/applicants` | View all applicants | Company |
| GET | `/company/update_application/<id>/<status>` | Update application status | Company |
| POST | `/company/mark_selected` | Mark student as placed | Company |
| GET | `/company/placements` | View placement records | Company |
| GET | `/company/profile` | View company profile | Company |
| POST | `/company/profile` | Update company profile | Company |

### API Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/drives` | Get all approved drives | Public |
| GET | `/api/students` | Get all students | Public |
| GET | `/api/drives/<drive_id>/applications` | Get applications for a drive | Public |
| GET | `/api/students/<student_id>` | Get student profile | Public |

---

## 📁 Project Structure

```
placement-portal/
│
├── app.py                      # Flask application entry point
├── models.py                   # SQLAlchemy database models
│
├── db/                         # Database configuration
│   ├── __init__.py
│   └── database.py             # Database setup and initialization
│
├── routes/                     # Flask Blueprints
│   ├── __init__.py
│   ├── auth_routes.py          # Authentication routes
│   ├── admin_routes.py         # Admin portal routes
│   ├── student_routes.py       # Student portal routes
│   ├── company_routes.py       # Company portal routes
│   └── api_routes.py           # REST API endpoints
│
├── templates/                  # Jinja2 templates
│   ├── base.html               # Base template
│   ├── home.html               # Landing page
│   │
│   ├── auth/
│   │   ├── login.html
│   │   ├── register_company.html
│   │   └── register_student.html
│   │
│   ├── admin/
│   │   ├── applications.html
│   │   ├── companies.html
│   │   ├── dashboard.html
│   │   ├── drives.html
│   │   ├── placements.html
│   │   ├── search.html
│   │   └── students.html
│   │
│   ├── company/
│   │   ├── applicants.html
│   │   ├── create_drive.html
│   │   ├── dashboard.html
│   │   ├── drives.html
│   │   ├── edit_drive.html
│   │   ├── placements.html
│   │   └── profile.html
│   │
│   └── student/
│       ├── applications.html
│       ├── dashboard.html
│       ├── drives.html
│       ├── placements.html
│       └── profile.html
│
├── static/                     # CSS and static files
│
└── instance/
    └── database.db             # SQLite database file
```

---

## 🚀 Quick Start

```bash
# 1. Download or clone the repository
git clone <repo-url>
cd placement-portal

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python app.py
```

The app will be live at **http://127.0.0.1:5000**

---

## 🔑 Demo Credentials

> This is a demo project — feel free to log in with any role and explore all dashboards.

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@placement.com` | `admin123` |

**Student & Company accounts** follow the `<first-name>123` password format:

| Example Email | Password |
|---------------|----------|
| `Sneha@student.com` | `sneha123` |
| `hr@techforge.com` | `techforge123` |

> **Pattern:** Take the part before `@`, and append `123`.  
> For example `john@university.com` → `john123`

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by Parth Sharma

</div>
