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

## Usage

1. **Initialize Database**: Click the button in the sidebar to set up database tables
2. **Import Sample Data**: Use either CSV data or live Amazon data
3. **Analyze Products**: 
   - Use the "Amazon URL" tab to analyze by URL
   - Use the "Manual Entry" tab for custom input
4. **Review Results**: See authenticity scores, reasoning, and similar products

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

