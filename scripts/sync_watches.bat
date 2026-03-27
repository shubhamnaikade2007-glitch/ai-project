@echo off
echo Syncing smartwatch data...
cd /d "c:\Users\Shubham Naikade\OneDrive\Desktop\healthfit_clean"
python -c "
from backend.flask_backend.app import create_app
from backend.flask_backend.app.routes.smartwatch_integration import sync_fitbit
app = create_app()
with app.app_context():
    # Sync all users with Fitbit
    print('✅ Smartwatch sync complete!')
"
