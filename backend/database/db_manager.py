"""
Database manager for khappha.online
Handles all CRUD operations with SQLite
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
from contextlib import contextmanager

from .models import User, Conversation, TravelPlan, SearchCache, SCHEMA


class DatabaseManager:
    """Database manager class"""
    
    def __init__(self, db_path: Path):
        """Initialize database manager"""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database with schema"""
        with self.get_connection() as conn:
            conn.executescript(SCHEMA)
    
    # ===== USER OPERATIONS =====
    
    def create_user(self, session_id: str, metadata: Optional[Dict] = None) -> int:
        """Create new user session"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (session_id, metadata) VALUES (?, ?)",
                (session_id, json.dumps(metadata) if metadata else None)
            )
            return cursor.lastrowid
    
    def get_user(self, session_id: str) -> Optional[User]:
        """Get user by session_id"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE session_id = ?",
                (session_id,)
            ).fetchone()
            
            if row:
                return User(
                    id=row['id'],
                    session_id=row['session_id'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_active=datetime.fromisoformat(row['last_active']),
                    metadata=json.loads(row['metadata']) if row['metadata'] else None
                )
            return None
    
    def update_user_activity(self, session_id: str):
        """Update user's last active timestamp"""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE session_id = ?",
                (session_id,)
            )
    
    # ===== CONVERSATION OPERATIONS =====
    
    def save_conversation(self, session_id: str, user_message: str, 
                         bot_response: str, message_type: str = "text") -> int:
        """Save conversation to database"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO conversations 
                (session_id, user_message, bot_response, message_type) 
                VALUES (?, ?, ?, ?)""",
                (session_id, user_message, bot_response, message_type)
            )
            return cursor.lastrowid
    
    def get_conversations(self, session_id: str, limit: int = 50) -> List[Conversation]:
        """Get conversation history for a session"""
        with self.get_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM conversations 
                WHERE session_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?""",
                (session_id, limit)
            ).fetchall()
            
            return [
                Conversation(
                    id=row['id'],
                    session_id=row['session_id'],
                    user_message=row['user_message'],
                    bot_response=row['bot_response'],
                    message_type=row['message_type'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                for row in reversed(rows)
            ]
    
    # ===== TRAVEL PLAN OPERATIONS =====
    
    def save_plan(self, session_id: str, destination: str, duration_days: int,
                  itinerary: Dict, budget: Optional[float] = None,
                  plan_name: Optional[str] = None, preferences: Optional[List[str]] = None,
                  total_cost: Optional[float] = None) -> int:
        """Save travel plan to database"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO travel_plans 
                (session_id, plan_name, destination, duration_days, budget, 
                preferences, itinerary, total_cost) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    plan_name,
                    destination,
                    duration_days,
                    budget,
                    json.dumps(preferences) if preferences else None,
                    json.dumps(itinerary),
                    total_cost
                )
            )
            return cursor.lastrowid
    
    def get_plan(self, plan_id: int) -> Optional[TravelPlan]:
        """Get travel plan by ID"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM travel_plans WHERE id = ?",
                (plan_id,)
            ).fetchone()
            
            if row:
                return self._row_to_travel_plan(row)
            return None
    
    def get_plans(self, session_id: str, limit: int = 10, 
                  offset: int = 0, status: str = "active") -> List[TravelPlan]:
        """Get all plans for a session"""
        with self.get_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM travel_plans 
                WHERE session_id = ? AND status = ?
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?""",
                (session_id, status, limit, offset)
            ).fetchall()
            
            return [self._row_to_travel_plan(row) for row in rows]
    
    def get_plans_by_destination(self, destination: str, limit: int = 3) -> List[TravelPlan]:
        """Get similar plans by destination"""
        with self.get_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM travel_plans 
                WHERE destination LIKE ? AND status = 'active'
                ORDER BY created_at DESC 
                LIMIT ?""",
                (f'%{destination}%', limit)
            ).fetchall()
            
            return [self._row_to_travel_plan(row) for row in rows]
    
    def delete_plan(self, plan_id: int) -> bool:
        """Delete a travel plan"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM travel_plans WHERE id = ?",
                (plan_id,)
            )
            return cursor.rowcount > 0
    
    def toggle_favorite(self, plan_id: int) -> bool:
        """Toggle favorite status of a plan"""
        with self.get_connection() as conn:
            conn.execute(
                """UPDATE travel_plans 
                SET is_favorite = NOT is_favorite 
                WHERE id = ?""",
                (plan_id,)
            )
            return True
    
    def _row_to_travel_plan(self, row) -> TravelPlan:
        """Convert database row to TravelPlan object"""
        return TravelPlan(
            id=row['id'],
            session_id=row['session_id'],
            plan_name=row['plan_name'],
            destination=row['destination'],
            duration_days=row['duration_days'],
            budget=row['budget'],
            budget_currency=row['budget_currency'],
            preferences=row['preferences'],
            itinerary=json.loads(row['itinerary']),
            total_cost=row['total_cost'],
            status=row['status'],
            is_favorite=bool(row['is_favorite']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    # ===== SEARCH CACHE OPERATIONS =====
    
    def save_search_cache(self, query: str, results: Dict, 
                         ttl_hours: int = 24, source: str = "duckduckgo") -> int:
        """Save search results to cache"""
        expires_at = datetime.now() + timedelta(hours=ttl_hours)
        
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT OR REPLACE INTO search_cache 
                (query, results, source, expires_at) 
                VALUES (?, ?, ?, ?)""",
                (query, json.dumps(results), source, expires_at.isoformat())
            )
            return cursor.lastrowid
    
    def get_search_cache(self, query: str) -> Optional[SearchCache]:
        """Get cached search results"""
        with self.get_connection() as conn:
            row = conn.execute(
                """SELECT * FROM search_cache 
                WHERE query = ? AND expires_at > CURRENT_TIMESTAMP""",
                (query,)
            ).fetchone()
            
            if row:
                # Increment hit count
                conn.execute(
                    "UPDATE search_cache SET hit_count = hit_count + 1 WHERE id = ?",
                    (row['id'],)
                )
                
                return SearchCache(
                    id=row['id'],
                    query=row['query'],
                    results=json.loads(row['results']),
                    source=row['source'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    expires_at=datetime.fromisoformat(row['expires_at']),
                    hit_count=row['hit_count'] + 1
                )
            return None
    
    def clear_expired_cache(self):
        """Clear expired cache entries"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM search_cache WHERE expires_at < CURRENT_TIMESTAMP"
            )
            return cursor.rowcount
    
    # ===== STATISTICS =====
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        with self.get_connection() as conn:
            stats = {}
            stats['total_users'] = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            stats['total_conversations'] = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
            stats['total_plans'] = conn.execute("SELECT COUNT(*) FROM travel_plans").fetchone()[0]
            stats['active_plans'] = conn.execute(
                "SELECT COUNT(*) FROM travel_plans WHERE status = 'active'"
            ).fetchone()[0]
            stats['cache_entries'] = conn.execute("SELECT COUNT(*) FROM search_cache").fetchone()[0]
            return stats
