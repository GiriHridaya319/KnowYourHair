import pandas as pd
import numpy as np
from django.utils.text import slugify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..models import Product


class ProductRecommender:
    def __init__(self):
        self.product_data = pd.DataFrame(
            Product.objects.all().values('name', 'cost', 'feedback', 'details', 'image')
        )
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def get_recommendations_risk(self, risk_level):
        # Enhanced keyword lists for each risk level
        risk_keywords = self._get_enhanced_risk_keywords(risk_level)

        # Transform product details into TF-IDF vectors
        product_vectors = self.vectorizer.fit_transform(self.product_data['details'])

        # Transform risk keywords into TF-IDF vectors
        keyword_vector = self.vectorizer.transform(risk_keywords)

        # Calculate similarity between keywords and product details (how close the relation of two vector is)
        similarity_scores = cosine_similarity(keyword_vector, product_vectors)
        avg_scores = similarity_scores.mean(axis=0)

        # Get top N products based on similarity scores
        n = 30
        top_indices = np.argsort(avg_scores)[::-1][:n]  # highest score first 30

        # Randomly select 5 products from the top N
        selected_indices = np.random.choice(top_indices, size=5, replace=False)

        # Prepare recommendations
        recommendations = []
        for idx in selected_indices:
            product = self.product_data.iloc[idx]
            recommendations.append({
                'name': product['name'],
                'slug': slugify(product['name']),
                'cost': product['cost'],
                'feedback': product['feedback'],
                'details': product['details'],
                'image': product['image']
            })

        return recommendations, selected_indices

    def get_hybrid_recommendations(self, selected_product_name):
        """Get hybrid recommendations combining content and collaborative filtering"""
        # Get content-based recommendations
        content_recommendations = self._get_content_recommendations(selected_product_name)

        # Get collaborative recommendations
        collab_recommendations = self._get_collaborative_recommendations(selected_product_name)

        # Combine recommendations
        hybrid_recommendations = self._combine_recommendations(
            content_recommendations,
            collab_recommendations,
            weight_content=0.5
        )

        # Convert DataFrame to records if necessary
        if hasattr(hybrid_recommendations, 'to_dict'):
            hybrid_recommendations = hybrid_recommendations.to_dict('records')

        # Format recommendations with proper image paths
        formatted_recommendations = []
        for rec in hybrid_recommendations:
            formatted_rec = {
                'name': rec['name'].strip(),
                'slug': slugify(rec['name']),
                'image': rec['image'],
                'details': rec['details'],
                'cost': rec['cost'],
                'HybridScore': rec['HybridScore']
            }
            formatted_recommendations.append(formatted_rec)

        return formatted_recommendations

    def _get_content_recommendations(self, product_name, n_recommendations=5):
        """Content-based recommendations"""
        item_features = self.vectorizer.fit_transform(self.product_data['details'])
        item_similarity = cosine_similarity(item_features)  # each product similarity with every other product

        item_similarity_df = pd.DataFrame(
            item_similarity,
            index=self.product_data['name'],
            columns=self.product_data['name']
        )  # to see how similar the products are in dataframe format

        similar_scores = item_similarity_df[product_name].sort_values(ascending=False)  # sort product similarity score
        # with every other product in descending order
        similar_products = similar_scores.index[1:n_recommendations + 1].tolist()  # ignore the first one and top 5

        recommendations = self.product_data[
            self.product_data['name'].isin(similar_products)
        ].copy()  # get all data of the similar products
        recommendations['SimilarityScore'] = recommendations['name'].map(similar_scores)  # add new column for sim score

        return recommendations

    def _get_collaborative_recommendations(self, product_name, n_recommendations=5):
        """Collaborative filtering recommendations"""
        feedback_features = self.vectorizer.fit_transform(
            self.product_data['feedback'].astype(str)
        )

        feedback_similarity = cosine_similarity(feedback_features)
        feedback_similarity_df = pd.DataFrame(
            feedback_similarity,
            index=self.product_data['name'],
            columns=self.product_data['name']
        )

        similar_scores = feedback_similarity_df[product_name].sort_values(ascending=False)
        similar_products = similar_scores.index[1:n_recommendations + 1].tolist()

        recommendations = self.product_data[
            self.product_data['name'].isin(similar_products)
        ].copy()
        recommendations['CollaborativeScore'] = recommendations['name'].map(similar_scores)

        return recommendations

    def _combine_recommendations(self, content_recs, collab_recs, weight_content=0.5):  # equal importance to both
        """Combine content and collaborative recommendations"""
        # Normalize scores because both might have value in different ranges
        content_recs['NormalizedContentScore'] = self._normalize_scores(
            content_recs['SimilarityScore']
        )
        collab_recs['NormalizedCollabScore'] = self._normalize_scores(
            collab_recs['CollaborativeScore']
        )

        # Combine recommendations
        hybrid_recommendations = pd.concat([
            content_recs[['name', 'NormalizedContentScore']],
            collab_recs[['name', 'NormalizedCollabScore']]
        ], axis=0)

        # Calculate hybrid score ( linear combination)
        hybrid_recommendations['HybridScore'] = (
                hybrid_recommendations['NormalizedContentScore'].fillna(0) * weight_content +
                hybrid_recommendations['NormalizedCollabScore'].fillna(0) * (1 - weight_content)
        )

        # Get unique products with highest scores
        hybrid_recommendations = (
            hybrid_recommendations.groupby('name')['HybridScore']
            .max()
            .reset_index()
            .sort_values('HybridScore', ascending=False)
        )

        # Get full product details
        final_recommendations = self.product_data[
            self.product_data['name'].isin(hybrid_recommendations['name'])
        ].copy()

        final_recommendations['HybridScore'] = final_recommendations['name'].map(
            hybrid_recommendations.set_index('name')['HybridScore']
        )

        return final_recommendations.sort_values('HybridScore', ascending=False)

    def _get_enhanced_risk_keywords(self, risk_level):
        """Enhanced keyword lists for each risk level"""
        keywords = {
            'Low Risk': [
                "shine enhancement", "scalp nourishment", "vitamin-rich", "gentle cleansing",
                "moisturizing", "uv protection", "split end repair", "natural oils",
                "hydration", "softening", "frizz control", "shine & gloss", "detangling",
                "smoothness", "manageability", "silky-smooth", "non-sticky formula",
                "humidity control", "lightweight", "heat protection", "color protection",
                "daily care", "split ends prevention", "anti-frizz", "straightening & smoothening",
                "conditioning", "nourishment", "volumizer", "styling", "hair health",
                "shine serum", "scalp care", "hair mask", "leave-in conditioner"
            ],
            'Medium Risk': [
                "thickening", "volume boost", "strengthening", "follicle stimulation", "anti-breakage",
                "scalp revitalization", "keratin repair", "protein treatment", "hair growth support",
                "reducing hair fall", "damage repair", "nourishment", "conditioning", "anti-frizz",
                "scalp health", "hair elasticity", "hair strength", "hair repair", "anti-hair fall",
                "growth stimulating", "hair thickening", "scalp treatment", "hair serum", "split end treatment",
                "hair tonic", "scalp massage", "hair vitality", "hair density"
            ],
            'High Risk': [
                "follicle regeneration", "hair growth", "hair fall prevention", "nourishing repair",
                "damaged hair repair", "restorative", "regrowth", "scalp repair", "hair loss",
                "thinning hair", "hair restoration", "hair rejuvenation", "intensive care",
                "split-ends", "anti-hair fall", "growth stimulating", "hair revival",
                "regenerating serum", "hair reactivation", "hair fall control", "scalp renewal",
                "hair thickening serum", "anti-thinning", "hair growth oil", "scalp therapy",
                "hair fall treatment", "hair regrowth serum", "scalp nourishment", "hair recovery"
            ]
        }
        return keywords.get(risk_level, keywords['Low Risk'])


    def _normalize_scores(self, scores):
        """Normalize scores to 0-1 range"""
        return (scores - scores.min()) / (scores.max() - scores.min())