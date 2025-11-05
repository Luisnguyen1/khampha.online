"""
Database models and schema definitions for khappha.online
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


@dataclass
class User:
    """User model - Authenticated user tracking"""
    id: Optional[int] = None
    session_id: str = ""
    email: Optional[str] = None
    username: Optional[str] = None
    password_hash: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[str] = None
    travel_preferences: Optional[str] = None  # JSON string
    is_authenticated: bool = False
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary (exclude password)"""
        travel_prefs = None
        if self.travel_preferences:
            try:
                travel_prefs = json.loads(self.travel_preferences)
            except:
                pass
        
        return {
            'id': self.id,
            'session_id': self.session_id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'bio': self.bio,
            'phone': self.phone,
            'address': self.address,
            'avatar_url': self.avatar_url,
            'date_of_birth': self.date_of_birth,
            'travel_preferences': travel_prefs,
            'is_authenticated': self.is_authenticated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'metadata': self.metadata
        }


@dataclass
class Conversation:
    """Conversation model - Chat history"""
    id: Optional[int] = None
    session_id: str = ""
    conversation_session_id: Optional[str] = None  # Group conversations into sessions
    user_message: str = ""
    bot_response: str = ""
    message_type: str = "text"  # text, itinerary, recommendation
    plan_id: Optional[int] = None  # Link to travel plan if this conversation created a plan
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'conversation_session_id': self.conversation_session_id,
            'user_message': self.user_message,
            'bot_response': self.bot_response,
            'message_type': self.message_type,
            'plan_id': self.plan_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class TravelPlan:
    """Travel plan model - Itinerary storage"""
    id: Optional[int] = None
    session_id: str = ""
    user_id: Optional[int] = None
    conversation_id: Optional[int] = None  # Link to conversation that created this plan
    plan_name: Optional[str] = None
    destination: str = ""
    duration_days: int = 0
    budget: Optional[float] = None
    budget_currency: str = "VND"
    preferences: Optional[str] = None  # JSON array string
    itinerary: Dict[str, Any] = None  # JSON object
    total_cost: Optional[float] = None
    status: str = "draft"  # draft, active, archived, completed
    is_favorite: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'conversation_id': self.conversation_id,
            'plan_name': self.plan_name,
            'destination': self.destination,
            'duration_days': self.duration_days,
            'budget': self.budget,
            'budget_currency': self.budget_currency,
            'preferences': json.loads(self.preferences) if self.preferences else None,
            'itinerary': self.itinerary,
            'total_cost': self.total_cost,
            'status': self.status,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class SearchCache:
    """Search cache model - Cache search results"""
    id: Optional[int] = None
    query: str = ""
    results: Dict[str, Any] = None  # JSON object
    source: str = "duckduckgo"
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    hit_count: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'query': self.query,
            'results': self.results,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'hit_count': self.hit_count
        }


# SQL Schema
SCHEMA = """
-- Table 1: users - Quản lý người dùng với authentication
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    username TEXT UNIQUE,
    password_hash TEXT,
    full_name TEXT,
    bio TEXT,
    phone TEXT,
    address TEXT,
    avatar_url TEXT,
    date_of_birth TEXT,
    travel_preferences TEXT,
    is_authenticated INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- Table 2: conversations - Lịch sử chat
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    conversation_session_id TEXT,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    message_type TEXT DEFAULT 'text',
    plan_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES users(session_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES travel_plans(id) ON DELETE SET NULL
);

-- Table 3: travel_plans - Kế hoạch du lịch
CREATE TABLE IF NOT EXISTS travel_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_id INTEGER,
    conversation_id INTEGER,
    plan_name TEXT,
    destination TEXT NOT NULL,
    duration_days INTEGER NOT NULL,
    budget REAL,
    budget_currency TEXT DEFAULT 'VND',
    preferences TEXT,
    itinerary TEXT NOT NULL,
    total_cost REAL,
    status TEXT DEFAULT 'draft',
    is_favorite INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES users(session_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL
);

-- Table 4: search_cache - Cache kết quả tìm kiếm
CREATE TABLE IF NOT EXISTS search_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT UNIQUE NOT NULL,
    results TEXT NOT NULL,
    source TEXT DEFAULT 'duckduckgo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    hit_count INTEGER DEFAULT 0
);
-- Indexes để tối ưu performance
CREATE INDEX IF NOT EXISTS idx_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_session_id ON conversations(conversation_session_id);
CREATE INDEX IF NOT EXISTS idx_conv_plan ON conversations(plan_id);
CREATE INDEX IF NOT EXISTS idx_user_session ON users(session_id);
CREATE INDEX IF NOT EXISTS idx_plan_session ON travel_plans(session_id);
CREATE INDEX IF NOT EXISTS idx_plan_user ON travel_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_plan_conv ON travel_plans(conversation_id);
CREATE INDEX IF NOT EXISTS idx_plan_destination ON travel_plans(destination);
CREATE INDEX IF NOT EXISTS idx_plan_created ON travel_plans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cache_query ON search_cache(query);
CREATE INDEX IF NOT EXISTS idx_cache_expires ON search_cache(expires_at);

-- Trigger: Auto update timestamp
CREATE TRIGGER IF NOT EXISTS update_plan_timestamp 
AFTER UPDATE ON travel_plans
BEGIN
    UPDATE travel_plans SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
"""
