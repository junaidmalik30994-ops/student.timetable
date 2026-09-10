from app import create_app
from config import Config

app = create_app()

if __name__ == '__main__':
    print(f"Starting Student Time Table Application on http://127.0.0.1:{Config.PORT}")
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
