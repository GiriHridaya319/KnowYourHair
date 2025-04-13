import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KnowYourHair.settings')  # Update this to your project's settings module
django.setup()

from hairfallprediction.ml_models.recommender import ProductRecommender


class TestProductRecommender(unittest.TestCase):
    @patch('hairfallprediction.ml_models.recommender.Product.objects')
    def setUp(self, mock_product_objects):
        """Set up test fixtures"""
        print("Setting up ProductRecommender test environment...")

        # Create mock product data
        mock_queryset = MagicMock()
        self.mock_products = [
            {
                'name': 'Hair Growth Serum',
                'cost': 1200,
                'feedback': 'Great for hair growth and reducing hair fall',
                'details': 'Contains follicle regeneration formula and natural oils for hair growth',
                'image': 'products/serum.jpg'
            },
            {
                'name': 'Volumizing Shampoo',
                'cost': 800,
                'feedback': 'Adds volume to thin hair',
                'details': 'Thickening formula with volume boost and strengthening agents',
                'image': 'products/shampoo.jpg'
            },
            {
                'name': 'Moisturizing Conditioner',
                'cost': 700,
                'feedback': 'Left my hair smooth and silky',
                'details': 'Hydration formula with natural oils for shine enhancement and frizz control',
                'image': 'products/conditioner.jpg'
            },
            {
                'name': 'Scalp Treatment',
                'cost': 1500,
                'feedback': 'Reduced hair fall significantly',
                'details': 'Scalp revitalization with hair fall prevention and follicle stimulation',
                'image': 'products/treatment.jpg'
            },
            {
                'name': 'Hair Repair Mask',
                'cost': 1000,
                'feedback': 'Restored my damaged hair',
                'details': 'Damaged hair repair with nourishing ingredients for restorative effects',
                'image': 'products/mask.jpg'
            }
        ]
        mock_queryset.values.return_value = self.mock_products
        mock_product_objects.all.return_value = mock_queryset

        # Create instance of recommender
        self.recommender = ProductRecommender()
        print("ProductRecommender initialized successfully")

    def test_initialization(self):
        """Test that recommender initializes correctly"""
        print("Testing recommender initialization...")
        self.assertIsInstance(self.recommender.product_data, pd.DataFrame)
        self.assertEqual(len(self.recommender.product_data), 5)
        self.assertIsNotNone(self.recommender.vectorizer)
        print("Recommender initialization test passed")

    @patch('hairfallprediction.ml_models.recommender.np.random.choice')
    def test_get_recommendations_risk_low(self, mock_random_choice):
        """Test get_recommendations_risk method with low risk"""
        print("Testing get_recommendations_risk with low risk...")

        # Mock the random choice to return predictable indices
        mock_random_choice.return_value = np.array([2, 0, 1])

        recommendations, indices = self.recommender.get_recommendations_risk("Low Risk")
        print(f"Low risk recommendations: {recommendations}")
        print(f"Selected indices: {indices}")

        # Check we got recommendations
        self.assertEqual(len(recommendations), 3)

        # Check that recommendations contain expected fields
        for rec in recommendations:
            self.assertIn('name', rec)
            self.assertIn('slug', rec)
            self.assertIn('cost', rec)
            self.assertIn('feedback', rec)
            self.assertIn('details', rec)
            self.assertIn('image', rec)

        # Verify we got products that match low risk keywords
        low_risk_keywords = ["shine", "moisturizing", "hydration", "smoothness"]
        found_match = False
        for rec in recommendations:
            for keyword in low_risk_keywords:
                if keyword.lower() in rec['details'].lower():
                    found_match = True
                    break
        self.assertTrue(found_match, "No product matched low risk keywords")

        print("Low risk recommendations test passed")

    @patch('hairfallprediction.ml_models.recommender.np.random.choice')
    def test_get_recommendations_risk_medium(self, mock_random_choice):
        """Test get_recommendations_risk method with medium risk"""
        print("Testing get_recommendations_risk with medium risk...")

        # Mock the random choice to return predictable indices
        mock_random_choice.return_value = np.array([1, 3])

        recommendations, indices = self.recommender.get_recommendations_risk("Medium Risk")
        print(f"Medium risk recommendations: {recommendations}")
        print(f"Selected indices: {indices}")

        # Check we got recommendations
        self.assertEqual(len(recommendations), 2)

        # Verify we got products that match medium risk keywords
        medium_risk_keywords = ["thickening", "volume", "strengthening", "revitalization"]
        found_match = False
        for rec in recommendations:
            for keyword in medium_risk_keywords:
                if keyword.lower() in rec['details'].lower():
                    found_match = True
                    break
        self.assertTrue(found_match, "No product matched medium risk keywords")

        print("Medium risk recommendations test passed")

    @patch('hairfallprediction.ml_models.recommender.np.random.choice')
    def test_get_recommendations_risk_high(self, mock_random_choice):
        """Test get_recommendations_risk method with high risk"""
        print("Testing get_recommendations_risk with high risk...")

        # Mock the random choice to return predictable indices
        mock_random_choice.return_value = np.array([0, 4])

        recommendations, indices = self.recommender.get_recommendations_risk("High Risk")
        print(f"High risk recommendations: {recommendations}")
        print(f"Selected indices: {indices}")

        # Check we got recommendations
        self.assertEqual(len(recommendations), 2)

        # Verify we got products that match high risk keywords
        high_risk_keywords = ["regeneration", "growth", "hair fall", "repair", "restorative"]
        found_match = False
        for rec in recommendations:
            for keyword in high_risk_keywords:
                if keyword.lower() in rec['details'].lower():
                    found_match = True
                    break
        self.assertTrue(found_match, "No product matched high risk keywords")

        print("High risk recommendations test passed")

    @patch('hairfallprediction.ml_models.recommender.np.random.choice')
    def test_get_recommendations_risk_unknown(self, mock_random_choice):
        """Test get_recommendations_risk method with unknown risk level"""
        print("Testing get_recommendations_risk with unknown risk level...")

        # Mock the random choice to return predictable indices
        mock_random_choice.return_value = np.array([2, 0])

        recommendations, indices = self.recommender.get_recommendations_risk("Unknown Risk")
        print(f"Unknown risk recommendations: {recommendations}")

        # Should default to Low Risk
        self.assertEqual(len(recommendations), 2)

        print("Unknown risk recommendations test passed")

    def test_get_content_recommendations(self):
        """Test _get_content_recommendations method"""
        print("Testing _get_content_recommendations method...")

        product_name = 'Hair Growth Serum'
        recommendations = self.recommender._get_content_recommendations(product_name, n_recommendations=2)
        print(f"Content recommendations: {recommendations}")

        # Check we got recommendations
        self.assertEqual(len(recommendations), 2)

        # Check similarity score column was added
        self.assertIn('SimilarityScore', recommendations.columns)

        # Check we didn't get the original product
        self.assertFalse((recommendations['name'] == product_name).any())

        print("Content recommendations test passed")

    def test_get_collaborative_recommendations(self):
        """Test _get_collaborative_recommendations method"""
        print("Testing _get_collaborative_recommendations method...")

        product_name = 'Scalp Treatment'
        recommendations = self.recommender._get_collaborative_recommendations(product_name, n_recommendations=2)
        print(f"Collaborative recommendations: {recommendations}")

        # Check we got recommendations
        self.assertEqual(len(recommendations), 2)

        # Check collaborative score column was added
        self.assertIn('CollaborativeScore', recommendations.columns)

        # Check we didn't get the original product
        self.assertFalse((recommendations['name'] == product_name).any())

        print("Collaborative recommendations test passed")

    def test_normalize_scores(self):
        """Test _normalize_scores method"""
        print("Testing _normalize_scores method...")

        scores = pd.Series([0.2, 0.5, 0.8, 1.0])
        normalized = self.recommender._normalize_scores(scores)
        print(f"Original scores: {scores}")
        print(f"Normalized scores: {normalized}")

        # Check normalized range
        self.assertAlmostEqual(normalized.min(), 0.0)
        self.assertAlmostEqual(normalized.max(), 1.0)

        # Check relative order preserved
        self.assertTrue(normalized.iloc[0] < normalized.iloc[1])
        self.assertTrue(normalized.iloc[1] < normalized.iloc[2])
        self.assertTrue(normalized.iloc[2] < normalized.iloc[3])

        print("Normalize scores test passed")

    def test_combine_recommendations(self):
        """Test _combine_recommendations method"""
        print("Testing _combine_recommendations method...")

        # Create test data
        content_recs = pd.DataFrame({
            'name': ['Product A', 'Product B'],
            'SimilarityScore': [0.8, 0.6],
            'cost': [1000, 1200],
            'details': ['Details A', 'Details B'],
            'image': ['image_a.jpg', 'image_b.jpg'],
            'feedback': ['Good', 'Great']
        })

        collab_recs = pd.DataFrame({
            'name': ['Product C', 'Product A'],
            'CollaborativeScore': [0.9, 0.7],
            'cost': [800, 1000],
            'details': ['Details C', 'Details A'],
            'image': ['image_c.jpg', 'image_a.jpg'],
            'feedback': ['Excellent', 'Good']
        })

        # Set product data for reference
        self.recommender.product_data = pd.DataFrame({
            'name': ['Product A', 'Product B', 'Product C'],
            'cost': [1000, 1200, 800],
            'details': ['Details A', 'Details B', 'Details C'],
            'image': ['image_a.jpg', 'image_b.jpg', 'image_c.jpg'],
            'feedback': ['Good', 'Great', 'Excellent']
        })

        # Test with equal weights
        combined = self.recommender._combine_recommendations(content_recs, collab_recs, weight_content=0.5)
        print(f"Combined recommendations: {combined}")

        # Check we got all unique products
        self.assertEqual(len(combined), 3)

        # Check hybrid score column was added
        self.assertIn('HybridScore', combined.columns)

        # Check Product A appears (it was in both)
        self.assertTrue((combined['name'] == 'Product A').any())

        # Check proper sorting by hybrid score (higher first)
        self.assertTrue(combined.iloc[0]['HybridScore'] >= combined.iloc[1]['HybridScore'])

        print("Combine recommendations test passed")

    def test_get_hybrid_recommendations(self):
        """Test get_hybrid_recommendations method"""
        print("Testing get_hybrid_recommendations method...")

        # Mock the content and collaborative methods
        with patch.object(self.recommender, '_get_content_recommendations') as mock_content, \
                patch.object(self.recommender, '_get_collaborative_recommendations') as mock_collab:
            # Set up return values
            mock_content.return_value = pd.DataFrame({
                'name': ['Product A', 'Product B'],
                'SimilarityScore': [0.8, 0.6],
                'cost': [1000, 1200],
                'details': ['Details A', 'Details B'],
                'image': ['image_a.jpg', 'image_b.jpg'],
                'feedback': ['Good', 'Great']
            })

            mock_collab.return_value = pd.DataFrame({
                'name': ['Product C', 'Product A'],
                'CollaborativeScore': [0.9, 0.7],
                'cost': [800, 1000],
                'details': ['Details C', 'Details A'],
                'image': ['image_c.jpg', 'image_a.jpg'],
                'feedback': ['Excellent', 'Good']
            })

            # Set product data for reference
            self.recommender.product_data = pd.DataFrame({
                'name': ['Product A', 'Product B', 'Product C'],
                'cost': [1000, 1200, 800],
                'details': ['Details A', 'Details B', 'Details C'],
                'image': ['image_a.jpg', 'image_b.jpg', 'image_c.jpg'],
                'feedback': ['Good', 'Great', 'Excellent']
            })

            # Test the hybrid recommendations
            hybrid_recs = self.recommender.get_hybrid_recommendations('Product D')
            print(f"Hybrid recommendations: {hybrid_recs}")

            # Check results
            self.assertEqual(len(hybrid_recs), 3)

            # Check for expected fields
            for rec in hybrid_recs:
                self.assertIn('name', rec)
                self.assertIn('slug', rec)
                self.assertIn('image', rec)
                self.assertIn('details', rec)
                self.assertIn('cost', rec)
                self.assertIn('HybridScore', rec)

            # Verify methods were called with right parameters
            mock_content.assert_called_once_with('Product D')
            mock_collab.assert_called_once_with('Product D')

            print("Hybrid recommendations test passed")

    def test_get_enhanced_risk_keywords(self):
        """Test _get_enhanced_risk_keywords method"""
        print("Testing _get_enhanced_risk_keywords method...")

        # Test each risk level
        low_keywords = self.recommender._get_enhanced_risk_keywords("Low Risk")
        print(f"Low risk keywords count: {len(low_keywords)}")

        medium_keywords = self.recommender._get_enhanced_risk_keywords("Medium Risk")
        print(f"Medium risk keywords count: {len(medium_keywords)}")

        high_keywords = self.recommender._get_enhanced_risk_keywords("High Risk")
        print(f"High risk keywords count: {len(high_keywords)}")

        unknown_keywords = self.recommender._get_enhanced_risk_keywords("Unknown Risk")
        print(f"Unknown risk keywords count: {len(unknown_keywords)}")

        # Check we got keywords for each risk level
        self.assertTrue(len(low_keywords) > 0)
        self.assertTrue(len(medium_keywords) > 0)
        self.assertTrue(len(high_keywords) > 0)

        # Unknown should default to Low Risk
        self.assertEqual(unknown_keywords, low_keywords)

        # Check for expected keywords in each category
        self.assertIn("shine enhancement", low_keywords)
        self.assertIn("thickening", medium_keywords)
        self.assertIn("hair growth", high_keywords)

        print("Risk keywords test passed")


if __name__ == '__main__':
    print("Running ProductRecommender tests...")
    unittest.main()