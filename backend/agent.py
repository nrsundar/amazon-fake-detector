"""
Agent module for orchestrating product analysis using LLM and vector search.
"""

import os
import yaml
import json
from typing import Dict, Any, List, Tuple, Optional
from langchain.schema import BaseMessage, AIMessage, HumanMessage
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from models.llm_loader import LLMLoader
from models.embedding_model import EmbeddingModel
from backend.product_search import ProductSearch
from prompts.fake_product_prompt import get_system_prompt, get_analysis_prompt

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

class ProductAnalysisAgent:
    """
    Agent for analyzing product authenticity using LLM and vector search.
    """
    
    def __init__(self):
        """Initialize the product analysis agent."""
        self.llm_loader = LLMLoader()
        self.llm = self.llm_loader.load_llm()
        self.product_search = ProductSearch()
        self.embedding_model = EmbeddingModel()
        self.max_iterations = config["agent"]["max_iterations"]
        self.fake_threshold = config["agent"]["fake_threshold"]
        
    def analyze_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a product using LLM and vector search.
        
        Args:
            product_data (Dict[str, Any]): Product data including title, description, price, brand
            
        Returns:
            Dict[str, Any]: Analysis results including score, reasoning, and recommendation
        """
        # Step 1: Calculate initial authenticity score based on vector similarity
        initial_score, initial_reasoning, similar_products = self.product_search.analyze_product_authenticity(product_data)
        
        # Step 2: Enhanced analysis using LLM
        llm_analysis = self._perform_llm_analysis(product_data, initial_score, initial_reasoning, similar_products)
        
        # Step 3: Calculate final score
        final_score = max(initial_score, llm_analysis["score"])
        
        # Step 4: Prepare detailed reasoning
        if final_score >= self.fake_threshold:
            authenticity = "Potentially Fake"
        else:
            authenticity = "Likely Authentic"
            
        # Store the analyzed product
        product_id = self.product_search.store_analyzed_product(
            product_data=product_data,
            score=final_score,
            verified=False  # Products analyzed by agent are not considered verified
        )
        
        # Prepare the final result
        result = {
            "product_id": product_id,
            "title": product_data.get("title", ""),
            "score": final_score,
            "authenticity": authenticity,
            "initial_reasoning": initial_reasoning,
            "llm_reasoning": llm_analysis["reasoning"],
            "warning_indicators": llm_analysis["warning_indicators"],
            "similar_products": similar_products,
            "recommendations": llm_analysis["recommendations"]
        }
        
        return result
        
    def _perform_llm_analysis(
        self, 
        product_data: Dict[str, Any], 
        initial_score: float, 
        initial_reasoning: str,
        similar_products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform enhanced analysis using LLM.
        
        Args:
            product_data (Dict[str, Any]): Product data
            initial_score (float): Initial authenticity score
            initial_reasoning (str): Initial reasoning
            similar_products (List[Dict[str, Any]]): Similar products for comparison
            
        Returns:
            Dict[str, Any]: LLM analysis results
        """
        # Prepare prompt with product details and initial analysis
        title = product_data.get("title", "")
        description = product_data.get("description", "")
        price = product_data.get("price", 0)
        brand = product_data.get("brand", "")
        
        # Create formatted similar products text
        similar_products_text = ""
        for idx, product in enumerate(similar_products[:3], 1):  # Limit to top 3 for clarity
            similar_products_text += f"Product {idx}:\n"
            similar_products_text += f"Title: {product.get('title', '')}\n"
            similar_products_text += f"Brand: {product.get('brand', '')}\n"
            similar_products_text += f"Price: ${product.get('price', 0):.2f}\n"
            similar_products_text += f"Similarity: {product.get('similarity', 0):.2f}\n\n"
            
        # Get analysis prompt
        analysis_prompt = get_analysis_prompt()
        
        # Format the prompt
        prompt = analysis_prompt.format(
            title=title,
            description=description,
            price=price,
            brand=brand,
            initial_score=initial_score,
            initial_reasoning=initial_reasoning,
            similar_products=similar_products_text
        )
        
        # Get LLM response
        llm_response = self.llm.invoke(prompt)
        
        # Process LLM response
        try:
            # Try to parse as JSON first
            result = self._extract_json_from_response(llm_response)
            
            if not result:
                # Fallback to parsing structured text
                result = self._parse_structured_response(llm_response)
                
            # Ensure all required fields are present
            if not all(key in result for key in ["score", "reasoning", "warning_indicators", "recommendations"]):
                # Fill in missing fields
                if "score" not in result:
                    result["score"] = initial_score
                if "reasoning" not in result:
                    result["reasoning"] = "Analysis incomplete. Using initial assessment."
                if "warning_indicators" not in result:
                    result["warning_indicators"] = []
                if "recommendations" not in result:
                    result["recommendations"] = []
                    
            return result
        except Exception as e:
            print(f"Error processing LLM response: {e}")
            # Fallback to initial analysis
            return {
                "score": initial_score,
                "reasoning": f"LLM analysis failed: {e}. Using initial assessment: {initial_reasoning}",
                "warning_indicators": [],
                "recommendations": ["Manually verify this product due to analysis error."]
            }
            
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response.
        
        Args:
            response (str): LLM response text
            
        Returns:
            Dict[str, Any]: Extracted JSON or empty dict if not found
        """
        try:
            # Find JSON blocks in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx+1]
                result = json.loads(json_str)
                return result
            return {}
        except Exception:
            return {}
            
    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        """
        Parse structured text response from LLM.
        
        Args:
            response (str): LLM response text
            
        Returns:
            Dict[str, Any]: Parsed response
        """
        result = {
            "score": 0.0,
            "reasoning": "",
            "warning_indicators": [],
            "recommendations": []
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
                
            # Check for section headers
            if "score:" in line.lower():
                current_section = "score"
                # Try to extract score value
                try:
                    score_text = line.split(":", 1)[1].strip()
                    # Handle both numeric and text formats
                    if score_text.replace(".", "", 1).isdigit():
                        result["score"] = float(score_text)
                    else:
                        # Try to extract numeric part
                        import re
                        score_match = re.search(r'(\d+(\.\d+)?)', score_text)
                        if score_match:
                            result["score"] = float(score_match.group(1))
                except Exception:
                    pass
            elif any(header in line.lower() for header in ["reasoning:", "analysis:", "assessment:"]):
                current_section = "reasoning"
                reasoning_text = line.split(":", 1)[1].strip() if ":" in line else line
                result["reasoning"] = reasoning_text
            elif any(header in line.lower() for header in ["warning", "indicator", "red flag"]):
                current_section = "warning_indicators"
                if ":" in line:
                    indicator = line.split(":", 1)[1].strip()
                    if indicator:
                        result["warning_indicators"].append(indicator)
            elif any(header in line.lower() for header in ["recommendation", "suggest"]):
                current_section = "recommendations"
                if ":" in line:
                    recommendation = line.split(":", 1)[1].strip()
                    if recommendation:
                        result["recommendations"].append(recommendation)
            elif current_section == "reasoning":
                result["reasoning"] += " " + line
            elif current_section == "warning_indicators" and line.startswith("-"):
                result["warning_indicators"].append(line[1:].strip())
            elif current_section == "recommendations" and line.startswith("-"):
                result["recommendations"].append(line[1:].strip())
                
        # If no explicit score was found, try to infer from reasoning
        if result["score"] == 0.0:
            reasoning_lower = result["reasoning"].lower()
            if any(word in reasoning_lower for word in ["fake", "counterfeit", "suspicious", "not authentic"]):
                result["score"] = 0.8
            elif any(word in reasoning_lower for word in ["authentic", "genuine", "legitimate"]):
                result["score"] = 0.2
            else:
                result["score"] = 0.5
                
        return result
