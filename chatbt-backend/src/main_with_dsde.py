"""
Enhanced ChatBT Backend with DSDE Integration
Combines ChatBT specialists with Dynamic Speculative Decoding Engine for optimal performance
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
import numpy as np

# Import ChatBT specialists and orchestrator
from orchestrator import PythonOrchestrator
from specialists.core_pythonic_specialist import CorePythonicSpecialist
from specialists.standard_library_specialist import StandardLibrarySpecialist
from specialists.code_critic_specialist import CodeCriticSpecialist

# Import DSDE components
from dsde import DSDecoder, DSDecodeConfig, SignalConfig, AdapterConfig
from dsde.utils import DSDecodeResult, PerformanceMetrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='')

# Secure secret key configuration
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    # Generate a secure random secret key for development
    import secrets
    SECRET_KEY = secrets.token_hex(32)
    logger.warning("No SECRET_KEY environment variable set. Generated temporary key for development.")
    logger.warning("For production, set SECRET_KEY environment variable!")

app.config['SECRET_KEY'] = SECRET_KEY

# Enable CORS with proper configuration
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
CORS(app, origins=CORS_ORIGINS)

# Initialize SocketIO with proper CORS
socketio = SocketIO(app, cors_allowed_origins=CORS_ORIGINS, async_mode='threading')

# Global variables with thread safety
orchestrator = None
specialists = {}
dsde_decoder = None
chat_history = []
system_metrics = {
    'total_queries': 0,
    'avg_response_time': 0.0,
    'specialist_usage': {},
    'dsde_metrics': {},
    'uptime_start': time.time()
}

# Thread safety locks
import threading
metrics_lock = threading.Lock()
chat_history_lock = threading.Lock()

def initialize_chatbt_system():
    """Initialize ChatBT specialists and orchestrator"""
    global orchestrator, specialists
    
    try:
        logger.info("Initializing ChatBT specialists...")
        
        # Initialize individual specialists
        specialists['core_pythonic'] = CorePythonicSpecialist()
        specialists['stdlib_specialist'] = StandardLibrarySpecialist()
        specialists['code_critic'] = CodeCriticSpecialist()
        
        # Initialize orchestrator
        orchestrator = PythonOrchestrator()
        
        logger.info("ChatBT specialists initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize ChatBT specialists: {e}")
        traceback.print_exc()
        return False

def initialize_dsde_system():
    """Initialize DSDE system for enhanced performance"""
    global dsde_decoder
    
    try:
        logger.info("Initializing DSDE system...")
        
        # Configure DSDE
        signal_config = SignalConfig(
            short_window_size=4,
            long_window_size=12,
            kld_threshold=0.1,
            variance_threshold=0.05
        )
        
        adapter_config = AdapterConfig(
            min_speculation_length=1,
            max_speculation_length=6,
            default_speculation_length=3,
            stability_threshold_high=0.7,
            stability_threshold_low=0.3,
            enable_batch_capping=True
        )
        
        dsde_config = DSDecodeConfig(
            enable_dynamic_sl=True,
            enable_batch_optimization=True,
            enable_performance_monitoring=True,
            signal_config=signal_config,
            adapter_config=adapter_config,
            debug_mode=False
        )
        
        # Initialize DSDE decoder
        dsde_decoder = DSDecoder(
            draft_model=None,  # Would be actual models in production
            target_model=None,
            config=dsde_config
        )
        
        logger.info("DSDE system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize DSDE system: {e}")
        traceback.print_exc()
        return False

def initialize_database():
    """Initialize SQLite database for chat history and metrics"""
    try:
        conn = sqlite3.connect('chatbt_dsde.db')
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
                dsde_metrics TEXT,
                metadata TEXT
            )
        ''')
        
        # Create DSDE metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dsde_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sequence_id TEXT,
                tokens_generated INTEGER,
                tokens_accepted INTEGER,
                speculation_rounds INTEGER,
                average_sl REAL,
                acceptance_rate REAL,
                speedup_estimate REAL,
                processing_time REAL,
                signal_metrics TEXT
            )
        ''')
        
        # Create system metrics table
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

def save_chat_to_db(user_message: str, bot_response: str, 
                   orchestration_result: Any = None, dsde_result: DSDecodeResult = None):
    """Save chat interaction to database with DSDE metrics"""
    try:
        conn = sqlite3.connect('chatbt_dsde.db')
        cursor = conn.cursor()
        
        # Extract orchestration data
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
        
        # Extract DSDE metrics
        dsde_metrics = None
        if dsde_result:
            dsde_metrics = json.dumps(dsde_result.to_dict())
        
        cursor.execute('''
            INSERT INTO chat_history 
            (user_message, bot_response, query_type, specialists_used, confidence, 
             processing_time, dsde_metrics, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_message, bot_response, query_type, specialists_used, confidence, 
              processing_time, dsde_metrics, metadata))
        
        # Save DSDE metrics separately if available
        if dsde_result:
            cursor.execute('''
                INSERT INTO dsde_metrics
                (sequence_id, tokens_generated, tokens_accepted, speculation_rounds,
                 average_sl, acceptance_rate, speedup_estimate, processing_time, signal_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dsde_result.sequence_id, dsde_result.tokens_generated, dsde_result.tokens_accepted,
                  dsde_result.speculation_rounds, dsde_result.average_sl, dsde_result.acceptance_rate,
                  dsde_result.speedup_estimate, dsde_result.total_time, 
                  json.dumps(dsde_result.final_metrics)))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to save chat to database: {e}")

def update_system_metrics(orchestration_result: Any = None, dsde_result: DSDecodeResult = None):
    """Update system metrics including DSDE performance with thread safety"""
    global system_metrics
    
    with metrics_lock:  # Thread-safe access to system_metrics
        system_metrics['total_queries'] += 1
        
        # Update orchestration metrics
        if orchestration_result:
            total_time = system_metrics['avg_response_time'] * (system_metrics['total_queries'] - 1)
            total_time += orchestration_result.processing_time
            system_metrics['avg_response_time'] = total_time / system_metrics['total_queries']
            
            for resp in orchestration_result.specialist_responses:
                specialist_name = resp.specialist_name
                system_metrics['specialist_usage'][specialist_name] = \
                    system_metrics['specialist_usage'].get(specialist_name, 0) + 1
        
        # Update DSDE metrics
        if dsde_result:
            if 'dsde_metrics' not in system_metrics:
                system_metrics['dsde_metrics'] = {
                    'total_tokens_generated': 0,
                    'total_tokens_accepted': 0,
                    'total_speculation_rounds': 0,
                    'average_acceptance_rate': 0.0,
                    'average_speedup': 0.0,
                    'processed_sequences': 0
                }
            
            dsde_metrics = system_metrics['dsde_metrics']
            dsde_metrics['total_tokens_generated'] += dsde_result.tokens_generated
            dsde_metrics['total_tokens_accepted'] += dsde_result.tokens_accepted
            dsde_metrics['total_speculation_rounds'] += dsde_result.speculation_rounds
            dsde_metrics['processed_sequences'] += 1
        
        # Update running averages
        n = dsde_metrics['processed_sequences']
        dsde_metrics['average_acceptance_rate'] = (
            (dsde_metrics['average_acceptance_rate'] * (n - 1) + dsde_result.acceptance_rate) / n
        )
        dsde_metrics['average_speedup'] = (
            (dsde_metrics['average_speedup'] * (n - 1) + dsde_result.speedup_estimate) / n
        )

@app.route('/')
def index():
    """Serve the main application"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health')
def health_check():
    """Enhanced health check with DSDE status"""
    uptime = time.time() - system_metrics['uptime_start']
    
    health_data = {
        'status': 'healthy',
        'uptime_seconds': uptime,
        'specialists_loaded': len(specialists),
        'orchestrator_ready': orchestrator is not None,
        'dsde_ready': dsde_decoder is not None,
        'total_queries': system_metrics['total_queries']
    }
    
    # Add DSDE performance summary
    if dsde_decoder:
        dsde_summary = dsde_decoder.get_performance_summary()
        health_data['dsde_performance'] = dsde_summary
    
    return jsonify(health_data)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with DSDE acceleration"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not orchestrator or not dsde_decoder:
            return jsonify({'error': 'System not initialized'}), 500
        
        # Process query through orchestrator
        start_time = time.time()
        
        # Run async orchestrator in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get orchestrator result
            orchestration_result = loop.run_until_complete(
                orchestrator.process_query(user_message)
            )
            
            # Enhance with DSDE if applicable
            dsde_result = None
            if len(user_message) > 50:  # Use DSDE for longer queries
                sequence_data = {
                    'id': f"seq_{int(time.time() * 1000)}",
                    'prompt': user_message,
                    'max_tokens': min(200, len(user_message.split()) * 2)
                }
                
                context_info = {
                    sequence_data['id']: {
                        'task_type': orchestration_result.query_type.value,
                        'temperature': 0.7,
                        'current_length': len(user_message)
                    }
                }
                
                dsde_results = loop.run_until_complete(
                    dsde_decoder.decode_batch([sequence_data], context_info)
                )
                
                if dsde_results:
                    dsde_result = dsde_results[0]
                    
        finally:
            loop.close()
        
        processing_time = time.time() - start_time
        
        # Prepare enhanced response
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
        
        # Add DSDE performance data
        if dsde_result:
            response_data['dsde_performance'] = {
                'tokens_generated': dsde_result.tokens_generated,
                'tokens_accepted': dsde_result.tokens_accepted,
                'acceptance_rate': dsde_result.acceptance_rate,
                'speculation_rounds': dsde_result.speculation_rounds,
                'speedup_estimate': dsde_result.speedup_estimate,
                'average_speculation_length': dsde_result.average_sl
            }
        
        # Save to database and update metrics
        save_chat_to_db(user_message, orchestration_result.primary_response, 
                       orchestration_result, dsde_result)
        update_system_metrics(orchestration_result, dsde_result)
        
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

@app.route('/api/dsde/performance', methods=['GET'])
def get_dsde_performance():
    """Get detailed DSDE performance metrics"""
    try:
        if not dsde_decoder:
            return jsonify({'error': 'DSDE not initialized'}), 500
        
        # Get comprehensive performance data
        performance_summary = dsde_decoder.get_performance_summary()
        
        # Add database metrics
        conn = sqlite3.connect('chatbt_dsde.db')
        cursor = conn.cursor()
        
        # Get recent DSDE metrics
        cursor.execute('''
            SELECT AVG(acceptance_rate), AVG(speedup_estimate), AVG(average_sl),
                   COUNT(*), SUM(tokens_generated), SUM(tokens_accepted)
            FROM dsde_metrics 
            WHERE timestamp > datetime('now', '-1 hour')
        ''')
        
        recent_stats = cursor.fetchone()
        conn.close()
        
        if recent_stats and recent_stats[0] is not None:
            performance_summary['recent_hour_stats'] = {
                'avg_acceptance_rate': recent_stats[0],
                'avg_speedup': recent_stats[1],
                'avg_speculation_length': recent_stats[2],
                'total_sequences': recent_stats[3],
                'total_tokens_generated': recent_stats[4],
                'total_tokens_accepted': recent_stats[5]
            }
        
        return jsonify(performance_summary)
        
    except Exception as e:
        logger.error(f"DSDE performance error: {e}")
        return jsonify({'error': f'Failed to get DSDE performance: {str(e)}'}), 500

@app.route('/api/dsde/optimize', methods=['POST'])
def optimize_dsde_settings():
    """Optimize DSDE settings based on current performance"""
    try:
        if not dsde_decoder:
            return jsonify({'error': 'DSDE not initialized'}), 500
        
        data = request.get_json()
        target_acceptance_rate = data.get('target_acceptance_rate', 0.7)
        target_speedup = data.get('target_speedup', 2.0)
        
        # Get current performance
        performance = dsde_decoder.get_performance_summary()
        current_acceptance = performance.get('overall_acceptance_rate', 0.5)
        current_speedup = performance.get('average_speedup', 1.0)
        
        # Suggest optimizations
        optimizations = []
        
        if current_acceptance < target_acceptance_rate:
            optimizations.append({
                'parameter': 'max_speculation_length',
                'current_value': dsde_decoder.config.adapter_config.max_speculation_length,
                'suggested_value': max(1, dsde_decoder.config.adapter_config.max_speculation_length - 1),
                'reason': 'Low acceptance rate suggests shorter speculation lengths'
            })
        elif current_acceptance > target_acceptance_rate + 0.1:
            optimizations.append({
                'parameter': 'max_speculation_length',
                'current_value': dsde_decoder.config.adapter_config.max_speculation_length,
                'suggested_value': min(8, dsde_decoder.config.adapter_config.max_speculation_length + 1),
                'reason': 'High acceptance rate allows for longer speculation lengths'
            })
        
        if current_speedup < target_speedup:
            optimizations.append({
                'parameter': 'stability_threshold_high',
                'current_value': dsde_decoder.config.adapter_config.stability_threshold_high,
                'suggested_value': max(0.5, dsde_decoder.config.adapter_config.stability_threshold_high - 0.1),
                'reason': 'Lower stability threshold to enable more aggressive speculation'
            })
        
        return jsonify({
            'current_performance': {
                'acceptance_rate': current_acceptance,
                'speedup': current_speedup
            },
            'targets': {
                'acceptance_rate': target_acceptance_rate,
                'speedup': target_speedup
            },
            'optimizations': optimizations,
            'recommendation': 'Apply suggested optimizations gradually and monitor performance'
        })
        
    except Exception as e:
        logger.error(f"DSDE optimization error: {e}")
        return jsonify({'error': f'Failed to optimize DSDE: {str(e)}'}), 500

@app.route('/api/metrics')
def get_metrics():
    """Get comprehensive system metrics including DSDE"""
    try:
        uptime = time.time() - system_metrics['uptime_start']
        
        # Get orchestrator metrics
        orchestrator_metrics = orchestrator.get_metrics() if orchestrator else {}
        specialist_stats = orchestrator.get_specialist_stats() if orchestrator else {}
        
        # Get DSDE metrics
        dsde_metrics = dsde_decoder.get_performance_summary() if dsde_decoder else {}
        
        response_data = {
            'system_metrics': {
                **system_metrics,
                'uptime_seconds': uptime,
                'uptime_formatted': f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m"
            },
            'orchestrator_metrics': orchestrator_metrics,
            'specialist_stats': specialist_stats,
            'dsde_metrics': dsde_metrics,
            'specialists_loaded': list(specialists.keys()),
            'database_stats': get_database_stats(),
            'timestamp': time.time()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return jsonify({'error': f'Failed to get metrics: {str(e)}'}), 500

def get_database_stats():
    """Get enhanced database statistics including DSDE data"""
    try:
        conn = sqlite3.connect('chatbt_dsde.db')
        cursor = conn.cursor()
        
        # Chat history stats
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        total_chats = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(confidence) FROM chat_history WHERE confidence IS NOT NULL")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT AVG(processing_time) FROM chat_history WHERE processing_time IS NOT NULL")
        avg_processing_time = cursor.fetchone()[0] or 0.0
        
        # DSDE stats
        cursor.execute("SELECT COUNT(*) FROM dsde_metrics")
        total_dsde_sequences = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(acceptance_rate), AVG(speedup_estimate) FROM dsde_metrics")
        dsde_stats = cursor.fetchone()
        avg_acceptance_rate = dsde_stats[0] or 0.0
        avg_speedup = dsde_stats[1] or 0.0
        
        conn.close()
        
        return {
            'total_chats': total_chats,
            'avg_confidence': avg_confidence,
            'avg_processing_time': avg_processing_time,
            'total_dsde_sequences': total_dsde_sequences,
            'avg_acceptance_rate': avg_acceptance_rate,
            'avg_speedup': avg_speedup
        }
        
    except Exception as e:
        logger.error(f"Database stats error: {e}")
        return {}

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info("Client connected to WebSocket")
    emit('connection_status', {
        'status': 'connected', 
        'specialists_ready': len(specialists) > 0,
        'dsde_ready': dsde_decoder is not None
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info("Client disconnected from WebSocket")

@socketio.on('get_dsde_status')
def handle_dsde_status():
    """Handle DSDE status request"""
    if dsde_decoder:
        status = dsde_decoder.get_performance_summary()
        emit('dsde_status', status)
    else:
        emit('dsde_status', {'error': 'DSDE not initialized'})

def run_initialization():
    """Run complete system initialization"""
    logger.info("Starting ChatBT with DSDE initialization...")
    
    # Initialize database
    if not initialize_database():
        logger.error("Database initialization failed")
        return False
    
    # Initialize ChatBT specialists
    if not initialize_chatbt_system():
        logger.error("ChatBT specialists initialization failed")
        return False
    
    # Initialize DSDE system
    if not initialize_dsde_system():
        logger.error("DSDE system initialization failed")
        return False
    
    logger.info("Complete system initialization completed successfully")
    return True

if __name__ == '__main__':
    # Run initialization
    if not run_initialization():
        logger.error("System initialization failed, exiting...")
        exit(1)
    
    # Start the server
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting ChatBT with DSDE on {host}:{port}")
    logger.info("All specialists and DSDE loaded and ready!")
    logger.info("DSDE Features: Dynamic speculation length, KLD-based stability, batch optimization")
    
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)

