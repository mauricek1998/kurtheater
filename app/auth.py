import json
import os
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, username, name, roles, is_supervisor):
        self.id = username
        self.name = name
        self.roles = roles
        self.is_supervisor = is_supervisor

def load_users():
    users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), current_app.config['USERS_FILE'])
    if not os.path.exists(users_file):
        return {}
    with open(users_file, 'r') as f:
        return json.load(f)['users']

def get_user(username):
    users = load_users()
    if username not in users:
        return None
    user_data = users[username]
    return User(
        username=username,
        name=user_data['name'],
        roles=user_data['roles'],
        is_supervisor=user_data['is_supervisor']
    )

def verify_password(username, password):
    users = load_users()
    if username not in users:
        return False
    stored_password = users[username]['password']
    return check_password_hash(stored_password, password)

def hash_password(password):
    return generate_password_hash(password)

def save_users(users_data):
    users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), current_app.config['USERS_FILE'])
    with open(users_file, 'w') as f:
        json.dump({'users': users_data}, f, indent=4)

def add_user(username, password, name, roles, is_supervisor=False):
    users = load_users()
    if username in users:
        return False, "Benutzername existiert bereits"
    
    users[username] = {
        'password': hash_password(password),
        'name': name,
        'roles': roles,
        'is_supervisor': is_supervisor
    }
    save_users(users)
    return True, "Benutzer erfolgreich erstellt" 