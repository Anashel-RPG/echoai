# api_base.py
import logging

class APIBase:
    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers

    def start_job(self, data):
        raise NotImplementedError("This method should be implemented by subclasses")

    def check_job_status(self, job_id):
        raise NotImplementedError("This method should be implemented by subclasses")

    def download_job_content(self, job_id):
        raise NotImplementedError("This method should be implemented by subclasses")