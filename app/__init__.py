from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from .auth import get_user

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # CORS-Konfiguration
    CORS(app, resources={r"/*": {"origins": "*"}}, 
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Login-Manager initialisieren
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Bitte melden Sie sich an, um diese Seite zu sehen.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(username):
        return get_user(username)

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app
