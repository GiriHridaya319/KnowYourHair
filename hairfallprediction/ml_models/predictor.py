from ..models import HairfallData
import numpy as np
import joblib
import pandas as pd


class HairfallPredictor:
    def __init__(self):
        self.model = joblib.load('hairfallprediction/models/finalhairfall_risk_model_tuned.pkl')
        self.age_model = joblib.load('hairfallprediction/models/finalage_prediction_model_tuned.pkl')

        # Get training data from database for age predictions
        self.training_data = pd.DataFrame(
            HairfallData.objects.all().values()
        )

    def predict_risk(self, user_data):
        feature_order = [
            'Gender', 'Age', 'Hairline Pattern', 'Hair Fall Rate', 'Nutrition',
            'Chemical Product Usage', 'Genetics', 'Past Chronic Illness',
            'Sleep Disturbance', 'Water Quality Issue', 'Stress', 'Food Habit',
            'Hormonal Changes', 'Hair Care Habits', 'Smoking'
        ]
        input_array_from_user = np.array([user_data[feature] for feature in feature_order]).reshape(1, -1)

        prediction = self.model.predict(input_array_from_user)[0]

        risk_mapping = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}
        risk_level = risk_mapping.get(prediction, "Unknown")

        age_prediction = None
        if risk_level in ["Medium Risk", "High Risk"]:
            # Get current user age
            current_age = float(user_data['Age'])

            # Create DataFrame for age prediction
            user_data_df = pd.DataFrame([user_data], columns=feature_order)

            # Prepare input data for age prediction
            age_features = user_data_df.drop('Age', axis=1)
            age_features['Label'] = prediction  # Add predicted risk as a feature

            # Ensure feature order matches training
            if hasattr(self.age_model, 'feature_names_in_'):
                age_features = age_features[self.age_model.feature_names_in_]

            # Predict age
            predicted_age = self.age_model.predict(age_features)[0]

            # Only adjust if prediction is less than current age
            if predicted_age < current_age:
                if risk_level == "High Risk":
                    predicted_age = current_age + 3  # Immediate risk
                else:  # Medium Risk
                    predicted_age = current_age + 6  # Medium-term


            # Format age prediction
            age_prediction = {
                'years': int(predicted_age),
                'months': round((predicted_age - int(predicted_age)) * 12)
            }

            # Adjust months if they equal 12
            if age_prediction['months'] == 12:
                age_prediction['years'] += 1
                age_prediction['months'] = 0

        return {
            'risk_level': risk_level,
            'age_prediction': age_prediction,

        }

    def get_prediction_details(self, risk_level, age_prediction, contributing_factors):
        """Format prediction details for display"""
        details = [f"\nPredicted Hair Fall Risk: {risk_level}"]

        if age_prediction and risk_level in ["Medium Risk", "High Risk"]:
            years = age_prediction['years']
            months = age_prediction['months']
            details.append(f"Estimated Age of Hair Loss Onset: {years} years")
            if months > 0:
                details.append(f"                              and {months} months")

            if contributing_factors:
                details.append("\nTop factors influencing the prediction:")
                for factor, importance in contributing_factors.items():
                    details.append(f"- {factor}: {importance:.3f}")
        else:
            details.append("No significant risk predicted for hair fall. However, it's "
                           "important to care for your hair health to avoid future problems.")

        return "\n".join(details)