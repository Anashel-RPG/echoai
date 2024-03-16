# process.py
import glob
import os
import config
import logging
import json
from job_manager import start_processing
from file_reader import read_structure_parameters, read_scene_descriptions
from job_payload_creator import create_job_payloads
from audio import process_audio_file

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def start_slideshow():
    image_screen = ImageScreen(config.IMAGE_FOLDER_PATH)
    image_screen.start()

def read_trigger_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

def start_process(audio_scenes):
    logging.info("Script started.")

    # Preparing the download folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_folder = os.path.join(script_dir, 'downloaded_images')
    try:
        os.makedirs(download_folder, exist_ok=True)
    except Exception as e:
        logging.error(f"Error creating the downloaded images folder: {e}")

    # Initialize scene_descriptions and a flag for cached scenes
    # scene_descriptions = {}

    # Check for conversation mode and audio mode first
    if config.CONVERSATION_MODE:
        print("Conversation Mode Started")

        if config.AUDIO_MODE:
            print("Audio Mode Started")
            prompts = [scene['prompt'] for scene in audio_scenes]  # Extract prompts
            scene_descriptions = {"Scene Description": prompts}

        else:
            # Handle conversation mode without audio
            print("Conversation Mode with No Audio")
            with open("config-files/conversation-capture.txt", 'r', encoding='utf-8') as file:
                text = file.read()
            sentences = text.replace('\n', ' ').split('.')
            min_length = 10
            conversation_sentences = [
                sentence.strip() for sentence in sentences
                if len(sentence.split()) > min_length and not sentence.endswith('.')
            ]
            scene_descriptions = {"Scene Description": conversation_sentences}

        if os.path.exists(config.FILE_CACHE):
            # Check for cached scenes
            logging.info("Processing Cache")
            with open(config.FILE_CACHE, 'r', encoding='utf-8') as file:
                cached_scenes = json.load(file)
                scene_descriptions = {"Scene Description": cached_scenes}
                scenes_cached = True
    else:
        print("Processing Scene from CSV")
        # Fetch scene CSV data as a fallback
        scene_descriptions = read_scene_descriptions(config.SCENES_FILE_PATH)

    logging.info("Done processing")
    print("!!=======!!")
    print(scene_descriptions)
    print("!!=======!!")

    # Calculate total_images_to_generate
    total_images_to_generate = len(scene_descriptions['Scene Description']) * config.NUM_ITERATIONS

    print(f"Images to Generate: {total_images_to_generate}")

    structure_params = read_structure_parameters(config.STRUCTURE_CSV_PATH)
    job_payloads, prompts = create_job_payloads(structure_params, scene_descriptions, total_images_to_generate, api_type='default')
    assert job_payloads, "No job payloads were created."

    start_processing(job_payloads) # Start processing the jobs

    print("Job Completed")

    if config.SLIDESHOW_ENABLED:
        slideshow_process.join()
