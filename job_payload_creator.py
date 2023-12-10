# job_payload_creator.py
import json
import random
import config
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_job_payloads(structure_params, scene_descriptions, num_images_to_generate):
    logging.info("Creating job payloads...")
    job_payloads = []  # List to store generated job payloads
    prompts = []  # List to store prompts associated with each payload
    used_prompts = set()  # Added to track used prompts

    # Parse MODEL_IDS from config
    model_ids = json.loads(config.MODEL_IDS)

    # random.shuffle(scene_descriptions['Scene Description'])  # Shuffle scene descriptions
    scene_descriptions_list = scene_descriptions['Scene Description']
    for key in structure_params:  # Shuffle each parameter list
        random.shuffle(structure_params[key])

    try:
        scene_index = 0  # Initialize a scene index
        for index in range(num_images_to_generate):
            # scene = random.choice(scene_descriptions['Scene Description'])
            scene = scene_descriptions_list[scene_index % len(scene_descriptions_list)]
            scene_index += 1  # Increment the scene index

            if index >= num_images_to_generate:
                break  # Ensures we don't generate more payloads than needed

            selected_options = {key: random.choice(value) for key, value in structure_params.items() if key != 'Environment'}
            environment = random.choice(structure_params['Environment'])
            prompt = f"{environment} {scene}"

            for key in ['Ambiance', 'Main Style', 'Color Palette', 'Unique', 'Inspiration', 'Camera', 'Effect']:
                if key in selected_options:
                    prompt += f", {selected_options[key]}"

            # Check if the prompt is unique before appending
            if prompt not in used_prompts:
                used_prompts.add(prompt)  # Add the unique prompt to the set
                prompts.append(prompt)  # Append only unique prompts
            else:
                continue  # Skip the current iteration if the prompt is not unique

            # Generate a unique identifier for this job
            # job_id = str(uuid.uuid4())
            # prompt_with_id = f"{job_id}:{prompt}"  # Append the ID to the prompt

            # Define the array of styles in all caps
            styles = ["ANIME", "CINEMATIC", "CREATIVE", "DYNAMIC", "GENERAL",
                      "PHOTOGRAPHY", "RAYTRACED", "3D RENDER", "SKETCH COLOR", "VIBRANT"]

            # Randomly select a style from the array
            # Replace "presetStyle": config.PRESET_STYLE,
            random_style = random.choice(styles)

            # Select a random model ID
            model_id = random.choice(model_ids)

            # Override code. Uncomment to have fixed environment
            if hasattr(config, 'OVERRIDE_STRING'):
                prompt = re.sub("<SCENE>", scene, config.OVERRIDE_STRING)
                random_style = config.OVERRIDE_STYLE
                model_id = config.OVERRIDE_MODEL

            payload = {
                "height": config.IMAGE_HEIGHT,
                "modelId": model_id,
                "prompt": prompt,
                "width": config.IMAGE_WIDTH,
                "alchemy": config.ALCHEMY,
                "contrastRatio": config.CONTRAST_RATIO,
                "promptMagic": config.PROMPT_MAGIC,
                "public": config.PUBLIC,
                "scheduler": config.SCHEDULER,
                "nsfw": config.NSFW,
                "num_images": config.NUM_IMAGES,
                "presetStyle": random_style,
                "photoRealStrength": config.PHOTOREALSTRENGTH,
                "guidance_scale": config.GUIDANCE_SCALE,
                "num_inference_steps": config.NUM_INFERENCE_STEPS,
                "highContrast": config.HIGH_CONTRAST,
                "weighting": config.WEIGHTING,
                "sd_version": config.SD_VERSION,
                "photoReal": config.PHOTO_REAL
            }

            job_payloads.append(payload)  # Append the payload after setting the prompt with UID
            # prompts.append(prompt_with_id)  # Store prompt with ID
            # logging.info(f"Generated payload for scene '{scene}'")

        logging.info(f"Number of job payloads generated: {len(job_payloads)}")

    except Exception as e:
        logging.error(f"An error occurred while generating job payloads: {e}")
        raise

    return job_payloads, prompts
