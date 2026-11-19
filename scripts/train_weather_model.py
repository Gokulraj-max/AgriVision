import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib
from agrivision.config import WEIGHTS_DIR
from agrivision.models.weather_risk_model import WeatherDiseaseRiskModel

def train_weather_model():
    print("Training Weather-Based Disease Risk Random Forest Model...")
    builder = WeatherDiseaseRiskModel()
    X, y = builder._generate_synthetic_training_data(n_samples=5000)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf = RandomForestClassifier(n_estimators=150, max_depth=7, random_state=42)
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    y_prob = rf.predict_proba(X_test)

    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=["Low Risk", "Moderate Risk", "High Risk"]))

    roc_auc = roc_auc_score(y_test, y_prob, multi_class="ovr")
    print(f"Multi-Class ROC-AUC Score: {roc_auc:.4f}")

    save_path = WEIGHTS_DIR / "weather_risk_rf.pkl"
    joblib.dump(rf, save_path)
    print(f"Saved weather model to {save_path}")

if __name__ == "__main__":
    train_weather_model()
