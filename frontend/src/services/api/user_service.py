import sys
import os
from typing import List, Dict, Optional

src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.base.api_client import APIClient
from config import API_ENDPOINTS

class UserService:
    def __init__(self):
        self.client = APIClient("")
        self.endpoints = API_ENDPOINTS["users"]

    def list_users(self) -> List[Dict]:
        response = self.client.get(self.endpoints["list"])
        if isinstance(response, dict) and "data" in response:
            return response["data"]
        elif isinstance(response, list):
            return response
        return []

    def get_user(self, user_id: str) -> Dict:
        response = self.client.get(f"{self.endpoints['get']}/{user_id}")
        if isinstance(response, dict) and "data" in response:
            return response["data"]
        return response

    def update_user(self, user_id: str, data: Dict) -> Dict:
        return self.client.patch(f"{self.endpoints['update']}/{user_id}", data=data)

    def delete_user(self, user_id: str) -> None:
        self.client.delete(f"{self.endpoints['delete']}/{user_id}")

