"""
SpiceWork Database Module
Handles database initialization and operations
"""
import sqlite3
import os
from typing import List, Dict, Optional, Any


class SpiceWorkDB:
    """SpiceWork Database handler for managing spice inventory"""
    
    def __init__(self, db_path: str = "spicework.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create spices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                origin TEXT,
                heat_level INTEGER,
                quantity REAL,
                unit TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_all_spices(self) -> List[Dict[str, Any]]:
        """
        Get all spices from the database
        
        Returns:
            List of spice dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM spices ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_spice_by_id(self, spice_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific spice by ID
        
        Args:
            spice_id: The spice ID
            
        Returns:
            Spice dictionary or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM spices WHERE id = ?", (spice_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def create_spice(self, name: str, origin: Optional[str] = None,
                     heat_level: Optional[int] = None, quantity: Optional[float] = None,
                     unit: Optional[str] = None, description: Optional[str] = None) -> int:
        """
        Create a new spice entry
        
        Args:
            name: Name of the spice
            origin: Origin of the spice
            heat_level: Heat level (0-10 scale)
            quantity: Quantity in stock
            unit: Unit of measurement
            description: Description of the spice
            
        Returns:
            ID of the created spice
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO spices (name, origin, heat_level, quantity, unit, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, origin, heat_level, quantity, unit, description))
        conn.commit()
        spice_id = cursor.lastrowid
        conn.close()
        
        return spice_id
    
    def update_spice(self, spice_id: int, name: Optional[str] = None,
                     origin: Optional[str] = None, heat_level: Optional[int] = None,
                     quantity: Optional[float] = None, unit: Optional[str] = None,
                     description: Optional[str] = None) -> bool:
        """
        Update an existing spice
        
        Args:
            spice_id: ID of the spice to update
            name: New name (optional)
            origin: New origin (optional)
            heat_level: New heat level (optional)
            quantity: New quantity (optional)
            unit: New unit (optional)
            description: New description (optional)
            
        Returns:
            True if updated, False if not found
        """
        # Get current spice
        current = self.get_spice_by_id(spice_id)
        if not current:
            return False
        
        # Update only provided fields
        updated_name = name if name is not None else current['name']
        updated_origin = origin if origin is not None else current['origin']
        updated_heat = heat_level if heat_level is not None else current['heat_level']
        updated_quantity = quantity if quantity is not None else current['quantity']
        updated_unit = unit if unit is not None else current['unit']
        updated_desc = description if description is not None else current['description']
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE spices 
            SET name = ?, origin = ?, heat_level = ?, quantity = ?, unit = ?, description = ?
            WHERE id = ?
        """, (updated_name, updated_origin, updated_heat, updated_quantity, 
              updated_unit, updated_desc, spice_id))
        conn.commit()
        conn.close()
        
        return True
    
    def delete_spice(self, spice_id: int) -> bool:
        """
        Delete a spice
        
        Args:
            spice_id: ID of the spice to delete
            
        Returns:
            True if deleted, False if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM spices WHERE id = ?", (spice_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def search_spices(self, query: str) -> List[Dict[str, Any]]:
        """
        Search spices by name or description
        
        Args:
            query: Search query
            
        Returns:
            List of matching spice dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM spices 
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY name
        """, (f"%{query}%", f"%{query}%"))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
