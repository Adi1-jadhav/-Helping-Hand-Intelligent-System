from flask import Flask
from routes.auth import auth
from routes.main import main
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

# Entry point for local dev
if __name__ == '__main__':
    flask_app = create_app()
    flask_app.run(debug=True)

# Entry point for Gunicorn
app = create_app()
