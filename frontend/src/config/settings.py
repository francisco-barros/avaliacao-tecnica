import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "http://localhost:5000")

if os.getenv("DOCKER_ENV") == "true":
    API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:5000")
    WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "http://backend:5000")

