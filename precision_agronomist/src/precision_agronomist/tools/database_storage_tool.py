from crewai.tools import BaseTool
from typing import Type, List, Dict
from pydantic import BaseModel, Field, PrivateAttr
import json
from pathlib import Path
from datetime import datetime
import sqlite3


class DetectionStorageInput(BaseModel):
    """Input schema for storing detection results."""
    session_id: str = Field(..., description="Unique session ID for this detection run")
    image_path: str = Field(..., description="Path to the analyzed image")
    detections: str = Field(..., description="JSON string of detection results")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Detection timestamp")


class DatabaseStorageTool(BaseTool):
    name: str = "Disease Detection Storage"
    description: str = (
        "Stores plant disease detection results in a SQLite database for historical "
        "tracking and trend analysis. Each detection is logged with timestamp, image info, "
        "and detected diseases for later pattern analysis."
    )
    args_schema: Type[BaseModel] = DetectionStorageInput
    
    # Use PrivateAttr for instance attributes that aren't model fields
    _db_path: Path = PrivateAttr(default=None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._db_path = Path("precision_agronomist/disease_tracking.db")
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        
        # Create detections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                image_path TEXT NOT NULL,
                disease_class TEXT NOT NULL,
                confidence REAL NOT NULL,
                bbox_x1 REAL,
                bbox_y1 REAL,
                bbox_x2 REAL,
                bbox_y2 REAL,
                severity TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                total_images INTEGER,
                total_detections INTEGER,
                unique_diseases INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON detections(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_disease_class 
            ON detections(disease_class)
        """)
        
        conn.commit()
        conn.close()

    def _run(
        self, 
        session_id: str,
        image_path: str,
        detections: str,
        timestamp: str = None
    ) -> str:
        """
        Store detection results in database
        
        Args:
            session_id: Unique session identifier
            image_path: Path to analyzed image
            detections: JSON string with detection results
            timestamp: Detection timestamp (auto-generated if not provided)
            
        Returns:
            Status message with storage confirmation
        """
        try:
            if timestamp is None:
                timestamp = datetime.now().isoformat()
            
            # Parse detections JSON
            detection_data = json.loads(detections)
            
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            # Store each detection
            stored_count = 0
            for detection in detection_data.get('detections', []):
                # Determine severity based on confidence and disease type
                severity = self._calculate_severity(
                    detection['class'],
                    detection['confidence']
                )
                
                cursor.execute("""
                    INSERT INTO detections (
                        session_id, timestamp, image_path, disease_class,
                        confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2, severity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    timestamp,
                    image_path,
                    detection['class'],
                    detection['confidence'],
                    detection['bbox'].get('x1'),
                    detection['bbox'].get('y1'),
                    detection['bbox'].get('x2'),
                    detection['bbox'].get('y2'),
                    severity
                ))
                stored_count += 1
            
            conn.commit()
            conn.close()
            
            return (
                f"✅ Stored {stored_count} detection(s) in database\n"
                f"📊 Session: {session_id}\n"
                f"🖼️ Image: {Path(image_path).name}\n"
                f"💾 Database: {self._db_path}"
            )
            
        except Exception as e:
            return f"⚠️ Failed to store detections: {str(e)}"
    
    def _calculate_severity(self, disease_class: str, confidence: float) -> str:
        """Calculate severity based on disease type and confidence"""
        # Diseases get severity, healthy plants are low
        if 'healthy' in disease_class.lower():
            return 'low'
        elif confidence >= 0.9:
            return 'high'
        elif confidence >= 0.7:
            return 'moderate'
        else:
            return 'low'

