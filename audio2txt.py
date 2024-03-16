# audio2txt.py
import os
import json
import config
import requests
import platform
from colorama import init, Fore, Style
from preprocess.summary import genSummary
from preprocess.scene import loadScene
import soundfile as sf
import numpy as np

def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def process_audio2txt():
    #### SETTING UP ####
    init()  # Initialize colorama
    os.environ['TERM'] = 'xterm-256color'

    ### GENERATE SUMMARY ###
    # Create an output folder with the new name
    file_path = "./output/" + config.JOB
    os.makedirs(file_path, exist_ok=True)

    # Check if the input directory exists
    if os.path.exists(config.INPUT_PATH):
        # List all .wav files in the directory
        wav_files = [f for f in os.listdir(config.INPUT_PATH) if f.endswith('.wav')]
        # Sort files by modification time in descending order
        wav_files.sort(key=lambda x: os.path.getmtime(os.path.join(config.INPUT_PATH, x)), reverse=True)
        if wav_files:
            # Set file_name to the most recent .wav file
            file_name = os.path.join(config.INPUT_PATH, wav_files[0])
            print(f"Most recent .wav file: {file_name}")
        else:
            print("No .wav files found in the directory.")
            exit(1)
    else:
        print("The specified input directory does not exist.")
        exit(1)

    ## Translate entire wav
    print(Fore.LIGHTBLACK_EX + "Converting Audio to Text")
    transcript = translate_audio(file_name)

    # Format the transcript by adding a line break after each period
    formatted_transcript = transcript.replace('. ', '.\n')

    # Write the transcript to the file
    with open(file_path + "/audio2txt.txt", 'w') as file:
        file.write(formatted_transcript)

    ### GENERATE SUMMARY ###
    story_payload = genSummary(file_path)

    #### BUILD OUR SCENE ####
    print("Building the scene")
    # Assuming story_payload is a dictionary that contains 'sentences' and other keys
    story_payload = json.loads(story_payload)

    # Initialize an empty list for scenes
    scenes = loadScene(story_payload)

    #### SAVE THE FILE ####
    job_folder = config.JOB_FOLDER  # Ensure this is correctly pointing to your desired folder

    # Create the directory if it doesn't exist
    os.makedirs(job_folder, exist_ok=True)

    output_file_path = os.path.join(job_folder)
    print("output_file_path:" + output_file_path)

    # Writing to JSON file
    with open((output_file_path + '/02-Scene.json'), 'w', encoding='utf-8') as file:
        json.dump(scenes, file, indent=4, ensure_ascii=False)

    # Writing to CSV file
    csv_file_path = os.path.join(output_file_path, '02-Scene.csv')
    with open(csv_file_path, 'w', encoding='utf-8') as file:
        file.write('Scene Description\n')  # Writing the header

        for scene in scenes:
            # file.write(scene['prompt'])
            file.write(scene['preprod'] + '\n')  # Write the prompt
            file.write(scene['prompt'] + '\n')  # Write the prompt
            file.write(scene['original'])  # Write the original

            # Check if this is the last scene to avoid writing an extra newline at the end
            if scene != scenes[-1]:
                file.write('\n')  # Write an empty line only if it's not the last scene

    print("Scene Completed")
    print("====================================")
    return scenes


def convert_to_mono_and_reduce_bitrate(file_path, target_path="temp_converted_file.wav"):
    data, samplerate = sf.read(file_path)
    if data.ndim > 1:  # Check if audio is stereo
        data = np.mean(data, axis=1)  # Convert to mono by averaging both channels

    sf.write(target_path, data, samplerate, format='WAV', subtype='PCM_16')
    return target_path

def translate_audio(file_path, model="whisper-1", language="en"):
    url = "https://api.openai.com/v1/audio/translations"
    headers = {
        "Authorization": f"Bearer {config.OPENAI_API_KEY}"
    }

    # Convert and reduce the size of the audio file
    converted_file_path = convert_to_mono_and_reduce_bitrate(file_path)

    try:
        with open(converted_file_path, 'rb') as audio_file:
            files = {
                'file': (converted_file_path, audio_file, 'audio/wav'),
                'model': (None, model),
                'language': (None, language)
            }
            response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            response_data = response.json()
            text = response_data.get('text')
        else:
            print(f"Failed to translate audio: {response.status_code} - {response.text}")
            text = None
    except Exception as e:
        print(f"An error occurred during translation: {e}")
        text = None
    finally:
        # Cleanup action: Delete the temporary converted file
        os.remove(converted_file_path)
        return text