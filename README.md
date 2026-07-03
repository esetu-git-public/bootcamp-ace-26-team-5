# bootcamp-ace-26-team-5
Bootcamp by ACE students Team 1

# 🏥 Healthcare Insurance Claim Fraud Detection System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
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
| 🟢 Low | Auto Approval |
| 🟡 Medium | Claim Officer Review |
| 🔴 High | Fraud Investigation |

---

### 👥 Role-Based Access

- Admin
- Claim Officer
- Fraud Investigator
- Manager

---

### 📊 Dashboard

- Total Claims
- Fraud Claims
- Genuine Claims
- Pending Claims
- Fraud Detection Rate
- Monthly Trends
- Processing Time
- Investigation Status

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

- JWT Authentication
- Role-Based Authorization
- Audit Logs
- Secure Database

---

# 🏗️ System Architecture

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
                    FastAPI Backend
                           │
     ┌─────────────────────┼──────────────────────┐
     │                     │                      │
 Authentication      Business Logic         ML Engine
     │                     │                      │
     │              Risk Scoring          Fraud Prediction
     │              Auto Approval         Explainability
     │              Audit Logs            Probability
     │
                  SQLite Database
```

---

# ⚙️ Project Workflow

```
Claim Submitted
       │
       ▼
Data Validation
       │
       ▼
Preprocessing
       │
       ▼
Feature Engineering
       │
       ▼
Fraud Detection Model
       │
       ▼
Fraud Probability
       │
       ▼
Risk Engine
       │
 ┌─────┼───────────────┐
 │     │               │
 ▼     ▼               ▼
Low  Medium          High
 │     │               │
 ▼     ▼               ▼
Auto Claim       Fraud
Approve Officer Investigator
 │     │               │
 └─────┴───────────────┘
       │
       ▼
Database
       │
       ▼
Dashboard
       │
       ▼
Reports
```

---

# 🧠 Machine Learning Pipeline

```
Dataset
   │
   ▼
Data Cleaning
   │
   ▼
Missing Value Handling
   │
   ▼
Encoding
   │
   ▼
Feature Engineering
   │
   ▼
Train/Test Split
   │
   ▼
Model Training
(Random Forest / XGBoost)
   │
   ▼
Model Evaluation
   │
   ▼
Best Model Saved
   │
   ▼
Prediction API
```

---

# 📁 Project Structure

```
healthcare-fraud-detection/

├── dataset/
├── models/
├── ml/
├── backend/
├── frontend/
├── database/
├── reports/
├── logs/
├── docs/
├── README.md
├── requirements.txt
└── run.py
```

---

# 🛠️ Technology Stack

## Frontend

- React.js
- Tailwind CSS
- Axios
- React Router
- Chart.js

---

## Backend

- FastAPI
- Python
- JWT Authentication
- Pydantic

---

## Machine Learning

- Scikit-learn
- Random Forest
- XGBoost
- Pandas
- NumPy
---

## Database

- SQLite
- SQLAlchemy

---

## Tools

- Git
- GitHub
- VS Code
- Postman

---

# 👨‍💻 User Roles

## 👑 Admin

- Manage Users
- Manage Roles
- View All Claims
- Generate Reports
- Audit Logs
- Dashboard

---

## 👨‍💼 Claim Officer

- View Assigned Claims
- Review Medium Risk Claims
- Approve Claims
- Reject Claims

---

## 🕵️ Fraud Investigator

- View High Risk Claims
- Review AI Prediction
- Investigate Documents
- Final Decision

---

## 📊 Manager

- Dashboard
- Analytics
- Reports
- Fraud Trends

---

# 📈 Business Workflow Example

### Step 1

Customer submits a healthcare claim.

↓

### Step 2

Backend validates the claim.

↓

### Step 3

ML model predicts fraud probability.

↓

Example

```
Fraud Probability = 87%
```

↓

### Step 4

Risk Engine

```
87%

↓

HIGH RISK
```

↓

### Step 5

Claim routed to Fraud Investigator.

↓

### Step 6

Investigator reviews claim.

↓

### Step 7

Final decision stored.

↓

### Step 8

Dashboard updates automatically.

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
- Processing Time: **2–5 seconds**
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
- ✅ Backend Development
- ✅ Database Integration
- ✅ Frontend Development
- ✅ Dashboard
- ✅ Reports
- ✅ Testing
- ✅ Documentation

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

- Explainable AI (SHAP)
- Real-time Notifications
- Email Alerts
- Cloud Deployment
- OCR for Medical Documents
- Deep Learning Models
- Mobile Application
- Multi-language Support

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

The **Healthcare Insurance Claim Fraud Detection System** combines **Machine Learning**, **FastAPI**, **React**, and **SQLite** to create an intelligent claim processing platform. By automating fraud detection and streamlining the review process, it helps reduce financial losses, improve operational efficiency, and support faster decision-making for insurance providers.

---

<div align="center">

### ⭐ If you found this project useful, consider giving it a star!

**Made with ❤️ using Python, FastAPI, React & Machine Learning**

</div>
