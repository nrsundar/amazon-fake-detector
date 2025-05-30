"""
Amazon Fake Product Detector
Main application file for Streamlit interface.
"""

import os
import yaml
import streamlit as st
import pandas as pd
import json
import time
from typing import Dict, Any, List, Tuple, Optional

# Import required modules from our project
from models.embedding_model import EmbeddingModel
from models.llm_loader import LLMLoader
from backend.database import Database
from backend.agent import ProductAnalysisAgent
from backend.product_search import ProductSearch
from backend.amazon_scraper import scrape_amazon_product, extract_sample_products

# Set page configuration
st.set_page_config(
    page_title="Amazon Fake Product Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Initialize the database on first run
@st.cache_resource
def initialize_database():
    """Initialize the database and return connection status."""
    db = Database()
    try:
        db.initialize_database()
        return True
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return False

# Initialize embedding model
@st.cache_resource
def load_embedding_model():
    """Load and initialize the embedding model."""
    return EmbeddingModel()

# Initialize LLM
@st.cache_resource
def load_llm():
    """Load and initialize the language model."""
    llm_loader = LLMLoader()
    return llm_loader.load_llm()

# Initialize agent
@st.cache_resource
def load_agent():
    """Load and initialize the product analysis agent."""
    return ProductAnalysisAgent()

# Initialize product search
@st.cache_resource
def load_product_search():
    """Load and initialize the product search."""
    return ProductSearch()

# Import sample data function
def import_sample_data():
    """Import sample products data into the database."""
    try:
        # Load sample data from CSV
        df = pd.read_csv("data/sample_products.csv")
        
        # Initialize components
        embedding_model = load_embedding_model()
        product_search = load_product_search()
        
        # Process each product
        success_count = 0
        for _, row in df.iterrows():
            product_data = {
                "title": row["title"],
                "description": row["description"],
                "price": float(row["price"]),
                "brand": row["brand"],
                "verified": bool(row["verified"])
            }
            
            # Get embedding for the product
            embedding = embedding_model.get_embeddings(
                f"Title: {product_data['title']}. Description: {product_data['description']}. Brand: {product_data['brand']}."
            )
            
            # Calculate a fake score (inverse of verified status)
            score = 0.2 if product_data["verified"] else 0.8
            
            # Add embedding and score
            product_data["embedding"] = embedding
            product_data["score"] = score
            
            # Store in database
            db = Database()
            db.insert_product(product_data)
            success_count += 1
            
        return success_count
    except Exception as e:
        st.error(f"Error importing sample data: {e}")
        return 0

# Display header and sidebar
def display_header():
    """Display application header and description."""
    st.title("Amazon Fake Product Detector")
    st.markdown("""
    This application helps detect potentially counterfeit Amazon products by analyzing product details.
    Enter the product information below and get an authenticity analysis.
    """)
    
    # Display app image
    st.image("https://pixabay.com/get/gf23ee85e456b085f54e3f28394c11224e2069f6ed587e1fb0d9b5a0984932cc89897c1f1c1dc94b98758499b32b592a251854a0c9b4f0394bceda58b3ca1ee1d_1280.jpg", 
             caption="Verify product authenticity before purchasing", 
             use_container_width=True)

# Display sidebar with additional information
def display_sidebar():
    """Display application sidebar with information and controls."""
    st.sidebar.title("About")
    st.sidebar.markdown("""
    **Amazon Fake Product Detector** uses advanced AI techniques to analyze product listings 
    and identify potential counterfeit items.
    
    ### How it works:
    1. Enter product details from Amazon
    2. Our system analyzes the information using:
       - Vector similarity search
       - Local LLM analysis
       - Price and brand comparison
    3. Get results showing authenticity score and reasoning
    
    ### Technologies used:
    - PostgreSQL with pgvector
    - Local LLMs via Ollama
    - LangChain for orchestration
    - Vector embeddings for similarity search
    """)
    
    st.sidebar.title("Controls")
    
    # Initialize database button
    if st.sidebar.button("Initialize Database"):
        with st.sidebar:
            with st.spinner("Initializing database..."):
                if initialize_database():
                    st.success("Database initialized successfully!")
                else:
                    st.error("Database initialization failed. Check logs for details.")
    
    # Sample data options in an expander
    with st.sidebar.expander("Import Sample Data"):
        # Option 1: Import from CSV
        if st.button("Import Sample Data from CSV"):
            with st.spinner("Importing sample data from CSV..."):
                count = import_sample_data()
                if count > 0:
                    st.success(f"Successfully imported {count} sample products from CSV!")
                else:
                    st.error("Failed to import sample data from CSV. Check logs for details.")
        
        # Option 2: Import from Amazon URLs
        if st.button("Import Live Sample Data from Amazon"):
            with st.spinner("Importing sample data from Amazon..."):
                count = import_amazon_sample_data()
                if count > 0:
                    st.success(f"Successfully imported {count} live products from Amazon!")
                else:
                    st.error("Failed to import sample data from Amazon. Check logs for details.")
    
    # Display example images
    st.sidebar.title("Counterfeit Awareness")
    st.sidebar.image("https://pixabay.com/get/gab31bcff3b44f9a9c7a9e9e36dfb6fd76de0537e4cc95dbec9e368011e40a56c664521ea97ed42efbb81aeeca1bb377cc400f90a146b1f1296ccbf76230c80fa_1280.jpg", 
                     caption="Verify before you buy", 
                     use_container_width=True)
    
    # Add verification tips
    st.sidebar.title("Verification Tips")
    st.sidebar.markdown("""
    ### How to verify authenticity:
    - Check the seller's ratings and reviews
    - Look for suspicious pricing (too good to be true)
    - Inspect product packaging when received
    - Verify warranty and return policies
    - Contact the manufacturer if unsure
    """)

# Display product input form
def display_product_form():
    """Display form for entering product details."""
    st.header("Analyze Amazon Product")
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["Enter Product Details Manually", "Enter Amazon Product URL"])
    
    with tab1:
        with st.form("manual_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Product Title", 
                                     placeholder="Enter the full product title from Amazon")
                
                description = st.text_area("Product Description", 
                                          placeholder="Copy and paste the product description", 
                                          height=150)
            
            with col2:
                price = st.number_input("Price ($)", 
                                       min_value=0.01, 
                                       step=0.01, 
                                       format="%.2f",
                                       help="Enter the product price in USD")
                
                brand = st.text_input("Brand", 
                                     placeholder="Enter the brand name displayed on the listing")
                
                st.markdown("### Why provide this information?")
                st.markdown("""
                - **Title**: Used to identify product type and check for suspicious wording
                - **Description**: Analyzed for quality, consistency, and red flags
                - **Price**: Compared with similar authentic products
                - **Brand**: Verified against known authentic listings
                """)
            
            submit_button = st.form_submit_button("Analyze Product")
            
            if submit_button:
                if not title or not description or not brand:
                    st.error("Please fill in all the required fields: Title, Description, and Brand.")
                    return None
                    
                return {
                    "title": title,
                    "description": description,
                    "price": price,
                    "brand": brand
                }
    
    with tab2:
        with st.form("url_product_form"):
            amazon_url = st.text_input("Amazon Product URL", 
                                      placeholder="https://www.amazon.com/dp/PRODUCT_ID",
                                      help="Enter the full URL of the Amazon product")
            
            st.markdown("### How it works:")
            st.markdown("""
            1. Enter the full Amazon product URL
            2. Our system will extract product details automatically
            3. Analysis will be performed using the extracted data
            
            **Note:** This feature extracts information from the product page. 
            For best results, make sure the URL points to a valid Amazon product page.
            """)
            
            url_submit_button = st.form_submit_button("Fetch & Analyze Product")
            
            if url_submit_button:
                if not amazon_url or not amazon_url.startswith("https://www.amazon.com"):
                    st.error("Please enter a valid Amazon product URL.")
                    return None
                
                # Show loading message
                with st.spinner("Fetching product details from Amazon..."):
                    # Scrape product details from the URL
                    product_data = scrape_amazon_product(amazon_url)
                    
                    if not product_data:
                        st.error("Failed to extract product details from the URL. Please check the URL or try the manual entry method.")
                        return None
                    
                    # Show the extracted data
                    st.success("Product details extracted successfully!")
                    st.write("**Title:** " + product_data.get("title", ""))
                    st.write("**Brand:** " + product_data.get("brand", ""))
                    st.write("**Price:** $" + str(product_data.get("price", 0.0)))
                    
                    return product_data
    
    return None

# Function to import sample products from Amazon URLs
def import_amazon_sample_data():
    """Import sample products data from Amazon URLs."""
    try:
        # List of sample Amazon URLs for real products
        sample_urls = [
            "https://www.amazon.com/Apple-MacBook-13-inch-256GB-Storage/dp/B0CHX3QBCH/",
            "https://www.amazon.com/Samsung-Factory-Unlocked-Android-Smartphone/dp/B0DCFTC11Z/",
            "https://www.amazon.com/PlayStation-Pro-Console-Marvel-Wolverine-Limited/dp/B0CWG9FZ17/",
            "https://www.amazon.com/Beats-Studio-Cancelling-Earbuds-Built-Microphone/dp/B0BXK9RK81/"
        ]
        
        # Initialize components
        embedding_model = load_embedding_model()
        product_search = load_product_search()
        
        # Extract product details from URLs
        with st.spinner("Fetching sample products from Amazon..."):
            products = extract_sample_products(sample_urls)
            
            if not products:
                st.error("Failed to fetch sample products from Amazon. Please try again later.")
                return 0
            
            # Process each product
            success_count = 0
            for product in products:
                # Get embedding for the product
                text_for_embedding = f"Title: {product['title']}. Description: {product['description']}. Brand: {product['brand']}."
                embedding = embedding_model.get_embeddings(text_for_embedding)
                
                # Calculate a fake score (random but consistently applied)
                import hashlib
                # Use the ASIN to get a consistent fake score for each product
                asin = product.get('asin', '')
                hash_val = int(hashlib.md5(asin.encode()).hexdigest(), 16) % 100
                score = 0.2 if hash_val > 50 else 0.8
                verified = hash_val > 50
                
                # Prepare product data for database
                product_data = {
                    "title": product['title'],
                    "description": product['description'],
                    "price": float(product['price']),
                    "brand": product['brand'],
                    "embedding": embedding,
                    "score": score,
                    "verified": verified
                }
                
                # Store in database
                db = Database()
                db.insert_product(product_data)
                success_count += 1
            
            return success_count
    except Exception as e:
        st.error(f"Error importing Amazon sample data: {e}")
        return 0

# Display analysis results
def display_analysis_results(analysis_result: Dict[str, Any]):
    """
    Display the product analysis results.
    
    Args:
        analysis_result (Dict[str, Any]): The analysis result from the agent
    """
    st.header("Analysis Results")
    
    # Extract results
    score = analysis_result.get("score", 0.5)
    authenticity = analysis_result.get("authenticity", "Unknown")
    llm_reasoning = analysis_result.get("llm_reasoning", "")
    warning_indicators = analysis_result.get("warning_indicators", [])
    recommendations = analysis_result.get("recommendations", [])
    
    # Display score and authenticity
    cols = st.columns([2, 3])
    
    with cols[0]:
        # Display score gauge
        if score < 0.4:
            color = "green"
            emoji = "✅"
            authenticity = "Likely Authentic"
        elif score < 0.7:
            color = "orange"
            emoji = "⚠️"
            authenticity = "Possibly Counterfeit"
        else:
            color = "red"
            emoji = "❌"
            authenticity = "Likely Counterfeit"
            
        st.markdown(f"""
        <div style="padding: 20px; border-radius: 10px; background-color: {color}20; border: 1px solid {color}; text-align: center;">
            <h1 style="color: {color}; margin: 0;">{emoji} {authenticity}</h1>
            <h2 style="margin: 10px 0;">Score: {score:.2f}/1.00</h2>
            <p>(Higher score indicates higher risk of being counterfeit)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display verification image
        if score < 0.4:
            st.image("https://pixabay.com/get/gf8df5cc44370e143041a3d32f02f02b4f8658fb6dd3780423488b01084b0ac71bd3b1adaebd990aac015906b6a62aad568b65d84f850dada14527ebc880d43ab_1280.jpg", 
                     use_container_width=True)
        else:
            st.image("https://pixabay.com/get/gc0706fd6fdb06038392f99bb859ed8748ec1374de74a87804c3aa5e27255b9ef97056f326fac6468db2674bc0d0df216a0056cd037bf46fb416d7cd1c3c3d995_1280.jpg", 
                     use_container_width=True)
    
    with cols[1]:
        # Display detailed analysis
        st.subheader("Detailed Analysis")
        st.markdown(llm_reasoning)
        
        if warning_indicators:
            st.subheader("Warning Indicators")
            for indicator in warning_indicators:
                st.markdown(f"- {indicator}")
        
        if recommendations:
            st.subheader("Recommendations")
            for recommendation in recommendations:
                st.markdown(f"- {recommendation}")
    
    # Display similar products
    st.header("Similar Products for Comparison")
    similar_products = analysis_result.get("similar_products", [])
    
    if similar_products:
        # Create columns for similar products
        cols = st.columns(min(3, len(similar_products)))
        
        for i, product in enumerate(similar_products[:3]):  # Display up to 3 similar products
            with cols[i]:
                st.subheader(f"Similar Product {i+1}")
                st.markdown(f"**Title:** {product.get('title', 'N/A')}")
                st.markdown(f"**Brand:** {product.get('brand', 'N/A')}")
                st.markdown(f"**Price:** ${product.get('price', 0):.2f}")
                st.markdown(f"**Similarity:** {product.get('similarity', 0):.2f}")
                
                # Display verification status
                if product.get('verified', False):
                    st.markdown("**Status:** ✅ Verified Authentic")
                else:
                    st.markdown("**Status:** ⚠️ Not Verified")
    else:
        st.info("No similar products found for comparison.")

# Display recently analyzed products
def display_recent_products():
    """Display recently analyzed products from the database."""
    st.header("Recently Verified Products")
    
    try:
        # Get recently verified products
        db = Database()
        recent_products = db.get_recently_verified_products(limit=4)
        
        if not recent_products:
            st.info("No verified products in the database yet. Try importing sample data or analyzing some products.")
            return
        
        # Display products in columns
        cols = st.columns(min(4, len(recent_products)))
        
        for i, product in enumerate(recent_products):
            with cols[i]:
                st.subheader(f"{product.get('title', 'Unknown Product')[:30]}...")
                st.markdown(f"**Brand:** {product.get('brand', 'N/A')}")
                st.markdown(f"**Price:** ${product.get('price', 0):.2f}")
                
                # Display verification status and score
                score = product.get('score', 0.5)
                if score < 0.4:
                    st.markdown("**Status:** ✅ Verified Authentic")
                else:
                    st.markdown("**Status:** ⚠️ Possibly Counterfeit")
                
                st.markdown(f"**Score:** {score:.2f}/1.00")
    except Exception as e:
        st.error(f"Error loading recent products: {e}")

# Main application function
def main():
    """Main application function."""
    # Check/initialize database at startup
    db_initialized = initialize_database()
    
    # Load required components
    load_embedding_model()
    load_llm()
    agent = load_agent()
    
    # Display header and sidebar
    display_header()
    display_sidebar()
    
    # Display a separator
    st.markdown("---")
    
    # Display product form
    product_data = display_product_form()
    
    # Process if form is submitted
    if product_data:
        with st.spinner("Analyzing product... This may take a moment as we consult the local LLM..."):
            # Analyze the product
            try:
                analysis_result = agent.analyze_product(product_data)
                
                # Display analysis results
                display_analysis_results(analysis_result)
            except Exception as e:
                st.error(f"Error analyzing product: {e}")
                st.info("Please try again, ensure the database is initialized, or check your inputs.")
    
    # Display a separator
    st.markdown("---")
    
    # Display recently analyzed products
    display_recent_products()

if __name__ == "__main__":
    main()
