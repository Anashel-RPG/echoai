# Trigger.py
import openai
import threading
import config
import re
import random

# Set your API key
api_key = config.OPENAI_API_KEY

# Create an OpenAI client instance with the API key
client = openai.Client(api_key=api_key)


def get_ongoing_conversation():
    # Capture a set of sentence
    num_sentences_to_capture = 5

    try:
        # Read the content of the conversation
        with open("config-files/conversation-capture.txt", "r", encoding='utf-8') as file:
            text = file.read()

        # Split the text into sentences
        sentences = re.split(r'(?<=[.!?]) +', text)

        # Ensure there are enough sentences to extract
        if len(sentences) < num_sentences_to_capture:
            return "Generate a lore sentence for a science fiction game"

        # Randomly select a starting index
        start_index = random.randint(0, len(sentences) - num_sentences_to_capture)

        # Capture the specified number of successive sentences
        conversation_capture = ' '.join(sentences[start_index:start_index + num_sentences_to_capture])
    except Exception as e:
        print(f"An error occurred: {e}")
        conversation_capture = "Generate a lore sentence for a science fiction game"

    try:
        print(f"Source Material: {conversation_capture}")
        # Create a completion request using the client

        #######################
        # FIRST PASS SETTINGS #
        #######################
        response = client.completions.create(
            model="text-davinci-003",  # Specify the model
            prompt=f"""
                    Take this text: "{conversation_capture}" and do the following:
                    1. Translate this in english and shorten it in 3 sentence: 
                    2. Remove all mention of character or person name. 
                    3. If the summary include a creature or a human, make an visually interesting description and add focus on it's clothing and surrounding. Avoid having a character holding item.
                    4. If the sentence focus more on the location, provide details of the scene content and ambiance
                    """,
            max_tokens=150
        )

        # Extract the response content
        conversation_result = response.choices[0].text.strip()
        print(f"CONVERSATION CAPTURED: {conversation_result}")

    except Exception as e:
        print(f"An error occurred: {e}")
        scene_description = "Error in generating content"

    return conversation_result


def update_trigger_file():
    universe = config.UNIVERSE

    wild_card_theme = get_ongoing_conversation()

    try:
        # Create a completion request using the client

        ########################
        # SECOND PASS SETTINGS #
        ########################
        response = client.completions.create(
            model="text-davinci-003",  # Specify the model
            prompt=f"""
                    We need to transform into a one line scene description the main concept of the following sentence: "{wild_card_theme}". Using this as a reference, generate 1 new scene description of maximum 15 words. The scene description should be rich and vivid, focusing on either a character clothing or a specific location. Include specific adjective to create and evocative visual. Avoid generalizations and aim for the richness and vivid specificity.

                        The description should follow similar structure as these example:
                        - hoodie with arcane symbols and short skirt
                        - secret agent wearing undead queen bone armor
                        - subway terminal to nowhere
                        - beautiful satanic female necromancer blood queen ritualistic neck tattoo
                        - Assassins creed agent blond girl with black leather fishnet leg wearing gold and white hood with battle high heel boots
                        - a stone angel stands with its eyes covered
                        - arcane satanic engraving in the city road
                        - beautiful model with half computer code body and half human in a combat zone
                        - street of tokyo under quarantine of catastrophic supernatural event
                        - portrait of a realistic doll with porcelain kintsugi skin cracked skin
                        - dark gold theme dark noir style detailed beautiful face portrait of a girl in liquid red short liquid dress on the street
                        - action pose beautiful pale skin girl supermodel glamour shot wearing short skirt with and high leather boot and scruffy hair
                    
                    Include very unique aesthetic attribute as seen in these example and ensure it's always visually appealing. Avoid abstract word or fiction name. Do not include any other information other then the scene in one line. DO NOT UNDER ANY CONDITION ADD PREFIX OR SUFFIX OR LINE BEFORE AND AFTER THE OUTPUT.
                        """,
            max_tokens=150
        )

        # Extract the response content
        openai_response = response.choices[0].text.strip()

        # 1. Strip everything before and including the first colon, if it exists
        if ':' in openai_response:
            openai_response = openai_response.split(':', 1)[1].strip()

        # 2. Remove line breaks and carriage returns
        openai_response = openai_response.replace('\n', ' ').replace('\r', ' ')

        # 3. Remove all punctuation
        openai_response = re.sub(r'[^\w\s]', '', openai_response)

        scene_description = openai_response + " " + universe
        print(f"Scene Summary: {scene_description}")

    except Exception as e:

        print(f"An error occurred: {e}")

        scene_description = "Error in generating content"

    # Use the file path from config.py
    file_path = config.TRIGGER_FILE_PATH

    # Update the file
    with open(file_path, 'w') as file:
        file.write(scene_description)

def start_trigger_update():
    # Start the update_trigger_file function as a background thread
    update_thread = threading.Thread(target=update_trigger_file)
    update_thread.start()
