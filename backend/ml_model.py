import joblib
import numpy as np
from typing import Dict, List
import os

class DropoutPredictor:
    """Wrapper class for the trained dropout prediction model"""
    
    def __init__(self):
        """Load the trained model and encoders"""
        print("🔄 Loading ML model and encoders...")
        
        # Check if model files exist
        required_files = [
            'dropout_model.pkl',
            'encoder_gender.pkl',
            'encoder_grade.pkl',
            'encoder_parent.pkl',
            'encoder_income.pkl',
            'feature_names.pkl'
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"❌ Model file not found: {file}. Did you run train_model.py?")
        
        # Load model and encoders
        self.model = joblib.load('dropout_model.pkl')
        self.le_gender = joblib.load('encoder_gender.pkl')
        self.le_grade = joblib.load('encoder_grade.pkl')
        self.le_parent = joblib.load('encoder_parent.pkl')
        self.le_income = joblib.load('encoder_income.pkl')
        self.feature_names = joblib.load('feature_names.pkl')
        
        print("✅ Model loaded successfully!")
    
    def _encode_features(self, student_data: Dict) -> np.ndarray:
        """Convert raw student data into encoded feature array"""
        features = [
            student_data['age'],
            student_data['attendance_rate'],
            student_data['distance_to_school'],
            self.le_gender.transform([student_data['gender']])[0],
            self.le_grade.transform([student_data['previous_grade']])[0],
            self.le_parent.transform([student_data['parent_education']])[0],
            self.le_income.transform([student_data['household_income']])[0]
        ]
        return np.array(features).reshape(1, -1)
    
    def predict(self, student_data: Dict) -> Dict:
        """
        Make a dropout risk prediction for a single student
        
        Args:
            student_data: Dictionary with student information
            
        Returns:
            Dictionary with risk_score, risk_category, confidence, and top_risk_factors
        """
        # Encode features
        features_array = self._encode_features(student_data)
        
        # Get prediction probability
        risk_score = self.model.predict_proba(features_array)[0][1]
        
        # Categorize risk level
        if risk_score > 0.7:
            category = "high"
        elif risk_score > 0.4:
            category = "medium"
        else:
            category = "low"
        
        # Get feature importance for this prediction
        feature_importance = self.model.feature_importances_
        top_indices = np.argsort(feature_importance)[-3:][::-1]
        top_factors = [self.feature_names[i].replace('_', ' ').title() for i in top_indices]
        
        return {
            "risk_score": float(risk_score),
            "risk_category": category,
            "confidence": 0.85,
            "top_risk_factors": top_factors
        }
    
    def predict_batch(self, students: List[Dict]) -> List[Dict]:
        """
        Make predictions for multiple students
        
        Args:
            students: List of student data dictionaries
            
        Returns:
            List of prediction dictionaries
        """
        predictions = []
        for student in students:
            result = self.predict(student)
            predictions.append({
                **student,
                **result
            })
        return predictions

# Initialize predictor (singleton pattern - loaded once at startup)
try:
    predictor = DropoutPredictor()
except FileNotFoundError as e:
    print(f"⚠️  Warning: {e}")
    print("⚠️  API will start but predictions will fail until model is trained.")
    predictor = None