import joblib
import numpy as np
import os

class DiabetesPredictor:
    def __init__(self, model_path="logistic_model.pkl", scaler_path="scaler.pkl"):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self.load_models()
    
    def load_models(self):
        """Load the trained model and scaler"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
            else:
                raise FileNotFoundError("Model or scaler files not found")
        except Exception as e:
            print(f"Error loading models: {e}")
            raise
    
    def predict(self, features):
        """Make a prediction based on input features"""
        if self.model is None or self.scaler is None:
            raise ValueError("Models not loaded properly")
        
        # Ensure features is a 2D array
        if len(features) == 8:  # Single prediction
            features = [features]
        
        # Scale input
        scaled_data = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(scaled_data)[0]
        probability = self.model.predict_proba(scaled_data)[0][1]
        
        return prediction, probability
    
    def get_feature_names(self):
        """Return the expected feature names in order"""
        return ['HighBP', 'GenHlth', 'BMI', 'Age', 'HighChol', 'CholCheck', 'Income', 'PhysHlth']