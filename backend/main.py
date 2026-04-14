from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from models import StudentInput, PredictionResponse, BatchStudentInput, BatchPredictionResponse
from ml_model import predictor
from database import get_db, PredictionHistory

app = FastAPI(
    title="EduPredict API",
    description="Student Dropout Risk Prediction System with History Tracking",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "🎓 EduPredict API is running",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "predict": "/predict",
            "batch": "/predict/batch",
            "history": "/history",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check with database connection test"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "model_loaded": predictor is not None,
        "database": db_status
    }

@app.post("/predict", response_model=PredictionResponse)
def predict_dropout(student: StudentInput, db: Session = Depends(get_db)):
    """
    Predict dropout risk for a single student
    Results are automatically saved to database
    """
    if predictor is None:
        raise HTTPException(
            status_code=503, 
            detail="Model not loaded. Please train the model first."
        )
    
    try:
        # Make prediction
        result = predictor.predict(student.model_dump())
        
        # Save to database
        db_prediction = PredictionHistory(
            age=student.age,
            gender=student.gender,
            attendance_rate=student.attendance_rate,
            previous_grade=student.previous_grade,
            distance_to_school=student.distance_to_school,
            parent_education=student.parent_education,
            household_income=student.household_income,
            risk_score=result['risk_score'],
            risk_category=result['risk_category']
        )
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)  # Get the ID that was assigned
        
        # Add ID to response
        result['prediction_id'] = db_prediction.id
        
        return result
    except Exception as e:
        db.rollback()  # Undo changes if something went wrong
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(batch: BatchStudentInput, db: Session = Depends(get_db)):
    """Predict dropout risk for multiple students"""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")
    
    try:
        students_data = [student.model_dump() for student in batch.students]
        predictions = predictor.predict_batch(students_data)
        
        # Save all predictions to database
        for student, pred in zip(batch.students, predictions):
            db_prediction = PredictionHistory(
                age=student.age,
                gender=student.gender,
                attendance_rate=student.attendance_rate,
                previous_grade=student.previous_grade,
                distance_to_school=student.distance_to_school,
                parent_education=student.parent_education,
                household_income=student.household_income,
                risk_score=pred['risk_score'],
                risk_category=pred['risk_category']
            )
            db.add(db_prediction)
        
        db.commit()
        
        # Count risk categories
        high_risk = sum(1 for p in predictions if p['risk_category'] == 'high')
        medium_risk = sum(1 for p in predictions if p['risk_category'] == 'medium')
        low_risk = sum(1 for p in predictions if p['risk_category'] == 'low')
        
        return {
            "predictions": predictions,
            "total_students": len(predictions),
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

@app.get("/history")
def get_history(
    limit: int = 10, 
    risk_category: str = None,
    db: Session = Depends(get_db)
):
    """
    Get prediction history
    
    - **limit**: Number of records to return (default: 10, max: 100)
    - **risk_category**: Filter by risk level (optional: 'low', 'medium', 'high')
    """
    # Build query
    query = db.query(PredictionHistory).order_by(PredictionHistory.timestamp.desc())
    
    # Apply filters
    if risk_category:
        if risk_category not in ['low', 'medium', 'high']:
            raise HTTPException(status_code=400, detail="Invalid risk_category. Must be: low, medium, or high")
        query = query.filter(PredictionHistory.risk_category == risk_category)
    
    # Limit results
    limit = min(limit, 100)  # Max 100 records
    predictions = query.limit(limit).all()
    
    # Convert to list of dicts
    results = []
    for pred in predictions:
        results.append({
            "id": pred.id,
            "age": pred.age,
            "gender": pred.gender,
            "attendance_rate": pred.attendance_rate,
            "previous_grade": pred.previous_grade,
            "distance_to_school": pred.distance_to_school,
            "parent_education": pred.parent_education,
            "household_income": pred.household_income,
            "risk_score": pred.risk_score,
            "risk_category": pred.risk_category,
            "timestamp": pred.timestamp.isoformat()
        })
    
    return {
        "count": len(results),
        "predictions": results
    }

@app.get("/history/stats")
def get_history_stats(db: Session = Depends(get_db)):
    """Get statistics about prediction history"""
    total = db.query(PredictionHistory).count()
    high_risk = db.query(PredictionHistory).filter(PredictionHistory.risk_category == 'high').count()
    medium_risk = db.query(PredictionHistory).filter(PredictionHistory.risk_category == 'medium').count()
    low_risk = db.query(PredictionHistory).filter(PredictionHistory.risk_category == 'low').count()
    
    # Get average risk score
    avg_risk = db.query(PredictionHistory).with_entities(
        PredictionHistory.risk_score
    ).all()
    avg_risk_score = sum(r[0] for r in avg_risk) / len(avg_risk) if avg_risk else 0
    
    return {
        "total_predictions": total,
        "risk_distribution": {
            "high": high_risk,
            "medium": medium_risk,
            "low": low_risk
        },
        "average_risk_score": round(avg_risk_score, 3)
    }

@app.delete("/history/clear")
def clear_history(db: Session = Depends(get_db)):
    """Delete all prediction history (use with caution!)"""
    count = db.query(PredictionHistory).count()
    db.query(PredictionHistory).delete()
    db.commit()
    return {
        "message": f"Deleted {count} predictions from history",
        "deleted_count": count
    }

@app.get("/model/info")
def model_info():
    """Get information about the loaded model"""
    if predictor is None:
        return {"error": "Model not loaded"}
    
    return {
        "model_type": "Random Forest Classifier",
        "features": predictor.feature_names,
        "feature_importance": {
            name: float(imp) 
            for name, imp in zip(predictor.feature_names, predictor.model.feature_importances_)
        }
    }