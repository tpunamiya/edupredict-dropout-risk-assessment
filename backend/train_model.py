# %%
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# %%
df = pd.read_csv('../data/synthetic_students.csv')
df.head()

# %%
# Encode categorical variables
print("🔄 Encoding categorical features...")
le_gender = LabelEncoder()
le_grade = LabelEncoder()
le_parent = LabelEncoder()
le_income = LabelEncoder()

df['gender_encoded'] = le_gender.fit_transform(df['gender'])
df['grade_encoded'] = le_grade.fit_transform(df['previous_grade'])
df['parent_edu_encoded'] = le_parent.fit_transform(df['parent_education'])
df['income_encoded'] = le_income.fit_transform(df['household_income'])

# Features and target
features = ['age', 'attendance_rate', 'distance_to_school', 
            'gender_encoded', 'grade_encoded', 'parent_edu_encoded', 'income_encoded']
X = df[features]
y = df['dropout']

print(f"📊 Dataset: {len(df)} students, {y.sum()} dropouts ({y.mean():.1%})")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train model
print("🔄 Training Random Forest model...")
model = RandomForestClassifier(
    n_estimators=200, 
    max_depth=15,
    min_samples_split=10,
    random_state=42,
    class_weight='balanced'  # Handle class imbalance
)
model.fit(X_train, y_train) 

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("\n" + "="*50)
print("📈 MODEL PERFORMANCE")
print("="*50)
print(f"✅ Accuracy: {accuracy:.3f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['No Dropout', 'Dropout']))

# Feature importance
print("\n" + "="*50)
print("🔍 TOP RISK FACTORS (Feature Importance)")
print("="*50)
feature_importance = sorted(
    zip(features, model.feature_importances_), 
    key=lambda x: x[1], 
    reverse=True
)
for feat, importance in feature_importance:
    print(f"  {feat:25s}: {importance:.3f}")

# Save model and encoders
print("\n🔄 Saving models...")
joblib.dump(model, 'dropout_model.pkl')
joblib.dump(le_gender, 'encoder_gender.pkl')
joblib.dump(le_grade, 'encoder_grade.pkl')
joblib.dump(le_parent, 'encoder_parent.pkl')
joblib.dump(le_income, 'encoder_income.pkl')
joblib.dump(features, 'feature_names.pkl')

print("\n✅ All models saved successfully!")
print("📁 Files created:")
print("  - dropout_model.pkl")
print("  - encoder_*.pkl")
print("  - feature_names.pkl")

# %%



