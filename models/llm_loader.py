"""
LLM loader module for loading language models.
This version uses a simple text generation approach for demonstration.
"""

import os
import yaml
import random
from typing import Dict, Any, Optional, List
from langchain.schema import BaseMessage, AIMessage, HumanMessage

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

class LLMLoader:
    """
    Class for simulating language model responses.
    This is a simplified version for demonstration that doesn't require external LLM APIs.
    """
    
    def __init__(self, 
                 model_name: Optional[str] = None, 
                 temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None,
                 top_p: Optional[float] = None):
        """
        Initialize the LLM loader with optional parameters.
        
        Args:
            model_name (str, optional): The name of the model to simulate
            temperature (float, optional): Temperature parameter (unused in simulation)
            max_tokens (int, optional): Maximum tokens (unused in simulation)
            top_p (float, optional): Top-p sampling parameter (unused in simulation)
        """
        # Use parameters or default from config
        self.model_name = model_name or config["llm"]["model_name"]
        self.temperature = temperature or config["llm"]["temperature"]
        self.max_tokens = max_tokens or config["llm"]["max_tokens"]
        self.top_p = top_p or config["llm"]["top_p"]
        
    def load_llm(self):
        """
        Load and configure the simulated language model.
        
        Returns:
            An object with an invoke method that simulates LLM responses
        """
        # Return a simple LLM simulator
        return SimpleLLMSimulator(
            model_name=self.model_name,
            temperature=self.temperature
        )
        
    def update_parameters(self, params: Dict[str, Any]) -> None:
        """
        Update the LLM parameters.
        
        Args:
            params (Dict[str, Any]): Dictionary of parameters to update
        """
        if "model_name" in params:
            self.model_name = params["model_name"]
        if "temperature" in params:
            self.temperature = params["temperature"]
        if "max_tokens" in params:
            self.max_tokens = params["max_tokens"]
        if "top_p" in params:
            self.top_p = params["top_p"]
            

class SimpleLLMSimulator:
    """
    A simple simulator for language model responses.
    Used for demonstration purposes when actual LLM access isn't available.
    """
    
    def __init__(self, model_name: str, temperature: float = 0.1):
        """
        Initialize the LLM simulator.
        
        Args:
            model_name (str): Name to identify this simulator
            temperature (float): Controls randomness (higher = more variation)
        """
        self.model_name = model_name
        self.temperature = temperature
        
    def invoke(self, prompt: str) -> str:
        """
        Generate a simulated response to the given prompt.
        
        Args:
            prompt (str): The input prompt
            
        Returns:
            str: A simulated response
        """
        # Check for various prompt types and generate appropriate responses
        if "authenticate" in prompt.lower() or "fake product" in prompt.lower():
            return self._generate_product_analysis()
        elif "json" in prompt.lower():
            return self._generate_json_response()
        else:
            return "I'm a simulated LLM response. For this demo, I'm providing pre-written answers instead of actual AI generation."
    
    def _generate_product_analysis(self) -> str:
        """Generate a simulated product analysis response."""
        authenticity_score = round(random.uniform(0.2, 0.9), 2)
        
        if authenticity_score > 0.7:
            return self._generate_fake_product_response(authenticity_score)
        else:
            return self._generate_authentic_product_response(authenticity_score)
    
    def _generate_authentic_product_response(self, score: float) -> str:
        """Generate a response for likely authentic products."""
        return f"""
        {{
            "score": {score},
            "reasoning": "The product appears to be authentic based on consistent branding, appropriate pricing compared to similar products, and detailed product description that matches official specifications.",
            "warning_indicators": [],
            "recommendations": [
                "Verify the seller's ratings and history",
                "Check product reviews from verified purchasers",
                "Confirm the product has proper warranty information"
            ]
        }}
        """
    
    def _generate_fake_product_response(self, score: float) -> str:
        """Generate a response for likely counterfeit products."""
        return f"""
        {{
            "score": {score},
            "reasoning": "The product shows several signs of being potentially counterfeit, including significantly lower price than authentic versions, inconsistent branding elements, and vague product specifications that don't match official documentation.",
            "warning_indicators": [
                "Price is substantially below market average",
                "Brand name has subtle misspellings or variations",
                "Description contains grammatical errors or inconsistencies",
                "Images appear to be low quality or edited"
            ],
            "recommendations": [
                "Avoid purchasing this product",
                "Report the listing to the marketplace",
                "Look for authorized sellers of this brand",
                "Consider alternatives from verified sellers"
            ]
        }}
        """
    
    def _generate_json_response(self) -> str:
        """Generate a simulated JSON response."""
        return """
        {
            "analysis": "completed",
            "score": 0.75,
            "confidence": "medium",
            "details": {
                "price_analysis": "significantly below market average",
                "description_quality": "poor",
                "brand_consistency": "suspicious",
                "overall_assessment": "likely counterfeit"
            }
        }
        """
