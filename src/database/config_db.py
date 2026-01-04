"""Base de datos SQLite para configuración del asistente"""

import sqlite3
import os
from typing import Optional, Dict, Any
from pathlib import Path


class AssistantConfigDB:
    """Gestiona la configuración del asistente en SQLite"""
    
    # Valores por defecto
    DEFAULT_CONFIG = {
        "sarcasm_level": 3,  # 0-10
        "humor_level": 5,    # 0-10
        "response_length": "medium",  # "short", "medium", "long"
        "formality": "informal",  # "formal", "informal", "very_formal"
        "treatment": "tú",  # "tú", "usted", "señor", "señora"
    }
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa la base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos. Si es None, usa ~/.assistant_config.db
        """
        if db_path is None:
            home = Path.home()
            db_path = str(home / ".assistant_config.db")
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa la base de datos y crea las tablas si no existen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Crear tabla de configuración
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assistant_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insertar valores por defecto si no existen
        for key, value in self.DEFAULT_CONFIG.items():
            cursor.execute(
                "INSERT OR IGNORE INTO assistant_config (key, value) VALUES (?, ?)",
                (key, str(value))
            )
        
        conn.commit()
        conn.close()
    
    def get_config(self) -> Dict[str, Any]:
        """
        Obtiene toda la configuración del asistente
        
        Returns:
            Diccionario con la configuración
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT key, value FROM assistant_config")
        rows = cursor.fetchall()
        
        conn.close()
        
        config = {}
        for key, value in rows:
            # Convertir valores numéricos
            if value.isdigit():
                config[key] = int(value)
            elif value.replace('.', '', 1).isdigit():
                config[key] = float(value)
            else:
                config[key] = value
        
        # Asegurar que todos los valores por defecto estén presentes
        for key, default_value in self.DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = default_value
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración específico
        
        Args:
            key: Clave de configuración
            default: Valor por defecto si no existe
            
        Returns:
            Valor de la configuración
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM assistant_config WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row is None:
            return default if default is not None else self.DEFAULT_CONFIG.get(key)
        
        value = row[0]
        # Convertir valores numéricos
        if value.isdigit():
            return int(value)
        elif value.replace('.', '', 1).isdigit():
            return float(value)
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """
        Establece un valor de configuración
        
        Args:
            key: Clave de configuración
            value: Valor a establecer
            
        Returns:
            True si se actualizó correctamente
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO assistant_config (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
            """,
            (key, str(value))
        )
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def set_multiple(self, config: Dict[str, Any]) -> bool:
        """
        Establece múltiples valores de configuración
        
        Args:
            config: Diccionario con las configuraciones a establecer
            
        Returns:
            True si se actualizaron correctamente
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for key, value in config.items():
            cursor.execute(
                """
                INSERT INTO assistant_config (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, str(value))
            )
        
        conn.commit()
        conn.close()
        
        return True
    
    def reset_to_defaults(self) -> bool:
        """
        Restablece la configuración a los valores por defecto
        
        Returns:
            True si se restableció correctamente
        """
        return self.set_multiple(self.DEFAULT_CONFIG)

