# Audio.py
import openai
import config
import requests
import os
import json

# Set your API key
api_key = config.OPENAI_API_KEY

# Create an OpenAI client instance with the API key
client = openai.Client(api_key=api_key)

def translate_audio(file_path, model="whisper-1", language="en"):
    url = "https://api.openai.com/v1/audio/translations"
    headers = {
        "Authorization": f"Bearer {config.OPENAI_API_KEY}"
    }
    try:
        with open(file_path, 'rb') as audio_file:
            files = {
                'file': (file_path, audio_file, 'audio/wav'),
                'model': (None, model),
                'language': (None, language)
            }
            response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            response_data = response.json()
            return response_data.get('text')
        else:
            print(f"Failed to translate audio: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred during translation: {e}")
        return None


def process_audio_file(file_name):
    ## Translate entire ewave
    transcript = translate_audio(file_name)

    # Path to save the transcript
    save_path = 'config-files/audio-translation.txt'

    # Writing the transcript to the file
    with open(save_path, 'w') as file:
        file.write(transcript)
        print(f"Transcript saved to {save_path}")

    # Format the transcript by adding a line break after each period
    formatted_transcript = transcript.replace('. ', '.\n')

    # Backup conversation
    file_path = 'config-files/conversation-capture.txt'

    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the transcript to the file
    with open(file_path, 'w') as file:
        file.write(formatted_transcript)

    save_transcript_to_file(formatted_transcript)


def clean_translation(content, context):
    print(f"Raw Content: {content}")
    # Breakdown in multiple sentence
    pass_prompt = f"""
        Text to breakdown in scene:'{content}'. Summary of the universe of the story: '{context}'
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "Generate a structured scene description focusing on objective elements. Begin with a concise phrase summarizing the scene's core, using no more than 8 words, e.g., 'Futuristic city center with towering architecture at night, full moon, after the rain, reflective surface, wet'. Follow with details in a keyword-focused format, excluding personal names and subjective descriptors. Example details: 'chrome skyscrapers, glass facades, cobblestone pathways, synthetic fiber cloak, ambient neon lighting, clear night sky'. Ensure the description is rich in vocabulary for vivid scene construction without personal names or subjective interpretations. Respond in the following valid JSON structure: "
                           "{"
                           "\"Scene 1\": {"
                           "\"Scene Description\": \"String of 30 words in the following format: Scene core description of maximum 10 words, followed by 8 scene details formatted in a keywords structure\", "
                           "\"Camera Angle\": \"Specify briefly, e.g., 'Close-up' or 'Wide-angle'.\", "
                           "\"Ambiance\": \"Use a few words to describe the mood, e.g., 'Warm', 'Tense'.\", "
                           "\"Additional Details\": \"Include brief details like 'Handheld camera', 'Soft lighting'.\""
                           "}, "
                           "\"Scene 2\": {"
                           "\"Scene Description\": \"String of 30 words in the following format: Scene core description of maximum 10 words, followed by 8 scene details formatted in a keywords structure\", "
                           "\"Camera Angle\": \"Specify briefly, e.g., 'Close-up' or 'Wide-angle'.\", "
                           "\"Ambiance\": \"Use a few words to describe the mood, e.g., 'Joyful', 'Quiet'.\", "
                           "\"Additional Details\": \"Include brief details like 'Steady shot', 'Bright lighting'.\""
                           "}"
                           "} Analyze this conversation and create multiples descriptive scenes."
            },
            {"role": "user", "content": pass_prompt}
        ]
    )

    # Extract the JSON string from the response
    json_string = response.choices[0].message.content

    try:
        # Parse the JSON string
        parsed_json = json.loads(json_string)
        print(f"parsed json: {parsed_json}")

        # Initialize an empty list to store the transformed scenes
        conversation_capture = []

        # Iterate over each scene in the parsed JSON
        for scene, details in parsed_json.items():
            # Construct the scene description string
            scene_description = details['Scene Description'].replace('.', '')
            additional_details = ', '.join([details[key] for key in details if key != 'Scene Description'])
            scene_str = f"{scene_description}, {additional_details}."  # Only add one period at the end

            # Add the constructed string to the conversation capture list
            conversation_capture.append(scene_str)

    except json.JSONDecodeError as e:
        print(f"An error occurred while parsing JSON: {e}")
        conversation_capture = []

    # Join all the scene descriptions into a single string
    clean_translation = " ".join(conversation_capture)

    # Ensure the translation ends with a period
    if not clean_translation.endswith('.'):
        clean_translation += '.'

    return clean_translation


def get_context(content):
    # Breakdown in multiple sentence
    pass_prompt = f"""
        The following is a conversation that was captured: '{content}'.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "text"},
        messages=[
            {
                "role": "system",
                "content": "Provide a summary of the context of this story. Make a sentence that describe what is the overall tone and core elements that need describe the entire text so every time we read a single sentence, we have the context of the full text. Your summary should be descriptive and written in two sentence"
            },
            {"role": "user", "content": pass_prompt}
        ]
    )

    # Extract the JSON string from the response
    context_summary = response.choices[0].message.content

    return context_summary

def save_transcript_to_file(transcript, file_name="config-files/audio-feed.json"):
    # Remove line breaks from the transcript
    transcript = transcript.replace('\n', ' ')

    context = get_context(transcript)
    print(f"Context: {context}")
    print(f"Transcript: {transcript}")

    # Define the file path for the transcript text file
    text_file_path = 'config-files/conversation-capture.txt'

    # Read existing content from the text file
    if os.path.exists(text_file_path):
        with open(text_file_path, "r", encoding='utf-8') as text_file:
            existing_content = text_file.read()
    else:
        existing_content = ""

    # Write the context followed by the existing content to the text file
    with open(text_file_path, "w", encoding='utf-8') as text_file:
        text_file.write("Context: " + context + "\n" + existing_content)

    try:
        # Split the transcript into sentences and remove empty strings
        sentences = [sentence.strip() for sentence in transcript.split('.') if sentence.strip()]

        # Log the number of sentences detected
        print(f"Number of sentences detected: {len(sentences)}")

        # Process sentences in pairs
        processed_sentences = []
        i = 0
        while i < len(sentences):
            # Combine the current sentence with the next one, if available
            if i + 1 < len(sentences):
                combined_sentence = sentences[i] + " " + sentences[i + 1]
                i += 2  # Move to the next pair
            else:
                combined_sentence = sentences[i]
                i += 1  # Move to the last sentence if an odd number of sentences

            cleaned_sentence = clean_translation(combined_sentence, context)
            processed_sentences.append(cleaned_sentence)

        print(f"Processed Sentences: {processed_sentences}")

        # Read existing content from the file
        if os.path.exists(file_name):
            with open(file_name, "r", encoding='utf-8') as file:
                try:
                    existing_content = json.load(file)
                except json.JSONDecodeError:
                    existing_content = []
        else:
            existing_content = []

        # Combine existing content with new processed sentences
        all_content = existing_content + processed_sentences

        # Save the combined content back to the file
        with open(file_name, "w", encoding='utf-8') as file:
            json.dump(all_content, file, indent=2)

    except Exception as e:
        print(f"An error occurred while saving the file: {e}")
