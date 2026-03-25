# 🏃 HealthFit AI — Intelligent Health & Fitness Platform

A full-stack AI-powered health and fitness monitoring application built with:
- **Backend**: Flask + MySQL
- **Frontend**: React + TypeScript + Redux Toolkit
- **AI**: Scikit-learn, TensorFlow, MediaPipe, OpenCV
- **Database**: MySQL (no Docker required)

---

## 🚀 Quick Start (Windows)

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL 8.0+ (running on port 3306 with password `root123`)

### 1. Database Setup
```bash
# Open MySQL Workbench or MySQL CLI and run:
mysql -u root -proot123 < database/mysql/schema.sql
mysql -u root -proot123 < database/mysql/sample_data.sql
```

### 2. Automated Setup
```bash
scripts\setup_mysql.bat
```

### 3. Manual Setup (if script fails)

#### Backend
```bash
cd backend/flask-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy ..\..\env.example .env
python run.py
```

#### AI Models API
```bash
cd ai-models
pip install -r requirements-ai.txt
python api/main.py
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

---

## 📁 Project Structure

```
healthfit/
├── backend/flask-backend/     # Flask REST API
│   ├── app/
│   │   ├── models/            # SQLAlchemy database models
│   │   ├── routes/            # API route handlers
│   │   └── config.py
│   └── run.py
├── database/mysql/            # SQL schema and seed data
├── ai-models/                 # AI/ML components
│   ├── sklearn_models/        # Health risk prediction
│   ├── tensorflow_models/     # Deep learning models
│   ├── mediapipe_integration/ # Exercise form analysis
│   ├── opencv_processing/     # Food scanning
│   └── api/                   # FastAPI AI service
├── frontend/                  # React TypeScript app
│   └── src/
│       ├── pages/             # Page components
│       ├── components/        # Shared components
│       ├── services/          # API service layer
│       ├── store/             # Redux state
│       └── hooks/             # Custom hooks
└── scripts/                   # Setup & utility scripts
```

---

## 🌐 API Endpoints

### Auth (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Create account |
| POST | `/login` | Login & get JWT |
| POST | `/logout` | Invalidate token |
| GET | `/me` | Get current user |

### Health (`/api/health`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/metrics` | Get all metrics |
| POST | `/metrics` | Add new metric |
| GET | `/metrics/latest` | Get latest readings |
| GET | `/summary` | Health summary |

### Appointments (`/api/appointments`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List appointments |
| POST | `/` | Book appointment |
| PUT | `/:id` | Update appointment |
| DELETE | `/:id` | Cancel appointment |

### Nutrition (`/api/nutrition`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/meals` | Get meal log |
| POST | `/meals` | Log a meal |
| GET | `/recommendations` | AI meal suggestions |

### AI (`/api/ai`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict-risk` | Health risk prediction |
| POST | `/analyze-sleep` | Sleep quality analysis |
| POST | `/detect-stress` | Stress level detection |
| POST | `/analyze-exercise` | Exercise form check |

---

## 🔐 Default Credentials (Sample Data)
- **Patient**: `patient@healthfit.com` / `password123`
- **Doctor**: `doctor@healthfit.com` / `password123`
- **Admin**: `admin@healthfit.com` / `admin123`

---

## 🛠 Troubleshooting
Run `scripts\fix_all.bat` to auto-diagnose common issues.
"# ai-project" 
