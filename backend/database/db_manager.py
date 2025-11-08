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
    
    def update_user_location(self, session_id: str, latitude: float, longitude: float) -> bool:
        """Update user's geolocation
        
        Args:
            session_id: User session ID
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """UPDATE users 
                    SET latitude = ?, longitude = ?, location_updated_at = CURRENT_TIMESTAMP 
                    WHERE session_id = ?""",
                    (latitude, longitude, session_id)
                )
                return True
        except Exception as e:
            print(f"Error updating user location: {str(e)}")
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
    
    # ===== HOTEL OPERATIONS =====
    
    def save_plan_hotel(self, plan_id: int, hotel_data: Dict[str, Any]) -> bool:
        """Save or update hotel for a plan (UPSERT based on UNIQUE constraint)"""
        try:
            with self.get_connection() as conn:
                # Check if plan exists
                plan = conn.execute("SELECT id FROM travel_plans WHERE id = ?", (plan_id,)).fetchone()
                if not plan:
                    return False
                
                # Process address - convert dict to string if needed
                address = hotel_data.get('address')
                if isinstance(address, dict):
                    # Extract readable address from dict structure
                    parts = []
                    if address.get('area', {}).get('name'):
                        parts.append(address['area']['name'])
                    if address.get('city', {}).get('name'):
                        parts.append(address['city']['name'])
                    if address.get('country', {}).get('name'):
                        parts.append(address['country']['name'])
                    address = ', '.join(parts) if parts else None
                
                # Extract city from address dict or use provided city
                city = hotel_data.get('city')
                if not city and isinstance(hotel_data.get('address'), dict):
                    city = hotel_data.get('address', {}).get('city', {}).get('name')
                
                # Extract hotel data and save to database
                conn.execute("""
                    INSERT INTO plan_hotels (
                        plan_id, hotel_id, hotel_name, address, city,
                        latitude, longitude, star_rating, guest_rating, review_count,
                        checkin_date, checkout_date, nights, rooms, guests,
                        room_type, price_per_night, total_price, currency,
                        discount_percent, original_price, amenities, images,
                        cancellation_policy, is_refundable, hotel_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(plan_id) DO UPDATE SET
                        hotel_id = excluded.hotel_id,
                        hotel_name = excluded.hotel_name,
                        address = excluded.address,
                        city = excluded.city,
                        latitude = excluded.latitude,
                        longitude = excluded.longitude,
                        star_rating = excluded.star_rating,
                        guest_rating = excluded.guest_rating,
                        review_count = excluded.review_count,
                        checkin_date = excluded.checkin_date,
                        checkout_date = excluded.checkout_date,
                        nights = excluded.nights,
                        rooms = excluded.rooms,
                        guests = excluded.guests,
                        room_type = excluded.room_type,
                        price_per_night = excluded.price_per_night,
                        total_price = excluded.total_price,
                        currency = excluded.currency,
                        discount_percent = excluded.discount_percent,
                        original_price = excluded.original_price,
                        amenities = excluded.amenities,
                        images = excluded.images,
                        cancellation_policy = excluded.cancellation_policy,
                        is_refundable = excluded.is_refundable,
                        hotel_data = excluded.hotel_data,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    plan_id,
                    hotel_data.get('hotel_id'),
                    hotel_data.get('name'),
                    address,  # Use processed address string
                    city,  # Use extracted city
                    hotel_data.get('latitude'),
                    hotel_data.get('longitude'),
                    hotel_data.get('star_rating'),
                    hotel_data.get('review_score'),  # guest_rating in DB
                    hotel_data.get('review_count'),
                    hotel_data.get('checkin_date'),
                    hotel_data.get('checkout_date'),
                    hotel_data.get('number_of_nights'),  # nights in DB
                    hotel_data.get('number_of_rooms', 1),  # rooms in DB
                    hotel_data.get('number_of_guests', 2),  # guests in DB
                    hotel_data.get('room_type'),
                    hotel_data.get('price_per_night') or hotel_data.get('price'),
                    hotel_data.get('total_price'),
                    hotel_data.get('currency', 'VND'),
                    hotel_data.get('discount_percent'),
                    hotel_data.get('original_price'),
                    json.dumps(hotel_data.get('amenities')) if hotel_data.get('amenities') else None,
                    json.dumps(hotel_data.get('images')) if hotel_data.get('images') else None,
                    hotel_data.get('cancellation_policy'),
                    1 if hotel_data.get('is_refundable') else 0,
                    json.dumps(hotel_data)  # Store full hotel data as JSON
                ))
                return True
        except Exception as e:
            print(f"Error saving hotel: {e}")
            return False
    
    def get_plan_hotel(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """Get hotel data for a plan"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM plan_hotels WHERE plan_id = ?",
                (plan_id,)
            ).fetchone()
            
            if row:
                images = json.loads(row['images']) if row['images'] else []
                return {
                    'id': row['id'],
                    'plan_id': row['plan_id'],
                    'hotel_id': row['hotel_id'],
                    'name': row['hotel_name'],
                    'address': row['address'],
                    'city': row['city'],
                    'star_rating': row['star_rating'],
                    'review_score': row['guest_rating'],
                    'review_count': row['review_count'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'amenities': json.loads(row['amenities']) if row['amenities'] else [],
                    'images': images,
                    'image_url': images[0] if images else None,
                    'room_type': row['room_type'],
                    'price_per_night': row['price_per_night'],
                    'currency': row['currency'],
                    'total_price': row['total_price'],
                    'discount_percent': row['discount_percent'],
                    'original_price': row['original_price'],
                    'checkin_date': row['checkin_date'],
                    'checkout_date': row['checkout_date'],
                    'number_of_nights': row['nights'],
                    'number_of_rooms': row['rooms'],
                    'number_of_guests': row['guests'],
                    'cancellation_policy': row['cancellation_policy'],
                    'is_refundable': bool(row['is_refundable']),
                    'selected_at': row['selected_at'],
                    'updated_at': row['updated_at']
                }
            return None
    
    def delete_plan_hotel(self, plan_id: int) -> bool:
        """Delete hotel from a plan"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM plan_hotels WHERE plan_id = ?",
                    (plan_id,)
                )
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting hotel: {e}")
            return False
    
    def update_plan_dates(self, plan_id: int, new_start_date: str, new_duration_days: int) -> bool:
        """Update plan dates and auto-adjust hotel dates
        
        Args:
            plan_id: ID of the plan
            new_start_date: New start date (YYYY-MM-DD or DD/MM/YYYY)
            new_duration_days: New duration in days
            
        Returns:
            bool: Success status
        """
        try:
            from datetime import datetime, timedelta
            
            # Parse start date (handle both formats)
            if '/' in new_start_date:
                # DD/MM/YYYY format
                day, month, year = new_start_date.split('/')
                start_date = datetime(int(year), int(month), int(day))
            else:
                # YYYY-MM-DD format
                start_date = datetime.strptime(new_start_date, '%Y-%m-%d')
            
            # Calculate end date
            end_date = start_date + timedelta(days=new_duration_days)
            
            # Format dates
            start_date_str = start_date.strftime('%d/%m/%Y')
            end_date_str = end_date.strftime('%d/%m/%Y')
            
            with self.get_connection() as conn:
                # Update travel_plans
                conn.execute("""
                    UPDATE travel_plans 
                    SET start_date = ?, 
                        end_date = ?, 
                        duration_days = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (start_date_str, end_date_str, new_duration_days, plan_id))
                
                # Update plan_hotels if exists
                hotel = conn.execute(
                    "SELECT id FROM plan_hotels WHERE plan_id = ?",
                    (plan_id,)
                ).fetchone()
                
                if hotel:
                    # Update hotel dates to match plan dates
                    checkout = start_date + timedelta(days=new_duration_days)
                    nights = new_duration_days
                    
                    # Recalculate total price
                    price_row = conn.execute(
                        "SELECT price_per_night FROM plan_hotels WHERE plan_id = ?",
                        (plan_id,)
                    ).fetchone()
                    
                    if price_row and price_row['price_per_night']:
                        new_total_price = price_row['price_per_night'] * nights
                        
                        conn.execute("""
                            UPDATE plan_hotels 
                            SET checkin_date = ?,
                                checkout_date = ?,
                                nights = ?,
                                total_price = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE plan_id = ?
                        """, (
                            start_date.strftime('%Y-%m-%d'),
                            checkout.strftime('%Y-%m-%d'),
                            nights,
                            new_total_price,
                            plan_id
                        ))
                    else:
                        conn.execute("""
                            UPDATE plan_hotels 
                            SET checkin_date = ?,
                                checkout_date = ?,
                                nights = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE plan_id = ?
                        """, (
                            start_date.strftime('%Y-%m-%d'),
                            checkout.strftime('%Y-%m-%d'),
                            nights,
                            plan_id
                        ))
                
                return True
        except Exception as e:
            print(f"Error updating plan dates: {e}")
            return False
    
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
