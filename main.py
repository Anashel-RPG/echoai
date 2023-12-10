# main.py
from screen import ImageScreen
import json
import time
import shutil
import os
import config
import multiprocessing
import logging
from job_manager import start_processing
from file_reader import read_structure_parameters, read_scene_descriptions
from job_payload_creator import create_job_payloads
from trigger import start_trigger_update


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def start_slideshow():
    image_screen = ImageScreen(config.IMAGE_FOLDER_PATH)
    image_screen.start()

def read_trigger_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

def main():
    logging.info("Script started.")

    # Define the path to the 'downloaded_images' folder relative to the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_folder = os.path.join(script_dir, 'downloaded_images')

    # Clear the 'downloaded_images' folder
    try:
        # if os.path.exists(download_folder):
            # shutil.rmtree(download_folder)
        os.makedirs(download_folder, exist_ok=True)
    except Exception as e:
        logging.error(f"Error creating the downloaded images folder: {e}")

    # Start the slideshow process if enabled
    if config.SLIDESHOW_ENABLED:
        slideshow_process = multiprocessing.Process(target=start_slideshow)
        slideshow_process.start()

    # Read the input files and create the job payloads
    # Fetch scene CSV data
    scene_descriptions = read_scene_descriptions(config.SCENES_FILE_PATH)

    # Fetch structure CSV data
    structure_params = read_structure_parameters(config.STRUCTURE_CSV_PATH)

    if config.USE_TRIGGER_FILE:
        last_content = None
        while True:
            current_content = read_trigger_file(config.TRIGGER_FILE_PATH)
            if current_content != last_content:
                last_content = current_content
                scene_descriptions = {'Scene Description': [current_content]}

                # Create job payloads for a single image
                job_payloads, prompts = create_job_payloads(structure_params, scene_descriptions, 1)
                assert job_payloads, "No job payloads were created."

                logging.info(f"Payload Ready: {job_payloads}")

                # Log example job payload
                # if job_payloads:
                #    logging.info("\nExample Job Payload:")
                #    logging.info(json.dumps(job_payloads[0], indent=4))

                # Start processing the job
                start_processing(job_payloads)

                # Start the trigger update thread
                start_trigger_update()

            time.sleep(1)  # Delay between checks
    else:
        # Calculate the total number of images to generate
        total_images_to_generate = len(scene_descriptions[list(scene_descriptions.keys())[0]]) * config.NUM_ITERATIONS
        logging.info(f"Images to Generate: {total_images_to_generate}")

        job_payloads, prompts = create_job_payloads(structure_params, scene_descriptions, total_images_to_generate)
        assert job_payloads, "No job payloads were created."

        # Log example job payload
        if job_payloads:
            logging.info("\nExample Job Payload:")
            logging.info(json.dumps(job_payloads[0], indent=4))

        # Initialize Job Manager and pass the job list to it
        start_processing(job_payloads) # Start processing the jobs

    logging.info("Script ended.")

    # Wait for the slideshow process to complete before the script ends
    if config.SLIDESHOW_ENABLED:
        slideshow_process.join()

if __name__ == "__main__":
    main()
