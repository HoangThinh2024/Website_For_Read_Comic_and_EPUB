import os
from flask import Flask
from models import db

def create_app():
    app = Flask(__name__)

    # Config
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(base_dir, 'library.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(base_dir, "uploads")
    app.config["COVER_FOLDER"] = os.path.join(base_dir, "uploads", "covers")
    app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB

    # Ensure directories exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["COVER_FOLDER"], exist_ok=True)

    # Init DB
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Blueprints
    from routes.library import library_bp
    from routes.upload import upload_bp
    app.register_blueprint(library_bp)
    app.register_blueprint(upload_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=5000)
