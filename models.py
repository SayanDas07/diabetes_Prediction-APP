from flask_login import UserMixin
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                high_bp INTEGER NOT NULL,
                gen_hlth INTEGER NOT NULL,
                bmi REAL NOT NULL,
                age INTEGER NOT NULL,
                high_chol INTEGER NOT NULL,
                chol_check INTEGER NOT NULL,
                income INTEGER NOT NULL,
                phys_hlth INTEGER NOT NULL,
                prediction INTEGER NOT NULL,
                probability REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, email, password):
        """Create a new user in the database"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            password_hash = generate_password_hash(password)
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return User(user_data[0], user_data[1], user_data[2])
        return None
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, username, email, password_hash FROM users WHERE username = ? OR email = ?',
            (username, username)
        )
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data[3], password):
            return User(user_data[0], user_data[1], user_data[2])
        return None
    
    def save_prediction(self, user_id, features, prediction, probability):
        """Save prediction to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO predictions 
            (user_id, high_bp, gen_hlth, bmi, age, high_chol, chol_check, income, phys_hlth, prediction, probability)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, *features, prediction, probability))
        conn.commit()
        conn.close()
    
    def get_user_predictions(self, user_id):
        """Get all predictions for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM predictions 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        predictions = cursor.fetchall()
        conn.close()
        return predictions
