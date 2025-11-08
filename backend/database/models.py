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
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_updated_at: Optional[datetime] = None
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
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_updated_at': self.location_updated_at.isoformat() if self.location_updated_at else None,
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
    start_date: Optional[str] = None  # ISO format: YYYY-MM-DD
    end_date: Optional[str] = None  # ISO format: YYYY-MM-DD
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
            'start_date': self.start_date,
            'end_date': self.end_date,
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


@dataclass
class PlanHotel:
    """Plan hotel model - Selected hotel for a travel plan"""
    id: Optional[int] = None
    plan_id: int = 0
    hotel_id: str = ""
    hotel_name: str = ""
    address: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    star_rating: Optional[int] = None
    guest_rating: Optional[float] = None
    review_count: Optional[int] = None
    checkin_date: str = ""  # ISO format: YYYY-MM-DD
    checkout_date: str = ""  # ISO format: YYYY-MM-DD
    nights: int = 0
    rooms: int = 1
    guests: int = 2
    room_type: Optional[str] = None
    price_per_night: Optional[float] = None
    total_price: float = 0
    currency: str = "VND"
    discount_percent: Optional[float] = None
    original_price: Optional[float] = None
    amenities: Optional[str] = None  # JSON array string
    images: Optional[str] = None  # JSON array string
    cancellation_policy: Optional[str] = None
    is_refundable: bool = False
    hotel_data: Optional[str] = None  # Full JSON data from API
    selected_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'hotel_id': self.hotel_id,
            'hotel_name': self.hotel_name,
            'address': self.address,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'star_rating': self.star_rating,
            'guest_rating': self.guest_rating,
            'review_count': self.review_count,
            'checkin_date': self.checkin_date,
            'checkout_date': self.checkout_date,
            'nights': self.nights,
            'rooms': self.rooms,
            'guests': self.guests,
            'room_type': self.room_type,
            'price_per_night': self.price_per_night,
            'total_price': self.total_price,
            'currency': self.currency,
            'discount_percent': self.discount_percent,
            'original_price': self.original_price,
            'amenities': json.loads(self.amenities) if self.amenities else None,
            'images': json.loads(self.images) if self.images else None,
            'cancellation_policy': self.cancellation_policy,
            'is_refundable': self.is_refundable,
            'hotel_data': json.loads(self.hotel_data) if self.hotel_data else None,
            'selected_at': self.selected_at.isoformat() if self.selected_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class PlanFlight:
    """Plan flight model - Selected flight for a travel plan"""
    id: Optional[int] = None
    plan_id: int = 0
    flight_type: str = "outbound"  # outbound (chiều đi) hoặc inbound (chiều về)
    bundle_key: str = ""
    carrier_name: str = ""
    carrier_code: str = ""
    carrier_logo: Optional[str] = None
    flight_number: str = ""
    origin_airport: str = ""
    origin_code: str = ""
    origin_city: Optional[str] = None
    destination_airport: str = ""
    destination_code: str = ""
    destination_city: Optional[str] = None
    departure_time: str = ""
    arrival_time: str = ""
    duration: int = 0
    stops: int = 0
    cabin_class: str = "Economy"
    price: float = 0
    currency: str = "VND"
    adults: int = 1
    children: int = 0
    infants: int = 0
    is_overnight: bool = False
    layover_info: Optional[str] = None
    segments: Optional[str] = None
    flight_data: Optional[str] = None
    selected_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'flight_type': self.flight_type,
            'bundle_key': self.bundle_key,
            'carrier_name': self.carrier_name,
            'carrier_code': self.carrier_code,
            'carrier_logo': self.carrier_logo,
            'flight_number': self.flight_number,
            'origin_airport': self.origin_airport,
            'origin_code': self.origin_code,
            'origin_city': self.origin_city,
            'destination_airport': self.destination_airport,
            'destination_code': self.destination_code,
            'destination_city': self.destination_city,
            'departure_time': self.departure_time,
            'arrival_time': self.arrival_time,
            'duration': self.duration,
            'stops': self.stops,
            'cabin_class': self.cabin_class,
            'price': self.price,
            'currency': self.currency,
            'adults': self.adults,
            'children': self.children,
            'infants': self.infants,
            'is_overnight': self.is_overnight,
            'layover_info': json.loads(self.layover_info) if self.layover_info else [],
            'segments': json.loads(self.segments) if self.segments else [],
            'flight_data': json.loads(self.flight_data) if self.flight_data else None,
            'selected_at': self.selected_at.isoformat() if self.selected_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
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
    latitude REAL,
    longitude REAL,
    location_updated_at TIMESTAMP,
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
    start_date TEXT,
    end_date TEXT,
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
