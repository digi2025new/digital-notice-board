import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def create_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notices (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            file_path TEXT,
            file_type TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'password') ON CONFLICT DO NOTHING")

    conn.commit()
    conn.close()

    print("Database setup complete!")

if __name__ == "__main__":
    create_db()
