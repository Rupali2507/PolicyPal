from flask import Flask
from app.routes import api, initialize_service

def create_app():
    app = Flask(__name__)
    
    # Register blueprint
    app.register_blueprint(api, url_prefix='/api')
    
    # Initialize service
    initialize_service()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)