import os
from flask import Flask
from backend.config import Config

def create_app():
    # Definir rutas absolutas para frontend
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    template_dir = os.path.join(base_dir, "frontend", "templates")
    static_dir = os.path.join(base_dir, "frontend", "static")

    app = Flask(__name__, 
                template_folder=template_dir, 
                static_folder=static_dir)
    
    app.config.from_object(Config)

    # Registrar Blueprints
    from backend.app.routes.auth import auth_bp
    from backend.app.routes.dashboard import dashboard_bp
    from backend.app.routes.transactions import transactions_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)

    return app
