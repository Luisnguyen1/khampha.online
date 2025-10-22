"""
Main Flask application for khappha.online
"""
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import uuid
import logging
from datetime import datetime

from config import config, Config
from database.db_manager import DatabaseManager
from agents.ai_agent import TravelAgent

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


# ===== ROUTES =====

@app.route('/')
def index():
    """Landing page"""
    return render_template('landingpage.html', app_name=Config.APP_NAME)


@app.route('/chat')
def chat_page():
    """Main chat interface"""
    return render_template('main_chat.html', app_name=Config.APP_NAME)


@app.route('/plans')
def plans_page():
    """Plans list page"""
    return render_template('danh_sach_ke_hoach.html', app_name=Config.APP_NAME)


@app.route('/plans/<int:plan_id>')
def plan_detail(plan_id):
    """Plan detail page"""
    plan = db.get_plan(plan_id)
    if not plan:
        return render_template('404.html'), 404
    return render_template('chi_tiet_ke_hoach.html', app_name=Config.APP_NAME, plan=plan)


@app.route('/plans/<int:plan_id>/edit')
def edit_plan(plan_id):
    """Edit plan page"""
    plan = db.get_plan(plan_id)
    if not plan:
        return render_template('404.html'), 404
    return render_template('edit_ke_hoach.html', app_name=Config.APP_NAME, plan=plan)


# ===== API ROUTES =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    stats = db.get_stats()
@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint - Main AI interaction"""
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
        
        # Get conversation history
        conversations = db.get_conversations(session_id, limit=10)
        history = [
            {'user': conv.user_message, 'bot': conv.bot_response}
            for conv in conversations
        ]
        
        # Use AI agent to process message
        agent_response = ai_agent.chat(user_message, conversation_history=history)
        
        if not agent_response['success']:
            return jsonify({
                'success': False,
                'error': agent_response.get('message', 'AI processing error')
            }), 500
        
        bot_response = agent_response['message']
        
        # Save conversation
        db.save_conversation(session_id, user_message, bot_response)
        
        # Prepare response
        response_data = {
            'success': True,
            'response': bot_response,
            'session_id': session_id,
            'has_plan': agent_response.get('has_plan', False),
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
        
        # Save plan
        plan_id = db.save_plan(
            session_id=session_id,
            plan_name=data.get('plan_name'),
            destination=data['destination'],
            duration_days=data['duration_days'],
            budget=data.get('budget'),
            preferences=data.get('preferences'),
            itinerary=data['itinerary'],
            total_cost=data.get('total_cost')
        )
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'message': 'Plan saved successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error saving plan: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plans', methods=['GET'])
def get_plans():
    """Get all plans for current session"""
    try:
        session_id = get_or_create_session()
        
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        status = request.args.get('status', 'active')
        
        plans = db.get_plans(session_id, limit=limit, offset=offset, status=status)
        
        return jsonify({
            'success': True,
            'plans': [plan.to_dict() for plan in plans],
            'total': len(plans),
            'limit': limit,
            'offset': offset
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
