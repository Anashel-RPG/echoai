# job_data_store.py
import logging

# Reducing the chance of repeat image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global dictionary to store job data
job_data_store = {}
logging.info(f"Job data store reset")

def store_job_data(job_id, prompt):
    global job_data_store
    job_data_store[job_id] = {
        "prompt": prompt
    }
    # logging.info(f"Job data stored: ID {job_id}, Prompt {prompt[:30]}...")

    # Log the current state of the job_data_store
    # logging.info(f"Current state of job_data_store: {job_data_store}")

def get_job_data(job_id):
    global job_data_store
    data = job_data_store.get(job_id)
    if data:
        logging.info(f"Retrieved job data for ID {job_id}: {data}")
    else:
        logging.warning(f"No job data found for ID {job_id}")
    return data
