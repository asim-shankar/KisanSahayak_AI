import sqlite3
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

class FarmerDatabase:
    def __init__(self, db_path: str = "farmers.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Farmers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT UNIQUE,
                name TEXT,
                location TEXT,
                crops TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Queries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id INTEGER,
                query TEXT,
                response TEXT,
                query_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farmer_id) REFERENCES farmers (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_farmer(self, phone: str, name: str, location: str, crops: List[str]) -> int:
        """Register a new farmer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        crops_json = json.dumps(crops)
        cursor.execute('''
            INSERT OR REPLACE INTO farmers (phone_number, name, location, crops)
            VALUES (?, ?, ?, ?)
        ''', (phone, name, location, crops_json))
        
        farmer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return farmer_id
    
    def get_farmer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Get farmer details by phone number"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM farmers WHERE phone_number = ?', (phone,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0], 
                'phone': row[1], 
                'name': row[2], 
                'location': row[3], 
                'crops': json.loads(row[4]),
                'created_at': row[5]
            }
        return None
    
    def save_query(self, farmer_id: int, query: str, response: str, query_type: str):
        """Save farmer query and response"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO queries (farmer_id, query, response, query_type)
            VALUES (?, ?, ?, ?)
        ''', (farmer_id, query, response, query_type))
        
        conn.commit()
        conn.close()
