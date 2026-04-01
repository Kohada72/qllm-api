import requests



class QLLMApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def is_healthy(self) -> bool:
        try:
            return requests.get(f"{self.base_url}/docs").status_code == 200
        except:
            return False

    def submit_job(self, payload: dict) -> str:
        response = requests.post(f"{self.base_url}/experiments/", json=payload)
        if response.status_code == 202:
            return response.json().get("job_id")
        else:
            return None