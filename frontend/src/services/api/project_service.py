import sys
import os
from typing import List, Dict, Optional

src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.base.api_client import APIClient
from config import API_ENDPOINTS

class ProjectService:
    def __init__(self):
        self.client = APIClient("")
        self.endpoints = API_ENDPOINTS["projects"]

    def list_projects(self) -> List[Dict]:
        response = self.client.get(self.endpoints["list"])
        if isinstance(response, dict) and "data" in response:
            return response["data"]
        elif isinstance(response, list):
            return response
        return []

    def get_project(self, project_id: str) -> Dict:
        response = self.client.get(f"{self.endpoints['get']}/{project_id}")
        if isinstance(response, dict) and "data" in response:
            return response["data"]
        return response

    def create_project(self, data: Dict) -> Dict:
        response = self.client.post(self.endpoints["create"], data=data)
        if isinstance(response, dict) and "data" in response:
            return response["data"]
        return response

    def update_project(self, project_id: str, data: Dict) -> Dict:
        response = self.client.patch(f"{self.endpoints['update']}/{project_id}", data=data)
        if isinstance(response, dict) and "data" in response:
            return response["data"]
        return response

    def delete_project(self, project_id: str) -> None:
        self.client.delete(f"{self.endpoints['delete']}/{project_id}")

    def add_member(self, project_id: str, user_id: str) -> None:
        response = self.client.post(f"{self.endpoints['add_member']}/{project_id}/members", data={"user_id": user_id})

    def remove_member(self, project_id: str, user_id: str) -> None:
        self.client.delete(f"{self.endpoints['remove_member']}/{project_id}/members/{user_id}")

