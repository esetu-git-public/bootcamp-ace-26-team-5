**MVP DEVELOPMENT REPORT**

**AI-Powered Insurance Claim Fraud Detection System**

Development Methodology: Agile Scrum

Sprint Model: Incremental MVP Delivery

Total Sprints: 6

# **What Is Our MVP Strategy?**

Instead of building the complete application at once, our project follows an Incremental MVP (Minimum Viable Product) approach. Each sprint delivers a functional, demonstrable product increment that adds business value while moving toward the final system.

### ***Every sprint answers three questions:***

* What business problem are we solving?

* What working functionality will we deliver?

* How does it contribute to the final product?

# **MVP Roadmap**

| Sprint | MVP Goal | Working Deliverable | Progress |
| :---- | :---- | :---- | :---: |
| Sprint 1 | Authentication MVP | Users can securely access the system | **✅ 100%** |
| Sprint 2 | Claim Management MVP | Claims can be submitted and stored | **✅ 100%** |
| Sprint 3 | AI Prediction MVP | AI predicts fraud with explainability | **✅ 100%** |
| Sprint 4 | Business Workflow MVP | End-to-end approval workflow | **🚧 In Progress** |
| Sprint 5 | Analytics & Testing MVP | Stable system with testing & reports | **⏳ Planned** |
| Sprint 6 | Final Release MVP | Production-ready project | **⏳ Planned** |

# **Sprint 1**

**Authentication MVP**

### ***Sprint Goal***

Build the project foundation and secure role-based authentication.

### ***Business Value***

Users can securely access the application according to their roles.

### ***Parallel Team Activities***

| Team | Parallel Activities |
| :---- | :---- |
| **Frontend** | Landing Page Signup Page Login Page Protected Routes |
| **Backend** | JWT Authentication Login APIs Signup APIs Role Authorization |
| **Database** | Supabase Setup Users Table Authentication Tables |
| **Machine Learning** | Dataset Collection Dataset Understanding Data Cleaning Plan |
| **QA** | Authentication Test Cases Login Testing |

### ***MVP Deliverable***

| Users can: Register Login Access role-based dashboards |
| :---- |

### ***Sprint Outcome***

A secure authentication system is fully functional.

# **Sprint 2**

**Claim Management MVP**

### ***Sprint Goal***

Enable complete insurance claim submission.

### ***Business Value***

Users can submit insurance claims digitally.

### ***Parallel Team Activities***

| Team | Parallel Activities |
| :---- | :---- |
| **Frontend** | Claim Submission Form My Claims Claim Details |
| **Backend** | Claim APIs Validation CRUD Operations |
| **Database** | Claims Table Relationships Data Storage |
| **Machine Learning** | Feature Engineering Input Pipeline Data Preparation |
| **QA** | Form Validation Tests API Tests |

### ***MVP Deliverable***

| Users can: Submit Claims View Claims Track Claim Status |
| :---- |

### ***Sprint Outcome***

Complete claim management workflow is functional.

# **Sprint 3**

**AI Fraud Detection MVP**

### ***Sprint Goal***

Integrate AI into the claim workflow.

### ***Business Value***

Claims receive fraud predictions automatically.

### ***Parallel Team Activities***

| Team | Parallel Activities |
| :---- | :---- |
| **Frontend** | Prediction Result Page Risk Score UI Explainability UI |
| **Backend** | ML Integration Prediction APIs Store Predictions |
| **Database** | Predictions Table Model Result Storage |
| **Machine Learning** | TensorFlow/Keras Model Fraud Prediction Explainable AI Risk Thresholds |
| **QA** | Prediction Testing Model Validation |

### ***MVP Deliverable***

| Users can: Fraud Probability Risk Level Explainability Reasons |
| :---- |

### ***Sprint Outcome***

AI fraud prediction becomes operational.

# **Sprint 4  *(Current Sprint)***

**Business Workflow MVP**

### ***Sprint Goal***

Complete the insurance claim approval workflow.

### ***Business Value***

Business users can process claims from submission to approval.

### ***Parallel Team Activities***

| Team | Parallel Activities |
| :---- | :---- |
| **Frontend** | User Dashboard Manager Dashboard Claim Inspector Dashboard Notification Panel API Integration |
| **Backend** | Auto Approval Logic Investigation Queue Notification APIs Dashboard APIs Audit Logs |
| **Database** | Notifications Table Analytics Queries Performance Optimization |
| **Machine Learning** | Improve Explainability TensorFlow Model Optimization API Integration Accuracy Improvement |
| **QA** | TDD Integration Testing Workflow Testing |

### ***MVP Deliverable***

| User submits claim ↓ AI Prediction ↓ Low Risk   →   Auto Approval *or* Medium / High Risk   →   Claim Inspector Review ↓ Manager Dashboard Updated |
| :---: |

### ***Sprint Outcome***

Complete business process becomes functional.

# **Sprint 5**

**Analytics & Quality MVP**

### ***Sprint Goal***

Improve reliability and provide business insights.

### ***Business Value***

Managers can monitor system performance with confidence.

### ***Parallel Team Activities***

| Team | Parallel Activities |
| :---- | :---- |
| **Frontend** | Analytics Dashboard Charts Reports |
| **Backend** | Analytics APIs Reporting APIs |
| **Database** | Query Optimization Dashboard Optimization |
| **Machine Learning** | Final Model Optimization Explainability Improvements |
| **QA** | Unit Testing API Testing Integration Testing Regression Testing |

### ***MVP Deliverable***

| Users can: Analytics Dashboard Reports Fully Tested System |
| :---- |

### ***Sprint Outcome***

Reliable and business-ready MVP.

# **Sprint 6**

**Production Release MVP**

### ***Sprint Goal***

Prepare the application for deployment and final demonstration.

### ***Business Value***

Deliver a complete, production-ready solution.

### ***Parallel Team Activities***

| Team | Parallel Activities |
| :---- | :---- |
| **Frontend** | UI Polish Responsive Design Performance Improvements |
| **Backend** | Bug Fixes Security Enhancements |
| **Database** | Final Optimization Backup Validation |
| **Machine Learning** | Final Validation Performance Evaluation |
| **QA** | User Acceptance Testing Final Regression Testing |

### ***MVP Deliverable***

| Users can: Authentication Claim Submission AI Fraud Prediction Explainability Notifications Analytics Manager Dashboard Claim Inspector Dashboard Fully Tested Product |
| :---- |

### ***Sprint Outcome***

Production-ready Insurance Claim Fraud Detection System.

# **MVP Progress Summary**

| Sprint | MVP Produced | Status |
| :---- | :---- | :---: |
| Sprint 1 | Authentication System | **✅ Complete** |
| Sprint 2 | Claim Submission System | **✅ Complete** |
| Sprint 3 | AI Fraud Prediction System | **✅ Complete** |
| Sprint 4 | Business Workflow System | **🚧 In Progress** |
| Sprint 5 | Analytics & Quality System | **⏳ Planned** |
| Sprint 6 | Final Product Release | **⏳ Planned** |

# **Final MVP Vision**

At the end of Sprint 6, the application will provide:

* Secure role-based authentication.

* Digital insurance claim submission.

* AI-powered fraud detection using TensorFlow/Keras.

* Explainable AI with fraud reasons.

* Automatic approval for low-risk claims.

* Manual review for medium- and high-risk claims.

* High-risk notifications for Claim Inspectors.

* Manager analytics dashboard with business insights.

* Supabase-backed data management.

* Comprehensive testing using Test-Driven Development.

* A complete, end-to-end working product ready for demonstration.

*This report demonstrates a true Agile MVP approach, where every sprint delivers a usable increment and all teams (Frontend, Backend, Database, ML, and QA) contribute in parallel toward a progressively more capable product.*