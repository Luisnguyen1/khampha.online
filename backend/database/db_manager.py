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
import sys
from pathlib import Path

# Add backend to path for utils import
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from utils.auth import hash_password, verify_password


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
                return self._row_to_user(row)
            return None
    
    def create_user_account(self, email: str, username: str, password: str, 
                           full_name: Optional[str] = None, session_id: Optional[str] = None) -> tuple[Optional[int], Optional[str]]:
        """Create authenticated user account
        
        Returns:
            (user_id, error_message) - user_id if success, error_message if failed
        """
        try:
            # Hash password
            hashed_password, salt = hash_password(password)
            # Combine hash and salt with separator
            password_hash = f"{hashed_password}:{salt}"
            
            with self.get_connection() as conn:
                # Check if email or username already exists
                existing = conn.execute(
                    "SELECT email, username FROM users WHERE email = ? OR username = ?",
                    (email, username)
                ).fetchone()
                
                if existing:
                    if existing['email'] == email:
                        return None, "Email đã được sử dụng"
                    if existing['username'] == username:
                        return None, "Username đã được sử dụng"
                
                # Create user
                cursor = conn.execute(
                    """INSERT INTO users 
                    (email, username, password_hash, full_name, session_id, is_authenticated) 
                    VALUES (?, ?, ?, ?, ?, 1)""",
                    (email, username, password_hash, full_name, session_id)
                )
                return cursor.lastrowid, None
        except Exception as e:
            return None, f"Lỗi tạo tài khoản: {str(e)}"
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()
            
            if row:
                return self._row_to_user(row)
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()
            
            if row:
                return self._row_to_user(row)
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
            
            if row:
                return self._row_to_user(row)
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password
        
        Returns:
            User object if authenticated, None otherwise
        """
        user = self.get_user_by_email(email)
        if not user or not user.password_hash:
            return None
        
        # Split hash and salt
        try:
            hashed_password, salt = user.password_hash.split(':')
            if verify_password(password, hashed_password, salt):
                return user
        except ValueError:
            # Invalid password_hash format
            pass
        
        return None
    
    def update_user_session(self, user_id: int, session_id: str):
        """Update user's session_id"""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE users SET session_id = ?, last_active = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id, user_id)
            )
    
    def _row_to_user(self, row) -> User:
        """Convert database row to User object"""
        return User(
            id=row['id'],
            session_id=row['session_id'],
            email=row['email'] if 'email' in row.keys() else None,
            username=row['username'] if 'username' in row.keys() else None,
            password_hash=row['password_hash'] if 'password_hash' in row.keys() else None,
            full_name=row['full_name'] if 'full_name' in row.keys() else None,
            bio=row['bio'] if 'bio' in row.keys() else None,
            phone=row['phone'] if 'phone' in row.keys() else None,
            address=row['address'] if 'address' in row.keys() else None,
            avatar_url=row['avatar_url'] if 'avatar_url' in row.keys() else None,
            date_of_birth=row['date_of_birth'] if 'date_of_birth' in row.keys() else None,
            travel_preferences=row['travel_preferences'] if 'travel_preferences' in row.keys() else None,
            is_authenticated=bool(row['is_authenticated']) if 'is_authenticated' in row.keys() else False,
            created_at=datetime.fromisoformat(row['created_at']),
            last_active=datetime.fromisoformat(row['last_active']),
            metadata=json.loads(row['metadata']) if row['metadata'] else None
        )
    
    def update_user_activity(self, session_id: str):
        """Update user's last active timestamp"""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE session_id = ?",
                (session_id,)
            )
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """Update user profile information
        
        Args:
            user_id: User ID
            profile_data: Dictionary with profile fields (full_name, bio, phone, address, date_of_birth, travel_preferences)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            allowed_fields = ['full_name', 'bio', 'phone', 'address', 'date_of_birth', 'travel_preferences', 'username']
            update_fields = []
            values = []
            
            for field in allowed_fields:
                if field in profile_data:
                    update_fields.append(f"{field} = ?")
                    # Convert travel_preferences dict to JSON string if needed
                    if field == 'travel_preferences' and isinstance(profile_data[field], dict):
                        values.append(json.dumps(profile_data[field]))
                    else:
                        values.append(profile_data[field])
            
            if not update_fields:
                return False
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            
            with self.get_connection() as conn:
                conn.execute(query, tuple(values))
                return True
        except Exception as e:
            print(f"Error updating profile: {str(e)}")
            return False
    
    def update_user_avatar(self, user_id: int, avatar_url: str) -> bool:
        """Update user avatar URL"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "UPDATE users SET avatar_url = ? WHERE id = ?",
                    (avatar_url, user_id)
                )
                return True
        except Exception as e:
            print(f"Error updating avatar: {str(e)}")
            return False
    
    def change_user_password(self, user_id: int, current_password: str, new_password: str) -> tuple[bool, Optional[str]]:
        """Change user password
        
        Returns:
            (success, error_message)
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user or not user.password_hash:
                return False, "Người dùng không tồn tại"
            
            # Verify current password
            try:
                hashed_password, salt = user.password_hash.split(':')
                if not verify_password(current_password, hashed_password, salt):
                    return False, "Mật khẩu hiện tại không đúng"
            except ValueError:
                return False, "Lỗi xác thực mật khẩu"
            
            # Hash new password
            new_hashed, new_salt = hash_password(new_password)
            new_password_hash = f"{new_hashed}:{new_salt}"
            
            with self.get_connection() as conn:
                conn.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (new_password_hash, user_id)
                )
                return True, None
        except Exception as e:
            return False, f"Lỗi đổi mật khẩu: {str(e)}"
    
    def delete_user_account(self, user_id: int, password: str) -> tuple[bool, Optional[str]]:
        """Delete user account (requires password confirmation)
        
        Returns:
            (success, error_message)
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user or not user.password_hash:
                return False, "Người dùng không tồn tại"
            
            # Verify password
            try:
                hashed_password, salt = user.password_hash.split(':')
                if not verify_password(password, hashed_password, salt):
                    return False, "Mật khẩu không đúng"
            except ValueError:
                return False, "Lỗi xác thực mật khẩu"
            
            # Delete user (CASCADE will handle related data)
            with self.get_connection() as conn:
                conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
                return True, None
        except Exception as e:
            return False, f"Lỗi xóa tài khoản: {str(e)}"
    
    def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """Get user statistics for profile"""
        with self.get_connection() as conn:
            stats = {}
            
            # Get user's session_id
            user = self.get_user_by_id(user_id)
            if not user:
                return stats
            
            # Total plans
            stats['total_plans'] = conn.execute(
                "SELECT COUNT(*) FROM travel_plans WHERE user_id = ? OR session_id = ?",
                (user_id, user.session_id)
            ).fetchone()[0]
            
            # Completed plans
            stats['completed_plans'] = conn.execute(
                "SELECT COUNT(*) FROM travel_plans WHERE (user_id = ? OR session_id = ?) AND status = 'completed'",
                (user_id, user.session_id)
            ).fetchone()[0]
            
            # Unique destinations
            stats['destinations'] = conn.execute(
                "SELECT COUNT(DISTINCT destination) FROM travel_plans WHERE user_id = ? OR session_id = ?",
                (user_id, user.session_id)
            ).fetchone()[0]
            
            # Total days traveled
            result = conn.execute(
                "SELECT SUM(duration_days) FROM travel_plans WHERE (user_id = ? OR session_id = ?) AND status = 'completed'",
                (user_id, user.session_id)
            ).fetchone()
            stats['total_days'] = result[0] if result[0] else 0
            
            return stats
    
    # ===== CONVERSATION OPERATIONS =====
    
    def save_conversation(self, session_id: str, user_message: str, 
                         bot_response: str, message_type: str = "text",
                         plan_id: Optional[int] = None,
                         conversation_session_id: Optional[str] = None) -> int:
        """Save conversation to database
        
        Args:
            plan_id: ID of travel plan created in this conversation (if any)
            conversation_session_id: ID to group conversations into sessions
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO conversations 
                (session_id, conversation_session_id, user_message, bot_response, message_type, plan_id) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (session_id, conversation_session_id, user_message, bot_response, message_type, plan_id)
            )
            return cursor.lastrowid
    
    def update_conversation_plan(self, conversation_id: int, plan_id: int) -> bool:
        """Update conversation with plan_id after plan is created"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "UPDATE conversations SET plan_id = ? WHERE id = ?",
                (plan_id, conversation_id)
            )
            return cursor.rowcount > 0
    
    def get_conversations(self, session_id: Optional[str] = None, user_id: Optional[int] = None,
                         limit: int = 50) -> List[Conversation]:
        """Get conversation history for a session or user
        
        Args:
            session_id: Session ID (for non-authenticated users)
            user_id: User ID (for authenticated users) - NOT IMPLEMENTED YET
        """
        # TODO: Add user_id column to conversations table
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
                    conversation_session_id=row['conversation_session_id'] if 'conversation_session_id' in row.keys() else None,
                    user_message=row['user_message'],
                    bot_response=row['bot_response'],
                    message_type=row['message_type'],
                    plan_id=row['plan_id'] if 'plan_id' in row.keys() else None,
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                for row in reversed(rows)
            ]
    def get_chat_sessions(self, session_id: Optional[str] = None, user_id: Optional[int] = None) -> List[Dict]:
        """Get chat sessions grouped by conversation_session_id
        
        Returns a list of session summaries with:
        - id: conversation_session_id
        - title: first user message (truncated)
        - message_count: number of messages in this session
        - created_at: first message timestamp
        - last_message_at: last message timestamp
        """
        with self.get_connection() as conn:
            # Group by conversation_session_id
            rows = conn.execute(
                """
                SELECT 
                    conversation_session_id as id,
                    MIN(user_message) as first_message,
                    COUNT(*) as message_count,
                    MIN(created_at) as created_at,
                    MAX(created_at) as last_message_at
                FROM conversations 
                WHERE session_id = ? AND conversation_session_id IS NOT NULL
                GROUP BY conversation_session_id
                ORDER BY last_message_at DESC
                LIMIT 50
                """,
                (session_id,)
            ).fetchall()
            
            sessions = []
            for row in rows:
                # Create a short title from first message
                first_msg = row['first_message'] or 'Chat mới'
                # Remove @plan, @ask, @edit_plan prefixes
                for prefix in ['@plan ', '@ask ', '@edit_plan ']:
                    if first_msg.startswith(prefix):
                        first_msg = first_msg[len(prefix):]
                        break
                
                title = first_msg[:50] + ('...' if len(first_msg) > 50 else '')
                
                sessions.append({
                    'id': row['id'],
                    'title': title,
                    'message_count': row['message_count'],
                    'created_at': row['created_at'],
                    'last_message_at': row['last_message_at']
                })
            
            return sessions
    
    def get_conversations_by_session(self, session_id: str, conversation_session_id: str, limit: int = 100) -> List[Conversation]:
        """Get conversations for a specific conversation session
        
        Args:
            session_id: User session ID
            conversation_session_id: Conversation session ID to filter by
            limit: Maximum number of conversations to return
        """
        with self.get_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM conversations 
                WHERE session_id = ? AND conversation_session_id = ?
                ORDER BY created_at ASC 
                LIMIT ?""",
                (session_id, conversation_session_id, limit)
            ).fetchall()
            
            return [
                Conversation(
                    id=row['id'],
                    session_id=row['session_id'],
                    conversation_session_id=row['conversation_session_id'] if 'conversation_session_id' in row.keys() else None,
                    user_message=row['user_message'],
                    bot_response=row['bot_response'],
                    message_type=row['message_type'],
                    plan_id=row['plan_id'] if 'plan_id' in row.keys() else None,
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                for row in rows
            ]
    
    # ===== TRAVEL PLAN OPERATIONS =====
    
    def save_plan(self, session_id: str, destination: str, duration_days: int,
                  itinerary: Dict, budget: Optional[float] = None,
                  plan_name: Optional[str] = None, preferences: Optional[List[str]] = None,
                  total_cost: Optional[float] = None, user_id: Optional[int] = None,
                  conversation_id: Optional[int] = None, status: str = 'draft') -> int:
        """Save travel plan to database
        
        Args:
            status: Plan status (draft, active, archived, completed) - defaults to 'draft'
            user_id: User ID for authenticated users
            conversation_id: ID of conversation that created this plan
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO travel_plans 
                (session_id, user_id, conversation_id, plan_name, destination, duration_days, budget, 
                preferences, itinerary, total_cost, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    user_id,
                    conversation_id,
                    plan_name,
                    destination,
                    duration_days,
                    budget,
                    json.dumps(preferences) if preferences else None,
                    json.dumps(itinerary),
                    total_cost,
                    status
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
    
    def get_plans(self, session_id: Optional[str] = None, user_id: Optional[int] = None,
                  limit: int = 10, offset: int = 0, status: Optional[str] = None) -> List[TravelPlan]:
        """Get all plans for a session or user
        
        Args:
            session_id: Session ID (for non-authenticated users)
            user_id: User ID (for authenticated users)
            status: Filter by status (None = all statuses)
        """
        with self.get_connection() as conn:
            if user_id:
                if status:
                    rows = conn.execute(
                        """SELECT * FROM travel_plans 
                        WHERE user_id = ? AND status = ?
                        ORDER BY created_at DESC 
                        LIMIT ? OFFSET ?""",
                        (user_id, status, limit, offset)
                    ).fetchall()
                else:
                    rows = conn.execute(
                        """SELECT * FROM travel_plans 
                        WHERE user_id = ?
                        ORDER BY created_at DESC 
                        LIMIT ? OFFSET ?""",
                        (user_id, limit, offset)
                    ).fetchall()
            else:
                if status:
                    rows = conn.execute(
                        """SELECT * FROM travel_plans 
                        WHERE session_id = ? AND status = ?
                        ORDER BY created_at DESC 
                        LIMIT ? OFFSET ?""",
                        (session_id, status, limit, offset)
                    ).fetchall()
                else:
                    rows = conn.execute(
                        """SELECT * FROM travel_plans 
                        WHERE session_id = ?
                        ORDER BY created_at DESC 
                        LIMIT ? OFFSET ?""",
                        (session_id, limit, offset)
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
    
    def update_plan_status(self, plan_id: int, status: str) -> bool:
        """Update plan status (draft → active, etc.)"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "UPDATE travel_plans SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, plan_id)
            )
            return cursor.rowcount > 0
    
    def _row_to_travel_plan(self, row) -> TravelPlan:
        """Convert database row to TravelPlan object"""
        return TravelPlan(
            id=row['id'],
            session_id=row['session_id'],
            user_id=row['user_id'] if 'user_id' in row.keys() and row['user_id'] else None,
            conversation_id=row['conversation_id'] if 'conversation_id' in row.keys() and row['conversation_id'] else None,
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
