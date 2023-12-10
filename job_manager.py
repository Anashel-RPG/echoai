# job_manager.py
import threading
import time
import os
import json
import requests
from queue import Queue, Empty
from datetime import datetime
from image_downloader import download_image
from config import MAX_CONCURRENT_JOBS, RATE_LIMIT_DELAY, API_BASE_URL, HEADERS, API_CALL_DELAY
from job_data_store import get_job_data, store_job_data
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class API:
    total_api_credit_cost = 0  # Class-level variable to track the total cost
    total_images = 0  # Class-level variable to track the total images
    @staticmethod
    def start_job(data):
        url = API_BASE_URL + 'generations'
        headers = HEADERS
        payload = json.dumps(data)
        try:
            logging.info("Calling Leonardo GENERATE")
            logging.info("======")
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()  # Raises an HTTPError for certain status codes
            job_response = response.json()
            job_id = job_response.get('sdGenerationJob', {}).get('generationId')
            api_credit_cost = job_response.get('sdGenerationJob', {}).get('apiCreditCost', 0)  # Get the credit cost

            if job_id:
                logging.info(f"Job started with ID: {job_id}, Credit Cost: {api_credit_cost}")
                API.total_api_credit_cost += api_credit_cost  # Increment the total cost
                API.total_images += 1  # Increment the total images
                logging.info(f"== TOTAL COST: {API.total_api_credit_cost} API Credits ==")
                logging.info(f"== TOTAL IMAGES: {API.total_images} ==")
                store_job_data(job_id, data['prompt'])  # Store the job ID and prompt
                return job_id
            else:
                logging.error("Failed to start job: No 'generationId' found in response.")
                return None
        except requests.exceptions.HTTPError as e:
            # HTTP error occurred
            logging.error(f"HTTP error occurred while starting the job: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            # Other errors (e.g., network issues, JSON decoding issue, etc.)
            logging.error(f"Error starting job: {e}")
        return None

    @staticmethod
    def check_job_status(job_id):
        url = API_BASE_URL + f'generations/{job_id}'
        headers = HEADERS
        # time.sleep(3)  # Wait for 1 second before making the API call
        time.sleep(API_CALL_DELAY)  # Use the configurable delay from config.py

        try:
            logging.info(f"Calling Leonardo STATUS for job ID {job_id}")  # Include job ID in log
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            job_status_response = response.json()
            status = job_status_response.get('generations_by_pk', {}).get('status', 'UNKNOWN')
            return status
        except Exception as e:
            logging.error(f"Error checking job status for ID {job_id}: {e}")
            return 'UNKNOWN'

    @staticmethod
    def download_job_content(job_id):
        url = API_BASE_URL + f'generations/{job_id}'
        headers = HEADERS
        try:
            logging.info(f"Calling Leonardo CDN DOWNLOAD")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            job_content_response = response.json()
            generated_images = job_content_response.get('generations_by_pk', {}).get('generated_images', [])

            # Extract additional metadata
            additional_metadata = {
                "inferenceSteps": job_content_response.get('generations_by_pk', {}).get('inferenceSteps'),
                "seed": job_content_response.get('generations_by_pk', {}).get('seed'),
                "presetStyle": job_content_response.get('generations_by_pk', {}).get('presetStyle'),
                "initStrength": job_content_response.get('generations_by_pk', {}).get('initStrength'),
                "guidanceScale": job_content_response.get('generations_by_pk', {}).get('guidanceScale'),
                "promptMagic": job_content_response.get('generations_by_pk', {}).get('promptMagic'),
                "promptMagicVersion": job_content_response.get('generations_by_pk', {}).get('promptMagicVersion'),
                "promptMagicStrength": job_content_response.get('generations_by_pk', {}).get('promptMagicStrength'),
                "photoReal": job_content_response.get('generations_by_pk', {}).get('photoReal'),
                "photoRealStrength": job_content_response.get('generations_by_pk', {}).get('photoRealStrength')
            }

            logging.info(f"Attempting to download content for job ID {job_id}")
            job_data = get_job_data(job_id)  # Retrieve job data

            if job_data:  # Check if job data is available
                for image in generated_images:
                    image_url = image.get('url')
                    if image_url:
                        local_path = os.path.join("downloaded_images", f"{job_id}_{image.get('id', 'unknown')}.jpg")
                        logging.info(f"Downloading image: {image_url}")
                        download_image(image_url, local_path, job_id, job_data['prompt'], additional_metadata)
                        print(f"NOW SHOWING: {job_data}")
        except Exception as e:
            logging.error(f"Error downloading content for job ID {job_id}: {e}")


queue_processor = Queue()

class Job:
    def __init__(self, data):
        self.data = data
        self.status = 'pending'
        self.id = None
        self.start_time = datetime.now()
        self.last_checked = None
        self.check_count = 0
        self.previous_status = None
        self.last_log_time = None

    def start(self):
        self.id = API.start_job(self.data)
        self.start_time = datetime.now()

        if self.id:
            store_job_data(self.id, self.data['prompt'])
            self.status = 'processing'
        else:
            # Retry once if the job fails to start
            logging.info("== WARNING RETRY ==")
            logging.info(self.data['prompt'])
            time.sleep(5)  # Use the configurable delay from config.py
            self.id = API.start_job(self.data)
            if self.id:
                store_job_data(self.id, self.data['prompt'])  # Store job data in the job_data_store on successful retry
                self.status = 'processing'
            else:
                self.status = 'failed'
                logging.info("== RETRY FAILED ==")

        self.last_checked = datetime.now()

    def should_log(self):
        """Determines if the current status should be logged."""
        current_time = datetime.now()
        if self.previous_status != self.status or (
                self.last_log_time is None or (current_time - self.last_log_time).total_seconds() > 10):
            self.last_log_time = current_time
            return True
        return False

    def check_status(self):
        if self.id is None:  # Skip processing if job ID is None
            logging.error(f"== SKIPPING ID NONE ==")
            self.status = 'failed'
            return

        current_time = datetime.now()

        # Initial delay of 10 seconds before the first check
        if self.last_checked is None:
            if (current_time - self.start_time).total_seconds() < 10:
                if self.should_log():
                    logging.info(f"Initial delay in progress for job ID {self.id}.")
                threading.Timer(1, lambda: queue_processor.put(self)).start()
                return
            self.last_checked = current_time

        # Check job status at one-second intervals after the initial delay
        if (current_time - self.last_checked).total_seconds() >= 1:
            self.last_checked = current_time
            self.previous_status = self.status
            self.status = API.check_job_status(self.id)

            if self.should_log():
                logging.info(f"Checked status for job ID {self.id}: {self.status}")

            if self.status == 'COMPLETE':
                self.status = 'completed'
                if self.should_log():
                    logging.info(f"Job ID {self.id} completed, downloading content.")
                API.download_job_content(self.id)
            elif (current_time - self.start_time).total_seconds() > 10000000:
                self.status = 'failed'
                if self.should_log():
                    logging.error(f"Job ID {self.id} failed due to timeout.")
            else:
                threading.Timer(1, lambda: queue_processor.put(self)).start()
        else:
            threading.Timer(1, lambda: queue_processor.put(self)).start()

class JobManager:
    def __init__(self):
        self.jobs = []
        self.active_jobs = 0
        self.lock = threading.Lock()
        self.empty_queue_count = 0  # Counter for empty queue checks


    def run_job(self, job_payloads):
        with self.lock:
            for payload in job_payloads:
                if self.active_jobs < MAX_CONCURRENT_JOBS:
                    job = Job(payload)
                    self.jobs.append(job)
                    job.start()
                    self.active_jobs += 1
                    queue_processor.put(job)
                    logging.info(f"Job {job.id} started.")
                else:
                    self.jobs.append(Job(payload))
                    logging.info("Maximum concurrent jobs reached, job added to queue.")

    def process_queue(self):
        while True:
            all_jobs_done = len(self.jobs) == 0 and self.active_jobs == 0
            if all_jobs_done:
                logging.info("All jobs have been processed. Exiting.")
                break

            try:
                job = queue_processor.get(timeout=RATE_LIMIT_DELAY.total_seconds())
                job.check_status()

                with self.lock:
                    if job.status in ['completed', 'failed']:
                        if job in self.jobs:
                            self.jobs.remove(job)
                        self.active_jobs -= 1
                        logging.info(f"Job ID {job.id} is {job.status}. Active jobs count: {self.active_jobs}")

                        if self.jobs and self.active_jobs < MAX_CONCURRENT_JOBS:
                            next_job = self.jobs.pop(0)
                            next_job.start()
                            self.active_jobs += 1
                            queue_processor.put(next_job)
                            logging.info(f"Started next job ID {next_job.id}.")
            except Empty:
                self.empty_queue_count += 1
                logging.info(f"Queue is empty, waiting for jobs. Empty count: {self.empty_queue_count}")
                if self.empty_queue_count > 10:
                    logging.info("Queue has been empty for 10 checks. Terminating job processing.")
                    break


job_manager = JobManager()

# Ensure the directory for downloaded images exists
os.makedirs('downloaded_images', exist_ok=True)

def start_processing(job_payloads):
    job_manager.run_job(job_payloads)
    queue_thread = threading.Thread(target=job_manager.process_queue, daemon=True)
    queue_thread.start()
    queue_thread.join()  # Wait for the queue_thread to finish
    logging.info("All jobs completed.")