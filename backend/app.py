"""
Main Flask application for khappha.online
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response, stream_with_context
from flask_cors import CORS
from flask_session import Session
import os
import uuid
import json
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

# Initialize Flask-Session
Session(app)

# Set Flask app logger level
app.logger.setLevel(logging.DEBUG)

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


@app.route('/discover')
@require_login
def discover_page():
    """Discovery page - Tinder-style destination explorer"""
    user = get_current_user()
    return render_template('discover.html', app_name=Config.APP_NAME, user=user)


@app.route('/discover-debug')
def discover_debug():
    """Debug page for testing discovery feature without auth"""
    return render_template('discover-debug.html')


@app.route('/profile')
@require_login
def profile_page():
    """User profile page - requires authentication"""
    user = get_current_user()
    # Get user statistics
    stats = db.get_user_stats(user.id)
    return render_template('profile.html', app_name=Config.APP_NAME, user=user, stats=stats)


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
@app.route('/api/chat-stream', methods=['POST'])
def chat_stream():
    """Streaming chat endpoint using Server-Sent Events (SSE)"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing message'
        }), 400
    
    user_message = data['message'].strip()
    if not user_message:
        return jsonify({
            'success': False,
            'error': 'Empty message'
        }), 400
    
    # Get or create session
    session_id = get_or_create_session()
    
    # Get conversation session ID
    conversation_session_id = data.get('conversation_session_id')
    if not conversation_session_id:
        conversation_session_id = str(uuid.uuid4())
    
    def generate():
        """Generator function for streaming responses"""
        import json as json_module
        
        try:
            # Send thinking event
            yield f"event: thinking\ndata: {{\"status\": \"analyzing\"}}\n\n"
            
            # Get conversation history
            conversations = db.get_conversations(session_id, limit=10)
            history = [
                {'user': conv.user_message, 'bot': conv.bot_response}
                for conv in conversations
            ]
            
            # Get current plan if needed
            current_plan = data.get('current_plan')
            
            # Send thinking update
            yield f"event: thinking\ndata: {{\"status\": \"processing\"}}\n\n"
            
            # Use AI agent with streaming
            full_response = ""
            plan_data = None
            has_plan = False
            
            for chunk in ai_agent.chat_stream(
                user_message, 
                conversation_history=history,
                current_plan=current_plan
            ):
                # Stream each chunk
                if chunk.get('type') == 'text':
                    text = chunk.get('content', '')
                    full_response += text
                    yield f"event: message\ndata: {json_module.dumps({'text': text}, ensure_ascii=False)}\n\n"
                
                elif chunk.get('type') == 'plan':
                    has_plan = True
                    plan_data = chunk.get('content')
                    yield f"event: plan\ndata: {json_module.dumps(plan_data, ensure_ascii=False)}\n\n"
                
                elif chunk.get('type') == 'thinking':
                    status = chunk.get('content', 'processing')
                    yield f"event: thinking\ndata: {{\"status\": \"{status}\"}}\n\n"
            
            # Save plan if generated
            plan_id = None
            if has_plan and plan_data:
                try:
                    current_user = get_current_user()
                    user_id = current_user.id if current_user else None
                    
                    plan_id = db.save_plan(
                        session_id=session_id,
                        plan_name=plan_data.get('plan_name'),
                        destination=plan_data.get('destination'),
                        duration_days=plan_data.get('duration_days'),
                        budget=plan_data.get('budget'),
                        preferences=plan_data.get('preferences'),
                        start_date=plan_data.get('start_date'),
                        end_date=plan_data.get('end_date'),
                        itinerary=plan_data.get('itinerary'),
                        total_cost=plan_data.get('total_cost'),
                        user_id=user_id,
                        status='draft'
                    )
                    plan_data['id'] = plan_id
                except Exception as e:
                    app.logger.error(f"Error saving plan: {str(e)}")
            
            # Save conversation
            conversation_id = db.save_conversation(
                session_id,
                user_message,
                full_response,
                plan_id=plan_id,
                conversation_session_id=conversation_session_id
            )
            
            # Send completion event with metadata
            completion_data = {
                'conversation_id': conversation_id,
                'conversation_session_id': conversation_session_id,
                'has_plan': has_plan,
                'plan_id': plan_id
            }
            yield f"event: done\ndata: {json_module.dumps(completion_data, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            app.logger.error(f"Streaming error: {str(e)}")
            import json as json_module
            yield f"event: error\ndata: {json_module.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

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
        
        app.logger.info(f"📊 Session info: session_id={session_id}, conversation_session_id={conversation_session_id}")
        app.logger.info(f"📝 User message: '{user_message}'")
        app.logger.info(f"📦 Current plan provided: {current_plan is not None}")
        
        # If no current_plan provided but message suggests edit mode, 
        # try to get the latest plan from this conversation session
        if not current_plan and ('@edit' in user_message.lower() or 'sửa' in user_message.lower() or 'thay đổi' in user_message.lower()):
            app.logger.info("🔍 No current_plan provided, searching for latest plan in conversation session...")
            try:
                # Try to get latest plan from current conversation session
                if conversation_session_id:
                    # Get conversations from this session
                    session_conversations = db.get_conversations_by_session(session_id, conversation_session_id)
                    app.logger.info(f"   Found {len(session_conversations)} conversations in session {conversation_session_id}")
                    
                    # Find the most recent conversation with a plan
                    for conv in session_conversations:
                        if conv.plan_id:
                            app.logger.info(f"   Checking conversation with plan_id: {conv.plan_id}")
                            # Get the plan data
                            plan = db.get_plan(conv.plan_id)
                            if plan:
                                # Parse itinerary if it's a string
                                itinerary = plan.itinerary
                                if isinstance(itinerary, str):
                                    try:
                                        itinerary = json.loads(itinerary)
                                    except:
                                        itinerary = {}
                                
                                current_plan = {
                                    'id': plan.id,
                                    'plan_name': plan.plan_name,
                                    'destination': plan.destination,
                                    'duration_days': plan.duration_days,
                                    'budget': plan.budget,
                                    'preferences': plan.preferences,
                                    'itinerary': itinerary,
                                    'status': plan.status
                                }
                                app.logger.info(f"✅ Found plan: {plan.plan_name} (ID: {plan.id})")
                                break
                
                # If still no plan found, try to get the most recent draft plan for this session
                if not current_plan:
                    app.logger.info("   No plan found in conversation session, checking recent plans...")
                    recent_plans = db.get_plans(session_id, limit=5)
                    app.logger.info(f"   Found {len(recent_plans)} recent plans for session")
                    
                    if recent_plans:
                        # Get the most recent plan (first in list)
                        plan = recent_plans[0]
                        app.logger.info(f"   Latest plan: {plan.plan_name} (ID: {plan.id}, status: {plan.status})")
                        
                        # Parse itinerary if it's a string
                        itinerary = plan.itinerary
                        if isinstance(itinerary, str):
                            try:
                                itinerary = json.loads(itinerary)
                            except:
                                itinerary = {}
                        
                        current_plan = {
                            'id': plan.id,
                            'plan_name': plan.plan_name,
                            'destination': plan.destination,
                            'duration_days': plan.duration_days,
                            'budget': plan.budget,
                            'preferences': plan.preferences,
                            'itinerary': itinerary,
                            'status': plan.status
                        }
                        app.logger.info(f"✅ Using most recent plan: {plan.plan_name} (ID: {plan.id})")
                    else:
                        app.logger.warning("⚠️ No plans found for this session")
            except Exception as e:
                app.logger.error(f"❌ Error retrieving plan: {str(e)}")
                import traceback
                app.logger.error(traceback.format_exc())
        
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
                    start_date=plan_data.get('start_date'),
                    end_date=plan_data.get('end_date'),
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
        app.logger.info(f"💾 Saving plan - received data keys: {list(data.keys())}")
        
        # Validate required fields
        required_fields = ['destination', 'duration_days', 'itinerary']
        for field in required_fields:
            if field not in data:
                app.logger.error(f"❌ Missing required field: {field}")
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        session_id = get_or_create_session()
        app.logger.info(f"📝 Session ID: {session_id}")
        
        # Get current user if authenticated
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        app.logger.info(f"👤 User ID: {user_id}")
        
        # Get status (default to 'active' when user explicitly saves)
        status = data.get('status', 'active')
        
        # Get conversation_id if provided (for linking)
        conversation_id = data.get('conversation_id')
        
        app.logger.info(f"💾 Attempting to save: {data.get('plan_name')} - {data['destination']} - {data['duration_days']} days - Status: {status}")
        
        # Save plan
        plan_id = db.save_plan(
            session_id=session_id,
            plan_name=data.get('plan_name'),
            destination=data['destination'],
            duration_days=data['duration_days'],
            budget=data.get('budget'),
            preferences=data.get('preferences'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            itinerary=data['itinerary'],
            total_cost=data.get('total_cost'),
            user_id=user_id,
            conversation_id=conversation_id,
            status=status
        )
        
        app.logger.info(f"✅ Plan saved successfully with ID: {plan_id}")
        
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
        # Get all plans (draft + active + archived + completed)
        # Frontend will display tags based on status
        status = request.args.get('status', None)  # None = get all statuses
        
        app.logger.info(f"📋 Getting plans - Session: {session_id}, User: {user_id}, Status filter: {status or 'all'}, Limit: {limit}")
        
        plans = db.get_plans(
            session_id=session_id if not user_id else None,
            user_id=user_id,
            limit=limit, 
            offset=offset, 
            status=status
        )
        
        app.logger.info(f"✅ Found {len(plans)} plans")
        
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


@app.route('/api/plans/<int:plan_id>', methods=['PUT'])
def update_plan(plan_id):
    """Update a plan"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Get the plan to verify it exists
        plan = db.get_plan(plan_id)
        if not plan:
            return jsonify({
                'success': False,
                'error': 'Plan not found'
            }), 404
        
        # Verify user owns this plan
        current_user = get_current_user()
        if plan.user_id and current_user and plan.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        # Update plan fields
        update_fields = {}
        
        if 'plan_name' in data:
            update_fields['plan_name'] = data['plan_name']
        if 'destination' in data:
            update_fields['destination'] = data['destination']
        if 'duration_days' in data:
            update_fields['duration_days'] = data['duration_days']
        if 'budget' in data:
            update_fields['budget'] = data['budget']
        if 'preferences' in data:
            update_fields['preferences'] = data['preferences']
        if 'start_date' in data:
            update_fields['start_date'] = data['start_date']
        if 'end_date' in data:
            update_fields['end_date'] = data['end_date']
        if 'itinerary' in data:
            update_fields['itinerary'] = data['itinerary']
        if 'status' in data:
            update_fields['status'] = data['status']
        
        # Update in database
        success = db.update_plan(plan_id, update_fields)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to update plan'
            }), 500
        
        # Get updated plan
        updated_plan = db.get_plan(plan_id)
        
        return jsonify({
            'success': True,
            'message': 'Plan updated successfully',
            'plan': updated_plan.to_dict()
        })
        
    except Exception as e:
        app.logger.error(f"Error updating plan: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
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


@app.route('/api/plans/<int:plan_id>/search-hotels', methods=['POST'])
def search_hotels(plan_id):
    """Search hotels for a plan"""
    try:
        # Get plan to extract destination
        plan = db.get_plan(plan_id)
        if not plan:
            return jsonify({
                'success': False,
                'error': 'Plan not found'
            }), 404
        
        # Get request data
        data = request.get_json()
        checkin_date = data.get('checkin_date')
        checkout_date = data.get('checkout_date')
        
        if not checkin_date or not checkout_date:
            return jsonify({
                'success': False,
                'error': 'Check-in and check-out dates are required'
            }), 400
        
        # Import HotelSearcher
        from utils.hotel_search import HotelSearcher
        from config import Config
        
        # Initialize hotel searcher
        searcher = HotelSearcher(api_key=Config.RAPIDAPI_KEY)
        
        # Search hotels - plan is TravelPlan object, use .destination not ['destination']
        hotels = searcher.search_and_display(
            city_name=plan.destination,
            checkin_date=checkin_date,
            checkout_date=checkout_date,
            rooms=1,
            adults=2,
            max_results=10
        )
        
        # Format hotels for frontend
        formatted_hotels = []
        for hotel in hotels:
            formatted_hotels.append({
                'hotel_id': hotel.get('hotel_id'),
                'name': hotel.get('name'),
                'address': hotel.get('address'),
                'star_rating': hotel.get('star_rating'),
                'review_score': hotel.get('rating'),
                'review_count': hotel.get('review_count'),
                'price': hotel.get('price_per_night'),
                'price_total': hotel.get('price_total'),
                'currency': hotel.get('currency'),
                'image_url': hotel.get('images', [''])[0] if hotel.get('images') else None,
                'latitude': hotel.get('latitude'),
                'longitude': hotel.get('longitude')
            })
        
        return jsonify({
            'success': True,
            'hotels': formatted_hotels
        })
        
    except Exception as e:
        app.logger.error(f"Error searching hotels: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plans/<int:plan_id>/hotel', methods=['POST'])
def save_plan_hotel(plan_id):
    """Save selected hotel for a plan"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Hotel data is required'
            }), 400
        
        # Calculate number of nights
        from datetime import datetime
        checkin = datetime.strptime(data.get('checkin_date'), '%Y-%m-%d')
        checkout = datetime.strptime(data.get('checkout_date'), '%Y-%m-%d')
        nights = (checkout - checkin).days
        
        # Calculate total price
        price_per_night = data.get('price', 0)
        total_price = price_per_night * nights if price_per_night else data.get('price_total', 0)
        
        # Debug log
        app.logger.info(f"Hotel data received: price={price_per_night}, price_total={data.get('price_total')}, nights={nights}, calculated_total={total_price}")
        
        # Prepare hotel data
        hotel_data = {
            'hotel_id': data.get('hotel_id'),
            'name': data.get('name'),
            'address': data.get('address'),
            'city': data.get('city'),
            'country': data.get('country', 'Việt Nam'),
            'star_rating': data.get('star_rating'),
            'review_score': data.get('review_score'),
            'review_count': data.get('review_count'),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'image_url': data.get('image_url'),
            'images': [data.get('image_url')] if data.get('image_url') else data.get('images', []),
            'price_per_night': price_per_night,
            'total_price': total_price,
            'currency': data.get('currency', 'VND'),
            'checkin_date': data.get('checkin_date'),
            'checkout_date': data.get('checkout_date'),
            'number_of_nights': nights,
            'number_of_rooms': data.get('number_of_rooms', 1),
            'number_of_guests': data.get('number_of_guests', 2)
        }
        
        # Save to database
        success = db.save_plan_hotel(plan_id, hotel_data)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to save hotel'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Hotel saved successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error saving hotel: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plans/<int:plan_id>/hotel', methods=['GET'])
def get_plan_hotel(plan_id):
    """Get selected hotel for a plan"""
    try:
        hotel = db.get_plan_hotel(plan_id)
        
        return jsonify({
            'success': True,
            'hotel': hotel
        })
        
    except Exception as e:
        app.logger.error(f"Error getting hotel: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plans/<int:plan_id>/hotel', methods=['DELETE'])
def delete_plan_hotel(plan_id):
    """Delete selected hotel from a plan"""
    try:
        success = db.delete_plan_hotel(plan_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'No hotel found for this plan'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Hotel deleted successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error deleting hotel: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== FLIGHT ROUTES =====

@app.route('/api/plans/<int:plan_id>/search-flights', methods=['POST'])
def search_flights(plan_id):
    """Search flights for a plan"""
    try:
        # Get plan to extract origin and destination
        plan = db.get_plan(plan_id)
        if not plan:
            return jsonify({
                'success': False,
                'error': 'Plan not found'
            }), 404
        
        # Get request data
        data = request.get_json()
        origin = data.get('origin')  # City name or airport code
        destination = data.get('destination', plan.destination)
        departure_date = data.get('departure_date')
        return_date = data.get('return_date')  # Optional for one-way
        adults = data.get('adults', 1)
        children = data.get('children', 0)
        infants = data.get('infants', 0)
        cabin_class = data.get('cabin_class', 'Economy')
        
        if not origin or not destination or not departure_date:
            return jsonify({
                'success': False,
                'error': 'Origin, destination, and departure date are required'
            }), 400
        
        # Import FlightSearcher
        from utils.flight_search import AgodaFlightSearchAPI
        from config import Config
        
        # Initialize flight searcher
        searcher = AgodaFlightSearchAPI(api_key=Config.RAPIDAPI_KEY)
        
        # Get airport codes
        origin_code = searcher.get_airport_code(origin)
        dest_code = searcher.get_airport_code(destination)
        
        if not origin_code or not dest_code:
            return jsonify({
                'success': False,
                'error': 'Could not find airport codes for specified locations'
            }), 400
        
        # Search flights
        if return_date:
            # Round trip
            flights = searcher.search_round_trip_flight(
                origin=origin_code,
                destination=dest_code,
                departure_date=departure_date,
                return_date=return_date,
                adults=adults,
                children=children,
                infants=infants
            )
        else:
            # One way
            flights = searcher.search_one_way_flight(
                origin=origin_code,
                destination=dest_code,
                departure_date=departure_date,
                adults=adults,
                children=children,
                infants=infants
            )
        
        if not flights:
            return jsonify({
                'success': True,
                'flights': [],
                'message': 'No flights found for the specified criteria'
            })
        
        # Extract and format flight information
        formatted_flights = searcher.extract_flight_info(flights)
        
        return jsonify({
            'success': True,
            'flights': formatted_flights,
            'search_params': {
                'origin': origin,
                'origin_code': origin_code,
                'destination': destination,
                'destination_code': dest_code,
                'departure_date': departure_date,
                'return_date': return_date,
                'passengers': {
                    'adults': adults,
                    'children': children,
                    'infants': infants
                },
                'cabin_class': cabin_class
            }
        })
        
    except Exception as e:
        app.logger.error(f"Error searching flights: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plans/<int:plan_id>/flight', methods=['POST'])
def save_plan_flight(plan_id):
    """Save selected flight for a plan"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Flight data is required'
            }), 400
        
        # Determine flight type (outbound or return)
        flight_type = data.get('flight_type', 'outbound')
        
        # Prepare flight data
        flight_data = {
            'bundle_key': data.get('bundle_key', ''),
            'carrier_name': data.get('carrier_name', ''),
            'carrier_code': data.get('carrier_code', ''),
            'carrier_logo': data.get('carrier_logo'),
            'flight_number': data.get('flight_number', ''),
            'origin_airport': data.get('origin_airport', ''),
            'origin_code': data.get('origin_code', ''),
            'origin_city': data.get('origin_city'),
            'destination_airport': data.get('destination_airport', ''),
            'destination_code': data.get('destination_code', ''),
            'destination_city': data.get('destination_city'),
            'departure_time': data.get('departure_time', ''),
            'arrival_time': data.get('arrival_time', ''),
            'duration': data.get('duration', 0),
            'stops': data.get('stops', 0),
            'cabin_class': data.get('cabin_class', 'Economy'),
            'price_vnd': data.get('price_vnd', 0),
            'currency': data.get('currency', 'VND'),
            'adults': data.get('adults', 1),
            'children': data.get('children', 0),
            'infants': data.get('infants', 0),
            'overnight_flight': data.get('overnight_flight', False),
            'layover_info': data.get('layover_info', []),
            'segments': data.get('segments', [])
        }
        
        # Save to database
        success = db.save_plan_flight(plan_id, flight_data, flight_type)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to save flight'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Flight saved successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error saving flight: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plans/<int:plan_id>/flights', methods=['GET'])
def get_plan_flights(plan_id):
    """Get all selected flights for a plan"""
    try:
        flights = db.get_plan_flights(plan_id)
        
        return jsonify({
            'success': True,
            'flights': flights
        })
        
    except Exception as e:
        app.logger.error(f"Error getting flights: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plans/<int:plan_id>/flight/<int:flight_id>', methods=['DELETE'])
def delete_plan_flight(plan_id, flight_id):
    """Delete a selected flight from a plan"""
    try:
        success = db.delete_plan_flight(plan_id, flight_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Flight not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Flight deleted successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error deleting flight: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/flights/search-location', methods=['POST'])
def search_flight_location():
    """Search for airport codes by city name"""
    try:
        data = request.get_json()
        city_name = data.get('city_name')
        
        if not city_name:
            return jsonify({
                'success': False,
                'error': 'City name is required'
            }), 400
        
        from utils.flight_search import AgodaFlightSearchAPI
        from config import Config
        
        searcher = AgodaFlightSearchAPI(api_key=Config.RAPIDAPI_KEY)
        airport_code = searcher.get_airport_code(city_name)
        
        if not airport_code:
            return jsonify({
                'success': False,
                'error': f'No airport found for {city_name}'
            }), 404
        
        return jsonify({
            'success': True,
            'city_name': city_name,
            'airport_code': airport_code
        })
        
    except Exception as e:
        app.logger.error(f"Error searching location: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plans/<int:plan_id>/confirm', methods=['POST'])

def confirm_plan(plan_id):
    """Confirm a plan and update its status to confirmed"""
    try:
        success = db.update_plan_status(plan_id, 'confirmed')
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Plan not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Plan confirmed successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error confirming plan: {str(e)}")
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
        session.permanent = True  # Make session permanent
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
        session.permanent = True  # Make session permanent
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
        app.logger.error(f"Error getting current user info: {str(e)}")
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


# ===== PROFILE API ROUTES =====

@app.route('/api/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get current user profile"""
    try:
        user = get_current_user()
        stats = db.get_user_stats(user.id)
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'stats': stats
        })
    except Exception as e:
        app.logger.error(f"Error getting profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Lỗi hệ thống'
        }), 500


@app.route('/api/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dữ liệu không hợp lệ'
            }), 400
        
        # Sanitize inputs
        profile_data = {}
        if 'full_name' in data:
            profile_data['full_name'] = sanitize_input(data['full_name'], max_length=100)
        if 'username' in data:
            username = sanitize_input(data['username'], max_length=20)
            if not validate_username(username):
                return jsonify({
                    'success': False,
                    'error': 'Username không hợp lệ'
                }), 400
            profile_data['username'] = username
        if 'bio' in data:
            profile_data['bio'] = sanitize_input(data['bio'], max_length=500)
        if 'phone' in data:
            profile_data['phone'] = sanitize_input(data['phone'], max_length=20)
        if 'address' in data:
            profile_data['address'] = sanitize_input(data['address'], max_length=200)
        if 'date_of_birth' in data:
            profile_data['date_of_birth'] = data['date_of_birth']
        if 'travel_preferences' in data:
            profile_data['travel_preferences'] = data['travel_preferences']
        
        success = db.update_user_profile(user.id, profile_data)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Không thể cập nhật thông tin'
            }), 500
        
        # Get updated user
        updated_user = db.get_user_by_id(user.id)
        
        return jsonify({
            'success': True,
            'message': 'Cập nhật thông tin thành công',
            'user': updated_user.to_dict()
        })
        
    except Exception as e:
        app.logger.error(f"Error updating profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Lỗi hệ thống'
        }), 500


@app.route('/api/profile/avatar', methods=['POST'])
@require_auth
def upload_avatar():
    """Upload user avatar"""
    try:
        user = get_current_user()
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Không có file được chọn'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Vui lòng chọn file'
            }), 400
        
        # Check if image
        if '.' not in file.filename:
            return jsonify({
                'success': False,
                'error': 'File không hợp lệ'
            }), 400
        
        ext = file.filename.rsplit('.', 1)[1].lower()
        allowed_image_exts = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
        
        if ext not in allowed_image_exts:
            return jsonify({
                'success': False,
                'error': f'Chỉ hỗ trợ: {", ".join(allowed_image_exts)}'
            }), 400
        
        # Generate unique filename
        filename = f"avatar_{user.id}_{uuid.uuid4()}.{ext}"
        filepath = Config.UPLOAD_FOLDER / filename
        
        # Save file
        file.save(str(filepath))
        avatar_url = f'/static/uploads/{filename}'
        
        # Update user avatar in database
        success = db.update_user_avatar(user.id, avatar_url)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Không thể cập nhật ảnh đại diện'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Cập nhật ảnh đại diện thành công',
            'avatar_url': avatar_url
        })
        
    except Exception as e:
        app.logger.error(f"Error uploading avatar: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Lỗi hệ thống'
        }), 500


@app.route('/api/user/location', methods=['POST'])
def save_user_location():
    """Save user's geolocation"""
    try:
        data = request.get_json()
        
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                'success': False,
                'error': 'Thiếu thông tin vị trí'
            }), 400
        
        latitude = data['latitude']
        longitude = data['longitude']
        
        # Validate coordinates
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                raise ValueError('Invalid coordinates')
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Tọa độ không hợp lệ'
            }), 400
        
        # Get or create session
        session_id = get_or_create_session()
        
        # Update location in database
        success = db.update_user_location(session_id, latitude, longitude)
        
        if success:
            app.logger.info(f"📍 Location saved for session {session_id}: ({latitude}, {longitude})")
            return jsonify({
                'success': True,
                'message': 'Đã lưu vị trí thành công'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Không thể lưu vị trí'
            }), 500
        
    except Exception as e:
        app.logger.error(f"Error saving location: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Lỗi hệ thống'
        }), 500


@app.route('/api/profile/password', methods=['PUT'])
@require_auth
def change_password():
    """Change user password"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data or 'current_password' not in data or 'new_password' not in data:
            return jsonify({
                'success': False,
                'error': 'Vui lòng nhập đầy đủ thông tin'
            }), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Validate new password
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        success, error = db.change_user_password(user.id, current_password, new_password)
        
        if not success:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Đổi mật khẩu thành công'
        })
        
    except Exception as e:
        app.logger.error(f"Error changing password: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Lỗi hệ thống'
        }), 500


@app.route('/api/profile', methods=['DELETE'])
@require_auth
def delete_account():
    """Delete user account"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Vui lòng xác nhận mật khẩu'
            }), 400
        
        password = data['password']
        
        success, error = db.delete_user_account(user.id, password)
        
        if not success:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Clear session
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Xóa tài khoản thành công'
        })
        
    except Exception as e:
        app.logger.error(f"Error deleting account: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Lỗi hệ thống'
        }), 500


# ===== CONFIG ENDPOINTS =====

@app.route('/api/config/google-maps-key', methods=['GET'])
def get_google_maps_key():
    """Get Google Maps API key"""
    try:
        return jsonify({
            'success': True,
            'api_key': Config.GOOGLE_MAPS_API_KEY
        })
    except Exception as e:
        app.logger.error(f"Error getting Google Maps key: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Lỗi hệ thống'
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
