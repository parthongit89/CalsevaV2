import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from database import db
from models import User

load_dotenv()

def create_database_if_not_exists():
    db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:parthpostgress89##@localhost:5432/calsevav2')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    result = urlparse(db_url)
    username = result.username or 'postgres'
    password = result.password or 'parthpostgress89##'
    host = result.hostname or 'localhost'
    port = result.port or 5432
    database = result.path.lstrip('/') or 'calsevav2'
    
    try:
        # Connect to default postgres DB to run admin query
        conn = psycopg2.connect(
            dbname="postgres",
            user=username,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if target db exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{database}'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(f"CREATE DATABASE {database}")
            print(f"Database '{database}' created successfully.")
        else:
            print(f"Database '{database}' already exists.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error during database creation check: {e}")

if __name__ == "__main__":
    # 1. Run database creation check
    create_database_if_not_exists()

    # 2. Setup Flask app context to drop/create tables
    app = Flask(__name__)
    db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:parthpostgress89##@localhost:5432/calsevav2')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        # Create all tables defined in models
        db.create_all()
        print("Database schemas created.")

        # Seed authenticated user examples for testing
        test_user = User.query.filter_by(employee_id='12345').first()
        if not test_user:
            user = User(
                employee_id='12345',
                email='parthongit89@gmail.com',
                phone='1234567890'
            )
            user.set_password('Password123!')
            db.session.add(user)
            db.session.commit()
            print("Seeded test user '12345' with password 'Password123!' successfully.")
        else:
            print("Test user '12345' already exists in database.")
