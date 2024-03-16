# summary.py
import json
import re
from chatgpt import queryGPT
from colorama import Fore, Style

def loadScene(story_payload):
    scenes = []  # Initialize an empty list for scenes
    scenes_rewrite = []  # Initialize an empty list for scenes

    print("== Structuring Sentence")

    # Processing sentences in batches for better structuring
    batch_size = 2  # Adjust the batch size as needed

    for i in range(0, len(story_payload["sentences"]), batch_size):
        batch = story_payload["sentences"][i:i + batch_size]

        numberScenes = len(batch)
        # Instructions
        system_prompt_overview = f"""
                The following are sentences from a story. Please reorganize and describe each scene to create a coherent and sequential series of scenes.
                Scene should not have any dialog and focus on what the an image should show.
                Each scene should be visually descriptive and capture key moments, making it suitable for illustration in a comic book or moodboard.
                You need to make {numberScenes} scene
                Your response should fill in the appropriate values in a JSON structure as follow:
                 {{"scenes": [
                      "Scene description as a string",
                      "Scene description as a string"
                    ]}}
                """

        scene_state_response = queryGPT(system_prompt_overview, json.dumps(batch, indent=4), "json", False)

        if scene_state_response is not None:
            try:
                scene_state = json.loads(scene_state_response)
                if 'scenes' in scene_state:
                    scenes_rewrite.extend(scene_state['scenes'])  # Append scenes to the list
                else:
                    print("No 'scenes' key in JSON response")
            except json.JSONDecodeError:
                print(f"Failed to decode JSON response: {scene_state_response}")

    # Replace the original sentences with the new structured scenes
    # print("Transform raw scene structure:")
    # print(json.dumps(story_payload["sentences"], indent=4))
    # print("Into the following storyboard:")
    # print(json.dumps(scenes_rewrite, indent=4))

    story_payload["sentences"] = scenes_rewrite

    previous_sentence = "This is the first scene"

    # Loop through each sentence
    for i, sentence in enumerate(story_payload["sentences"]):
        # if i < 4 or i > 9:
        #    continue  # Skip to the next iteration without processing the current one

        # Set next sentence based on the current index
        if i < len(story_payload["sentences"]) - 1:
            next_sentence = story_payload["sentences"][i + 1]
        else:
            next_sentence = "No next sentence, this is the last scene"

        print("#### INPUT ####")
        print(sentence)
        print(" ")

        print("===== PASS 1 : Scene analysis")
        # Generate the initial analysis of the sentence
        system_prompt_analysis = f"""
                Analyse this new sentence and provide the following information according to the following JSON structure:
                {{
                  "guidance": "How this sentence should be transform to make it a distinct scene (visual only)", 
                  "isCharacterScene": "Boolean (Indicate if the sentence would be better represent as a focus on a character / creature instead of the visual of a room, a location, or a landscape.)",
                  "hasDialog": "Boolean (Does the story contain dialogue? Answer true or false)",
                  "components": "Array (List major components that should be part of a visual representation of the sentence)"
                }}
                Your response should fill in the appropriate values for each field based on your analysis of the text.
            """
        scene_state_response = queryGPT(system_prompt_analysis, sentence, "json", False)
        try:
            scene_state = json.loads(scene_state_response)
        except json.JSONDecodeError:
            print(f"Failed to decode JSON response: {scene_state_response}")
            continue

        print(json.dumps(scene_state, indent=4))
        print(" ")

        # Skip sentence if it contains dialogue
        # if scene_state.get('hasDialog'):
        #    continue

        # Determine the type of scene to create based on 'isCharacterScene'
        if scene_state['isCharacterScene']:
            system_prompt = """
                    Create a visual scene from the user sentence. Replace character name or individual name with character style. If information is unknown, create keywords. Provide the following information according to the following JSON structure:
                    {
                      "Scene": "Descriptive phrase of maximum 255 characters (Describe the key visual vividly as a cinematic shot)",
                      "Character": "Keywords string maximum 255 characters (Describe the character)",
                      "Background": "Keywords string maximum 255 characters (Describe the background visual vividly as a cinematic shot)",
                      "Hair": "Keywords string maximum 128 characters (Hair color, style and length)",
                      "Ethnicity": "String (Character skin color, gender and ethnicity)",
                      "Age": "Integer (Character age estimate)",
                      "Cloth": "String (Describe the character cloth in 10 words)",
                      "Facial": "String (Describe facial attribute and emotion)",
                      "Unique": "String (Describe unique attribute of the character, including magic effect if applicable)",
                      "Camera": "String (Describe the camera type, lense and angle best use to convey the scene)"
                    }
                    Your response should fill in the appropriate values for each field based on your analysis of the text.
                """
        else:
            system_prompt = """
                    Create a visual scene from the user sentence. If information is unknown, create keywords. Provide the following information following this strict JSON structure:
                    {
                      "Scene": "Descriptive phrase of maximum 255 characters (Describe the key visual vividly as a cinematic shot)",
                      "Background": "Keywords string maximum 255 characters (Describe the background visual vividly as a cinematic shot)",
                      "Condition": "Keywords string maximum 128 characters (Describe the time of day and weather)",
                      "Light": "String (Describe the light ambience, color and style in 10 keywords)",
                      "Unique": "String (Describe unique attribute of the character, including magic effect if applicable)",
                      "Camera": "String (Describe the camera type, lens and angle best use to convey the scene in 10 keywords)"
                    }
                    Your response should fill in the appropriate values for each field based on your analysis of the text.
                """



        print("===== PASS 2 : Scene analysis")
        # Get scene details
        scene_details_response = queryGPT(system_prompt, ("Guidance & direction: " + scene_state.get("guidance", "") +
                                                          " " + sentence), "json", False)
        try:
            scene_details = json.loads(scene_details_response)
        except json.JSONDecodeError:
            print(f"Failed to decode JSON response: {scene_details_response}")
            continue

        scene_details.update({
            "aesthetic": story_payload["aesthetic"],
            "guidance": scene_state["guidance"],
            "themes": story_payload["themes"],
            "loreSource": story_payload["loreSource"],
            "universe": story_payload["summary"]
        })

        print(json.dumps(scene_details, indent=4))
        print(" ")


        print("===== PASS 3 : Scene building for Character or Landscape or Room")
        if scene_state['isCharacterScene']:
            prompt_conversion = scene_details.get("Scene", "") + ", person with " + scene_details.get("Hair",
                                                                                            "") + " " + scene_details.get(
                "aesthetic", "") + " " + scene_details.get("Character", "") + " background " + scene_details.get(
                "Background", "") + " " + scene_details.get("Camera", "")
        else:
            prompt_conversion = scene_details.get("Scene", "") + ", weather " + scene_details.get("Condition",
                                                                                                "") + " landscape " + scene_details.get(
                "Background", "") + " " + scene_details.get("aesthetic", "") + " " + scene_details.get("Light",
                                                                                                       "") + " " + scene_details.get(
                "Camera", "")

        print(prompt_conversion)
        print(" ")



        print("===== PASS 4 : Conversion as string ")
        # Generate a text description of the scene
        system_prompt_description = """
                Convert the image JSON attribute from this json into a short text that capture the essence of hte information. Identify the key elements of the entire scene
                and start the sentence with this, followed by visual description of the other attributes. The text need to be in one paragraph.
            """
        scene_description = queryGPT(system_prompt_description, json.dumps(scene_details), "text", False)

        ## print(scene_description)

        # print("== Condensing")
        # Condensing the scene
        system_prompt_description = """
                Using exactly the same information in this text, restructure it to follow a more organized sentence with a keyword dictionnary style seperated by comma.
                The first string need to be of 10 words and describe one most important component of that visual description with very very specific detail follow by a keyword structure.
                Example 1) To create a rich complex image: "Highly detailed illustration of a hidden world inside planet earth made of crystal, continents on surface, atmosphere, galaxies in the background,
                holographic shimmer, whimsical lighting, enchanted ambiance, soft textures, imaginative artwork, ethereal glow, silent Luminescence, whispering Silent,
                iridescent Encounter, vibrant background, by Skyrn99, rule of thirds, high quality, high detail, high resolution, bokeh, backlight, long exposure"
                Example 2) To create a powerful simple symbol: "Phoenix, simple tattoo graphic style, flying, made of fire, wings shedding flames"
                Example 3) Photorealistic focus on a individual: "realistic full body portrait of young attractive Russian girl , photo taken by Nikon DSLR + sigma art 50mm f1.4 bokeh , professional Russian photograph cinematic preset color style"
                Example 4) Keyword approach with a weight emphasis (1.0 to 1.3): "(Double-exposure art collaboration: Stoddard, Drepina, Shaden on weathered paper:1.3)(Dynamic, vintage mixed media fusion: digital collage, cut and paste animation)(Various collage themes: portrait, landscape, photography, abstract, mosaic, fashion, surrealism, street art, illustration, assemblage:1.1)(Eclectic and exquisite paper layering:1.3)(Avant-garde digital collages in sketchbook style with dark, gritty, and realistic sketches)(((Bold and loose lines on paper: turnaround character sheet)))(Create detailed illustration with intense, vibrant colors)((Hand-drawn sketches in sketchbook style))(Watercolor paint)(Infographic)(Papier-mache)(Marker drawing)(Digital illustration)(Acrylic painting)(Dripping)(Blueprint)(Still life photography)(Art installation)(Ink)(Ghibli)(Akira Toriyama)(Light painting)(Recycled sculptures)(Infrared photography)(String art)(Liquid crystal art)(Pinhole photography)(Smoke art)(Nature installations)"
                Example 5) Extremly creative freedom for the AI with little instructions: "extreme closeup of a female Face completely covered by a Vintage porcellaine pattern, white, Blue, Gold"
                Warning: Avoid too many componentn in an image. Avoid complex setting. Avoid too many details. AI prompt need clarity and focus. Since they are short, you need rich vocabulary and avoid redundant description of the same componetns.
                """
        # scene_condensed_2 = queryGPT(system_prompt_description, scene_description, "text", False)

        # Clean-up for prompt
        scene_condensed = re.sub(r'[^a-zA-Z0-9():.,\s]', '', scene_description).replace('\n', '')
        # scene_condensed_2 = re.sub(r'[^a-zA-Z0-9():.,\s]', '', scene_condensed_2).replace('\n', '')

        print(Style.RESET_ALL + "Adding the scene:")
        print(scene_condensed + Fore.LIGHTBLACK_EX)
        print(" ")

        # Append the scene description to the scenes list
        scene_entry = {
            "preprod": prompt_conversion,
            "prompt": scene_condensed,
            "original": sentence
        }
        scenes.append(scene_entry)

    return scenes
