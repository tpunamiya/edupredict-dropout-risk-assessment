# EduPredict: Student Dropout Risk Assessment

A full-stack machine learning application for predicting student dropout risk in low-resource educational settings in India.

## Overview

EduPredict helps schools and NGOs identify at-risk students early, enabling targeted interventions to reduce India's 12-15% secondary school dropout rate.

##  Features

- **ML-powered predictions** using Random Forest classifier
- **Risk categorization** (Low, Medium, High)
- **Prediction history** with SQLite database
- **Statistics dashboard** with real-time metrics
- **CSV export** for data analysis
- **UI** built with React

## Tech Stack

**Backend:**
- Python 3.x
- FastAPI
- Pydantic (validation)
- scikit-learn (ML)
- SQLAlchemy (ORM)
- SQLite (database)

**Frontend:**
- React
- Axios
- CSS3

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python train_model.py  # Train the ML model
uvicorn main:app --reload
```

Backend runs on: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs on: `http://localhost:3000`

## API Endpoints

- `POST /predict` - Get dropout risk prediction
- `GET /history` - View prediction history
- `GET /history/stats` - Get statistics
- `GET /health` - Health check

Full API docs: `http://localhost:8000/docs`

## Use Case

Designed for schools and NGOs working in low-resource areas to:
- Identify students at risk of dropping out
- Prioritize intervention resources
- Track outcomes over time
- Make data-driven decisions
