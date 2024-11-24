# ml_model/quantile_regression.py
import numpy as np
import pandas as pd
from sklearn.linear_model import QuantileRegressor

def predict_aluminum_output(raw_material):
    # Example data (replace with actual historical data for training)
    data = {
        'quantity': [100, 150, 200, 250, 300],  # Raw material quantity
        'quality': [80, 85, 90, 95, 100],      # Raw material quality
        'output': [60, 75, 100, 120, 140]      # Actual output in kg
    }
    df = pd.DataFrame(data)

    # Features (quantity, quality)
    X = df[['quantity', 'quality']]
    
    # Target (aluminum output)
    y = df['output']

    # Train a Quantile Regressor model
    quantile_model = QuantileRegressor(quantile=0.9)  # Predict 90th percentile of output
    quantile_model.fit(X, y)

    # Prediction using the input raw material (quantity, quality)
    X_new = np.array([[raw_material.quantity, raw_material.quality]])
    prediction = quantile_model.predict(X_new)

    return prediction[0]  # Predicted aluminum output in kg
