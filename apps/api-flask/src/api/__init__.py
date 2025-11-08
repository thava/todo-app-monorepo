"""API package initialization"""


def register_blueprints(app):
    """Register all API blueprints"""
    from .health import health_bp
    from .auth import auth_bp
    from .todos import todos_bp
    from .users import users_bp
    from .admin import admin_bp
    from .root import root_bp

    app.register_blueprint(root_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(todos_bp, url_prefix='/todos')
    app.register_blueprint(users_bp, url_prefix='/me')
    app.register_blueprint(admin_bp, url_prefix='/admin')
