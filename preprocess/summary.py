# summary.py
import config
import json
import re
import os
from utils import protect_dates, restore_dates
from chatgpt import queryGPT

def genSummary(file_name):
    # Create the story summary
    print("Generating Analysis")

    MAX_TOKENS = 14000
    TOKEN_ESTIMATE_RATIO = 3  # Approximation: 1 token ≈ 4 characters

    # Find the first .txt file in /input
    input_folder = "./output/" + config.JOB

    try:
        txt_file = next(f for f in os.listdir(input_folder) if f.endswith(".txt"))
    except StopIteration:
        print("No .txt file found in the input directory.")
        exit()

    # Read the file content
    with open(os.path.join(input_folder, txt_file), 'r', encoding='utf-8') as file:
        text_to_analyze = file.read()

    # Protect dates
    protected_text, dates = protect_dates(text_to_analyze)

    # Clean up the summary variable
    cleaned_text = [
        re.sub(r'\s+', ' ', sentence).strip()
        for sentence in protected_text.replace('\n', ' ').replace('\r', '').split('.')
        if len(re.sub(r'[^\w\s]', '', sentence).split()) >= 6
    ]

    # Initialize an empty list to store the final sentences after review
    final_sentences = []

    # Loop in the array to see if the sentences are too long and would benefit to be broken down
    print("Optimizing Sentences")

    for sentence in cleaned_text:
        # print(sentence)

        # Loop in the array to see if the sentence are too long and would benefit to be broken down
        system_prompt = """
                Evaluate if the provided text would benefit to be broken down into multiples sentence. Convert the result in an array of sentence.
                Return the result in the following JSON structure reference:
                {
                    "sentence1": "Revised sentence with added detail so it still sounds descriptive and captures the original content",
                    "sentence2": "Another revised sentence with added detail so it still sounds descriptive and captures the original content"
                }
                Your response should fill in the appropriate values for each field based on your analysis of the text.
            """

        # Analyze the text
        sentence_review = queryGPT(system_prompt, sentence, "json", False)

        parsed_review = json.loads(sentence_review)
        print(json.dumps(parsed_review, indent=4))
        print(" ")

        # Directly append the sentence if only one sentence is expected
        for key, sentence in parsed_review.items():
            # Append each sentence to the final_sentences list
            final_sentences.append(sentence)

    # end of loop
    # print("Final Sentence")
    # print(final_sentences)
    cleaned_text = final_sentences

    # Remove all non-standard English characters (keep only ASCII)
    # and ensure no trailing spaces
    cleaned_text = [re.sub(r'[^\x00-\x7F]+', '', sentence).strip() for sentence in cleaned_text]

    # Restore dates
    source = [restore_dates(sentence, dates) for sentence in cleaned_text]

    # Concatenate sentences into a single string
    concatenated_text = '. '.join(source) + '.'

    # Truncate based on character count
    if len(concatenated_text) > MAX_TOKENS * TOKEN_ESTIMATE_RATIO:
        text_to_analyze = concatenated_text[:MAX_TOKENS * TOKEN_ESTIMATE_RATIO]
    else:
        text_to_analyze = concatenated_text

    system_prompt = """
        Analyze the provided text and format your response in english according to the following JSON structure:
        {
          "summary": "String (Provide a detailed but concise summary of the text, ideally in about 400 words)",
          "story": "Boolean (Is this a story? Answer true or false)",
          "isRealistic": "Boolean (Indicate whether the text is realistic or fictional. Answer true if it is realistic, false if it is fictional)",
          "themes": "Array (List major themes)",
          "mainConflict": "String (Describe the primary conflict or challenge in the story. Be succinct but clear. If there is no main conflict, state 'none')",
          "aesthetic": "String (Describe the best aesthetic to build this in a visual form. Use only keywords)",
          "hasDialog": "Boolean (Does the story contain dialogue? Answer true or false)",
          "characterCount": "Integer (Provide the number of unique characters or entities present in the story)",
          "characterNames": "Array of strings (List the names of all the main characters or entities in the story. Focus on central characters or entities only, including god or creature)",
          "era": "String (Specify the historical or speculative time period of the story, or use 'undefined' if not applicable. Avoid abstract terms and focus on identifiable time periods)",
          "lore": "String (Provide a descriptive abstraction of the story's universe or setting. Focus on key elements that define the story's world)",
          "loreSource": "String (Identify the source of the story's lore or the closest possible. This can be an established universe, author, or mythology, like 'Lovecraftian', 'Tolkien's Middle-earth', 'Greek mythology', etc. If no inspiration of any form are present, state 'original')"
        }
        Your response should fill in the appropriate values for each field based on your analysis of the text.
    """

    # Analyze the text
    analysis_result = queryGPT(system_prompt, text_to_analyze, "json", False)

    # Attempt to convert the string response to JSON object
    if isinstance(analysis_result, str):
        try:
            analysis_result = json.loads(analysis_result)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print("Received response:", analysis_result)
            exit()

    # Add the cleaned sentences and their count to the summary
    analysis_result["sentences_count"] = len(cleaned_text)
    analysis_result["sentences"] = cleaned_text

    # Save our analysis
    with open(f"{config.JOB_FOLDER}/01-Summary.json", 'w', encoding='utf-8') as json_file:
        json.dump(analysis_result, json_file, indent=4)

    return json.dumps(analysis_result, indent=4)