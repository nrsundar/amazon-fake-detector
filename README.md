# Amazon Fake Product Detector

A powerful tool for detecting potentially counterfeit Amazon products using AI techniques and similarity analysis.

## Features

### Core Functionality
- **Amazon URL Analysis**: Directly analyze products by entering Amazon product URLs
- **Manual Product Entry**: Enter product details manually for comprehensive analysis
- **Real-time Web Scraping**: Automatically extracts product information from Amazon pages using advanced scraping techniques
- **Authenticity Scoring**: Provides quantitative authenticity assessment with detailed reasoning

### Advanced AI Capabilities
- **Agentic AI Workflow**: Uses LangChain to create an intelligent agent that orchestrates the entire analysis process
- **Vector Database Search**: Employs PostgreSQL with pgvector extension for semantic similarity search across product databases
- **Intelligent Product Comparison**: AI agent automatically finds and compares similar products to detect anomalies
- **Multi-factor Analysis**: Agent considers price patterns, brand consistency, description quality, and similarity to known products

### Data Intelligence Features
- **Vector Embeddings**: Converts product descriptions into high-dimensional vectors for semantic understanding
- **Similarity Detection**: Finds products with similar characteristics using cosine similarity in vector space
- **Pattern Recognition**: Identifies suspicious pricing, description patterns, and brand inconsistencies
- **Live Data Import**: Import and analyze real product data from Amazon for building comparison database

### User Experience
- **Interactive Dashboard**: Clean Streamlit interface with tabbed navigation
- **Recent Analysis History**: Track previously analyzed products with verification status
- **Detailed Reasoning**: AI agent provides clear explanations for authenticity decisions
- **Visual Analytics**: Charts and metrics showing product comparison results

## Technology Stack

### AI & Machine Learning
- **Agentic AI**: LangChain-powered intelligent agent for autonomous product analysis
- **Vector Database**: PostgreSQL with pgvector extension for high-performance semantic search
- **Text Embeddings**: Advanced text vectorization for semantic understanding of product descriptions
- **Pattern Analysis**: AI-driven detection of counterfeit product indicators

### Data Processing
- **Web Scraping**: Trafilatura for robust extraction of product data from Amazon
- **Real-time Analysis**: Live processing of product information with immediate results
- **Vector Operations**: Efficient similarity calculations using cosine distance in vector space

### Infrastructure
- **Frontend**: Streamlit for responsive web interface
- **Database**: PostgreSQL with vector extension for scalable data storage
- **Analysis Engine**: LangChain orchestration for complex AI workflows

## Quick Start

### 1. Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/amazon-fake-detector.git
   cd amazon-fake-detector
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements_github.txt
   ```

3. Set up environment variables:
   ```bash
   export PGHOST=your_postgres_host
   export PGDATABASE=your_database_name
   export PGUSER=your_username
   export PGPASSWORD=your_password
   export PGPORT=5432
   ```

4. Run the application:
   ```bash
   streamlit run main.py
   ```

### 2. Deployment Options

#### Option A: Streamlit Cloud (Free)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select your repository
4. Set the main file path: `main.py`
5. Add environment variables in the Secrets section:
   ```toml
   PGHOST = "your_postgres_host"
   PGDATABASE = "your_database_name"
   PGUSER = "your_username"
   PGPASSWORD = "your_password"
   PGPORT = "5432"
   ```

#### Option B: Heroku

1. Create a Heroku account
2. Install Heroku CLI
3. Create a new app: `heroku create your-app-name`
4. Add PostgreSQL addon: `heroku addons:create heroku-postgresql:hobby-dev`
5. Deploy: `git push heroku main`

#### Option C: Railway

1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Add PostgreSQL database
4. Set environment variables
5. Deploy automatically

## How to Test and Use

### Step 1: Initial Setup
1. **Access the Application**: Visit the live demo or run locally
2. **Initialize Database**: Click "Initialize Database" in the sidebar to create necessary tables
3. **Import Sample Data**: Click "Import Sample Data" to populate the database with comparison products

### Step 2: Testing Product Analysis

#### Method A: Manual Entry (Recommended for Testing)
1. Navigate to the **"Manual Entry"** tab
2. Enter product details:
   ```
   Title: Apple iPhone 15 Pro Max
   Description: Latest iPhone with titanium design, A17 Pro chip, and advanced camera system
   Price: 1199
   Brand: Apple
   ```
3. Click **"Analyze Product"** to see the AI analysis

#### Method B: Amazon URL Analysis
1. Go to the **"Amazon URL"** tab
2. Paste a valid Amazon product URL (e.g., `https://www.amazon.com/dp/B0D4QDHRTT`)
3. Click **"Analyze Product"**
   - Note: Amazon's anti-bot protection may limit URL scraping

### Step 3: Understanding Results

#### Risk Indicator System
The application displays a **color-coded risk assessment**:

- **🟢 LOW RISK (0.0-0.3)**: Highly Authentic - Strong authenticity indicators
- **🔵 MODERATE RISK (0.3-0.5)**: Likely Authentic - Minor concerns detected  
- **🟡 ELEVATED RISK (0.5-0.7)**: Potentially Suspicious - Proceed with caution
- **🟠 HIGH RISK (0.7-0.85)**: Likely Counterfeit - Strong risk indicators
- **🔴 CRITICAL RISK (0.85-1.0)**: Highly Suspicious - Avoid this product

#### Analysis Components
1. **Authenticity Score**: Numerical risk assessment (0-1 scale)
2. **Risk Level Badge**: Color-coded risk category
3. **Progress Bar**: Visual representation of risk level
4. **Detailed Reasoning**: AI explanation of the assessment
5. **Similar Products**: Comparison with verified products in database

### Step 4: Testing Different Scenarios

#### Test Case 1: Authentic Product
```
Title: Apple MacBook Air M2
Description: 13.6-inch Liquid Retina display, 8GB RAM, 256GB SSD
Price: 1099
Brand: Apple
```
*Expected: LOW to MODERATE risk level*

#### Test Case 2: Suspicious Product
```
Title: Aple iPhone 15 Pro (note misspelling)
Description: Cheap iPhone with all features
Price: 99
Brand: Aple
```
*Expected: HIGH to CRITICAL risk level*

#### Test Case 3: Luxury Item Test
```
Title: Rolex Submariner Watch
Description: Luxury Swiss watch with automatic movement
Price: 500
Brand: Rolex
```
*Expected: HIGH risk due to unusually low price*

### Step 5: Interpreting AI Analysis

The system evaluates products based on:
- **Price Analysis**: Comparison with typical market prices
- **Brand Consistency**: Spelling and authenticity of brand names
- **Description Quality**: Professional vs. suspicious language patterns
- **Similarity Matching**: Comparison with verified authentic products
- **Pattern Recognition**: Detection of common counterfeit indicators

### Troubleshooting

**Common Issues:**
- **URL Analysis Fails**: Use Manual Entry instead due to Amazon's anti-scraping measures
- **No Similar Products Found**: Import sample data first to populate comparison database
- **Database Errors**: Ensure PostgreSQL is properly configured with vector extension

**Getting Accurate Results:**
1. Always initialize the database before first use
2. Import sample data to improve comparison accuracy
3. Test with both obviously authentic and suspicious products
4. Review the detailed reasoning to understand AI decision-making

## Database Setup

For production deployment, you'll need a PostgreSQL database with pgvector extension:

```sql
CREATE EXTENSION vector;
```

## Configuration

Update `config.yaml` with your specific settings:
- Database connection details
- LLM model preferences
- Application settings

## Project Structure

## 🚀 Live Demo

Try the application now: **[Amazon Fake Product Detector - Live Demo](https://b19501a0-5229-42e9-a9d6-bff8a5e8b0d6-00-un7115e0hxtr.picard.replit.dev/)**

*Experience the full AI-powered analysis with vector database search and agentic workflow in action.*

