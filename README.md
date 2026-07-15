# bootcamp-ace-26-team-5
Bootcamp by ACE students Team 5

# 🏥 Healthcare Insurance Claim Fraud Detection System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange?style=for-the-badge&logo=scikitlearn)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite)
![License](https://img.shields.io/badge/Academic-Project-success?style=for-the-badge)

### AI-Powered Healthcare Insurance Claim Fraud Detection Platform

*A full-stack machine learning system that automates fraud detection, risk assessment, claim processing, and management reporting.*

</div>

---

# 📖 Project Overview

Healthcare insurance companies process thousands of claims every day. Manually verifying every claim is time-consuming, expensive, and prone to human error.

This project provides an **AI-powered Healthcare Insurance Claim Fraud Detection System** that automatically analyzes insurance claims, predicts fraudulent activity using Machine Learning, assigns a risk score, and routes claims through an intelligent workflow.

Instead of only predicting whether a claim is fraudulent, the system provides a complete business workflow including:

- 🤖 AI-based Fraud Detection
- 📊 Risk Scoring
- ✅ Automatic Claim Approval
- 👨‍💼 Manual Investigation
- 📈 Management Dashboard
- 📑 Reports & Analytics
- 🔐 Role-Based Access Control
- 📝 Audit Trail

---

# 🎯 Problem Statement

Insurance fraud results in significant financial losses every year.

Traditional claim verification:

- Slow
- Manual
- Error-prone
- Difficult to scale

Our solution introduces Machine Learning to:

- Detect suspicious claims
- Reduce fraudulent payouts
- Speed up genuine claim approvals
- Assist investigators with AI-generated insights

---

# 🚀 Project Objectives

- Detect fraudulent healthcare insurance claims.
- Minimize false fraud alerts.
- Automatically approve genuine claims.
- Route suspicious claims for investigation.
- Generate business insights through dashboards.
- Maintain complete audit history.
- Support multiple user roles securely.

---

# 💡 Key Features

### 🤖 AI Fraud Detection

- Fraud Prediction
- Fraud Probability
- Risk Classification
- Explainable AI

---

### ⚡ Intelligent Risk Scoring

| Risk | Action |
|-------|---------|
| 🟢 Low | Auto Approval (Probability < 30%) |
| 🟡 Medium | Claim Officer Review (30% <= Probability < 70%) |
| 🔴 High | Fraud Investigation (Probability >= 70%) |

---

### 👥 Role-Based Access

- Admin
- Claim Officer (Employee)
- Fraud Investigator
- Supervisor (Manager)
- Customer (Patient)

---

### 📊 Dashboard

- Total Claims
- Fraud Claims
- Genuine Claims
- Pending Claims
- Fraud Detection Rate
- Monthly Trends
- Average Claim Amount
- Risk Distribution
- Top Fraud Reasons

---

### 📑 Reports

- Daily Reports
- Weekly Reports
- Monthly Reports
- Fraud Trends
- Claim Statistics
- Investigator Performance

---

### 🔒 Security

- JWT Authentication (Access/Refresh Tokens)
- Role-Based Authorization (RBAC)
- Database Audit Logs (All transitions tracked)
- Secure Database (Bcrypt Hashed Passwords)

---

# 🏗️ System Architecture & Dual-Database Support

This project utilizes a modern dual-provider database design, allowing for seamless transition between local development and cloud production.

```
                    Healthcare Fraud Detection System

                           Users
                              │
     ┌────────────┬─────────────┬──────────────┬────────────┐
     │            │             │              │
   Admin     Claim Officer  Investigator   Manager
     │            │             │              │
     └────────────┴─────────────┴──────────────┘
                    React Frontend
                           │
                     Flask Backend
                           │
     ┌─────────────────────┼──────────────────────┐
     │                     │                      │
 Authentication      Business Logic         ML Engine
  (JWT Tokens)     (Services/Repos)    (predict.py Wrapper)
     │                     │                      │
     │              Risk Scoring          Fraud Prediction
     │              Auto Approval         Explainability
     │              Audit Logs            Probability
     │
     └─────────────────────┬──────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      SQLite Database            Supabase Cloud
     (Local Development)     (Production PostgreSQL)
```

### 🗄️ Dual-Database Engine (SQLite & Supabase)
- **SQLite (Default):** Runs locally using `database/claims.db` without requiring an internet connection or external registration. Perfect for testing and offline development.
- **Supabase (PostgreSQL):** Connects to a cloud database project. Staging or production environments use this option to store users, claims, predictions, and notifications.
- **Automatic Routing:** The backend dynamically checks the `DB_PROVIDER` environment variable (defaults to `sqlite`). All repositories (`user_repository.py`, `claim_repository.py`, etc.) execute provider-specific SQL calls or API requests depending on this setting.

---

# ⚙️ Claims Processing Workflow

When a healthcare claim is submitted, it goes through a multi-stage validation, scoring, and routing pipeline:

1. **Submission:** Claim data (including diagnosis/procedure codes, claim amounts, length of stay, state, and provider information) is sent via the REST API.
2. **Feature Engineering:** The ML inference engine computes dynamic features:
   - **Approval Ratio:** Approved Amount divided by Claim Amount.
   - **High Claim:** Flags claims with amounts exceeding $700.
   - **Long Stay:** Flags stays of 7 days or longer.
   - **Frequent Visitor:** Flags patients with 5+ visits in the past year.
   - **High Provider Load:** Flags healthcare providers with 70+ monthly claims.
   - **Risk Score:** Combined sum of all flag features.
3. **ML Scoring:** A Keras 3 neural network model (trained with a PyTorch backend) predicts the probability of fraud.
4. **Intelligent Risk Engine Routing:**
   - 🟢 **Low Risk (<30%):** Automatically sets status to `APPROVED`, writes to audit logs, and triggers a success notification.
   - 🟡 **Medium Risk (30% to 70%):** Sets status to `UNDER_REVIEW` and routes the claim to the Claim Officer's review queue.
   - 🔴 **High Risk (>=70%):** Sets status to `INVESTIGATION` and routes the claim to the Fraud Investigator's high-risk queue.
5. **Human-in-the-Loop Decision:** Claims officers and investigators review explanation tags, modify status, and commit final approvals/rejections.
6. **Audit Trail:** Every transition is tracked by the system audit logger.

---

# 🧠 Machine Learning & Inference Pipeline

The core AI capability of the system is powered by Keras 3:

- **Model Engine:** Keras 3 neural network classifier using PyTorch backend (`best_model.keras`).
- **Preprocessor:** Numerical features (imputation + standard scaling) and categorical features (One-Hot encoding) are transformed using a serialized preprocessor pipeline (`preprocessor_keras.pkl`).
- **Explainability Module:** If a claim gets flagged, the system inspects the computed features (e.g. high claim amount, visit frequency) and automatically generates natural language reason tags so investigators understand *why* the model scored the claim as suspicious.
- **Alternative Models:** Scikit-Learn classifiers (XGBoost, Random Forest, Logistic Regression, Decision Tree) are also preserved for evaluation and performance benchmarking.

---

# 📁 Project Structure

```
healthcare-fraud-detection/
├── backend/                        # Flask Backend Service
│   ├── app.py                      # Flask Application Entrypoint
│   ├── config.py                   # Environment and Path Settings
│   ├── database.py                 # SQLAlchemy initialization context
│   ├── models.py                   # Database table SQLAlchemy mappings
│   ├── middleware/                 # Auth and error middleware decorators
│   ├── routes/                     # Blueprint controllers (auth, claims, etc.)
│   ├── services/                   # Business and ML integration layer
│   ├── repositories/               # ORM database query files
│   ├── validators/                 # Request validation schemas
│   └── utils/                      # Password hashing, response templates, logger
├── database/                       # SQLite DB and migration scripts
│   ├── schema.sql                  # Main SQLite schema setup
│   ├── init_db.py                  # Database creator helper
│   ├── seed_data.py                # Hashed password mockup data seeder
│   └── claims.db                   # SQLite database (Git ignored)
├── ml/                             # Machine Learning module
│   ├── Insurance_Fraud_Detection.ipynb # Training notebook
│   ├── predict.py                  # Live model scoring and preprocessing
│   └── models/                     # Serialized pkl model and transformers
├── frontend/                       # React Frontend Service
│   ├── src/                        # UI screens, api client, and components
│   ├── package.json                # Frontend requirements
│   └── vite.config.js              # Bundler configuration
├── docs/                           # Empty placeholder specifications
└── README.md                       # Main documentation (this file)
```

---

# 🚀 Setup & Run Instructions

This project supports running in **SQLite mode** (local development, default) or **Supabase mode** (cloud Postgres database).

For detailed configuration options, see [DEPLOYMENT.md](file:///d:/ML%20bootcamp%20project/bootcamp-ace-26-team-5/healthcare-fraud-detection/DEPLOYMENT.md).

### ⚡ Single-Command Setup & Startup (Recommended)
You can automatically configure environment variables, initialize/seed the local SQLite database, install all backend and frontend dependencies, and launch both servers concurrently in a single command from the project root folder:

- **Windows:**
  Using PowerShell (Recommended):
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\\run.ps1
  ```
  Or using Command Prompt:
  ```cmd
  run.bat
  ```
- **macOS / Linux:**
  ```bash
  chmod +x run.sh ran.sh
  ./run.sh    # or: ./ran.sh
  ```

### 1. Prerequisites
- **Python:** 3.11+
- **Node.js:** 18+

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd healthcare-fraud-detection/backend
   ```
2. Set up virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   
   pip install -r requirements.txt
   ```
3. Copy environment variables:
   ```bash
   copy .env.example .env
   ```
4. Initialize and seed the local database:
   ```bash
   # From root directory:
   python database/init_db.py
   python database/seed_data.py
   ```
5. Start backend:
   ```bash
   python app.py
   ```

### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd healthcare-fraud-detection/frontend
   ```
2. Install packages:
   ```bash
   npm install
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```
4. Access the portal at `http://localhost:5173`.


---

# 🛠️ Technology Stack

## Frontend

- React.js (v19)
- Tailwind CSS
- Axios (API Client)
- React Router (v7)
- Recharts (Analytics Charts)

---

## Backend

- Flask (v3)
- Python (v3.11+)
- Flask-SQLAlchemy (ORM)
- Flask-JWT-Extended (Authentication)
- Bcrypt (Password encryption)

---

## Machine Learning

- Scikit-learn
- XGBoost
- Joblib (Model loading)
- Pandas
- NumPy
---

## Database

- SQLite
- SQLAlchemy ORM

---

## Tools

- Git
- GitHub
- VS Code
- Postman

---

# 👨‍💻 User Roles

## 👑 Admin

- Manage Users & Roles
- View All Claims and System logs
- Generate Management Reports
- Read Database Audit Logs
- Global Analytics Dashboard

---

## 👨💼 Claim Officer (Employee)

- View Assigned Claims
- Review Medium Risk Claims (30%-70% probability)
- Approve or Reject Claims manually

---

## 🕵️ Fraud Investigator

- View High Risk Claims (>= 70% probability)
- Review ML explanation remarks
- Investigate claim details & file attachments
- Log final approve/reject decisions

---

## 📊 Manager / Supervisor

- View Analytics Dashboards
- Review Fraud Trends and averages
- Export Claim Statistics Reports

---

# 📈 Business Workflow Example

### Step 1

Customer submits a healthcare claim.

↓

### Step 2

Backend validates the claim structure.

↓

### Step 3

Inference engine pre-processes inputs and XGBoost predicts fraud probability.

↓

Example

```
Fraud Probability = 87%
```

↓

### Step 4

Risk Engine routes claim to `HIGH RISK` manual queue.

↓

### Step 5

Claim is routed to the Fraud Investigator queue.

↓

### Step 6

Investigator reviews claim details and prediction reasons.

↓

### Step 7

Investigator submits decision, updating database state.

↓

### Step 8

Dashboard and audit logs update automatically in real-time.

---

# 📊 Dataset Features

Some important features include:

- Patient Age
- Patient Gender
- Diagnosis Code
- Procedure Code
- Claim Amount
- Approved Amount
- Insurance Type
- Claim Status
- Provider Specialty
- Previous Visits
- Length of Stay
- Chronic Condition Flag
- Days Between Service & Claim

Target Column

```
Is_Fraud
```

---

# 📈 Expected Results

- Fraud Detection Accuracy: **90–95% (target)**
- Processing Time: **< 1 second**
- Reduced Manual Investigation
- Faster Claim Approval
- Improved Fraud Detection
- Better Decision Making

---

# 📅 Development Roadmap

- ✅ Project Planning
- ✅ Dataset Analysis
- ✅ Data Preprocessing
- ✅ Model Training
- ✅ Backend Development (Flask Restruct)
- ✅ Database Integration (SQLAlchemy ORM)
- ✅ ML Integration (predict.py wrapper)
- ⏳ Frontend Development (Axios Integration)
- ⏳ Testing
- ⏳ Documentation

---

# 👥 Team Responsibilities

| Role | Responsibility |
|------|----------------|
| Team Lead | Architecture, ML Integration, Code Review |
| Frontend Developer | UI, Dashboard, Forms |
| Backend Developer | APIs, Authentication, Business Logic |
| Database Engineer | Database Design, SQL, Relationships |
| AI/ML Engineer | Data Processing, Model Training, Prediction |
| Documentation & Testing | SRS, Testing, Reports, Presentation |

---

# 🔮 Future Enhancements

- Explainable AI (SHAP / LIME integrations)
- Real-time Email Notifications (Flask-Mail)
- SMS & WhatsApp alerts (Twilio integration)
- Cloud Database deployment (Supabase migration)
- OCR for Medical Documents processing

---

# 📚 Academic Purpose

This project is developed as part of an academic initiative to demonstrate the integration of:

- Artificial Intelligence
- Machine Learning
- Full Stack Web Development
- Database Management
- Software Engineering Principles

into a complete healthcare fraud detection platform.

---

# ⭐ Conclusion

The **Healthcare Insurance Claim Fraud Detection System** combines **Machine Learning**, **Flask**, **React**, and **SQLite** to create an intelligent claim processing platform. By automating fraud detection and streamlining the review process, it helps reduce financial losses, improve operational efficiency, and support faster decision-making for insurance providers.

---

<div align="center">

### ⭐ If you found this project useful, consider giving it a star!

**Made with ❤️ using Python, Flask, React & Machine Learning**

</div>
