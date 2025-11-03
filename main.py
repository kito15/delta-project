import os
from app import create_app, db
from app.models.user import User
from app.models.analysis import Analysis

# Determine environment (Railway sets PORT environment variable)
config_name = 'production' if os.getenv('PORT') else os.getenv('FLASK_ENV', 'development')

# Create Flask application
app = create_app(config_name)

# Shell context for Flask CLI
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Analysis': Analysis
    }

if __name__ == '__main__':
    # Railway provides PORT environment variable
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
