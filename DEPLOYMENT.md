# Deployment Guide

## Files to Download for GitHub

You need to download these files from your Replit project to upload to GitHub:

### Required Files:
```
amazon-fake-detector/
├── main.py
├── config.yaml
├── requirements.txt (rename from requirements_github.txt)
├── runtime.txt
├── .gitignore
├── setup.sh
├── README.md
├── DEPLOYMENT.md
├── .streamlit/
│   └── config.toml
├── models/
│   ├── embedding_model.py
│   └── llm_loader.py
├── backend/
│   ├── database.py
│   ├── agent.py
│   ├── product_search.py
│   └── amazon_scraper.py
├── prompts/
│   └── fake_product_prompt.py
├── data/
│   └── sample_products.csv
└── docs/
    └── deployment-guide.md
```

## Step-by-Step GitHub Setup

### 1. Create GitHub Repository
1. Go to GitHub.com and sign in
2. Click "New repository"
3. Name: `amazon-fake-detector`
4. Description: "AI-powered Amazon product authenticity checker"
5. Set to Public
6. Don't initialize with README
7. Click "Create repository"

### 2. Prepare Your Files
1. Download all the files listed above from Replit
2. Rename `requirements_github.txt` to `requirements.txt`
3. Create the folder structure as shown above

### 3. Upload to GitHub
You can either:

**Option A: Use GitHub Web Interface**
1. Click "uploading an existing file"
2. Drag and drop all your files
3. Commit with message: "Initial commit: Amazon Fake Product Detector"

**Option B: Use Git Commands**
```bash
git init
git add .
git commit -m "Initial commit: Amazon Fake Product Detector"
git branch -M main
git remote add origin https://github.com/yourusername/amazon-fake-detector.git
git push -u origin main
```

### 4. Deploy on Streamlit Cloud (Recommended)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign up" and connect your GitHub account
3. Click "New app"
4. Select your repository: `amazon-fake-detector`
5. Main file path: `main.py`
6. Click "Advanced settings"
7. Add these secrets:
   ```
   PGHOST = "your_database_host"
   PGDATABASE = "your_database_name"
   PGUSER = "your_username"
   PGPASSWORD = "your_password"
   PGPORT = "5432"
   ```
8. Click "Deploy"

### 5. Database Setup for Production

You'll need a PostgreSQL database with pgvector extension. Options:

**Free Options:**
- Neon.tech (has pgvector support)
- Supabase (PostgreSQL with extensions)
- Railway (PostgreSQL addon)

**Setup Steps:**
1. Create database
2. Run: `CREATE EXTENSION vector;`
3. Use the connection details in your Streamlit Cloud secrets

### 6. Testing Your Deployment

1. Wait for deployment to complete
2. Click on your app URL
3. Test the "Initialize Database" button
4. Try importing sample data
5. Test product analysis with both manual entry and Amazon URLs

## Troubleshooting

**Common Issues:**
- **Database connection errors**: Check your environment variables
- **Import errors**: Ensure all files are uploaded correctly
- **Streamlit errors**: Check the logs in Streamlit Cloud dashboard

**Getting Help:**
- Check Streamlit Cloud logs
- Verify all required files are present
- Ensure database credentials are correct