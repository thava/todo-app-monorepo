"""Application entry point"""
import os
from src.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port)
