# AWS Deployment Guide for Amazon Fake Product Detector

This guide provides instructions for deploying the Amazon Fake Product Detector application on AWS using EC2 for the application server and Aurora PostgreSQL for the database with pgvector support.

## Architecture Overview

![AWS Architecture](https://pixabay.com/get/g58ee79afc20398ccc13a2bc109bf9266cc944501258d2fe13be4a6389ab03505e10a408617cf687a7a672aac9416fc7b137bbf89d8aac22fa5e1419f35dd846c_1280.jpg)

The deployment architecture consists of:

1. **Amazon EC2**: Hosts the Streamlit application and Ollama
2. **Amazon Aurora PostgreSQL**: Database with pgvector extension
3. **Application Load Balancer**: Routes traffic to the EC2 instance
4. **Amazon S3**: Stores application logs and backups (optional)
5. **Amazon CloudWatch**: Monitors application performance (optional)

## Prerequisites

- AWS account with appropriate permissions
- AWS CLI installed and configured
- Basic knowledge of AWS services
- SSH key pair for EC2 access

## Step 1: Set Up Amazon Aurora PostgreSQL with pgvector

### Create a PostgreSQL-Compatible Aurora DB Cluster

1. Navigate to the RDS console: https://console.aws.amazon.com/rds/
2. Click "Create database"
3. Choose "Standard Create"
4. Select "Aurora (PostgreSQL Compatible)"
5. Choose the latest PostgreSQL version that supports pgvector (PostgreSQL 13.4+)
6. For "Templates", select "Dev/Test" or "Production" based on your needs
7. Configure settings:
   - DB cluster identifier: `amazon-fake-detector-db`
   - Master username: (choose a username)
   - Master password: (choose a secure password)
8. For "Instance configuration", choose an appropriate size (e.g., db.r5.large)
9. For "Availability & durability", choose "Create an Aurora Replica" for production
10. Configure connectivity:
    - VPC: (choose your VPC)
    - Create a new security group: `amazon-fake-detector-db-sg`
    - Public access: No (recommended for security)
11. Under "Additional configuration":
    - Initial database name: `amazon_fake_detector`
    - Enable "Enable Backtrack" if you want point-in-time recovery
12. Click "Create database"

### Enable pgvector Extension

After the database is created, you'll need to enable the pgvector extension:

1. Connect to the Aurora database using a PostgreSQL client
2. Run the following SQL command:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

## Step 2: Set Up EC2 Instance

### Launch EC2 Instance

1. Navigate to the EC2 console: https://console.aws.amazon.com/ec2/
2. Click "Launch instance"
3. Choose a name: `amazon-fake-detector-app`
4. Select an Amazon Machine Image (AMI): Amazon Linux 2 or Ubuntu Server 20.04 LTS
5. Choose an instance type: t3.medium or larger (Ollama requires sufficient RAM)
6. Configure instance details:
   - Network: (choose your VPC)
   - Subnet: (choose a public subnet)
   - Auto-assign Public IP: Enable
7. Add storage: at least 20GB (Ollama models require significant disk space)
8. Configure security group:
   - Create a new security group: `amazon-fake-detector-app-sg`
   - Add rule: SSH (port 22) from your IP
   - Add rule: HTTP (port 80) from anywhere
   - Add rule: HTTPS (port 443) from anywhere
   - Add rule: Custom TCP (port 5000) from anywhere (for Streamlit)
9. Review and launch
10. Select an existing key pair or create a new one
11. Launch instance

### Configure EC2 Instance

1. Connect to your EC2 instance via SSH:
   ```
   ssh -i your-key.pem ec2-user@your-instance-public-ip
   ```

2. Update the system:
   ```
   sudo yum update -y  # For Amazon Linux
   # OR
   sudo apt update && sudo apt upgrade -y  # For Ubuntu
   ```

3. Install required packages:
   ```
   # For Amazon Linux
   sudo amazon-linux-extras install python3.8
   sudo yum install git docker -y
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker ec2-user
   
   # For Ubuntu
   sudo apt install -y python3 python3-pip git docker.io
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker ubuntu
   ```

4. Install Ollama:
   ```
   # Log out and log back in to apply docker group
   curl -fsSL https://ollama.com/install.sh | sh
   ```

5. Pull the required LLM model:
   ```
   ollama pull llama3  # Or your preferred model
   ```

6. Clone the repository:
   ```
   git clone https://github.com/yourusername/amazon-fake-detector.git
   cd amazon-fake-detector
   ```

7. Install Python dependencies:
   ```
   pip3 install -r requirements.txt
   ```

8. Configure the application:
   ```
   # Update config.yaml with your Aurora PostgreSQL connection details
   nano config.yaml
   ```

9. Create a systemd service to run the application:
   ```
   sudo nano /etc/systemd/system/amazon-fake-detector.service
   ```

   Add the following content:
   ```
   [Unit]
   Description=Amazon Fake Product Detector
   After=network.target

   [Service]
   User=ec2-user  # Use 'ubuntu' for Ubuntu
   WorkingDirectory=/home/ec2-user/amazon-fake-detector  # Adjust path as needed
   ExecStart=/usr/bin/python3 -m streamlit run main.py --server.port 5000
   Restart=on-failure
   Environment="PGHOST=your-aurora-endpoint"
   Environment="PGDATABASE=amazon_fake_detector"
   Environment="PGUSER=your-db-username"
   Environment="PGPASSWORD=your-db-password"
   Environment="PGPORT=5432"
   Environment="DATABASE_URL=postgresql://your-db-username:your-db-password@your-aurora-endpoint:5432/amazon_fake_detector"

   [Install]
   WantedBy=multi-user.target

