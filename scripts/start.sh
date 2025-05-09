#!/bin/bash

echo "📦 Running Alembic migrations..."
uv run alembic upgrade head


echo "🚀 Starting FastAPI server..."
uv run fastapi run app/main.py