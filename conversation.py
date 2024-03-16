# Conversation.py
import openai
import config
import os
import json
import re

# Set your API key
api_key = config.OPENAI_API_KEY

# Create an OpenAI client instance with the API key
client = openai.Client(api_key=api_key)

def prepare_scene(content):
    # First Pass
    pass_prompt = content

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "text"},
        messages=[
            {"role": "system",
             "content": f"""
             You must analyze a text and help the user structure it to be used as a prompt in an image generation AI.
             Ensure the summary is in English and limited to 300 tokens. Analyze the provided and make a summary that describe the scene for a mood board.
             Enrich the description to make a high quality concept art but do not loose any details of the scene.
             The goal is to create a vivid, engaging, and detailed scene, using rich and descriptive language to bring the scene to life vividly.
             """},
            {"role": "user", "content": pass_prompt}
        ])

    # Extracting text content from the response
    conversation_capture = response.choices[0].message.content
    conversation_capture = ' '.join([line.strip() for line in conversation_capture.split('\n') if line.strip()])

    return conversation_capture

def generate_scene(content, context):
    universe = config.FORCE_UNIVERSE
    print(f"Original Material: {content}")

    preprod_result = prepare_scene(content)

    print(f"Pass #1: {preprod_result}")

    if preprod_result is None:
        return None

    # Second Pass
    pass_prompt = preprod_result

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "text"},
        messages=[
            {"role": "system",
             "content": f"""
             Condense this text in one sentence of 50 words with no punctuation.
             Structure it to be used as a prompt in an image generation AI.
             Do not loose any of the key elements that define the scene main subject and the scene location.
             Ensure that you take account fo the following context to keep a consistency. The context is: '{context}'
             """},
            {"role": "user", "content": pass_prompt}
        ])

    # 1. Strip everything before and including the first colon, if it exists
    conversation_result = response.choices[0].message.content
    conversation_result = ' '.join([line.strip() for line in conversation_result.split('\n') if line.strip()])

    # 2. Remove line breaks and carriage returns
    conversation_result = conversation_result.replace('\n', ' ').replace('\r', ' ')

    # 3. Remove all punctuation
    conversation_result = re.sub(r'[^\w\s]', '', conversation_result)

    scene_description = conversation_result + " " + universe
    print(f"Pass #2: {scene_description}")

    # Read existing data
    if os.path.exists(config.FILE_CACHE):
        with open(config.FILE_CACHE, 'r', encoding='utf-8') as file:
            try:
                cached_scenes = json.load(file)
            except json.JSONDecodeError:
                cached_scenes = []
    else:
        cached_scenes = []

    # Append new data
    cached_scenes.append(scene_description)

    # Write back to the file
    with open(config.FILE_CACHE, 'w', encoding='utf-8') as file:
        json.dump(cached_scenes, file, indent=4)

    return scene_description