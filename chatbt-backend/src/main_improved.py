import os
import sys
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, send_from_directory, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_socketio import SocketIO, emit
import redis
from werkzeug.middleware.proxy_fix import ProxyFix

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from src.routes.user import user_bp
from src.routes.chatbt import chatbt_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """Application factory pattern for better configuration management"""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Load configuration from environment
    app.config.update(
        # Security Configuration
        SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(32)),
        
        # Database Configuration
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 
            f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True, 'pool_recycle': 300},
        
        # API Configuration
        API_BASE_URL=os.environ.get('API_BASE_URL', 'http://localhost:5000'),
        FRONTEND_URL=os.environ.get('FRONTEND_URL', 'http://localhost:5173'),
        
        # Debug and Environment
        DEBUG=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        TESTING=os.environ.get('FLASK_TESTING', 'False').lower() == 'true',
        
        # Rate Limiting
        RATELIMIT_STORAGE_URL=os.environ.get('REDIS_URL', 'redis://localhost:6379'),
        RATELIMIT_DEFAULT="100 per hour",
        
        # Caching
        CACHE_TYPE=os.environ.get('CACHE_TYPE', 'simple'),
        CACHE_REDIS_URL=os.environ.get('REDIS_URL', 'redis://localhost:6379'),
        CACHE_DEFAULT_TIMEOUT=300,
        
        # WebSocket Configuration
        SECRET_KEY_WEBSOCKET=os.environ.get('WEBSOCKET_SECRET', os.urandom(32)),
    )
    
    # Trust proxy headers for rate limiting
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup static file caching
    setup_static_caching(app)
    
    return app

def init_extensions(app):
    """Initialize Flask extensions"""
    
    # CORS Configuration
    cors_origins = [
        app.config['FRONTEND_URL'],
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # Rate Limiting
    try:
        limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://'),
            strategy="fixed-window"
        )
        app.limiter = limiter
        logger.info("Rate limiting initialized successfully")
    except Exception as e:
        logger.warning(f"Rate limiting initialization failed: {e}. Using in-memory fallback.")
        limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri="memory://",
        )
        app.limiter = limiter
    
    # Caching
    try:
        cache = Cache(app)
        app.cache = cache
        logger.info("Caching initialized successfully")
    except Exception as e:
        logger.warning(f"Cache initialization failed: {e}")
        # Fallback to simple cache
        app.config['CACHE_TYPE'] = 'simple'
        cache = Cache(app)
        app.cache = cache
    
    # WebSocket Support
    try:
        socketio = SocketIO(
            app, 
            cors_allowed_origins=cors_origins,
            async_mode='threading',
            logger=False,
            engineio_logger=False
        )
        app.socketio = socketio
        logger.info("WebSocket support initialized")
    except Exception as e:
        logger.warning(f"WebSocket initialization failed: {e}")
        app.socketio = None
    
    # Database
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

def register_blueprints(app):
    """Register application blueprints"""
    
    # Apply rate limiting to API routes
    @app.limiter.limit("30 per minute")
    def limited_api():
        pass
    
    # Register blueprints with rate limiting
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(chatbt_bp, url_prefix='/api/chatbt')
    
    # Apply rate limiting to chatbt routes
    for rule in app.url_map.iter_rules():
        if rule.endpoint and rule.endpoint.startswith('chatbt.'):
            app.view_functions[rule.endpoint] = app.limiter.limit("20 per minute")(
                app.view_functions[rule.endpoint]
            )

def register_error_handlers(app):
    """Register error handlers with proper logging"""
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"Bad request from {request.remote_addr}: {error}")
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning(f"Unauthorized access from {request.remote_addr}: {error}")
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"Forbidden access from {request.remote_addr}: {error}")
        return jsonify({'error': 'Forbidden', 'message': 'Access denied'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        logger.info(f"404 error from {request.remote_addr}: {request.url}")
        return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        logger.warning(f"Rate limit exceeded from {request.remote_addr}: {error}")
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.',
            'retry_after': error.retry_after
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'message': 'Something went wrong'}), 500

def setup_static_caching(app):
    """Setup static file caching with proper headers"""
    
    @app.after_request
    def add_cache_headers(response):
        # Cache static files for 1 year
        if request.endpoint == 'static':
            response.cache_control.max_age = 31536000  # 1 year
            response.cache_control.public = True
            
        # Cache API responses for 5 minutes (if successful)
        elif request.path.startswith('/api/') and response.status_code == 200:
            if 'chat' not in request.path:  # Don't cache chat responses
                response.cache_control.max_age = 300  # 5 minutes
                response.cache_control.public = True
                
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response

def validate_json_input(required_fields=None):
    """Decorator for input validation"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                logger.warning(f"Non-JSON request to {request.endpoint} from {request.remote_addr}")
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                logger.warning(f"Empty JSON request to {request.endpoint} from {request.remote_addr}")
                return jsonify({'error': 'Request body cannot be empty'}), 400
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    logger.warning(f"Missing fields {missing_fields} in request to {request.endpoint}")
                    return jsonify({
                        'error': 'Missing required fields',
                        'missing_fields': missing_fields
                    }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# WebSocket event handlers
def setup_websocket_handlers(app):
    """Setup WebSocket handlers for real-time updates"""
    if not app.socketio:
        return
    
    @app.socketio.on('connect')
    def handle_connect():
        logger.info(f"WebSocket client connected: {request.sid}")
        emit('status', {'message': 'Connected to ChatBT'})
    
    @app.socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f"WebSocket client disconnected: {request.sid}")
    
    @app.socketio.on('subscribe_training')
    def handle_training_subscription():
        """Subscribe to training progress updates"""
        logger.info(f"Client {request.sid} subscribed to training updates")
        emit('training_subscribed', {'status': 'subscribed'})
    
    @app.socketio.on('subscribe_emergence')
    def handle_emergence_subscription():
        """Subscribe to emergence monitoring updates"""
        logger.info(f"Client {request.sid} subscribed to emergence updates")
        emit('emergence_subscribed', {'status': 'subscribed'})

# Enhanced route for serving static files with caching
def create_static_route(app):
    """Create optimized static file serving route"""
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    @app.cache.cached(timeout=3600)  # Cache for 1 hour
    def serve_static(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            logger.error("Static folder not configured")
            return jsonify({'error': 'Static folder not configured'}), 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                logger.warning("index.html not found in static folder")
                return jsonify({'error': 'Application not built. Please run the frontend build process.'}), 404

# Health check endpoint
def create_health_routes(app):
    """Create health check and monitoring routes"""
    
    @app.route('/health')
    @app.cache.cached(timeout=60)
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            # Check database connection
            db.session.execute('SELECT 1')
            db_status = 'healthy'
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            db_status = 'unhealthy'
        
        health_data = {
            'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0',
            'database': db_status,
            'cache': 'healthy' if app.cache else 'disabled',
            'websocket': 'enabled' if app.socketio else 'disabled'
        }
        
        status_code = 200 if health_data['status'] == 'healthy' else 503
        return jsonify(health_data), status_code
    
    @app.route('/metrics')
    @app.limiter.limit("10 per minute")
    def metrics():
        """Basic metrics endpoint"""
        return jsonify({
            'requests_total': getattr(g, 'requests_total', 0),
            'active_connections': len(getattr(app, 'socketio', {}).get('clients', {})) if app.socketio else 0,
            'uptime': datetime.utcnow().isoformat()
        })

# Create and configure the application
app = create_app()

# Setup additional routes and handlers
create_static_route(app)
create_health_routes(app)
setup_websocket_handlers(app)

# Request logging middleware
@app.before_request
def log_request_info():
    """Log request information for monitoring"""
    logger.info(f"{request.method} {request.url} from {request.remote_addr}")
    g.start_time = datetime.utcnow()

@app.after_request
def log_response_info(response):
    """Log response information"""
    if hasattr(g, 'start_time'):
        duration = (datetime.utcnow() - g.start_time).total_seconds()
        logger.info(f"Response: {response.status_code} in {duration:.3f}s")
    return response

if __name__ == '__main__':
    # Production-ready server configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting ChatBT server on port {port} (debug={debug})")
    
    if app.socketio:
        # Run with WebSocket support
        app.socketio.run(
            app,
            host='0.0.0.0',
            port=port,
            debug=debug,
            use_reloader=debug,
            log_output=True
        )
    else:
        # Fallback to regular Flask
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug,
            use_reloader=debug
        )

