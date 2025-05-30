"""
Product search module for retrieving and comparing products.
"""

import os
import yaml
from typing import Dict, Any, List, Optional, Tuple
from models.embedding_model import EmbeddingModel
from backend.database import Database

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

class ProductSearch:
    """
    Class for searching and comparing products based on embeddings.
    """
    
    def __init__(self):
        """Initialize product search with embedding model and database."""
        self.embedding_model = EmbeddingModel()
        self.database = Database()
        self.fake_threshold = config["agent"]["fake_threshold"]
        
    def get_product_embedding(self, product_data: Dict[str, Any]) -> List[float]:
        """
        Get embedding vector for a product based on its attributes.
        
        Args:
            product_data (Dict[str, Any]): Product data including title, description, etc.
            
        Returns:
            List[float]: Embedding vector representing the product
        """
        # Combine product attributes into a single text
        title = product_data.get('title', '')
        description = product_data.get('description', '')
        brand = product_data.get('brand', '')
        
        # Create a combined text for embedding
        combined_text = f"Title: {title}. Description: {description}. Brand: {brand}."
        
        # Generate embedding
        embedding = self.embedding_model.get_embeddings(combined_text)
        
        return embedding
        
    def find_similar_products(self, product_data: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find products similar to the given product data.
        
        Args:
            product_data (Dict[str, Any]): Product data to compare
            limit (int): Maximum number of similar products to return
            
        Returns:
            List[Dict[str, Any]]: List of similar products with similarity scores
        """
        # Get embedding for the product
        embedding = self.get_product_embedding(product_data)
        
        # Search for similar products in the database
        similar_products = self.database.find_similar_products(embedding, limit)
        
        return similar_products
        
    def analyze_product_authenticity(self, product_data: Dict[str, Any]) -> Tuple[float, str, List[Dict[str, Any]]]:
        """
        Analyze a product's authenticity based on similar products.
        
        Args:
            product_data (Dict[str, Any]): Product data to analyze
            
        Returns:
            Tuple[float, str, List[Dict[str, Any]]]: 
                - Authentication score (0-1, higher is more likely fake)
                - Reasoning
                - List of similar products used for comparison
        """
        # Get embedding for the product
        embedding = self.get_product_embedding(product_data)
        
        # Find similar products
        similar_products = self.database.find_similar_products(embedding, limit=5)
        
        # If no similar products found, can't make a comparison
        if not similar_products:
            return 0.5, "No similar products found for comparison.", []
            
        # Calculate a weighted score based on price disparities and similarity
        price = product_data.get('price', 0)
        if not price or price <= 0:
            price_analysis = "No price information available for comparison."
            price_factor = 0.5
        else:
            # Calculate average price of similar products
            valid_prices = [p['price'] for p in similar_products if p['price'] is not None and p['price'] > 0]
            
            if not valid_prices:
                price_analysis = "No valid price information available for comparison."
                price_factor = 0.5
            else:
                avg_price = sum(valid_prices) / len(valid_prices)
                
                # Calculate price disparity percentage
                price_disparity = abs(price - avg_price) / avg_price if avg_price > 0 else 1.0
                
                # Extremely low prices are suspicious
                if price < avg_price * 0.5:
                    price_analysis = f"Price (${price:.2f}) is significantly lower than average (${avg_price:.2f}), which is suspicious."
                    price_factor = min(0.8 + price_disparity * 0.2, 1.0)  # Cap at 1.0
                # Extremely high prices are also suspicious but less so
                elif price > avg_price * 2:
                    price_analysis = f"Price (${price:.2f}) is significantly higher than average (${avg_price:.2f}), which could indicate premium version or potential price gouging."
                    price_factor = 0.6
                # Reasonable price range
                else:
                    price_analysis = f"Price (${price:.2f}) is within reasonable range of average (${avg_price:.2f})."
                    price_factor = max(0.3 - price_disparity * 0.3, 0.0)  # Lower is better, min at 0.0
        
        # Check brand consistency
        brand = product_data.get('brand', '').lower()
        if not brand:
            brand_analysis = "No brand information provided for comparison."
            brand_factor = 0.5
        else:
            similar_brands = [p['brand'].lower() for p in similar_products if p['brand']]
            brand_matches = sum(1 for b in similar_brands if b == brand)
            
            if similar_brands:
                brand_ratio = brand_matches / len(similar_brands)
                if brand_ratio >= 0.8:
                    brand_analysis = f"Brand '{brand}' is consistent with similar products."
                    brand_factor = 0.2
                elif brand_ratio >= 0.4:
                    brand_analysis = f"Brand '{brand}' appears in some similar products but not all."
                    brand_factor = 0.4
                else:
                    brand_analysis = f"Brand '{brand}' differs from most similar products, which is suspicious."
                    brand_factor = 0.8
            else:
                brand_analysis = "No brand information available for comparison."
                brand_factor = 0.5
        
        # Calculate overall authenticity score
        authenticity_score = 0.6 * price_factor + 0.4 * brand_factor
        
        # Generate reasoning
        reasoning = f"{price_analysis} {brand_analysis}"
        
        if authenticity_score >= self.fake_threshold:
            reasoning += f" Overall, this product shows significant indicators of being potentially counterfeit with a fake score of {authenticity_score:.2f}."
        else:
            reasoning += f" Overall, this product appears to be authentic with a fake score of {authenticity_score:.2f}."
            
        return authenticity_score, reasoning, similar_products
        
    def store_analyzed_product(self, product_data: Dict[str, Any], score: float, verified: bool = False) -> int:
        """
        Store an analyzed product in the database.
        
        Args:
            product_data (Dict[str, Any]): Product data to store
            score (float): Authentication score
            verified (bool): Whether the product is verified
            
        Returns:
            int: ID of the stored product
        """
        # Get embedding for the product
        embedding = self.get_product_embedding(product_data)
        
        # Add embedding and score to product data
        product_data['embedding'] = embedding
        product_data['score'] = score
        product_data['verified'] = verified
        
        # Store in database
        product_id = self.database.insert_product(product_data)
        
        return product_id
