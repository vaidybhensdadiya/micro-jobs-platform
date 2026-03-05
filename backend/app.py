from app import create_app

# This creates the app instance using the factory in app/__init__.py
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


