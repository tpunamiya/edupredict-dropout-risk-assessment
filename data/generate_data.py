# %%
import pandas as pd
import numpy as np
from faker import Faker

# %%
fake = Faker('en_IN')
np.random.seed(42)
def generate_students(n=1000):
    """Generate synthetic student data with realistic dropout patterns"""
    data = []
    for i in range(n):
        # Features that correlate with dropout
        attendance = np.random.normal(75, 15)
        attendance = np.clip(attendance, 0, 100)
        
        parent_edu = np.random.choice(['none', 'primary', 'secondary', 'higher'], 
                                       p=[0.2, 0.3, 0.35, 0.15])
        distance = np.random.exponential(5)
        previous_grade = np.random.choice(['A', 'B', 'C', 'D', 'F'], 
                                          p=[0.15, 0.25, 0.35, 0.15, 0.1])
        
        # Calculate dropout probability (simplified causal model)
        dropout_prob = 0.1
        dropout_prob += (100 - attendance) * 0.005  # Low attendance increases risk
        dropout_prob += distance * 0.02  # Distance increases risk
        if parent_edu == 'none': 
            dropout_prob += 0.2
        if previous_grade in ['D', 'F']: 
            dropout_prob += 0.25
        
        dropout_prob = min(dropout_prob, 0.95)  # Cap at 95%
        dropout = 1 if np.random.random() < dropout_prob else 0
        
        data.append({
            'student_id': f'STU{i:04d}',
            'age': np.random.randint(12, 18),
            'gender': np.random.choice(['male', 'female']),
            'attendance_rate': round(attendance, 2),
            'previous_grade': previous_grade,
            'distance_to_school': round(distance, 2),
            'parent_education': parent_edu,
            'household_income': np.random.choice(['low', 'medium', 'high'], 
                                                  p=[0.4, 0.4, 0.2]),
            'dropout': dropout
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_students(1000)
    df.to_csv('synthetic_students.csv', index=False)
    print(f"✅ Generated {len(df)} students")
    print(f"📊 Dropout rate: {df['dropout'].mean():.2%}")
    print(f"📁 Saved to: synthetic_students.csv")

# %%



