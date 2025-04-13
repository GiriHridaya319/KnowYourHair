import unittest
from unittest.mock import patch, MagicMock

from hairfallprediction.ml_models.predictor import HairfallPredictor
from hairfallprediction.ml_models.recommender import ProductRecommender


class TestHairfallPredictor(unittest.TestCase):
    def setUp(self):
        # Mock the joblib.load to avoid loading actual models
        with patch('joblib.load') as mock_load:
            # Create mock models
            mock_risk_model = MagicMock()
            mock_age_model = MagicMock()

            mock_load.side_effect = [mock_risk_model, mock_age_model]

            # Initialize the predictor
            self.predictor = HairfallPredictor()

        # Prepare common test data
        self.sample_user_data = {
            'Gender': 1,  # Assuming 1 for male, 0 for female
            'Age': 30,
            'Hairline Pattern': 1,
            'Hair Fall Rate': 2,
            'Nutrition': 1,
            'Chemical Product Usage': 2,
            'Genetics': 1,
            'Past Chronic Illness': 0,
            'Sleep Disturbance': 1,
            'Water Quality Issue': 0,
            'Stress': 2,
            'Food Habit': 1,
            'Hormonal Changes': 0,
            'Hair Care Habits': 1,
            'Smoking': 0
        }

    def test_predict_risk_low_risk(self):
        # Mock model to return low risk
        self.predictor.model.predict.return_value = [0]

        result = self.predictor.predict_risk(self.sample_user_data)

        self.assertEqual(result['risk_level'], "Low Risk")
        self.assertIsNone(result['age_prediction'])

    def test_predict_risk_medium_risk(self):
        # Mock model to return medium risk
        self.predictor.model.predict.return_value = [1]
        # self.predictor.age_model.predict.return_value = [35]

        result = self.predictor.predict_risk(self.sample_user_data)

        self.assertEqual(result['risk_level'], "Medium Risk")
        # self.assertIsNotNone(result['age_prediction'])

    def test_predict_risk_high_risk(self):
        # Mock model to return high risk
        self.predictor.model.predict.return_value = [2]
        result = self.predictor.predict_risk(self.sample_user_data)

        self.assertEqual(result['risk_level'], "High Risk")
        # self.assertIsNotNone(result['age_prediction'])
        # self.assertEqual(result['age_prediction']['years'], 33)

    def test_get_prediction_details_low_risk(self):
        details = self.predictor.get_prediction_details(
            risk_level="Low Risk",
            age_prediction=None,
            contributing_factors=None
        )

        self.assertIn("No significant risk predicted", details)


class TestProductRecommender(unittest.TestCase):
    def setUp(self):
        # Mock Product data for testing
        self.mock_products = [
            {
                'name': 'Moisturizing Shampoo',
                'cost': 15.99,
                'feedback': 'Great for dry hair',
                'details': 'Hydrating shampoo with natural oils',
                'image': 'moisturizing-shampoo.jpg'
            },
            {
                'name': 'Hair Growth Serum',
                'cost': 29.99,
                'feedback': 'Helps with hair growth',
                'details': 'Advanced serum for hair follicle stimulation',
                'image': 'growth-serum.jpg'
            },
            {
                'name': 'Scalp Treatment Oil',
                'cost': 24.50,
                'feedback': 'Reduces hair fall',
                'details': 'Intensive scalp care and hair fall prevention',
                'image': 'scalp-oil.jpg'
            }
        ]

        # Patch the Product.objects.all() method
        with patch('hairfallprediction.models.Product.objects.all') as mock_objects:
            mock_queryset = MagicMock()
            mock_queryset.values.return_value = self.mock_products
            mock_objects.return_value = mock_queryset

        # Initialize the recommender
        self.recommender = ProductRecommender()

    def test_get_recommendations_risk_low_risk(self):
        # Test low risk recommendations
        recommendations, indices = self.recommender.get_recommendations_risk('Low Risk')

        self.assertEqual(len(recommendations), 5)
        for rec in recommendations:
            self.assertIn('name', rec)
            self.assertIn('slug', rec)
            self.assertIn('cost', rec)
            self.assertIn('details', rec)

    def test_get_recommendations_risk_medium_risk(self):
        # Test medium risk recommendations
        recommendations, indices = self.recommender.get_recommendations_risk('Medium Risk')

        self.assertEqual(len(recommendations), 5)
        for rec in recommendations:
            self.assertTrue(all(key in rec for key in
                                ['name', 'slug', 'cost', 'details', 'image', 'feedback']))

    def test_enhanced_risk_keywords(self):
        # Test keyword generation for different risk levels
        low_risk_keywords = self.recommender._get_enhanced_risk_keywords('Low Risk')
        medium_risk_keywords = self.recommender._get_enhanced_risk_keywords('Medium Risk')
        high_risk_keywords = self.recommender._get_enhanced_risk_keywords('High Risk')

        self.assertTrue(len(low_risk_keywords) > 0)
        self.assertTrue(len(medium_risk_keywords) > 0)
        self.assertTrue(len(high_risk_keywords) > 0)

        # Ensure each list returns keywords
        self.assertGreater(len(low_risk_keywords), 10)
        self.assertGreater(len(medium_risk_keywords), 10)
        self.assertGreater(len(high_risk_keywords), 10)

    def test_invalid_risk_level(self):
        # Test with an invalid risk level (should default to Low Risk)
        recommendations, indices = self.recommender.get_recommendations_risk('Invalid Risk')

        self.assertEqual(len(recommendations), 5)
        for rec in recommendations:
            self.assertTrue(all(key in rec for key in
                                ['name', 'slug', 'cost', 'details', 'image', 'feedback']))


if __name__ == '__main__':
    unittest.main()