# config.py
from datetime import timedelta
import logging
import json
import time
import random

import config

### VALUE YOU WANT TO PROVIDE ###

# Forcing a universe is useful when working with Conversation or Audio mode
# This will be added at the start of your scene
# Ex: FORCE_UNIVERSE = "In a post-apocalyptic world, "
FORCE_UNIVERSE = ""

# If you wish to change the negative prompt
NEGATIVE = "(worst quality, low quality, normal quality:2), blurry, bad quality, watermark, logo, (text)"

# When using override mode; set your prefix and suffix to force a style to your scene
# Ex: SCENE = "diablo 4 concept art of <SCENE>, realistic heavy details watercolor ink and acrylic, Boken"

SCENE = "12k hyper realistic <SCENE>, role playing game, stunning visual masterpiece (double exposure), RAW photo, depth of field, illuminated, film grain super 8mm"

# When using override mode; Force a specific Style
# Style Options: "BOKEH", "CINEMATIC", "CREATIVE", "FASHION", "FILM", "FOOD", "HDR",
# "LONG EXPOSURE", "MACRO", "MONOCHROME", "MOODY", "NEUTRAL", "PORTRAIT", "RETRO",
# "STOCK PHOTO", "UNPROCESSED", "VIBRANT", "NONE"

STYLE = "CINEMATIC"

# Location of the prompt scene and structure csv you wish to used
SCENES_FILE_PATH = 'config-files/scene.csv'
STRUCTURE_CSV_PATH = 'config-files/structure.csv'

### END OF CUSTOM VALUE ###

### SCROLL AT THE END OF THE FILE TO ENTER YOUR API KEY ###
### WARNING: If you are streaming on Youtube or Twitch, DO NOT SCROLL =) ###

############## LAUNCH WITH WIZARD MODE vs CONFIG FILE
WIZARD = 1

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Customize your CONFIG if you don't want to use the wizard at launch
# WARNING: some combination of config value won't work
# Fore example, using broadcast mode with override mode will not work
# Echoai can also work with Dalle, CivitAI, Prodia and a Midjourney provider
# But this is a beta features and might not work as expected.

############## RANDOM PROVIDER
RANDOM_MODE = 0
BROADCAST_MODE = 0

############## START OF THE VARIABLE YOU CAN CHANGE
RENDER_MODE = "Leonardo"
# RENDER_MODE = "Prodia"
# RENDER_MODE = "Civitai"
# RENDER_MODE = "Midjourney"
# RENDER_MODE = "Dalle"

# Number of times we generate all image from the scene list
NUM_ITERATIONS = 1
MAX_CONCURRENT_JOBS = 5
RPS_Sleep = 0.5

# 16:9 Landscape Format
IMAGE_WIDTH = 1360
IMAGE_HEIGHT = 768

# 9:16 Portrait Format
# IMAGE_WIDTH = 896
# IMAGE_HEIGHT = 1216
# IMAGE_WIDTH = 768
# IMAGE_HEIGHT = 1024

METAINFO = False
SAMPLER = "DPM++ 2M Karras"
PRODIA_RATE = 0.7
MIDJOURNEY_RATE = 0.4
DALLE_RATE = 0.8
LEONARDO_RATE = 1

## Conversation Mode :
# If you want to generate image using sentence from the config-files/conversation-capture.txt
# Set USE_TRIGGER_FILE to True and it will process that conversation sequentially
# If you set RANDOM_READ to True, it will use random passage from it
# Set it to False to generate all image from your config-files/scene.csv file
CONVERSATION_MODE = False
AUDIO_MODE = False
RANDOM_READ = False

# Deep analysis with GPT 4 or fast with GPT 3
DEEP = True

## Slideshow :
# Set to True to see full screen image
# As they get downloaded in /downloaded_images
SLIDESHOW_ENABLED = False
FADE_SPEED = 0.01

############## END OF THE VARIABLE YOU CAN CHANGE

# Loading your override preference from config-files/override.txt
# Modified load_override_settings function
def load_override_settings(render_mode):
    with open('config-files/override.txt', 'r') as file:
        lines = file.readlines()
    settings = {}
    for line in lines:
        if line.startswith('#') or not line.strip():
            continue
        key, value = line.split('=')
        settings[key.strip()] = value.strip().strip('"')

    # Initialize default values
    override = settings.get("OVERRIDE") == "True"
    realistic_mode = settings.get("REALISTIC_MODE") == "True"
    style_mode = ""

    if render_mode == "Midjourney":
        model_mode = settings.get("REALISTIC_MODEL_MIDJOURNEY") if realistic_mode else settings.get("CREATIVE_MODEL_MIDJOURNEY")
    elif render_mode == "Leonardo":
        style_mode = STYLE
        model_mode = settings.get("REALISTIC_MODEL_LEONARDO") if realistic_mode else settings.get("CREATIVE_MODEL_LEONARDO")
    elif render_mode == "Prodia":
        style_mode = settings.get("STYLE_PRODIA")
        model_mode = settings.get("REALISTIC_MODE_PRODIA") if realistic_mode else settings.get("CREATIVE_MODEL_PRODIA")
    elif render_mode == "Civitai":
        style_mode = settings.get("STYLE_PRODIA")
        model_mode = settings.get("REALISTIC_MODEL_CIVITAI") if realistic_mode else settings.get("CREATIVE_MODEL_CIVITAI")
    elif render_mode == "Dalle":
        model_mode = ""
    else:
        # Default or error handling
        style_mode = ""
        model_mode = ""

    globals()['OVERRIDE_MODE'] = override
    globals()['REALISTIC_MODE'] = realistic_mode
    globals()['OVERRIDE_STRING'] = SCENE
    globals()['OVERRIDE_STYLE'] = style_mode
    globals()['OVERRIDE_MODEL'] = model_mode

# Load RENDER_MODE and then call load_override_settings with it
load_override_settings(RENDER_MODE)

# File paths
TRIGGER_FILE_PATH = 'config-files/trigger.txt'
IMAGE_FOLDER_PATH = 'downloaded_images'
CONFIG_FILE_PATH = 'config-files/leonardo.json'
CONVERSATION_FILE_PATH = "config-files/conversation-capture.txt"
OVERRIDE_PATH = 'config-files/override.txt'
INPUT_PATH = "input/"
FILE_CACHE = "config-files/cached_scenes.json"
GOOD_DIR = 'ranking_good'
BAD_DIR = 'ranking_bad'

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
# And control the API setting, timeout, etc...
JOB_TIMEOUT = timedelta(minutes=60)
JOB_STATUS_CHECK_DELAY = timedelta(seconds=30)
RATE_LIMIT_DELAY = timedelta(seconds=2)
API_CALL_DELAY = 2

## Array of model to use randomly
LEONARDO_MODEL_IDS = '["5c232a9e-9061-4777-980a-ddc8e65647c6", "aa77f04e-3eec-4034-9c07-d0f619684628", "1e60896f-3c26-4296-8ecc-53e2afecc132"]'

PRODIA_MODEL_IDS = '''[
  "dreamshaperXL10_alpha2.safetensors [c8afe2ef]",
  "dynavisionXL_0411.safetensors [c39cc051]",
  "juggernautXL_v45.safetensors [e75f5471]",
  "realismEngineSDXL_v10.safetensors [af771c3f]"
]'''

CIVITAI_MODEL_IDS = '''[
  "urn:air:sdxl:model:civitai:133005@240840",
  "urn:air:sdxl:model:civitai:3671@24073",
  "urn:air:sdxl:model:civitai:4384@128713",
  "urn:air:sdxl:model:civitai:25694@143906",
  "urn:air:sdxl:model:civitai:7240@119057"
]'''

## Array of style to use randomly

LEONARDO_STYLES = '''[
"CINEMATIC",
"CREATIVE",
"PHOTOGRAPHY",
"LEONARDO",
"RAYTRACED",
"VIBRANT"
]'''

LEONARDO_STYLES_ANIME = '''[
"ANIME",
"SKETCH_COLOR"
]'''

LEONARDO_STYLES_FULL = '''[
"Bokeh",
"Cinematic",
"Creative",
"Fashion",
"Film",
"Food",
"HDR",
"Long Exposure",
"Macro",
"Minimalist",
"Monochrome",
"Moody",
"Neutral",
"Portrait",
"Retro",
"Stock Photo",
"Unprocessed",
"Vibrant",
"None"
]'''

PRODIA_STYLES = '''[
"anime",
"cinematic",
"digital-art",
"neon-punk",
"photographic"]'''

PRODIA_SAMPLER = '''[
  "Euler",
  "Euler a",
  "LMS",
  "Heun",
  "DPM2",
  "DPM2 a",
  "DPM++ 2S a",
  "DPM++ 2M",
  "DPM++ SDE",
  "DPM fast",
  "DPM adaptive",
  "LMS Karras",
  "DPM2 Karras",
  "DPM2 a Karras",
  "DPM++ 2S a Karras",
  "DPM++ 2M Karras",
  "DPM++ SDE Karras"]'''

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


################ PROJECT GLOBAL VARIABLE AND SETUP
# Define a job ID for this project
timestamp = time.strftime("%Y_%m_%d_%H_%M")
random_number = random.randint(1000, 9999)
JOB = f"{timestamp}_{random_number}"
JOB_FOLDER = f"./output/{JOB}"


############## API KEY

# API settings LEONARDO
API_BASE_URL = 'https://cloud.leonardo.ai/api/rest/v1/'
LEONARDO_TOKEN = "ENTER-API-KEY-HERE"
AUTHORIZATION_TOKEN = f'Bearer {LEONARDO_TOKEN}'

# API settings OPENAI
OPENAI_API_KEY = "ENTER-API-KEY-HERE"

# API Settings TENSORART
URL = "ap-east-1.tensorart.cloud"
APP_ID = "ENTER-API-KEY-HERE"
PRIVATE_KEY_PATH = "input/tensorart_private_key.pem"

# API Settings CivitAI
CIVITAI_TOKEN = "ENTER-API-KEY-HERE"

# API Settings PRODIA
PRODIA_TOKEN = "ENTER-API-KEY-HERE"

# API Settings Mirdjourney
MIDJOURNEY_TOKEN = "ENTER-API-KEY-HERE"

# API Settings Dalle
DALLE_TOKEN = "ENTER-API-KEY-HERE"

# Headers with the authorization token for API calls
HEADERS = {
     "accept": "application/json",
     "authorization": AUTHORIZATION_TOKEN
 }