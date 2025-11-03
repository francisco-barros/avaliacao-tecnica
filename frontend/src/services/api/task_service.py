import sys
import os
from typing import List, Dict, Optional

src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.base.api_client import APIClient
from config import API_ENDPOINTS

class TaskService:
    def __init__(self):
        self.client = APIClient("")
        self.endpoints = API_ENDPOINTS["tasks"]

    def list_tasks(self, project_id: str) -> List[Dict]:
        response = self.client.get(f"{self.endpoints['list']}/{project_id}")
        if isinstance(response, dict) and "data" in response:
            return response["data"]
        elif isinstance(response, list):
            return response
        return []

    def create_task(self, data: Dict) -> Dict:
        response = self.client.post(self.endpoints["create"], data=data)
        if isinstance(response, dict) and "data" in response:
            return response["data"]
        return response

    def update_status(self, task_id: str, status: str) -> Dict:
        response = self.client.patch(f"{self.endpoints['update_status']}/{task_id}/status", data={"status": status})
        if isinstance(response, dict) and "data" in response:
            return response["data"]
        return response

    def reassign_task(self, task_id: str, assignee_id: Optional[str] = None) -> Dict:
        response = self.client.patch(f"{self.endpoints['reassign']}/{task_id}/assignee", data={"assignee_id": assignee_id})
        if isinstance(response, dict) and "data" in response:
            return response["data"]
        return response

