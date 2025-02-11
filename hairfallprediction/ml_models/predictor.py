from ..models import HairfallData
import numpy as np
import joblib
import pandas as pd


class HairfallPredictor:
    def __init__(self):
        self.model = joblib.load('hairfallprediction/models/hairfall_model.pkl')
        self.scaler = joblib.load('hairfallprediction/models/scaler.pkl')

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
            input_array_from_user = np.array([user_data[feature] for feature in feature_order])
            if self.scaler:
                input_array = self.scaler.transform(input_array_from_user)

            prediction = self.model.predict(input_array_from_user)[0]

            risk_mapping = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}
            risk_level = risk_mapping.get(prediction, "Unknown")

            age_prediction = None
            if risk_level in ["Medium Risk", "High Risk"]:
                base_age = float(user_data['Age'])
                adjusted_age = self._adjust_age_prediction(user_data, base_age)

                if risk_level == "Medium Risk":
                    adjusted_age += 5

                age_prediction = {
                    'years': int(adjusted_age),
                    'months': round((adjusted_age - int(adjusted_age)) * 12)
                }

            return {
                'risk_level': risk_level,
                'age_prediction': age_prediction
            }

    def _adjust_age_prediction(self, user_data, base_age):
            weight_factors = {
                "Chemical Product Usage": 1.4,
                "Genetics": 1.3,
                "Past Chronic Illness": 1.1,
                "Sleep Disturbance": 1.2,
                "Water Quality Issue": 1.1,
                "Stress": 1.2,
                "Food Habit": 1.3
            }
            adjust_age = base_age
            for factor, value in weight_factors.items():
                adjust_age += user_data[factor] * value
            return adjust_age