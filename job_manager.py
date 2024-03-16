# job_manager.py
import threading
import time
import os
import json
import requests
import config
import logging
from colorama import init, Fore, Style
import conversation
from queue import Queue, Empty
from datetime import datetime
from image_downloader import download_image
from config import MAX_CONCURRENT_JOBS, RATE_LIMIT_DELAY, API_BASE_URL, HEADERS, API_CALL_DELAY
from job_data_store import get_job_data, store_job_data

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class API:
    total_api_credit_cost = 0  # Class-level variable to track the total cost
    total_images = 0  # Class-level variable to track the total images
    @staticmethod
    def manipulate_content(content):
        logging.info("STATICMETHOD API [manipulate_content]")
        manipulated_content = conversation.generate_scene(content)
        logging.info("Manipulation Content Completed")
        return manipulated_content

    @staticmethod
    def start_job(data):
        logging.info("STATICMETHOD API [start_job]")
        time.sleep(config.RPS_Sleep)
        url = 'https://ws.echoai.space/jobs/create'
        headers = HEADERS
        payload = json.dumps(data)
        try:
            logging.info("Calling Echoai GENERATE")
            logging.info("======")
            logging.info(f"API Payload {payload}")
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            job_response = response.json()

            # Updated to match new response structure
            job_id = job_response.get('jobId')

            logging.info(f"API Response for Job Creation: {json.dumps(job_response, indent=2)}")

            if job_id:
                print(f"Job started with ID: {job_id}")
                # If apiCreditCost is not provided, remove the related code
                # API.total_api_credit_cost += api_credit_cost
                API.total_images += 1
                logging.info(f"== TOTAL IMAGES: {API.total_images} ==")
                store_job_data(job_id, data['prompt'])
                return job_id
            else:
                logging.error("Failed to start job: No 'jobId' found in response.")
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
        logging.info("STATICMETHOD API [check_job_status]")
        time.sleep(config.RPS_Sleep)
        url = f'https://ws.echoai.space/jobs/{job_id}'
        headers = HEADERS

        try:
            logging.info(f"Calling Echoai STATUS for job ID {job_id}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            job_status_response = response.json()
            print(f"API Response for Job {job_id}: {job_status_response.get('status')}")
            print(job_status_response)

            status = job_status_response.get('status', 'UNKNOWN').lower()
            if status in ['pending', 'success', 'error']:
                if status == 'success':
                    image_urls = job_status_response.get('images', [])
                    return status.upper(), image_urls
                else:
                    return status.upper(), None
            else:
                return 'UNKNOWN', None

        except requests.exceptions.HTTPError as e:
            logging.error(f"Error checking job status for ID {job_id}: {e}")
            return 'FAILED', None
        except Exception as e:
            logging.error(f"Error checking job status for ID {job_id}: {e}")
            return 'UNKNOWN', None

    @staticmethod
    def download_job_content_directly(job_id, image_urls, prompt):
        logging.info("STATICMETHOD API [download_job_content_directly]")
        try:
            logging.info(f"Attempting to download content for job ID {job_id}")
            for image_url in image_urls:
                if image_url:
                    download_image(image_url, "downloaded_images", job_id, prompt, {})
        except Exception as e:
            logging.error(f"Error downloading content for job ID {job_id}: {e}")

    @staticmethod
    def download_job_content(job_id):
        logging.info("STATICMETHOD API [download_job_content]")
        url = f'https://ws.echoai.space/jobs/{job_id}'
        headers = HEADERS

        try:
            logging.info(f"Calling Echoai CDN DOWNLOAD for job ID {job_id}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            job_content_response = response.json()
            # logging.info(f"Received job content response: {job_content_response}")

            if job_content_response.get('status') != 'success':
                logging.error(f"Failed to download content for job ID {job_id}: Status is not 'success'")
                return

            image_urls = job_content_response.get('images', [])
            logging.info(f"Attempting to download content for job ID {job_id}")

            job_data = get_job_data(job_id)

            if job_data:
                for image_url in image_urls:
                    if image_url:
                        download_image(image_url, "downloaded_images", job_id, job_data['prompt'], {})
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
        self.image_urls = []

    def start(self):
        logging.info("CLASS JOB [start]")
        self.id = API.start_job(self.data)
        self.start_time = datetime.now()

        if self.id:
            store_job_data(self.id, self.data['prompt'])
            self.status = 'processing'
        else:
            # Retry once if the job fails to start
            logging.info("== WARNING RETRY ==")
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
        logging.info("CLASS JOB [should_log]")
        """Determines if the current status should be logged."""
        current_time = datetime.now()
        if self.previous_status != self.status or (
                self.last_log_time is None or (current_time - self.last_log_time).total_seconds() > 10):
            self.last_log_time = current_time
            return True
        return False

    def check_status(self):
        logging.info("CLASS JOB [check_status]")

        # Check if the job is already completed to prevent repeated downloads ### change (added completion check)
        if self.status == 'completed':
            logging.info(f"Job ID {self.id} is already completed. Skipping further checks.")
            return

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
            status, image_urls = API.check_job_status(self.id)  # Unpack the tuple

            if self.should_log():
                logging.info(f"Checked status for job ID {self.id}: {status}")

            if status == 'SUCCESS':
                self.status = 'completed'
                if image_urls:
                    API.download_job_content_directly(self.id, image_urls, self.data['prompt'])
            elif status == 'FAILED' or (current_time - self.start_time).total_seconds() > 10000000:
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
        logging.info("CLASS JOBMANAGER [run_job]")
        with self.lock:
            while job_payloads:  # Loop until all payloads are processed
                payload = job_payloads.pop(0)  # Remove the first payload from the list
                if self.active_jobs < MAX_CONCURRENT_JOBS:
                    job = Job(payload)
                    self.jobs.append(job)
                    job.start()
                    self.active_jobs += 1
                    queue_processor.put(job)
                    logging.info(f"Job {job.id} started.")
                else:
                    self.jobs.append(Job(payload))

    def output_all_jobs(self):
        logging.info("Outputting all jobs:")
        for job in self.jobs:
            logging.info(f"Job ID: {job.id}, Status: {job.status}")

    def process_queue(self):
        logging.info("CLASS JOBMANAGER [process_queue]")
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
    logging.info("CLASS [start_processing]")
    job_manager.run_job(job_payloads)
    job_manager.output_all_jobs()
    queue_thread = threading.Thread(target=job_manager.process_queue, daemon=True)
    queue_thread.start()
    queue_thread.join()  # Wait for the queue_thread to finish
    logging.info("All jobs completed.")