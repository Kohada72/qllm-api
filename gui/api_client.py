import requests
from requests.exceptions import RequestException
from typing import List, Optional, Dict, Any



class QLLMApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def is_healthy(self) -> bool:
        """ジョブのSubmitボタンを解放するかを決める"""
        try:
            return requests.get(f"{self.base_url}/docs").status_code == 200
        except RequestException:
            return False

    def submit_job(self, payload: dict) -> Optional[str]:
        response = requests.post(f"{self.base_url}/experiments/", json=payload)
        return response.json().get("job_id") if response.status_code == 202 else None

    def get_jobs(self) -> List[Dict[str, Any]]:
        response = requests.get(f"{self.base_url}/experiments/")
        return response.json() if response.status_code == 200 else []

    def get_job_detail(self, job_id: str) -> Optional[Dict[str, Any]]:
        response = requests.get(f"{self.base_url}/experiments/{job_id}")
        return response.json() if response.status_code == 200 else None