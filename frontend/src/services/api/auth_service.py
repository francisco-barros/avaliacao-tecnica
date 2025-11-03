import sys
import os
from typing import Optional, Dict
import requests

src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.base.api_client import APIClient
from config import API_ENDPOINTS, API_TIMEOUT

class AuthService:
    def __init__(self):
        self.client = APIClient("")
        self.endpoints = API_ENDPOINTS["auth"]

    def login(self, email: str, password: str) -> Dict:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            self.endpoints["login"],
            headers=headers,
            json={"email": email, "password": password},
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, dict) and "data" in result:
            return result["data"]
        return result

    def refresh_token(self) -> Dict:
        headers = {"Content-Type": "application/json"}
        token = self._get_refresh_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        import requests
        from ...config import API_TIMEOUT
        response = requests.post(
            self.endpoints["refresh"], headers=headers, timeout=API_TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, dict) and "data" in result:
            return result["data"]
        return result

    def register(
        self, name: str, email: str, password: str, role: Optional[str] = None
    ) -> Dict:
        data = {"name": name, "email": email, "password": password}
        if role:
            data["role"] = role
        return self.client.post(self.endpoints["register"], data=data)

    def _get_refresh_token(self):
        from state.auth_state import get_refresh_token
        return get_refresh_token()

