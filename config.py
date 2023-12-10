# config.py
from datetime import timedelta
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

## Trigger File :
# Set to True if you want to generate image
# Using random portion from the conversation-capture.txt
# Set to False to generate all image from the scene.csv file
USE_TRIGGER_FILE = False

## Slideshow :
# Set to True to see full screen image
# As they get downloaded in /downloaded_images
SLIDESHOW_ENABLED = False
FADE_SPEED = 0.01

## Conversation Mode
UNIVERSE = "in the dark world of lovecraft"

# OVERRIDE SETTINGS
# Uncomment to enable override
# This will stop using randomized value from structure.csv
# And force theses to the Scene prompt

# OVERRIDE_STYLE = "RAYTRACED"
# OVERRIDE_STRING = "high perspective close-up view <SCENE>, glowing skin and surface, RAW photo, main color is black and white and yellow ink, cement with metal rod, Octane render 4k ultra high definition, Bird Eye Angle, Gritty urban reality"
# OVERRIDE_MODEL = "5c232a9e-9061-4777-980a-ddc8e65647c6" # Realistic
# OVERRIDE_MODEL = "1e60896f-3c26-4296-8ecc-53e2afecc132" # Creative

## When trigger file is False
# Number of times we generate all image from the scene list
NUM_ITERATIONS = 1

# 16:9 Landscape Format
IMAGE_WIDTH = 1360
IMAGE_HEIGHT = 768

# 4:3 Landscape Format
# IMAGE_WIDTH = 1024
# IMAGE_HEIGHT = 768

# Portrait Format
# IMAGE_WIDTH = 768
# IMAGE_HEIGHT = 1360

# File paths
TRIGGER_FILE_PATH = 'config-files/trigger.txt'
IMAGE_FOLDER_PATH = 'downloaded_images'
STRUCTURE_CSV_PATH = 'config-files/structure.csv'
SCENES_FILE_PATH = 'config-files/scene.csv'
CONFIG_FILE_PATH = 'config-files/leonardo.json'

# Initialize config_data as None
config_data = None

# Load configuration data
try:
    with open(CONFIG_FILE_PATH, 'r') as file:
        config_data = json.load(file)
except Exception as e:
    print(f"Error occurred while reading the file: {e}")
    raise

## When trigger file is False
# You can set up to 4 concurrent image processing thread
# And control the API setting, timeout, etc...
MAX_CONCURRENT_JOBS = 1
JOB_TIMEOUT = timedelta(minutes=60)
JOB_STATUS_CHECK_DELAY = timedelta(seconds=30)
RATE_LIMIT_DELAY = timedelta(seconds=2)
API_CALL_DELAY = 3

## Array of model to use randomly
MODEL_IDS = '["5c232a9e-9061-4777-980a-ddc8e65647c6", "1e60896f-3c26-4296-8ecc-53e2afecc132"]'

## If your leonardo.jsonf failed to load locally
# Leonardo settings
ALCHEMY = config_data.get("ALCHEMY", True)
CONTRAST_RATIO = config_data.get("CONTRAST_RATIO", 0.5)
PROMPT_MAGIC = config_data.get("PROMPT_MAGIC", True)
PROMPT_MAGIC_STRENGTH = config_data.get("PROMPT_MAGIC_STRENGTH", 0.5)
PROMPT_MAGIC_VERSION = config_data.get("PROMPT_MAGIC_VERSION", "v3")
PUBLIC = config_data.get("PUBLIC", False)
SCHEDULER = config_data.get("SCHEDULER", "LEONARDO")
NSFW = config_data.get("NSFW", True)
NUM_IMAGES = config_data.get("NUM_IMAGES", 1)
PRESET_STYLE = config_data.get("PRESET_STYLE", "RAYTRACED")
PHOTOREALSTRENGTH = config_data.get("PHOTOREALSTRENGTH", 0.55)
EXPANDED_DOMAIN = config_data.get("EXPANDED_DOMAIN", False)
GUIDANCE_SCALE = config_data.get("GUIDANCE_SCALE", 15)
NUM_INFERENCE_STEPS = config_data.get("NUM_INFERENCE_STEPS", 10)
HIGH_CONTRAST = config_data.get("HIGH_CONTRAST", True)
WEIGHTING = config_data.get("WEIGHTING", 0.75)
SD_VERSION = config_data.get("SD_VERSION", "v1_5")
PHOTO_REAL = config_data.get("PHOTO_REAL", False)

# API settings
API_BASE_URL = 'https://cloud.leonardo.ai/api/rest/v1/'
AUTHORIZATION_TOKEN = 'Bearer [Insert API KEY]'
OPENAI_API_KEY = '[Insert API KEY]'

# Headers with the authorization token for API calls
HEADERS = {
    "accept": "application/json",
    "authorization": AUTHORIZATION_TOKEN
}