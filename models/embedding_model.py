"""
Embedding model for converting text to vector representations.
Uses basic embedding approach for text representation.
"""

import os
import yaml
from typing import List
import numpy as np
import hashlib

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

class EmbeddingModel:
    """
    Class for generating embeddings from text using a simple hashing approach.
    """
    
    def __init__(self):
        """Initialize the embedding model using configuration settings."""
        self.dimension = config["embeddings"]["dimension"]
        
    def get_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for a given text using a simple hashing approach.
        
        Args:
            text (str): The text to embed
            
        Returns:
            List[float]: The embedding vector
        """
        if not text or not isinstance(text, str):
            return [0.0] * self.dimension  # Return zero vector for empty text
            
        # Generate a simple embedding using hash function
        # This is not suitable for production but works for demonstration
        embedding = self._hash_to_embedding(text, self.dimension)
        return embedding
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts (List[str]): List of texts to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not texts:
            return []
            
        # Filter out invalid texts
        valid_texts = [text for text in texts if isinstance(text, str) and text]
        
        if not valid_texts:
            return [[0.0] * self.dimension] * len(texts)
            
        # Generate embeddings for each text
        embeddings = [self.get_embeddings(text) for text in valid_texts]
        
        # If the original texts list had invalid entries, align the results
        if len(valid_texts) != len(texts):
            result = []
            valid_idx = 0
            for text in texts:
                if isinstance(text, str) and text:
                    result.append(embeddings[valid_idx])
                    valid_idx += 1
                else:
                    result.append([0.0] * self.dimension)
            return result
            
        return embeddings
        
    def _hash_to_embedding(self, text: str, dimension: int) -> List[float]:
        """
        Convert text to a fixed-dimension embedding using a hash function.
        
        Args:
            text (str): The text to embed
            dimension (int): The desired embedding dimension
            
        Returns:
            List[float]: The embedding vector
        """
        # Create a deterministic seed from the text
        hash_obj = hashlib.sha256(text.encode())
        seed = int(hash_obj.hexdigest(), 16) % (2**32)
        
        # Use numpy with the fixed seed to generate a reproducible vector
        np.random.seed(seed)
        raw_vector = np.random.uniform(-1, 1, dimension)
        
        # Normalize the vector to unit length
        norm = np.linalg.norm(raw_vector)
        if norm > 0:
            normalized = raw_vector / norm
        else:
            normalized = raw_vector
            
        # Convert to list and return
        return normalized.tolist()
