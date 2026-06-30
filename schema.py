import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask
from database import db
from models import User

def create_database_if_not_exists():
    try:
        # Connect to default postgres DB to run admin query
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="parthpostgress89##",
            host="localhost",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if target db exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'calsevav2'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute("CREATE DATABASE calsevav2")
            print("Database 'calsevav2' created successfully.")
        else:
            print("Database 'calsevav2' already exists.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error during database creation check: {e}")

if __name__ == "__main__":
    # 1. Run database creation check
    create_database_if_not_exists()

    # 2. Setup Flask app context to drop/create tables
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:parthpostgress89##@localhost:5432/calsevav2'
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
