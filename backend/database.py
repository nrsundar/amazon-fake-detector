"""
Database module for connecting to PostgreSQL with pgvector extension.
Handles database operations including vector similarity search.
"""

import os
import yaml
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

class Database:
    """
    Class for handling database operations with PostgreSQL and pgvector.
    """
    
    def __init__(self):
        """Initialize database connection using configuration settings."""
        self.connection_params = {
            'host': config['database']['host'],
            'database': config['database']['database'],
            'user': config['database']['user'],
            'password': config['database']['password'],
            'port': config['database']['port']
        }
        self.embedding_dimension = config['embeddings']['dimension']
        self.connection = None
        self.cursor = None
        
    def connect(self) -> None:
        """
        Establish connection to the PostgreSQL database.
        """
        try:
            # Directly use environment variables
            self.connection = psycopg2.connect(
                host=os.environ.get('PGHOST'),
                database=os.environ.get('PGDATABASE'),
                user=os.environ.get('PGUSER'),
                password=os.environ.get('PGPASSWORD'),
                port=os.environ.get('PGPORT')
            )
                
            self.cursor = self.connection.cursor()
            print("Connected to the database successfully")
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            raise
            
    def disconnect(self) -> None:
        """
        Close the database connection.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Disconnected from the database")
            
    def initialize_database(self) -> None:
        """
        Initialize the database with necessary extensions and tables.
        """
        try:
            self.connect()
            
            # Enable pgvector extension
            self.cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create products table with vector column
            self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                price NUMERIC(10, 2),
                brand TEXT,
                embedding vector({self.embedding_dimension}),
                verified BOOLEAN DEFAULT FALSE,
                score NUMERIC(5, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            # Create index on vector column for similarity search
            self.cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS products_embedding_idx 
            ON products USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
            """)
            
            self.connection.commit()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            self.disconnect()
            
    def insert_product(self, product_data: Dict[str, Any]) -> int:
        """
        Insert a product into the database.
        
        Args:
            product_data (Dict[str, Any]): Product data including embedding
            
        Returns:
            int: ID of the inserted product
        """
        try:
            self.connect()
            
            # Extract product fields
            title = product_data.get('title', '')
            description = product_data.get('description', '')
            price = product_data.get('price')
            brand = product_data.get('brand', '')
            embedding = product_data.get('embedding', [])
            verified = product_data.get('verified', False)
            score = product_data.get('score', 0.0)
            
            # Create the query
            query = sql.SQL("""
            INSERT INTO products (title, description, price, brand, embedding, verified, score)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """)
            
            # Execute the query
            self.cursor.execute(query, (
                title, 
                description, 
                price, 
                brand, 
                embedding, 
                verified, 
                score
            ))
            
            # Get the inserted ID
            product_id = self.cursor.fetchone()[0]
            
            self.connection.commit()
            return product_id
        except Exception as e:
            print(f"Error inserting product: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            self.disconnect()
            
    def find_similar_products(self, embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find products with similar embeddings using cosine similarity.
        
        Args:
            embedding (List[float]): Vector embedding to search for
            limit (int): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of similar products with similarity scores
        """
        try:
            self.connect()
            
            # Create the query for vector similarity search with explicit type casting
            query = sql.SQL("""
            SELECT id, title, description, price, brand, verified, score,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM products
            ORDER BY similarity DESC
            LIMIT %s
            """)
            
            # Execute the query
            self.cursor.execute(query, (embedding, limit))
            
            # Fetch and format results
            results = []
            for row in self.cursor.fetchall():
                results.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'price': float(row[3]) if row[3] else None,
                    'brand': row[4],
                    'verified': row[5],
                    'score': float(row[6]) if row[6] else None,
                    'similarity': float(row[7])
                })
                
            return results
        except Exception as e:
            print(f"Error finding similar products: {e}")
            raise
        finally:
            self.disconnect()
            
    def update_product_verification(self, product_id: int, verified: bool, score: float) -> None:
        """
        Update a product's verification status and score.
        
        Args:
            product_id (int): ID of the product to update
            verified (bool): Whether the product is verified
            score (float): Authentication score
        """
        try:
            self.connect()
            
            # Create the update query
            query = sql.SQL("""
            UPDATE products
            SET verified = %s, score = %s
            WHERE id = %s
            """)
            
            # Execute the query
            self.cursor.execute(query, (verified, score, product_id))
            
            self.connection.commit()
        except Exception as e:
            print(f"Error updating product verification: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            self.disconnect()
            
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a product by its ID.
        
        Args:
            product_id (int): ID of the product to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Product data if found, None otherwise
        """
        try:
            self.connect()
            
            # Create the query
            query = sql.SQL("""
            SELECT id, title, description, price, brand, verified, score, created_at
            FROM products
            WHERE id = %s
            """)
            
            # Execute the query
            self.cursor.execute(query, (product_id,))
            
            # Fetch the result
            row = self.cursor.fetchone()
            
            if not row:
                return None
                
            return {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'price': float(row[3]) if row[3] else None,
                'brand': row[4],
                'verified': row[5],
                'score': float(row[6]) if row[6] else None,
                'created_at': row[7]
            }
        except Exception as e:
            print(f"Error getting product by ID: {e}")
            raise
        finally:
            self.disconnect()
            
    def get_recently_verified_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently verified products.
        
        Args:
            limit (int): Maximum number of products to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of recently verified products
        """
        try:
            self.connect()
            
            # Create the query
            query = sql.SQL("""
            SELECT id, title, description, price, brand, verified, score, created_at
            FROM products
            WHERE verified = TRUE
            ORDER BY created_at DESC
            LIMIT %s
            """)
            
            # Execute the query
            self.cursor.execute(query, (limit,))
            
            # Fetch and format results
            results = []
            for row in self.cursor.fetchall():
                results.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'price': float(row[3]) if row[3] else None,
                    'brand': row[4],
                    'verified': row[5],
                    'score': float(row[6]) if row[6] else None,
                    'created_at': row[7]
                })
                
            return results
        except Exception as e:
            print(f"Error getting recently verified products: {e}")
            raise
        finally:
            self.disconnect()
