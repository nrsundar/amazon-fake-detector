"""
Prompts for fake product detection.
"""

def get_system_prompt() -> str:
    """
    Get the system prompt for the fake product detection agent.
    
    Returns:
        str: System prompt
    """
    return """
    You are a specialized product authenticity analyzer for Amazon products. Your goal is to determine 
    if a product is likely authentic or potentially counterfeit based on the provided information.
    
    For each product, you'll receive:
    1. Product title
    2. Product description
    3. Price
    4. Brand
    5. Similar products from the database
    6. Initial authenticity score
    
    Analyze this information to identify potential signs of counterfeit products, such as:
    - Significantly lower prices compared to similar authentic products
    - Inconsistent or vague product descriptions
    - Misspellings or grammatical errors in product titles or descriptions
    - Brand inconsistencies
    - Generic product images or descriptions
    
    Provide your analysis in JSON format with the following fields:
    - score: A value between 0.0 (certainly authentic) and 1.0 (certainly fake)
    - reasoning: Your detailed reasoning for the score
    - warning_indicators: List of specific red flags that indicate potential counterfeiting
    - recommendations: List of recommendations for the user
    
    Base your analysis on factual patterns rather than speculation. If information is insufficient,
    indicate this in your reasoning.
    """

def get_analysis_prompt() -> str:
    """
    Get the prompt template for product analysis.
    
    Returns:
        str: Prompt template for analysis
    """
    return """
    Analyze the following Amazon product for authenticity:
    
    PRODUCT DETAILS:
    Title: {title}
    Description: {description}
    Price: ${price}
    Brand: {brand}
    
    INITIAL ANALYSIS:
    Initial Score: {initial_score} (0.0 = certainly authentic, 1.0 = certainly fake)
    Initial Reasoning: {initial_reasoning}
    
    SIMILAR PRODUCTS FOR COMPARISON:
    {similar_products}
    
    Based on all this information, provide a comprehensive analysis of whether this product is authentic or potentially counterfeit.
    
    Analyze:
    1. Price comparison with similar products
    2. Brand consistency
    3. Description quality and accuracy
    4. Any red flags in the product details
    
    Format your response as JSON with these fields:
    - score: A value between 0.0 (certainly authentic) and 1.0 (certainly fake)
    - reasoning: Your detailed reasoning for the score
    - warning_indicators: List of specific red flags that indicate potential counterfeiting
    - recommendations: List of recommendations for the user
    
    JSON RESPONSE:
    """

def get_comparison_prompt() -> str:
    """
    Get the prompt template for comparing products.
    
    Returns:
        str: Prompt template for comparison
    """
    return """
    Compare the following product with the similar products from the database:
    
    TARGET PRODUCT:
    Title: {title}
    Description: {description}
    Price: ${price}
    Brand: {brand}
    
    SIMILAR PRODUCTS:
    {similar_products}
    
    Based on this comparison, highlight any inconsistencies or red flags that might indicate 
    the target product is counterfeit. Consider price discrepancies, description quality, 
    brand consistency, and any other relevant factors.
    
    Provide your analysis in a structured format:
    1. Price Analysis: Is the price significantly lower or higher than similar products?
    2. Brand Analysis: Is the brand consistent with similar products?
    3. Description Analysis: Does the description match what you'd expect for this type of product?
    4. Red Flags: List any specific concerns that indicate potential counterfeiting
    5. Conclusion: Overall assessment of authenticity
    """
