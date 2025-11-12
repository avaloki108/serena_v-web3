#!/usr/bin/env python3
"""
Example script demonstrating Qdrant integration with Serena.

This script shows how to:
1. Create a test project
2. Index it with Qdrant
3. Perform semantic code search
"""

import os
import tempfile
from pathlib import Path

# Example: Create a simple test project
def create_test_project():
    """Create a simple test project with some Python files."""
    project_dir = tempfile.mkdtemp(prefix="serena_qdrant_test_")
    print(f"Creating test project in: {project_dir}")
    
    # Create some example Python files
    (Path(project_dir) / "auth.py").write_text("""
def authenticate_user(username: str, password: str) -> bool:
    \"\"\"Authenticate a user with username and password.\"\"\"
    # This is a simplified example
    if not username or not password:
        return False
    # In production, you would hash the password and check against database
    return True

def generate_jwt_token(user_id: int) -> str:
    \"\"\"Generate a JWT token for authenticated user.\"\"\"
    import jwt
    import datetime
    
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, 'secret', algorithm='HS256')
""")
    
    (Path(project_dir) / "database.py").write_text("""
import sqlite3

def execute_query(query: str, params: tuple) -> list:
    \"\"\"Execute a database query.\"\"\"
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

def get_user_by_id(user_id: int) -> dict:
    \"\"\"Fetch user from database by ID.\"\"\"
    query = "SELECT * FROM users WHERE id = ?"
    results = execute_query(query, (user_id,))
    if results:
        return {'id': results[0][0], 'name': results[0][1]}
    return None
""")
    
    (Path(project_dir) / "api.py").write_text("""
from flask import Flask, request, jsonify
import auth

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    \"\"\"API endpoint for user login.\"\"\"
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if auth.authenticate_user(username, password):
        token = auth.generate_jwt_token(1)  # Simplified: assuming user_id=1
        return jsonify({'token': token}), 200
    
    return jsonify({'error': 'Authentication failed'}), 401

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    \"\"\"API endpoint to get user information.\"\"\"
    from database import get_user_by_id
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user), 200
    return jsonify({'error': 'User not found'}), 404
""")
    
    return project_dir


def demo_qdrant_indexing():
    """Demonstrate Qdrant indexing and search."""
    # Note: This is a simplified example showing the API usage
    # In practice, you would use the CLI commands or SerenaAgent
    
    print("\n" + "="*60)
    print("Qdrant Integration Demo")
    print("="*60)
    
    project_dir = create_test_project()
    
    print("\n1. To index this project with Qdrant, run:")
    print(f"   serena project generate-yml {project_dir}")
    print(f"   serena project index {project_dir}")
    
    print("\n2. To search for authentication code, run:")
    print(f"   serena project search \"authentication with JWT tokens\" {project_dir}")
    
    print("\n3. To search for database queries, run:")
    print(f"   serena project search \"SQL database query execution\" {project_dir}")
    
    print("\n4. To search for API endpoints, run:")
    print(f"   serena project search \"Flask API endpoint for login\" {project_dir}")
    
    print("\n" + "="*60)
    print("Prerequisites:")
    print("="*60)
    print("1. Start Qdrant: docker run -d --name qdrant -p 6333:6333 qdrant/qdrant")
    print("2. Start Ollama with embedding model: ollama pull qwen3-embedding:4b")
    print("\nProject created at:", project_dir)
    print("="*60)


if __name__ == "__main__":
    demo_qdrant_indexing()
