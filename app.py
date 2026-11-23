#!/usr/bin/env python3
"""
Kubernetes Todo App Backend
Simple Flask API that connects to PostgreSQL and serves the Todo app
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Database configuration from environment variables
DB_HOST = os.getenv('DB_HOST', 'postgres-service')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'appdb')
DB_USER = os.getenv('POSTGRES_USER', 'appuser')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'SecurePassword123!')

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        raise

def init_db():
    """Initialize database tables if they don't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create todos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                task VARCHAR(255) NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully")
    except psycopg2.Error as e:
        print(f"Database initialization error: {e}")

# Initialize database on startup
try:
    init_db()
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")

# Routes

@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT NOW()')
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'database': 'disconnected',
            'error': str(e)
        }), 503

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all todos from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT id, task, completed, created_at, updated_at
            FROM todos
            ORDER BY created_at DESC
        ''')
        
        todos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify([dict(todo) for todo in todos])
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos', methods=['POST'])
def create_todo():
    """Create a new todo"""
    try:
        data = request.get_json()
        task = data.get('task', '').strip()
        
        if not task:
            return jsonify({'error': 'Task cannot be empty'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            INSERT INTO todos (task, completed)
            VALUES (%s, FALSE)
            RETURNING id, task, completed, created_at, updated_at
        ''', (task,))
        
        todo = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify(dict(todo)), 201
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo"""
    try:
        data = request.get_json()
        completed = data.get('completed', False)
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            UPDATE todos
            SET completed = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, task, completed, created_at, updated_at
        ''', (completed, todo_id))
        
        todo = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if todo:
            return jsonify(dict(todo))
        else:
            return jsonify({'error': 'Todo not found'}), 404
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM todos WHERE id = %s', (todo_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Todo not found'}), 404
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Todo deleted'}), 200
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Get a specific todo"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT id, task, completed, created_at, updated_at
            FROM todos
            WHERE id = %s
        ''', (todo_id,))
        
        todo = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if todo:
            return jsonify(dict(todo))
        else:
            return jsonify({'error': 'Todo not found'}), 404
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors - serve index.html for client-side routing"""
    return send_from_directory('.', 'index.html')

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # For local development only
    # In Kubernetes, Nginx will handle serving
    print("Starting Todo App API...")
    print(f"Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    app.run(debug=False, host='0.0.0.0', port=5000)
