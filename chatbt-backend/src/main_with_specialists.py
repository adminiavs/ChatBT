"""
Enhanced ChatBT Backend with Full Specialist Integration
Includes Core Pythonic, Standard Library, Code Critic specialists and Orchestrator Engine
"""

import os
import asyncio
import logging
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sqlite3
import threading
import traceback

# Import all specialists and orchestrator
from orchestrator import PythonOrchestrator
from specialists.core_pythonic_specialist import CorePythonicSpecialist
from specialists.standard_library_specialist import StandardLibrarySpecialist
from specialists.code_critic_specialist import CodeCriticSpecialist

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chatbt-secret-key-2024')

# Enable CORS
CORS(app, origins="*")

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables
orchestrator = None
specialists = {}
chat_history = []
system_metrics = {
    'total_queries': 0,
    'avg_response_time': 0.0,
    'specialist_usage': {},
    'uptime_start': time.time()
}

def initialize_specialists():
    """Initialize all specialists and orchestrator"""
    global orchestrator, specialists
    
    try:
        logger.info("Initializing ChatBT specialists...")
        
        # Initialize individual specialists
        specialists['core_pythonic'] = CorePythonicSpecialist()
        specialists['stdlib_specialist'] = StandardLibrarySpecialist()
        specialists['code_critic'] = CodeCriticSpecialist()
        
        # Initialize orchestrator
        orchestrator = PythonOrchestrator()
        
        logger.info("All specialists initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize specialists: {e}")
        traceback.print_exc()
        return False

def initialize_database():
    """Initialize SQLite database for chat history"""
    try:
        conn = sqlite3.connect('chatbt.db')
        cursor = conn.cursor()
        
        # Create chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                query_type TEXT,
                specialists_used TEXT,
                confidence REAL,
                processing_time REAL,
                metadata TEXT
            )
        ''')
        
        # Create metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_name TEXT NOT NULL,
                metric_value TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def save_chat_to_db(user_message: str, bot_response: str, orchestration_result: Any = None):
    """Save chat interaction to database"""
    try:
        conn = sqlite3.connect('chatbt.db')
        cursor = conn.cursor()
        
        query_type = None
        specialists_used = None
        confidence = None
        processing_time = None
        metadata = None
        
        if orchestration_result:
            query_type = orchestration_result.query_type.value
            specialists_used = json.dumps([r.specialist_name for r in orchestration_result.specialist_responses])
            confidence = orchestration_result.confidence
            processing_time = orchestration_result.processing_time
            metadata = json.dumps(orchestration_result.metadata)
        
        cursor.execute('''
            INSERT INTO chat_history 
            (user_message, bot_response, query_type, specialists_used, confidence, processing_time, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_message, bot_response, query_type, specialists_used, confidence, processing_time, metadata))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to save chat to database: {e}")

def update_system_metrics(orchestration_result: Any = None):
    """Update system metrics"""
    global system_metrics
    
    system_metrics['total_queries'] += 1
    
    if orchestration_result:
        # Update average response time
        total_time = system_metrics['avg_response_time'] * (system_metrics['total_queries'] - 1)
        total_time += orchestration_result.processing_time
        system_metrics['avg_response_time'] = total_time / system_metrics['total_queries']
        
        # Update specialist usage
        for resp in orchestration_result.specialist_responses:
            specialist_name = resp.specialist_name
            system_metrics['specialist_usage'][specialist_name] = \
                system_metrics['specialist_usage'].get(specialist_name, 0) + 1

@app.route('/')
def index():
    """Serve the main application"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    uptime = time.time() - system_metrics['uptime_start']
    
    return jsonify({
        'status': 'healthy',
        'uptime_seconds': uptime,
        'specialists_loaded': len(specialists),
        'orchestrator_ready': orchestrator is not None,
        'total_queries': system_metrics['total_queries']
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint with full specialist integration"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not orchestrator:
            return jsonify({'error': 'Specialists not initialized'}), 500
        
        # Process query through orchestrator
        start_time = time.time()
        
        # Run async orchestrator in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            orchestration_result = loop.run_until_complete(
                orchestrator.process_query(user_message)
            )
        finally:
            loop.close()
        
        processing_time = time.time() - start_time
        
        # Prepare response
        response_data = {
            'response': orchestration_result.primary_response,
            'query_type': orchestration_result.query_type.value,
            'response_mode': orchestration_result.response_mode.value,
            'confidence': orchestration_result.confidence,
            'processing_time': processing_time,
            'specialists_used': [r.specialist_name for r in orchestration_result.specialist_responses],
            'specialist_details': [
                {
                    'name': r.specialist_name,
                    'confidence': r.confidence,
                    'processing_time': r.processing_time,
                    'response_preview': r.response[:100] + '...' if len(r.response) > 100 else r.response
                }
                for r in orchestration_result.specialist_responses
            ],
            'synthesis_notes': orchestration_result.synthesis_notes,
            'metadata': orchestration_result.metadata
        }
        
        # Save to database and update metrics
        save_chat_to_db(user_message, orchestration_result.primary_response, orchestration_result)
        update_system_metrics(orchestration_result)
        
        # Add to chat history
        chat_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'bot_response': orchestration_result.primary_response,
            'orchestration_data': response_data
        })
        
        # Emit real-time update
        socketio.emit('chat_response', response_data)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/analyze-code', methods=['POST'])
def analyze_code():
    """Dedicated code analysis endpoint"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        
        if 'code_critic' not in specialists:
            return jsonify({'error': 'Code Critic specialist not available'}), 500
        
        # Analyze code with Code Critic
        analysis = specialists['code_critic'].analyze_code(code, "user_code.py")
        
        # Get fix suggestions
        fixes = specialists['code_critic'].suggest_fixes(analysis['issues'])
        
        # Generate report
        report = specialists['code_critic'].generate_report(analysis)
        
        response_data = {
            'analysis': analysis,
            'fixes': fixes,
            'report': report,
            'summary': analysis['summary'],
            'metrics': analysis.get('metrics', {}),
            'timestamp': time.time()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Code analysis error: {e}")
        return jsonify({'error': f'Code analysis failed: {str(e)}'}), 500

@app.route('/api/suggest-library', methods=['POST'])
def suggest_library():
    """Library suggestion endpoint"""
    try:
        data = request.get_json()
        task = data.get('task', '').strip()
        
        if not task:
            return jsonify({'error': 'Task description is required'}), 400
        
        if 'stdlib_specialist' not in specialists:
            return jsonify({'error': 'Standard Library specialist not available'}), 500
        
        # Get library suggestions
        suggestions = specialists['stdlib_specialist'].suggest_module_for_task(task)
        
        # Get patterns for suggested modules
        detailed_suggestions = []
        for suggestion in suggestions[:3]:  # Top 3 suggestions
            patterns = specialists['stdlib_specialist'].get_patterns_by_module(suggestion['module'])
            detailed_suggestions.append({
                'module': suggestion['module'],
                'reason': suggestion['reason'],
                'patterns': [
                    {
                        'name': p.pattern_name,
                        'description': p.description,
                        'example': p.example,
                        'category': p.category
                    }
                    for p in patterns[:2]  # Top 2 patterns per module
                ]
            })
        
        response_data = {
            'task': task,
            'suggestions': detailed_suggestions,
            'timestamp': time.time()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Library suggestion error: {e}")
        return jsonify({'error': f'Library suggestion failed: {str(e)}'}), 500

@app.route('/api/pythonic-review', methods=['POST'])
def pythonic_review():
    """Pythonic code review endpoint"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        
        if 'core_pythonic' not in specialists:
            return jsonify({'error': 'Core Pythonic specialist not available'}), 500
        
        # Analyze for pythonic patterns
        analysis = specialists['core_pythonic'].analyze_code_for_pythonic_patterns(code)
        
        # Get improvement suggestions
        suggestions = specialists['core_pythonic'].suggest_pythonic_improvements(code)
        
        response_data = {
            'analysis': analysis,
            'suggestions': suggestions,
            'pythonic_score': len(analysis['pythonic_patterns']) / max(len(analysis['all_patterns']), 1),
            'timestamp': time.time()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Pythonic review error: {e}")
        return jsonify({'error': f'Pythonic review failed: {str(e)}'}), 500

@app.route('/api/metrics')
def get_metrics():
    """Get system metrics"""
    try:
        uptime = time.time() - system_metrics['uptime_start']
        
        # Get orchestrator metrics
        orchestrator_metrics = orchestrator.get_metrics() if orchestrator else {}
        specialist_stats = orchestrator.get_specialist_stats() if orchestrator else {}
        
        response_data = {
            'system_metrics': {
                **system_metrics,
                'uptime_seconds': uptime,
                'uptime_formatted': f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m"
            },
            'orchestrator_metrics': orchestrator_metrics,
            'specialist_stats': specialist_stats,
            'specialists_loaded': list(specialists.keys()),
            'database_stats': get_database_stats(),
            'timestamp': time.time()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return jsonify({'error': f'Failed to get metrics: {str(e)}'}), 500

def get_database_stats():
    """Get database statistics"""
    try:
        conn = sqlite3.connect('chatbt.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        total_chats = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(confidence) FROM chat_history WHERE confidence IS NOT NULL")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT AVG(processing_time) FROM chat_history WHERE processing_time IS NOT NULL")
        avg_processing_time = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            'total_chats': total_chats,
            'avg_confidence': avg_confidence,
            'avg_processing_time': avg_processing_time
        }
        
    except Exception as e:
        logger.error(f"Database stats error: {e}")
        return {}

@app.route('/api/chat-history')
def get_chat_history():
    """Get recent chat history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        conn = sqlite3.connect('chatbt.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, user_message, bot_response, query_type, 
                   specialists_used, confidence, processing_time
            FROM chat_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'timestamp': row[0],
                'user_message': row[1],
                'bot_response': row[2],
                'query_type': row[3],
                'specialists_used': json.loads(row[4]) if row[4] else [],
                'confidence': row[5],
                'processing_time': row[6]
            })
        
        return jsonify({'history': history})
        
    except Exception as e:
        logger.error(f"Chat history error: {e}")
        return jsonify({'error': f'Failed to get chat history: {str(e)}'}), 500

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info("Client connected to WebSocket")
    emit('connection_status', {'status': 'connected', 'specialists_ready': len(specialists) > 0})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info("Client disconnected from WebSocket")

@socketio.on('ping')
def handle_ping():
    """Handle ping for connection testing"""
    emit('pong', {'timestamp': time.time()})

def run_initialization():
    """Run initialization in a separate thread"""
    logger.info("Starting ChatBT initialization...")
    
    # Initialize database
    if not initialize_database():
        logger.error("Database initialization failed")
        return False
    
    # Initialize specialists
    if not initialize_specialists():
        logger.error("Specialists initialization failed")
        return False
    
    logger.info("ChatBT initialization completed successfully")
    return True

if __name__ == '__main__':
    # Run initialization
    if not run_initialization():
        logger.error("Initialization failed, exiting...")
        exit(1)
    
    # Start the server
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting ChatBT server on {host}:{port}")
    logger.info("All specialists loaded and ready!")
    
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)

