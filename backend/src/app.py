from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, datetime
import bcrypt
import os
import json
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../../frontend')

# Configure CORS with support for credentials and all origins in development
CORS(app, 
     resources={
         r"/api/*": {
             "origins": "*",  # Allow all origins in development
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }
     })

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dating_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)

# JWT Configuration
app.config['JWT_IDENTITY_CLAIM'] = 'sub'  # Use 'sub' as the identity claim
app.config['JWT_ALGORITHM'] = 'HS256'

jwt = JWTManager(app)

@jwt.user_identity_loader
def user_identity_lookup(user):
    # Return just the user ID as a string
    return str(user.id)

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    # Get the user ID from the token and convert to int for database query
    user_id = int(jwt_data['sub'])
    return User.query.get(user_id)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    profile = db.relationship('Profile', backref='user', uselist=False)
    settings = db.relationship('Settings', backref='user', uselist=False)
    sent_matches = db.relationship('Match', foreign_keys='Match.user_id', backref='user')
    received_matches = db.relationship('Match', foreign_keys='Match.matched_user_id', backref='matched_user')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver')

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bio = db.Column(db.Text)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    location = db.Column(db.String(100))
    profile_picture = db.Column(db.String(200))
    _interests = db.Column('interests', db.Text)

    @property
    def interests(self):
        return json.loads(self._interests) if self._interests else []

    @interests.setter
    def interests(self, value):
        self._interests = json.dumps(value) if value else '[]'

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    profile_visibility = db.Column(db.String(20), default='public')
    online_status = db.Column(db.Boolean, default=True)
    match_notifications = db.Column(db.Boolean, default=True)
    message_notifications = db.Column(db.Boolean, default=True)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    matched_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

# Routes
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/safety')
def serve_safety():
    return send_from_directory(app.static_folder, 'safety.html')

@app.route('/support')
def serve_support():
    return send_from_directory(app.static_folder, 'support.html')

@app.route('/about')
def serve_about():
    return send_from_directory(app.static_folder, 'about.html')

@app.route('/careers')
def serve_careers():
    return send_from_directory(app.static_folder, 'careers.html')

@app.route('/press')
def serve_press():
    return send_from_directory(app.static_folder, 'press.html')

@app.route('/api/careers/apply', methods=['POST'])
def upload_resume():
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        position = request.form.get('position')
        message = request.form.get('message')
        resume = request.files.get('resume')
        
        # Validate required fields
        if not all([name, email, position, resume]):
            return jsonify({'message': 'Missing required fields'}), 400
            
        # Validate file type
        allowed_extensions = {'pdf', 'doc', 'docx'}
        if '.' in resume.filename and resume.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'message': 'Invalid file type. Please upload a PDF, DOC, or DOCX file.'}), 400
            
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate secure filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{name.replace(' ', '_')}_{timestamp}_{secure_filename(resume.filename)}"
        filepath = os.path.join(upload_dir, filename)
        
        # Save the file
        resume.save(filepath)
        
        # In a production environment, you would typically:
        # 1. Save the application to a database
        # 2. Send a confirmation email to the applicant
        # 3. Notify the HR/recruitment team
        
        # Log the application (in production, you'd want to save this to a database)
        app.logger.info(f"New job application received: {name} - {email} - {position}")
        
        return jsonify({
            'message': 'Application submitted successfully!',
            'filename': filename
        }), 200
        
    except Exception as e:
        app.logger.error(f'Error processing application: {str(e)}')
        return jsonify({'message': 'An error occurred while processing your application'}), 500

@app.route('/privacy')
def serve_privacy():
    return send_from_directory(app.static_folder, 'privacy.html')

@app.route('/terms')
def serve_terms():
    return send_from_directory(app.static_folder, 'terms.html')

@app.route('/api/user/data', methods=['GET'])
@jwt_required()
def download_user_data():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    user_data = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'birth_date': user.birth_date.isoformat() if user.birth_date else None,
        'profile': {
            'bio': user.profile.bio if user.profile and hasattr(user, 'profile') else '',
            'age': user.profile.age if user.profile and hasattr(user, 'profile') else None,
            'gender': user.profile.gender if user.profile and hasattr(user, 'profile') else '',
            'location': user.profile.location if user.profile and hasattr(user, 'profile') else '',
            'interests': user.profile.interests if user.profile and hasattr(user, 'profile') else [],
            'profile_picture': user.profile.profile_picture if user.profile and hasattr(user, 'profile') else ''
        },
        'settings': {
            'profile_visibility': user.settings.profile_visibility if user.settings and hasattr(user, 'settings') else 'public',
            'online_status': user.settings.online_status if user.settings and hasattr(user, 'settings') else True,
            'match_notifications': user.settings.match_notifications if user.settings and hasattr(user, 'settings') else True,
            'message_notifications': user.settings.message_notifications if user.settings and hasattr(user, 'settings') else True
        },
        'account_created': user.created_at.isoformat() if hasattr(user, 'created_at') else None,
        'last_updated': user.updated_at.isoformat() if hasattr(user, 'updated_at') else None
    }

    # Create a response with the user data as a downloadable JSON file
    response = make_response(jsonify(user_data), 200)
    response.headers['Content-Disposition'] = f'attachment; filename=blendup_user_{user.id}_data.json'
    return response

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Input validation
    required_fields = ['name', 'email', 'password', 'birth_date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate email format
    if '@' not in data['email'] or '.' not in data['email']:
        return jsonify({'error': 'Invalid email format'}), 400
        
    # Check password strength
    if len(data['password']) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400
    
    # Hash password
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    # Create new user
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password.decode('utf-8'),
        birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Create default profile and settings
        profile = Profile(user_id=new_user.id)
        settings = Settings(user_id=new_user.id)
        db.session.add(profile)
        db.session.add(settings)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=new_user.id)
        
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Check if email and password are provided
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'message': 'Email and password are required',
                'error': 'missing_credentials'
            }), 400
            
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password',
                'error': 'invalid_credentials'
            }), 401
            
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password',
                'error': 'invalid_credentials'
            }), 401
        
        # Create access token with the user object
        # The user_identity_loader will handle the identity format
        access_token = create_access_token(identity=user)
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during login. Please try again.',
            'error': 'server_error'
        }), 500

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_profile():
    # Get the identity from the JWT token
    identity = get_jwt_identity()
    
    # If identity is a dictionary (new format), get the ID from it
    if isinstance(identity, dict) and 'id' in identity:
        user_id = identity['id']
    else:
        # For backward compatibility
        user_id = identity
    
    # Convert user_id to integer for database query
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    profile = user.profile
    return jsonify({
        'name': user.name,
        'email': user.email,
        'birth_date': user.birth_date.isoformat(),
        'profile': {
            'bio': profile.bio if profile else None,
            'age': profile.age if profile else None,
            'gender': profile.gender if profile else None,
            'location': profile.location if profile else None,
            'interests': profile.interests if profile else [],
            'profile_picture': profile.profile_picture if profile else None
        }
    }), 200

@app.route('/api/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    profile = user.profile
    
    if not profile:
        profile = Profile(user_id=user_id)
        db.session.add(profile)
    
    # Update profile fields
    if 'bio' in data:
        profile.bio = data['bio']
    if 'age' in data:
        profile.age = data['age']
    if 'gender' in data:
        profile.gender = data['gender']
    if 'location' in data:
        profile.location = data['location']
    if 'interests' in data:
        profile.interests = data['interests']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Profile update failed'}), 500

@app.route('/api/user/profile/picture', methods=['POST'])
@jwt_required()
def upload_profile_picture():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    if 'picture' not in request.files:
        return jsonify({'message': 'No picture provided'}), 400
    
    file = request.files['picture']
    if file.filename == '':
        return jsonify({'message': 'No picture selected'}), 400
    
    if file:
        filename = secure_filename(f"{user_id}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Update user's profile picture
        profile = user.profile
        if not profile:
            profile = Profile(user_id=user_id)
            db.session.add(profile)
        
        profile.profile_picture = filename
        db.session.commit()
        
        return jsonify({'message': 'Profile picture uploaded successfully'}), 200

@app.route('/api/matches/potential', methods=['GET'])
@jwt_required()
def get_potential_matches():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get users that haven't been matched with yet
    existing_matches = Match.query.filter(
        ((Match.user_id == user_id) | (Match.matched_user_id == user_id))
    ).with_entities(Match.matched_user_id, Match.user_id).all()
    
    excluded_ids = [user_id] + [m[0] if m[0] != user_id else m[1] for m in existing_matches]
    
    potential_matches = User.query.filter(
        User.id.notin_(excluded_ids)
    ).all()
    
    return jsonify([{
        'id': match.id,
        'name': match.name,
        'age': match.profile.age if match.profile else None,
        'location': match.profile.location if match.profile else None,
        'bio': match.profile.bio if match.profile else None,
        'interests': match.profile.interests if match.profile else [],
        'profile_picture': match.profile.profile_picture if match.profile else None
    } for match in potential_matches]), 200

@app.route('/api/matches/action', methods=['POST'])
@jwt_required()
def handle_match_action():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if 'action' not in data or 'target_user_id' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    target_user_id = data['target_user_id']
    action = data['action']
    
    if action == 'like':
        # Check if the other user has already liked
        existing_match = Match.query.filter_by(
            user_id=target_user_id,
            matched_user_id=user_id
        ).first()
        
        if existing_match:
            # It's a match!
            existing_match.status = 'accepted'
            db.session.commit()
            return jsonify({'message': 'It\'s a match!'}), 200
        else:
            # Create a new match
            new_match = Match(
                user_id=user_id,
                matched_user_id=target_user_id
            )
            db.session.add(new_match)
            db.session.commit()
            return jsonify({'message': 'Like recorded'}), 200
    
    elif action == 'dislike':
        # Record the dislike
        new_match = Match(
            user_id=user_id,
            matched_user_id=target_user_id,
            status='rejected'
        )
        db.session.add(new_match)
        db.session.commit()
        return jsonify({'message': 'Dislike recorded'}), 200
    
    return jsonify({'message': 'Invalid action'}), 400

@app.route('/api/messages', methods=['GET'])
@jwt_required()
def get_messages():
    user_id = get_jwt_identity()
    match_id = request.args.get('match_id')
    
    if not match_id:
        return jsonify({'message': 'Match ID required'}), 400
    
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == match_id)) |
        ((Message.sender_id == match_id) & (Message.receiver_id == user_id))
    ).order_by(Message.created_at).all()
    
    return jsonify([{
        'id': msg.id,
        'content': msg.content,
        'sender_id': msg.sender_id,
        'created_at': msg.created_at.isoformat(),
        'read': msg.read
    } for msg in messages]), 200

@app.route('/api/messages', methods=['POST'])
@jwt_required()
def send_message():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if 'receiver_id' not in data or 'content' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    new_message = Message(
        sender_id=user_id,
        receiver_id=data['receiver_id'],
        content=data['content']
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({'message': 'Message sent'}), 201

@app.route('/api/user/settings', methods=['GET'])
@jwt_required()
def get_settings():
    try:
        identity = get_jwt_identity()
        
        # If identity is a dictionary (new format), get the ID from it
        if isinstance(identity, dict) and 'id' in identity:
            user_id = identity['id']
        else:
            # For backward compatibility
            user_id = identity
            
        print(f"[DEBUG] Getting settings for user_id: {user_id}")
        
        # Convert user_id to integer for database query
        user_id_int = int(user_id)
        
        # Try to get settings or create default ones if they don't exist
        settings = Settings.query.filter_by(user_id=user_id_int).first()
        
        if not settings:
            print(f"[DEBUG] No settings found for user_id: {user_id}, creating default settings")
            settings = Settings(
                user_id=user_id,
                profile_visibility='public',
                online_status=True,
                match_notifications=True,
                message_notifications=True
            )
            db.session.add(settings)
            db.session.commit()
        
        response_data = {
            'profile_visibility': settings.profile_visibility,
            'online_status': settings.online_status,
            'match_notifications': settings.match_notifications,
            'message_notifications': settings.message_notifications
        }
        
        print(f"[DEBUG] Returning settings: {response_data}")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"[ERROR] Error in get_settings: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get settings',
            'error': str(e)
        }), 500

@app.route('/api/user/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    try:
        identity = get_jwt_identity()
        
        # If identity is a dictionary (new format), get the ID from it
        if isinstance(identity, dict) and 'id' in identity:
            user_id = identity['id']
        else:
            # For backward compatibility
            user_id = identity
            
        print(f"[DEBUG] Updating settings for user_id: {user_id}")
        
        user_id_int = int(user_id)  # Convert to integer for database query
        settings = Settings.query.filter_by(user_id=user_id_int).first()
        if not settings:
            print(f"[DEBUG] No settings found for user_id: {user_id}, creating new settings")
            settings = Settings(user_id=user_id_int)
            db.session.add(settings)
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
            
        print(f"[DEBUG] Received update data: {data}")
        
        # Update only the fields that are provided in the request
        if 'profile_visibility' in data:
            settings.profile_visibility = data['profile_visibility']
        if 'online_status' in data:
            settings.online_status = bool(data['online_status'])
        if 'match_notifications' in data:
            settings.match_notifications = bool(data['match_notifications'])
        if 'message_notifications' in data:
            settings.message_notifications = bool(data['message_notifications'])
        
        db.session.commit()
        
        response_data = {
            'success': True,
            'message': 'Settings updated successfully',
            'settings': {
                'profile_visibility': settings.profile_visibility,
                'online_status': settings.online_status,
                'match_notifications': settings.match_notifications,
                'message_notifications': settings.message_notifications
            }
        }
        
        print(f"[DEBUG] Settings updated: {response_data}")
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error updating settings: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update settings',
            'error': str(e)
        }), 500

@app.route('/api/user/delete', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    try:
        # Delete user's profile picture if exists
        if user.profile and user.profile.profile_picture:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.profile.profile_picture))
            except:
                pass
        
        # Delete user and all related data
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Account deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Account deletion failed'}), 500

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    init_db()
# Posts endpoints
@app.route('/api/posts', methods=['POST'])
@jwt_required()
def create_post():
    try:
        user_id = get_jwt_identity()
        content = request.form.get('content')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
            
        # Handle file upload if present
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'posts', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                image_path = f"uploads/posts/{filename}"
        
        post = Post(
            user_id=user_id,
            content=content,
            image_path=image_path
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'id': post.id,
            'content': post.content,
            'image_path': post.image_path,
            'created_at': post.created_at.isoformat(),
            'user': {
                'id': post.user.id,
                'name': post.user.name,
                'profile_picture': post.user.profile.profile_picture if post.user.profile else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['GET'])
@jwt_required()
def get_posts():
    try:
        user_id = get_jwt_identity()
        posts = Post.query.order_by(Post.created_at.desc()).all()
        
        return jsonify([{
            'id': post.id,
            'content': post.content,
            'image_path': post.image_path,
            'created_at': post.created_at.isoformat(),
            'user': {
                'id': post.user.id,
                'name': post.user.name,
                'profile_picture': post.user.profile.profile_picture if post.user.profile else None
            }
        } for post in posts])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    try:
        user_id = get_jwt_identity()
        post = Post.query.filter_by(id=post_id, user_id=user_id).first()
        
        if not post:
            return jsonify({'error': 'Post not found'}), 404
            
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Post deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 