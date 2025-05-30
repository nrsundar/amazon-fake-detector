#!/bin/bash

# Streamlit setup script for Streamlit Cloud deployment
mkdir -p ~/.streamlit/

echo "[general]\nemail = \"your-email@example.com\"" > ~/.streamlit/credentials.toml

echo "[server]\nheadless = true\nenableCORS=false\nport = \$PORT" > ~/.streamlit/config.toml

