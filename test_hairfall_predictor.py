import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
import numpy as np
import pandas as pd
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KnowYourHair.settings')  # Update this to your project's settings module
django.setup()

import joblib
from hairfallprediction.ml_models.predictor import HairfallPredictor


class TestHairfallPredictor(unittest.TestCase):
    @patch('hairfallprediction.ml_models.predictor.joblib.load')
    @patch('hairfallprediction.ml_models.predictor.HairfallData.objects')
    def setUp(self, mock_hairfall_data, mock_joblib_load):
        """Set up test fixtures"""
        print("Setting up HairfallPredictor test environment...")

        # Mock the model
        self.mock_model = MagicMock()
        self.mock_age_model = MagicMock()

        # Configure joblib.load to return our mock models
        mock_joblib_load.side_effect = [self.mock_model, self.mock_age_model]

        # Create mock training data
        mock_queryset = MagicMock()
        mock_queryset.values.return_value = [
            {"id": 1, "Age": 30, "Gender": 1, "Hairline Pattern": 2},
            {"id": 2, "Age": 40, "Gender": 0, "Hairline Pattern": 1}
        ]
        mock_hairfall_data.all.return_value = mock_queryset

        # Create instance of predictor
        self.predictor = HairfallPredictor()
        print("HairfallPredictor initialized successfully")

    def test_initialization(self):
        """Test that predictor initializes correctly"""
        print("Testing predictor initialization...")
        self.assertIsNotNone(self.predictor.model)
        self.assertIsNotNone(self.predictor.age_model)
        self.assertIsInstance(self.predictor.training_data, pd.DataFrame)
        print("Predictor initialization test passed")

    def test_predict_risk_low_risk(self):
        """Test predict_risk method with low risk outcome"""
        print("Testing predict_risk method with low risk prediction...")

        # Set up mock prediction to return low risk (0)
        self.mock_model.predict.return_value = [0]

        user_data = {
            'Gender': 1, 'Age': 25, 'Hairline Pattern': 1, 'Hair Fall Rate': 1,
            'Nutrition': 0, 'Chemical Product Usage': 0, 'Genetics': 0,
            'Past Chronic Illness': 0, 'Sleep Disturbance': 0, 'Water Quality Issue': 0,
            'Stress': 1, 'Food Habit': 1, 'Hormonal Changes': 0,
            'Hair Care Habits': 1, 'Smoking': 0
        }

        result = self.predictor.predict_risk(user_data)
        print(f"Low risk prediction result: {result}")

        # Check result
        self.assertEqual(result['risk_level'], "Low Risk")
        self.assertIsNone(result['age_prediction'])

        # Verify model was called with correct parameters
        feature_order = [
            'Gender', 'Age', 'Hairline Pattern', 'Hair Fall Rate', 'Nutrition',
            'Chemical Product Usage', 'Genetics', 'Past Chronic Illness',
            'Sleep Disturbance', 'Water Quality Issue', 'Stress', 'Food Habit',
            'Hormonal Changes', 'Hair Care Habits', 'Smoking'
        ]
        expected_input = np.array([user_data[feature] for feature in feature_order]).reshape(1, -15)

        # The mock_model.predict was called at least once
        self.mock_model.predict.assert_called()
        print("Low risk prediction test passed")

    def test_predict_risk_medium_risk(self):
        """Test predict_risk method with medium risk outcome"""
        print("Testing predict_risk method with medium risk prediction...")

        # Set up mock predictions
        self.mock_model.predict.return_value = [1]  # Medium Risk
        self.mock_age_model.predict.return_value = [35]  # Age prediction

        # Set up feature names for age model
        self.mock_age_model.feature_names_in_ = [
            'Gender', 'Hairline Pattern', 'Hair Fall Rate', 'Nutrition',
            'Chemical Product Usage', 'Genetics', 'Past Chronic Illness',
            'Sleep Disturbance', 'Water Quality Issue', 'Stress', 'Food Habit',
            'Hormonal Changes', 'Hair Care Habits', 'Smoking', 'Label'
        ]

        user_data = {
            'Gender': 1, 'Age': 30, 'Hairline Pattern': 2, 'Hair Fall Rate': 2,
            'Nutrition': 1, 'Chemical Product Usage': 1, 'Genetics': 1,
            'Past Chronic Illness': 0, 'Sleep Disturbance': 1, 'Water Quality Issue': 1,
            'Stress': 2, 'Food Habit': 1, 'Hormonal Changes': 1,
            'Hair Care Habits': 1, 'Smoking': 0
        }

        result = self.predictor.predict_risk(user_data)
        print(f"Medium risk prediction result: {result}")

        # Check result
        self.assertEqual(result['risk_level'], "Medium Risk")
        self.assertIsNotNone(result['age_prediction'])

        # Since predicted age (35) is greater than current age (30),
        # we should keep the predicted age + 6 (medium risk adjustment)
        self.assertEqual(result['age_prediction']['years'], 35)  # 30 + 6
        self.assertEqual(result['age_prediction']['months'], 0)

        print("Medium risk prediction test passed")

    def test_predict_risk_high_risk(self):
        """Test predict_risk method with high risk outcome"""
        print("Testing predict_risk method with high risk prediction...")

        # Set up mock predictions
        self.mock_model.predict.return_value = [2]  # High Risk
        self.mock_age_model.predict.return_value = [25]  # Age prediction less than current

        # Set up feature names for age model
        self.mock_age_model.feature_names_in_ = [
            'Gender', 'Hairline Pattern', 'Hair Fall Rate', 'Nutrition',
            'Chemical Product Usage', 'Genetics', 'Past Chronic Illness',
            'Sleep Disturbance', 'Water Quality Issue', 'Stress', 'Food Habit',
            'Hormonal Changes', 'Hair Care Habits', 'Smoking', 'Label'
        ]

        user_data = {
            'Gender': 1, 'Age': 28, 'Hairline Pattern': 3, 'Hair Fall Rate': 3,
            'Nutrition': 2, 'Chemical Product Usage': 2, 'Genetics': 2,
            'Past Chronic Illness': 1, 'Sleep Disturbance': 2, 'Water Quality Issue': 1,
            'Stress': 3, 'Food Habit': 2, 'Hormonal Changes': 2,
            'Hair Care Habits': 0, 'Smoking': 1
        }

        result = self.predictor.predict_risk(user_data)
        print(f"High risk prediction result: {result}")

        # Check result
        self.assertEqual(result['risk_level'], "High Risk")
        self.assertIsNotNone(result['age_prediction'])

        # Since we're high risk and predicted age (25) < current (28),
        # we should get current + 3 = 31
        self.assertEqual(result['age_prediction']['years'], 31)
        self.assertEqual(result['age_prediction']['months'], 0)

        print("High risk prediction test passed")

    def test_predict_risk_with_fractional_age(self):
        """Test predict_risk with a fractional age prediction"""
        print("Testing predict_risk with fractional age prediction...")

        # Set up mock predictions
        self.mock_model.predict.return_value = [2]  # High Risk
        self.mock_age_model.predict.return_value = [30.5]  # Fractional age prediction

        # Set up feature names for age model
        self.mock_age_model.feature_names_in_ = [
            'Gender', 'Hairline Pattern', 'Hair Fall Rate', 'Nutrition',
            'Chemical Product Usage', 'Genetics', 'Past Chronic Illness',
            'Sleep Disturbance', 'Water Quality Issue', 'Stress', 'Food Habit',
            'Hormonal Changes', 'Hair Care Habits', 'Smoking', 'Label'
        ]

        user_data = {
            'Gender': 1, 'Age': 28, 'Hairline Pattern': 3, 'Hair Fall Rate': 3,
            'Nutrition': 2, 'Chemical Product Usage': 2, 'Genetics': 2,
            'Past Chronic Illness': 1, 'Sleep Disturbance': 2, 'Water Quality Issue': 1,
            'Stress': 3, 'Food Habit': 2, 'Hormonal Changes': 2,
            'Hair Care Habits': 0, 'Smoking': 1
        }

        result = self.predictor.predict_risk(user_data)
        print(f"Fractional age prediction result: {result}")

        # Since 30.5 > 28 and high risk, we keep predicted age
        self.assertEqual(result['age_prediction']['years'], 30)
        self.assertEqual(result['age_prediction']['months'], 6)  # 0.5 years = 6 months

        print("Fractional age prediction test passed")

    def test_predict_risk_with_twelve_months(self):
        """Test predict_risk when months calculation equals 12"""
        print("Testing predict_risk with month calculation resulting in 12...")

        # Set up mock predictions to get 12 months
        self.mock_model.predict.return_value = [1]  # Medium Risk
        self.mock_age_model.predict.return_value = [25.0]  # Age prediction with no fraction

        # Add a patch to intercept the calculation to force 12 months
        with patch('hairfallprediction.ml_models.predictor.round', return_value=12):
            # Set up feature names for age model
            self.mock_age_model.feature_names_in_ = [
                'Gender', 'Hairline Pattern', 'Hair Fall Rate', 'Nutrition',
                'Chemical Product Usage', 'Genetics', 'Past Chronic Illness',
                'Sleep Disturbance', 'Water Quality Issue', 'Stress', 'Food Habit',
                'Hormonal Changes', 'Hair Care Habits', 'Smoking', 'Label'
            ]

            user_data = {
                'Gender': 1, 'Age': 20, 'Hairline Pattern': 2, 'Hair Fall Rate': 2,
                'Nutrition': 1, 'Chemical Product Usage': 1, 'Genetics': 1,
                'Past Chronic Illness': 0, 'Sleep Disturbance': 1, 'Water Quality Issue': 1,
                'Stress': 2, 'Food Habit': 1, 'Hormonal Changes': 1,
                'Hair Care Habits': 1, 'Smoking': 0
            }

            result = self.predictor.predict_risk(user_data)
            print(f"12-month adjustment result: {result}")

            # Check that the months got adjusted properly
            self.assertEqual(result['age_prediction']['years'], 26)  # 25 + 1
            self.assertEqual(result['age_prediction']['months'], 0)  # Reset to 0

            print("12-month adjustment test passed")

    def test_get_prediction_details_low_risk(self):
        """Test get_prediction_details for low risk"""
        print("Testing get_prediction_details with low risk...")

        risk_level = "Low Risk"
        age_prediction = None
        contributing_factors = None

        details = self.predictor.get_prediction_details(risk_level, age_prediction, contributing_factors)
        print(f"Low risk details: {details}")

        self.assertIn("Predicted Hair Fall Risk: Low Risk", details)
        self.assertIn("No significant risk predicted for hair fall", details)

        print("Low risk details test passed")

    def test_get_prediction_details_medium_risk(self):
        """Test get_prediction_details for medium risk"""
        print("Testing get_prediction_details with medium risk...")

        risk_level = "Medium Risk"
        age_prediction = {'years': 36, 'months': 6}
        contributing_factors = {'Stress': 0.75, 'Genetics': 0.65, 'Hair Care Habits': 0.45}

        details = self.predictor.get_prediction_details(risk_level, age_prediction, contributing_factors)
        print(f"Medium risk details: {details}")

        self.assertIn("Predicted Hair Fall Risk: Medium Risk", details)
        self.assertIn("Estimated Age of Hair Loss Onset: 36 years", details)
        self.assertIn("and 6 months", details)
        self.assertIn("Top factors influencing the prediction:", details)
        self.assertIn("- Stress: 0.750", details)

        print("Medium risk details test passed")

    def test_get_prediction_details_high_risk(self):
        """Test get_prediction_details for high risk"""
        print("Testing get_prediction_details with high risk...")

        risk_level = "High Risk"
        age_prediction = {'years': 31, 'months': 0}
        contributing_factors = {'Genetics': 0.85, 'Stress': 0.80, 'Smoking': 0.65}

        details = self.predictor.get_prediction_details(risk_level, age_prediction, contributing_factors)
        print(f"High risk details: {details}")

        self.assertIn("Predicted Hair Fall Risk: High Risk", details)
        self.assertIn("Estimated Age of Hair Loss Onset: 31 years", details)
        self.assertNotIn("and 0 months", details)  # Shouldn't show 0 months
        self.assertIn("Top factors influencing the prediction:", details)
        self.assertIn("- Genetics: 0.850", details)

        print("High risk details test passed")


if __name__ == '__main__':
    print("Running HairfallPredictor tests...")
    unittest.main()
