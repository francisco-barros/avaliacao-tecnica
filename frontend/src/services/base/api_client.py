import requests
import sys
import os
from typing import Optional, Dict, Any

src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from state.auth_state import get_token
from config import API_TIMEOUT

class APIClient:
    def __init__(self, base_url: str, timeout: int = API_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        token = get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def get(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        response = requests.get(
            url, headers=self._get_headers(), params=params, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def post(self, url: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        response = requests.post(
            url, headers=self._get_headers(), json=data, timeout=self.timeout
        )
        if response.status_code >= 400:
            error_data = {}
            try:
                error_data = response.json()
            except:
                error_data = {"message": response.text}
            error_msg = error_data.get("message", f"{response.status_code} {response.reason}")
            raise Exception(f"{response.status_code} {response.reason}: {error_msg}")
        return response.json()

    def patch(self, url: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        response = requests.patch(
            url, headers=self._get_headers(), json=data, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def delete(self, url: str) -> None:
        response = requests.delete(
            url, headers=self._get_headers(), timeout=self.timeout
        )
        if response.status_code >= 400:
            error_data = {}
            try:
                error_data = response.json()
            except:
                error_data = {"message": response.text}
            error_msg = error_data.get("message", f"{response.status_code} {response.reason}")
            raise Exception(f"{response.status_code} {response.reason}: {error_msg}")
        if response.status_code not in [200, 204]:
            response.raise_for_status()

