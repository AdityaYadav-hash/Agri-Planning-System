"""Train a Random Forest crop recommendation model."""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "crop_data.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "crop_model.pkl")

def train():
    df = pd.read_csv(DATA_PATH)
    X = df[["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Test accuracy: {acc:.2f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()
