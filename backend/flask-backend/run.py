"""
HealthFit AI - Flask Application Entry Point
Run with: python run.py
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    
    print(f"""
    ╔══════════════════════════════════════╗
    ║   HealthFit AI - Flask Backend       ║
    ║   Running on http://localhost:{port}    ║
    ║   Debug mode: {'ON ' if debug else 'OFF'}                   ║
    ╚══════════════════════════════════════╝
    """)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
