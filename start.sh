#!/bin/bash
# Railway startup script
set -e

# Get port from Railway or default to 8000
PORT=${PORT:-8000}

# Start the application
exec python -m uvicorn main:app --host 0.0.0.0 --port $PORT

