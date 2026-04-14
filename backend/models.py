# %%
from pydantic import BaseModel, Field
from typing import Literal, List

# %%
class StudentInput(BaseModel):
    """ Input schema for student data - validates income API requests """
    age: int = Field(ge=10, le=20, description = "Student age in years")
    gender: Literal["male","female"] # Literal type means only these values are allowed
    attendance_rate: float = Field(ge=0.0, le=100, description = "Attendance rate as a percentage") # ge = greater than or equal to, le = less than or equal to
    previous_grade: Literal["A","B","C","D","F"]
    distance_to_school: float = Field(ge=0.0, description = "Distance to school in kilometers")
    parent_education: Literal["none","primary","secondary","higher"]
    household_income: Literal["low","medium","high"]

    class Config:
        json_schema_extra = {
            "example": {
                "age": 15,
                "gender": "female",
                "attendance_rate": 85.5,
                "previous_grade": "B",
                "distance_to_school": 2.5,
                "parent_education": "secondary",
                "household_income": "medium"
            }
        }
class PredictionResponse(BaseModel):
    """ Schema for batch predictions"""
    risk_score: float = Field(ge=0.0, le=1.0, description = "Predicted risk score for dropping out (0-1)")
    risk_category: Literal["low","medium","high"] = Field(description = "Risk category based on risk score")
    confidence: float = Field(ge=0.0, le=1.0, description = "Model confidence in prediction (0-1)")
    top_risk_factors: List[str] = Field(description = "Most important factors contributing for this prediction")

class BatchStudentInput(BaseModel):
    """ Input schema for batch student data - validates batch prediction API requests """
    students: List[StudentInput] # List of student input data for batch predictions comes from the StudentInput schema

class BatchPredictionResponse(BaseModel):
    """ Schema for batch prediction responses"""
    predictions: List[dict]
    total_students: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int

# %%



