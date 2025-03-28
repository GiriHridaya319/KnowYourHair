import unittest

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Modify imports to match your project structure
from hairfallprediction.ml_models.predictor import HairfallPredictor
from hairfallprediction.ml_models.recommender import ProductRecommender
from hairfallprediction.models import Product  # Assuming this exists


class IntegrationTestHairfallSystem(unittest.TestCase):
    def setUp(self):
        # Create predictor and recommender instances
        self.predictor = HairfallPredictor()
        self.recommender = ProductRecommender()

        # Prepare a comprehensive user dataset
        self.comprehensive_user_data = {
            'Gender': 1,  # Male
            'Age': 35,
            'Hairline Pattern': 2,  # More advanced pattern
            'Hair Fall Rate': 3,  # High hair fall
            'Nutrition': 0,  # Poor nutrition
            'Chemical Product Usage': 3,  # High chemical usage
            'Genetics': 2,  # Strong genetic predisposition
            'Past Chronic Illness': 1,  # Some chronic illness history
            'Sleep Disturbance': 2,  # Significant sleep issues
            'Water Quality Issue': 1,  # Some water quality concerns
            'Stress': 3,  # High stress
            'Food Habit': 0,  # Poor food habits
            'Hormonal Changes': 1,  # Some hormonal changes
            'Hair Care Habits': 0,  # Poor hair care
            'Smoking': 1  # Smoker
        }

    def test_predict_and_recommend_workflow(self):
        """
        Integration test to verify the complete workflow:
        1. Predict hair fall risk
        2. Get product recommendations based on risk
        3. Validate recommendation relevance
        """
        # Step 1: Predict risk
        risk_prediction = self.predictor.predict_risk(self.comprehensive_user_data)

        # Verify risk prediction
        self.assertIn(risk_prediction['risk_level'],
                      ["Low Risk", "Medium Risk", "High Risk", "Unknown"])

        # Step 2: Get product recommendations
        recommendations, indices = self.recommender.get_recommendations_risk(
            risk_prediction['risk_level']
        )

        # Step 3: Validate recommendations
        self.assertEqual(len(recommendations), 5)

        # Check each recommendation has required fields
        for rec in recommendations:
            self.assertTrue(all(key in rec for key in
                                ['name', 'slug', 'cost', 'details', 'image', 'feedback']))

            # Additional checks based on risk level
            if risk_prediction['risk_level'] == "High Risk":
                # For high risk, ensure more specialized recommendations
                self.assertIn("growth", rec['details'].lower())

    def test_risk_prediction_detailed_analysis(self):
        """
        Comprehensive integration test that checks:
        1. Risk prediction accuracy
        2. Age prediction relevance
        3. Prediction details generation
        """
        # Predict risk
        risk_prediction = self.predictor.predict_risk(self.comprehensive_user_data)

        # Verify core prediction components
        self.assertIn(risk_prediction['risk_level'],
                      ["Low Risk", "Medium Risk", "High Risk"])

        # Get prediction details
        prediction_details = self.predictor.get_prediction_details(
            risk_level=risk_prediction['risk_level'],
            age_prediction=risk_prediction.get('age_prediction'),
            contributing_factors=None  # You might want to add logic to track contributing factors
        )

        # Verify prediction details
        self.assertIsNotNone(prediction_details)
        self.assertTrue(len(prediction_details) > 0)

        # Additional checks for age prediction
        if risk_prediction.get('age_prediction'):
            self.assertIn('years', risk_prediction['age_prediction'])
            self.assertGreater(risk_prediction['age_prediction']['years'],
                               self.comprehensive_user_data['Age'])

    def test_multiple_risk_level_recommendations(self):
        """
        Test product recommendations across different risk levels
        """
        risk_levels = ["Low Risk", "Medium Risk", "High Risk", "Unknown"]

        for risk_level in risk_levels:
            # Get recommendations
            recommendations, indices = self.recommender.get_recommendations_risk(risk_level)

            # Verify common recommendation requirements
            self.assertEqual(len(recommendations), 5)

            for rec in recommendations:
                self.assertTrue(all(key in rec for key in
                                    ['name', 'slug', 'cost', 'details', 'image', 'feedback']))

                # Verify cost is reasonable
                self.assertGreater(rec['cost'], 0)

                # Verify recommendation relevance
                recommended_keywords = self.recommender._get_enhanced_risk_keywords(risk_level)
                self.assertTrue(
                    any(keyword.lower() in rec['details'].lower()
                        for keyword in recommended_keywords)
                )


if __name__ == '__main__':
    unittest.main()