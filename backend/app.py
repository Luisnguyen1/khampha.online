"""
Main Flask application for khappha.online
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import uuid
import logging
from datetime import datetime

from config import config, Config
from database.db_manager import DatabaseManager
from agents.ai_agent import TravelAgent
from utils.auth import (
    validate_email, 
    validate_username, 
    validate_password, 
    sanitize_input,
    generate_session_token
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG
)

# Create logger
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])
Config.init_app(app)

# Set Flask app logger level
app.logger.setLevel(logging.INFO)

# Enable CORS
CORS(app)

# Initialize database
db = DatabaseManager(Config.DATABASE_PATH)

# Initialize AI Agent
ai_agent = TravelAgent(
    api_key=Config.GEMINI_API_KEY,
    model_name=Config.GEMINI_MODEL,
    temperature=Config.GEMINI_TEMPERATURE,
    max_tokens=Config.GEMINI_MAX_TOKENS
)

# ===== HELPER FUNCTIONS =====

def get_or_create_session():
    """Get or create user session"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        db.create_user(session['session_id'])
    else:
        db.update_user_activity(session['session_id'])
    
    return session['session_id']


def get_current_user():
    """Get current authenticated user from session"""
    user_id = session.get('user_id')
    if user_id:
        return db.get_user_by_id(user_id)
    return None


def require_auth(f):
    """Decorator to require authentication for API endpoints"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def require_login(f):
    """Decorator to require login for web pages - redirects to login"""
    from functools import wraps
    from flask import redirect, url_for, request as flask_request
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            # Store the original URL to redirect back after login
            session['next_url'] = flask_request.url
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


# ===== ROUTES =====

@app.route('/')
def index():
    """Landing page"""
    return render_template('landingpage.html', app_name=Config.APP_NAME)


@app.route('/chat')
@require_login
def chat_page():
    """Main chat interface - requires authentication"""
    user = get_current_user()
    return render_template('main_chat.html', app_name=Config.APP_NAME, user=user)


@app.route('/plans')
@require_login
def plans_page():
    """Plans list page - requires authentication"""
    user = get_current_user()
    return render_template('danh_sach_ke_hoach.html', app_name=Config.APP_NAME, user=user)


@app.route('/plans/<int:plan_id>')
@require_login
def plan_detail(plan_id):
    """Plan detail page - requires authentication"""
    user = get_current_user()
    plan = db.get_plan(plan_id)
    if not plan:
        return render_template('404.html'), 404
    # Verify user owns this plan
    if plan.user_id and plan.user_id != user.id:
        return render_template('404.html'), 404
    return render_template('chi_tiet_ke_hoach.html', app_name=Config.APP_NAME, plan=plan, user=user)


@app.route('/plans/<int:plan_id>/edit')
@require_login
def edit_plan(plan_id):
    """Edit plan page - requires authentication"""
    user = get_current_user()
    plan = db.get_plan(plan_id)
    if not plan:
        return render_template('404.html'), 404
    # Verify user owns this plan
    if plan.user_id and plan.user_id != user.id:
        return render_template('404.html'), 404
    return render_template('edit_ke_hoach.html', app_name=Config.APP_NAME, plan=plan, user=user)


@app.route('/login')
def login_page():
    """Login page"""
    # If already logged in, redirect to chat
    if get_current_user():
        return redirect(url_for('chat_page'))
    return render_template('login.html', app_name=Config.APP_NAME)


@app.route('/register')
def register_page():
    """Register page"""
    # If already logged in, redirect to chat
    if get_current_user():
        return redirect(url_for('chat_page'))
    return render_template('register.html', app_name=Config.APP_NAME)


# ===== API ROUTES =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    stats = db.get_stats()
@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint - Main AI interaction with mode support"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        # Get or create session
        session_id = get_or_create_session()
        
        # Get conversation session ID (for grouping messages)
        conversation_session_id = data.get('conversation_session_id')
        if not conversation_session_id:
            # Create new conversation session if not provided
            conversation_session_id = str(uuid.uuid4())
            app.logger.info(f"Created new conversation session: {conversation_session_id}")
        
        # Get conversation history
        conversations = db.get_conversations(session_id, limit=10)
        history = [
            {'user': conv.user_message, 'bot': conv.bot_response}
            for conv in conversations
        ]
        
        # Get current plan from request (for edit mode)
        current_plan = data.get('current_plan')
        
        # Use AI agent to process message
        agent_response = ai_agent.chat(
            user_message, 
            conversation_history=history,
            current_plan=current_plan
        )
        
        if not agent_response['success']:
            return jsonify({
                'success': False,
                'error': agent_response.get('message', 'AI processing error')
            }), 500
        
        bot_response = agent_response['message']
        
        # Auto-save plan if AI created one (as draft)
        plan_id = None
        if agent_response.get('has_plan') and agent_response.get('plan_data'):
            plan_data = agent_response['plan_data']
            
            # Get current user if authenticated
            current_user = get_current_user()
            user_id = current_user.id if current_user else None
            
            # Save plan as draft
            try:
                plan_id = db.save_plan(
                    session_id=session_id,
                    user_id=user_id,
                    conversation_id=None,  # Will update after saving conversation
                    plan_name=plan_data.get('plan_name'),
                    destination=plan_data.get('destination', ''),
                    duration_days=plan_data.get('duration_days', 0),
                    budget=plan_data.get('budget'),
                    preferences=plan_data.get('preferences'),
                    itinerary=plan_data.get('itinerary', {}),
                    status='draft'  # Auto-saved plans start as draft
                )
            except Exception as e:
                app.logger.error(f"Error auto-saving plan: {str(e)}")
        
        # Save conversation with plan_id link and conversation_session_id
        conversation_id = db.save_conversation(
            session_id, 
            user_message, 
            bot_response,
            plan_id=plan_id,
            conversation_session_id=conversation_session_id
        )
        
        # Update plan with conversation_id (circular reference)
        if plan_id and conversation_id:
            try:
                db.update_conversation_plan(conversation_id, plan_id)
                # Note: We can't easily update plan.conversation_id without another query
                # For now, conversation has plan_id which is the main link we need
            except Exception as e:
                app.logger.error(f"Error linking conversation to plan: {str(e)}")
        
        # Prepare response
        response_data = {
            'success': True,
            'response': bot_response,
            'session_id': session_id,
            'conversation_session_id': conversation_session_id,  # Return conversation session ID
            'has_plan': agent_response.get('has_plan', False),
            'mode': agent_response.get('mode', 'plan'),
            'plan_id': plan_id,  # Include plan_id in response
            'timestamp': datetime.now().isoformat()
        }
        
        # Include plan data if available
        if agent_response.get('has_plan') and agent_response.get('plan_data'):
            response_data['plan_data'] = agent_response['plan_data']
        
        return jsonify(response_data)
        
    except Exception as e:
        app.logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e) if Config.DEBUG else 'Something went wrong',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/save-plan', methods=['POST'])
def save_plan():
    """Save travel plan endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['destination', 'duration_days', 'itinerary']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        session_id = get_or_create_session()
        
        # Get current user if authenticated
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        
        # Get status (default to 'active' when user explicitly saves)
        status = data.get('status', 'active')
        
        # Get conversation_id if provided (for linking)
        conversation_id = data.get('conversation_id')
        
        # Save plan
        plan_id = db.save_plan(
            session_id=session_id,
            plan_name=data.get('plan_name'),
            destination=data['destination'],
            duration_days=data['duration_days'],
            budget=data.get('budget'),
            preferences=data.get('preferences'),
            itinerary=data['itinerary'],
            total_cost=data.get('total_cost'),
            user_id=user_id,
            conversation_id=conversation_id,
            status=status
        )
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'message': 'Kế hoạch đã được lưu thành công',
            'status': status
        })
        
    except Exception as e:
        app.logger.error(f"Error saving plan: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plans', methods=['GET'])
def get_plans():
    """Get all plans for current session or user"""
    try:
        session_id = get_or_create_session()
        
        # Get current user if authenticated
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        # Default to 'active' status (only show saved plans, not drafts)
        # Use ?status=all to get all, ?status=draft to get drafts only
        status = request.args.get('status', 'active')
        if status == 'all':
            status = None  # Get all statuses
        
        plans = db.get_plans(
            session_id=session_id if not user_id else None,
            user_id=user_id,
            limit=limit, 
            offset=offset, 
            status=status
        )
        
        return jsonify({
            'success': True,
            'plans': [plan.to_dict() for plan in plans],
            'total': len(plans),
            'limit': limit,
            'offset': offset,
            'authenticated': bool(current_user)
        })
        
    except Exception as e:
        app.logger.error(f"Error getting plans: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plans/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    """Get specific plan by ID"""
    try:
        plan = db.get_plan(plan_id)
        
        if not plan:
            return jsonify({
                'success': False,
                'error': 'Plan not found'
            }), 404
        
        return jsonify({
            'success': True,
            'plan': plan.to_dict()
        })
        
    except Exception as e:
        app.logger.error(f"Error getting plan: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plans/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    """Delete a plan"""
    try:
        success = db.delete_plan(plan_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Plan not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Plan deleted successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error deleting plan: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plans/<int:plan_id>/favorite', methods=['POST'])
def toggle_favorite(plan_id):
    """Toggle favorite status"""
    try:
        db.toggle_favorite(plan_id)
        
        return jsonify({
            'success': True,
            'message': 'Favorite status toggled'
        })
        
    except Exception as e:
        app.logger.error(f"Error toggling favorite: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plans/<int:plan_id>/status', methods=['PUT'])
def update_plan_status(plan_id):
    """Update plan status (draft -> active, etc.)"""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Status is required'
            }), 400
        
        status = data['status']
        valid_statuses = ['draft', 'active', 'archived', 'completed']
        
        if status not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        success = db.update_plan_status(plan_id, status)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Plan not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': f'Plan status updated to {status}'
        })
        
    except Exception as e:
        app.logger.error(f"Error updating plan status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get conversation history"""
    try:
        session_id = get_or_create_session()
        limit = request.args.get('limit', 50, type=int)
        
        conversations = db.get_conversations(session_id, limit=limit)
        
        return jsonify({
            'success': True,
            'conversations': [conv.to_dict() for conv in conversations],
            'total': len(conversations)
        })
        
    except Exception as e:
        app.logger.error(f"Error getting conversations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== CHAT SESSION MANAGEMENT =====

@app.route('/api/chat-sessions', methods=['GET'])
def get_chat_sessions():
    """Get all chat sessions grouped by date"""
    try:
        session_id = get_or_create_session()
        
        # Get current user if authenticated
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        
        # Get all conversations grouped by their first message
        sessions = db.get_chat_sessions(session_id=session_id, user_id=user_id)
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'total': len(sessions)
        })
        
    except Exception as e:
        app.logger.error(f"Error getting chat sessions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chat-sessions', methods=['POST'])
def create_chat_session():
    """Create a new chat session"""
    try:
        data = request.get_json() or {}
        session_id = get_or_create_session()
        
        # Get current user if authenticated
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        
        title = data.get('title', 'Chat mới')
        
        # Create a session marker (we'll use the first conversation ID)
        # For now, just return a new session object
        session_obj = {
            'id': str(uuid.uuid4()),
            'title': title,
            'created_at': datetime.now().isoformat(),
            'last_message_at': None,
            'message_count': 0
        }
        
        return jsonify({
            'success': True,
            'session': session_obj
        })
        
    except Exception as e:
        app.logger.error(f"Error creating chat session: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chat-sessions/<string:conversation_session_id>/messages', methods=['GET'])
def get_chat_session_messages(conversation_session_id):
    """Get messages for a specific chat session"""
    try:
        user_session_id = get_or_create_session()
        
        # Get current user if authenticated
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        
        # Get conversations for this conversation session
        conversations = db.get_conversations_by_session(user_session_id, conversation_session_id)
        
        # Convert to messages format with plan data
        messages = []
        for conv in conversations:
            msg_data = {
                'id': conv.id,
                'user_message': conv.user_message,
                'bot_response': conv.bot_response,
                'created_at': conv.created_at.isoformat() if conv.created_at else None,
                'plan_id': conv.plan_id
            }
            
            # If conversation has a plan, include plan data
            if conv.plan_id:
                plan = db.get_plan(conv.plan_id)
                if plan:
                    msg_data['plan_data'] = plan.to_dict()
            
            messages.append(msg_data)
        
        return jsonify({
            'success': True,
            'messages': messages,
            'total': len(messages)
        })
        
    except Exception as e:
        app.logger.error(f"Error getting chat session messages: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chat-sessions/<string:session_id>', methods=['PUT'])
def update_chat_session(session_id):
    """Update chat session (e.g., rename)"""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        # For now, just return success
        # In a real implementation, you'd update the session title in the database
        
        return jsonify({
            'success': True,
            'message': 'Session updated successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error updating chat session: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chat-sessions/<string:session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    """Delete a chat session"""
    try:
        user_session_id = get_or_create_session()
        
        # For now, just return success
        # In a real implementation, you'd delete conversations associated with this session
        # You might want to add a session_group_id field to conversations table
        
        return jsonify({
            'success': True,
            'message': 'Session deleted successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error deleting chat session: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== AUTHENTICATION ROUTES =====

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Vui lòng nhập {field}'
                }), 400
        
        # Sanitize inputs
        email = sanitize_input(data['email'].lower().strip(), max_length=100)
        username = sanitize_input(data['username'].strip(), max_length=20)
        password = data['password']
        full_name = sanitize_input(data.get('full_name', '').strip(), max_length=100) if data.get('full_name') else None
        
        # Validate email
        if not validate_email(email):
            return jsonify({
                'success': False,
                'error': 'Email không hợp lệ'
            }), 400
        
        # Validate username
        if not validate_username(username):
            return jsonify({
                'success': False,
                'error': 'Username phải từ 3-20 ký tự và chỉ chứa chữ, số, dấu gạch dưới'
            }), 400
        
        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Create session_id for new user
        session_id = generate_session_token()
        
        # Create user account
        user_id, error = db.create_user_account(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
            session_id=session_id
        )
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Store user_id in session
        session['user_id'] = user_id
        session['session_id'] = session_id
        session['is_authenticated'] = True
        
        user = db.get_user_by_id(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Đăng ký thành công',
            'user': user.to_dict() if user else None
        }), 201
        
    except Exception as e:
        app.logger.error(f"Error registering user: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Lỗi hệ thống, vui lòng thử lại'
        }), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Vui lòng nhập email và mật khẩu'
            }), 400
        
        email = sanitize_input(data['email'].lower().strip(), max_length=100)
        password = data['password']
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email và mật khẩu không được để trống'
            }), 400
        
        # Authenticate user
        user = db.authenticate_user(email, password)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Email hoặc mật khẩu không đúng'
            }), 401
        
        # Generate new session_id
        new_session_id = generate_session_token()
        
        # Update user session
        db.update_user_session(user.id, new_session_id)
        
        # Store in session
        session['user_id'] = user.id
        session['session_id'] = new_session_id
        session['is_authenticated'] = True
        
        return jsonify({
            'success': True,
            'message': 'Đăng nhập thành công',
            'user': user.to_dict()
        })
        
    except Exception as e:
        app.logger.error(f"Error logging in: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Lỗi hệ thống, vui lòng thử lại'
        }), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Đăng xuất thành công'
        })
        
    except Exception as e:
        app.logger.error(f"Error logging out: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Lỗi hệ thống'
        }), 500


@app.route('/api/auth/me', methods=['GET'])
def get_current_user_info():
    """Get current authenticated user info"""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({
                'success': False,
                'authenticated': False,
                'user': None
            })
        
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': user.to_dict()
        })
        
    except Exception as e:
        app.logger.error(f"Error getting current user: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Lỗi hệ thống'
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """File upload endpoint"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file extension
        if '.' not in file.filename:
            return jsonify({
                'success': False,
                'error': 'Invalid file'
            }), 400
        
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext not in Config.ALLOWED_EXTENSIONS:
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed: {", ".join(Config.ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = Config.UPLOAD_FOLDER / filename
        
        # Save file
        file.save(str(filepath))
        
        return jsonify({
            'success': True,
            'file_url': f'/uploads/{filename}',
            'file_name': file.filename,
            'file_size': os.path.getsize(filepath)
        })
        
    except Exception as e:
        app.logger.error(f"Error uploading file: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    app.logger.error(f"Internal error: {str(error)}")
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    return render_template('500.html'), 500


# ===== RUN APP =====

if __name__ == '__main__':
    print(f"🚀 Starting {Config.APP_NAME} v{Config.APP_VERSION}")
    print(f"🌍 Environment: {env}")
    print(f"🗄️  Database: {Config.DATABASE_PATH}")
    print(f"📂 Upload folder: {Config.UPLOAD_FOLDER}")
    print(f"\n✨ Server running on http://localhost:5000\n")
    
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=Config.DEBUG
    )
