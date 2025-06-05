from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, get_jwt
from flask_mail import Mail, Message
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import re
import time

from models import db, User, Report, Post, BlockedUser, UserProfile

app = Flask(__name__, 
    static_folder='../frontend',
    static_url_path='',
    template_folder='../frontend')

# Enable CORS with specific origins and allow credentials
CORS(app, resources={r"/api/*": {
    "origins": ["http://localhost:5001", "http://127.0.0.1:5001", "http://localhost:5000", "http://127.0.0.1:5000"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True
}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blendup.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']

# Configure email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")  # Set in .env
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
mail = Mail(app)

# Configure file upload
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize JWT
jwt = JWTManager(app)

# Token validation callbacks
@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    print(f"Invalid token error: {error_string}")
    return jsonify({'message': 'Invalid token'}), 401

@jwt.unauthorized_loader
def unauthorized_callback(error_string):
    print(f"Unauthorized error: {error_string}")
    return jsonify({'message': 'Missing token'}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"Expired token error: {jwt_payload}")
    return jsonify({'message': 'Token has expired'}), 401

# User identity callback
@jwt.user_identity_loader
def user_identity_lookup(user):
    if isinstance(user, User):
        return str(user.id)
    return str(user)

# User lookup callback
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=int(identity)).one_or_none()

# Initialize database
db.init_app(app)

# Create database tables
with app.app_context():
    try:
        # Create all tables
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(f"Registration attempt for email: {data.get('email')}")
        
        # Enhanced validation
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        required_fields = ['email', 'password']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Email validation
        email = data['email'].strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Password validation
        password = data['password']
        if len(password) < 8:
            return jsonify({'message': 'Password must be at least 8 characters long'}), 400
        if not re.search(r'[A-Z]', password):
            return jsonify({'message': 'Password must contain at least one uppercase letter'}), 400
        if not re.search(r'[a-z]', password):
            return jsonify({'message': 'Password must contain at least one lowercase letter'}), 400
        if not re.search(r'\d', password):
            return jsonify({'message': 'Password must contain at least one number'}), 400
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered'}), 409
        
        # Create user
        user = User(
            email=email,
            name=data.get('name', '').strip()
        )
        user.set_password(password)
        
        # Create user profile
        profile = UserProfile(user=user)
        
        db.session.add(user)
        db.session.add(profile)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Registration successful',
            'token': access_token,
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'requires_profile_setup': True
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({'message': 'Registration failed. Please try again.'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print(f"Login attempt for email: {data.get('email')}")
        
        # Enhanced validation
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        required_fields = ['email', 'password']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        email = data['email'].strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        if user.suspended:
            return jsonify({'message': 'Account is suspended. Please contact support.'}), 403
        
        # Check if profile setup is required
        profile = UserProfile.query.filter_by(user_id=user.id).first()
        requires_profile_setup = not (profile and profile.language and user.name)
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'requires_profile_setup': requires_profile_setup
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed. Please try again.'}), 500

@app.route('/api/report', methods=['POST'])
@jwt_required(optional=True)
def submit_report():
    user_id = get_jwt_identity()
    data = request.get_json()

    if 'reason' not in data:
        return jsonify({'message': 'Reason is required'}), 400

    report = Report(
        reporter_id=user_id,
        reported_user_id=data.get('reported_user_id'),
        reason=data['reason'],
        details=data.get('details')
    )

    db.session.add(report)
    db.session.commit()

    # Send email to admin
    try:
        msg = Message(
            subject='New User Report on Blendup',
            sender=app.config['MAIL_USERNAME'],
            recipients=['admin@blendup.com'],
            body=f"""
A new report has been submitted.

Reporter ID: {user_id}
Reported User ID: {data.get('reported_user_id')}
Reason: {data['reason']}
Details: {data.get('details')}
"""
        )
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send report email: {e}")

    # Auto-suspend if reported 5+ times
    if data.get('reported_user_id'):
        count = Report.query.filter_by(reported_user_id=data['reported_user_id']).count()
        if count >= 5:
            flagged_user = User.query.get(data['reported_user_id'])
            if flagged_user:
                flagged_user.suspended = True
                db.session.commit()

    return jsonify({'message': 'Report submitted. We will review it shortly.'}), 201

@app.route('/api/admin/reports', methods=['GET'])
@jwt_required()
def view_reports():
    user_id = get_jwt_identity()
    admin_user = User.query.get(user_id)

    # Add real admin check logic here
    if admin_user.email != 'adadmin@blendup.commin@blendup.com':
        return jsonify({'message': 'Unauthorized'}), 403

    reports = Report.query.order_by(Report.created_at.desc()).all()
    return jsonify([{
        'id': r.id,
        'reporter_id': r.reporter_id,
        'reported_user_id': r.reported_user_id,
        'reason': r.reason,
        'details': r.details,
        'created_at': r.created_at.isoformat()
    } for r in reports])

@app.route('/api/admin/report/<int:report_id>', methods=['GET'])
@jwt_required()
def view_report_details(report_id):
    user_id = get_jwt_identity()
    admin_user = User.query.get(user_id)

    if admin_user.email != '':
        return jsonify({'message': 'Unauthorized'}), 403

    report = Report.query.get_or_404(report_id)
    return jsonify({
        'id': report.id,
        'reporter_id': report.reporter_id,
        'reported_user_id': report.reported_user_id,
        'reason': report.reason,
        'details': report.details,
        'created_at': report.created_at.isoformat()
    })

@app.route('/api/admin/suspend/<int:user_id>', methods=['POST'])
@jwt_required()
def suspend_user(user_id):
    user_id = get_jwt_identity()
    admin_user = User.query.get(user_id)

    if admin_user.email != 'admin@blendup.com':
        return jsonify({'message': 'Unauthorized'}), 403

    flagged_user = User.query.get_or_404(user_id)
    flagged_user.suspended = True
    db.session.commit()

    return jsonify({'message': 'User suspended successfully'}), 200

@app.route('/api/user/check-suspension', methods=['GET'])
@jwt_required()
def check_suspension():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if user.suspended:
        return jsonify({'message': 'Account suspended due to multiple reports'}), 403
    
    return jsonify({'message': 'Account active'}), 200

@app.route('/api/user/warnings', methods=['GET'])
@jwt_required()
def get_warnings():
    user_id = get_jwt_identity()
    report_count = Report.query.filter_by(reported_user_id=user_id).count()

    warning = None
    if report_count >= 3:
        warning = "Your account has been reported multiple times. Continued violations may result in suspension."

    return jsonify({
        'reports_against_you': report_count,
        'warning': warning
    }), 200

@app.route('/api/profile/image', methods=['POST'])
@jwt_required()
def upload_profile_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not file or not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        # Generate a unique filename
        filename = secure_filename(f"profile_{user_id}_{datetime.utcnow().timestamp()}.{file.filename.rsplit('.', 1)[1].lower()}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure the upload directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the file
        file.save(file_path)
        
        # Update user's profile picture path
        user.profile_picture = f"/static/uploads/{filename}"
        db.session.commit()
        
        return jsonify({
            'message': 'Profile picture uploaded successfully',
            'url': user.profile_picture
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Profile picture upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def get_profile_picture(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"Error serving profile picture {filename}: {str(e)}")
        return jsonify({'message': 'Profile picture not found'}), 404

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    try:
        user_id = get_jwt_identity()
        print(f"Getting profile for user_id: {user_id}")
        
        user = User.query.get_or_404(user_id)
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'birth_date': user.birth_date.isoformat() if user.birth_date else None,
            'gender': user.gender,
            'location': user.location,
            'profile_picture': user.profile_picture,
            'created_at': user.created_at.isoformat(),
            'suspended': user.suspended
        }), 200
    except Exception as e:
        print(f"Profile error: {str(e)}")
        return jsonify({'message': 'Failed to load profile', 'error': str(e)}), 500

@app.route('/api/user/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Update user fields if provided
        if 'name' in data:
            user.name = data['name']
        if 'birth_date' in data:
            user.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        if 'gender' in data:
            user.gender = data['gender']
        if 'location' in data:
            user.location = data['location']
        
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Profile update error: {str(e)}")
        return jsonify({'message': 'Failed to update profile', 'error': str(e)}), 500

@app.route('/api/settings', methods=['GET'])
@jwt_required()
def get_settings():
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        # Create profile if it doesn't exist
        if not user.profile:
            user.profile = UserProfile()
            db.session.commit()
        
        return jsonify({
            'language': user.profile.language,
            'theme': user.profile.theme,
            'is_private': user.profile.is_private,
            'push_enabled': user.profile.push_enabled,
            'two_fa_enabled': user.profile.two_fa_enabled
        }), 200
    except Exception as e:
        print(f"Settings error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
@jwt_required()
def update_settings():
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        # Create profile if it doesn't exist
        if not user.profile:
            user.profile = UserProfile()
        
        data = request.get_json()
        
        # Update settings
        if 'language' in data:
            user.profile.language = data['language']
        if 'theme' in data:
            user.profile.theme = data['theme']
        if 'is_private' in data:
            user.profile.is_private = data['is_private']
        if 'push_enabled' in data:
            user.profile.push_enabled = data['push_enabled']
        if 'two_fa_enabled' in data:
            user.profile.two_fa_enabled = data['two_fa_enabled']
        
        db.session.commit()
        return jsonify({'message': 'Settings saved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Settings update error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    languages = [
        {"code": "en", "name": "English"},
        {"code": "hi", "name": "Hindi"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "zh", "name": "Chinese"},
        {"code": "ar", "name": "Arabic"},
        {"code": "ru", "name": "Russian"},
        {"code": "ja", "name": "Japanese"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "bn", "name": "Bengali"},
        {"code": "pa", "name": "Punjabi"},
        {"code": "gu", "name": "Gujarati"},
        {"code": "ta", "name": "Tamil"},
        {"code": "te", "name": "Telugu"},
        {"code": "ml", "name": "Malayalam"},
        {"code": "ur", "name": "Urdu"}
    ]
    return jsonify(languages), 200

@app.route('/api/user/block/<int:user_id>', methods=['POST'])
@jwt_required()
def block_user(user_id):
    try:
        blocker_id = get_jwt_identity()
        
        # Check if already blocked
        existing_block = BlockedUser.query.filter_by(
            blocker_id=blocker_id,
            blocked_id=user_id
        ).first()
        
        if existing_block:
            return jsonify({'message': 'User already blocked'}), 400
        
        # Create new block
        block = BlockedUser(
            blocker_id=blocker_id,
            blocked_id=user_id
        )
        
        db.session.add(block)
        db.session.commit()
        
        return jsonify({'message': 'User blocked successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Block user error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/unblock/<int:user_id>', methods=['POST'])
@jwt_required()
def unblock_user(user_id):
    try:
        blocker_id = get_jwt_identity()
        
        # Find and remove block
        block = BlockedUser.query.filter_by(
            blocker_id=blocker_id,
            blocked_id=user_id
        ).first()
        
        if not block:
            return jsonify({'message': 'User not blocked'}), 400
        
        db.session.delete(block)
        db.session.commit()
        
        return jsonify({'message': 'User unblocked successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Unblock user error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        return jsonify({'message': 'Successfully logged out'}), 200
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return jsonify({'message': 'Logout failed'}), 500

@app.route('/api/profile/setup', methods=['POST'])
@jwt_required()
def setup_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get form data
        data = request.form
        
        # Update user profile
        if 'name' in data:
            user.name = data['name'].strip()
        
        if 'location' in data:
            user.location = data['location'].strip()
        
        # Handle profile picture upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{user_id}_{int(time.time())}_{file.filename}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                user.profile_picture = filename
        
        # Update user profile settings
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)
        
        if 'language' in data:
            profile.language = data['language']
        
        if 'is_private' in data:
            profile.is_private = data['is_private'].lower() == 'true'
        
        # Handle interests
        if 'interests' in data:
            interests = data.getlist('interests') if isinstance(data.get('interests'), list) else [data['interests']]
            # Store interests in user profile (you might want to create a separate Interests model)
            profile.interests = ','.join(interests)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile setup completed successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'location': user.location,
                'profile_picture': user.profile_picture,
                'language': profile.language,
                'is_private': profile.is_private,
                'interests': profile.interests.split(',') if profile.interests else []
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Profile setup error: {str(e)}")
        return jsonify({'message': 'Profile setup failed. Please try again.'}), 500

# Frontend routes
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/signup')
@app.route('/signup.html')
def signup_page():
    return send_from_directory(app.static_folder, 'signup.html')

@app.route('/login')
@app.route('/login.html')
def login_page():
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/about')
@app.route('/about.html')
def about_page():
    return send_from_directory(app.static_folder, 'about.html')

@app.route('/profile')
@app.route('/profile.html')
def profile_page():
    return send_from_directory(app.static_folder, 'profile.html')

@app.route('/settings')
@app.route('/settings.html')
def settings_page():
    return send_from_directory(app.static_folder, 'settings.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

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
                'profile_picture': post.user.profile_picture
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['GET'])
@jwt_required()
def get_posts():
    try:
        posts = Post.query.order_by(Post.created_at.desc()).all()
        
        return jsonify([{
            'id': post.id,
            'content': post.content,
            'image_path': post.image_path,
            'created_at': post.created_at.isoformat(),
            'user': {
                'id': post.user.id,
                'name': post.user.name,
                'profile_picture': post.user.profile_picture
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
    try:
        print("\n=== Starting Flask Application ===")
        print("Current working directory:", os.getcwd())
        print("\nServer will be available at:")
        print("- http://127.0.0.1:8080")
        print("- http://localhost:8080")
        print("- http://0.0.0.0:8080")
        
        # Make sure we're in the correct directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print("\nScript directory:", script_dir)
        os.chdir(script_dir)
        print("Changed working directory to:", os.getcwd())
        
        # Create necessary directories
        upload_dir = os.path.join(script_dir, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        print("\nCreated upload directory:", upload_dir)
        
        # Initialize database
        with app.app_context():
            try:
                db.create_all()
                print("\nDatabase tables created successfully")
            except Exception as e:
                print(f"\nError creating database tables: {str(e)}")
                raise
        
        print("\n=== Starting Server ===")
        # Run the application with more permissive settings
        app.run(
            debug=True,
            port=5000,  # Using port 5000
            host='127.0.0.1',
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        print("\n=== Error Starting Server ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure no other application is using port 8080")
        print("2. Check if you have the required permissions")
        print("3. Verify that all dependencies are installed")
        print("4. Check if the database file is accessible")
        raise
