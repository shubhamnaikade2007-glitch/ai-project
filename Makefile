# ============================================================
# HealthFit AI - Makefile
# Usage: make <target>
# ============================================================

.PHONY: help setup db-setup backend ai-api frontend all clean

help:
	@echo "HealthFit AI - Available Commands"
	@echo "=================================="
	@echo "make setup        - Full project setup"
	@echo "make db-setup     - Initialize MySQL database"
	@echo "make backend      - Start Flask backend"
	@echo "make ai-api       - Start AI models API"
	@echo "make frontend     - Start React frontend"
	@echo "make all          - Start all services"
	@echo "make clean        - Remove venv and node_modules"

setup:
	cd backend/flask-backend && python -m venv venv && venv/Scripts/activate && pip install -r requirements.txt
	cd ai-models && pip install -r requirements-ai.txt
	cd frontend && npm install
	@echo "Setup complete!"

db-setup:
	mysql -u root -proot123 < database/mysql/schema.sql
	mysql -u root -proot123 < database/mysql/sample_data.sql
	@echo "Database initialized!"

backend:
	cd backend/flask-backend && venv/Scripts/activate && python run.py

ai-api:
	cd ai-models && python api/main.py

frontend:
	cd frontend && npm start

all:
	start cmd /k "cd backend/flask-backend && venv\Scripts\activate && python run.py"
	start cmd /k "cd ai-models && python api/main.py"
	start cmd /k "cd frontend && npm start"

clean:
	rmdir /s /q backend/flask-backend/venv
	rmdir /s /q frontend/node_modules
	@echo "Cleaned!"
