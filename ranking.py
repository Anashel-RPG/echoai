import os
import csv
import requests
from collections import Counter
import config
import re
import time
import concurrent.futures

def prepare_data():
    """
    Reads and prepares data from directories and CSV files.
    Returns dictionaries and arrays for scenes and structure keywords.
    """
    # Read file names from directories
    good_files = os.listdir(config.GOOD_DIR)
    bad_files = os.listdir(config.BAD_DIR)

    # Read and prepare scene data from CSV
    scenes = {}
    with open('config-files/scene.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            scenes[row['Scene Description']] = {'positive': 0, 'negative': 0}

    # Dynamically read and prepare structure data from CSV
    structure = {}
    with open('config-files/structure.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # Dynamically initialize the structure dictionary using the CSV column names
        fieldnames = reader.fieldnames
        if fieldnames:  # Check if fieldnames are not None
            structure = {fieldname: Counter() for fieldname in fieldnames}

        for row in reader:
            for category in structure:
                if row[category]:  # Check if the cell is not empty
                    # Initialize with 'positive' and 'negative' scores if not already present
                    if row[category] not in structure[category]:
                        structure[category][row[category]] = {'positive': 0, 'negative': 0}

    return good_files, bad_files, scenes, structure

def fetch_image_metadata(url):
    """
    Fetches metadata for a given image URL.
    Returns the JSON response if the 'prompt' key is present, otherwise None.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for unsuccessful requests

        metadata = response.json()
        if 'prompt' in metadata:
            return metadata
        else:
            return None
    except requests.RequestException as e:
        print(f"Error fetching metadata from {url}: {e}")
        return None

def fetch_and_update(file, positive, scenes, structure, file_count):
    """
    Fetches image metadata, updates scores, and logs the process.
    """
    print(f"Processing file {file}. {file_count} files remaining.")
    url = f"https://ws.echoai.space/jobs/info/{file}"
    metadata = fetch_image_metadata(url)
    if metadata:
        update_scores(metadata['prompt'], scenes, structure, positive)
        return f"File {file} processed."
    return f"Failed to process file {file}"

def process_image_prompts(good_files, bad_files, scenes, structure):
    """
    Processes image prompts, updating scores for scenes and keywords.
    Utilizes concurrent fetching of image metadata to improve performance.
    Displays a countdown of files remaining to be processed.
    """
    total_files = len(good_files) + len(bad_files)
    file_count = total_files

    # Process good_files concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_and_update, file, True, scenes, structure, file_count - i)
                   for i, file in enumerate(good_files)]
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
            file_count -= 1

    # Process bad_files concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_and_update, file, False, scenes, structure, file_count - i)
                   for i, file in enumerate(bad_files)]
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
            file_count -= 1

def update_scores(prompt, scenes, structure, positive):
    """
    Updates scores for scenes and keywords based on their presence in the prompt.
    Scores are only updated for existing scenes and keywords; no new entries are added.
    """
    updated_scenes_count = 0
    updated_keywords_count = 0

    # Update scene scores
    for scene in scenes.keys():
        if re.search(re.escape(scene), prompt, re.IGNORECASE):  # Using regex search for flexible matching
            scenes[scene]['positive' if positive else 'negative'] += 1
            updated_scenes_count += 1

    # Update structure scores
    for category in structure.keys():
        for keyword in structure[category].keys():
            if re.search(re.escape(keyword), prompt, re.IGNORECASE):  # Using regex search for flexible matching
                structure[category][keyword]['positive' if positive else 'negative'] += 1
                updated_keywords_count += 1

    # Logging the updates
    score_type = "Positive" if positive else "Negative"
    print(f"Updated scores for {updated_scenes_count} scenes and {updated_keywords_count} keywords with a {score_type} score.")

    # Optional: Output current state for scenes and structure
    # This part can be commented out or removed if you prefer not to log the full dictionaries
    print("\nCurrent Scenes and Scores:")
    for scene, scores in scenes.items():
        print(f"{scene}: {scores}")

    print("\nCurrent Structure and Scores:")
    for category, keywords in structure.items():
        print(f"Category: {category}")
        for keyword, scores in keywords.items():
            print(f"  {keyword}: {scores}")

def generate_report(scenes, structure):
    """
    Generates and formats the report for console output and saves it to a text file.
    """
    with open('report.txt', 'w', encoding='utf-8') as file:
        # ASCII Art Header
        file.write("===== Image Analysis Report =====\n\n")

        # Section 1: Best Keywords
        file.write("Section 1: Best Keywords\n")
        # Report table 1: Top 5 Best Scenes
        file.write("Report table 1: Top 5 Best Scenes\n")
        best_scenes = sorted(scenes.items(), key=lambda x: x[1]['positive'], reverse=True)[:5]
        for rank, (scene, scores) in enumerate(best_scenes, start=1):
            file.write(f"{rank}. {scene}: {scores['positive']}\n")

        # Report table 2: Top 5 Keywords
        file.write("Report table 2: Top 5 Keywords\n")
        all_keywords = [(keyword, sum(keyword_scores.values())) for category in structure for keyword, keyword_scores in structure[category].items()]
        top_keywords = sorted(all_keywords, key=lambda x: x[1], reverse=True)[:5]
        for rank, (keyword, score) in enumerate(top_keywords, start=1):
            file.write(f"{rank}. {keyword}: {score}\n")

        # Report table 3: Top 3 Keywords by Dictionary
        file.write("Report table 3: Top 3 Keywords by Dictionary\n")
        for category in structure:
            file.write(f"Category: {category}\n")
            top_category_keywords = sorted(structure[category].items(), key=lambda x: sum(x[1].values()), reverse=True)[:3]
            for rank, (keyword, scores) in enumerate(top_category_keywords, start=1):
                file.write(f"{rank}. {keyword}: {scores['positive']}\n")

        # Section 2: Complex Keywords
        file.write("\nSection 2: Complex Keywords\n")
        # Report table 1: Top 5 Complex Scenes
        file.write("Report table 1: Top 5 Complex Scenes\n")
        complex_scenes = {k: v for k, v in scenes.items() if v['positive'] >= 3 and v['negative'] >= 3}
        best_complex_scenes = sorted(complex_scenes.items(), key=lambda x: x[1]['positive'] + x[1]['negative'], reverse=True)[:5]
        for rank, (scene, scores) in enumerate(best_complex_scenes, start=1):
            file.write(f"{rank}. {scene}: Positive: {scores['positive']}, Negative: {scores['negative']}\n")

        # Report table 2: Top 3 Complex Keywords by Dictionary
        file.write("Report table 2: Top 3 Complex Keywords by Dictionary\n")
        for category in structure:
            file.write(f"Category: {category}\n")
            complex_keywords = {k: v for k, v in structure[category].items() if v['positive'] >= 3 and v['negative'] >= 3}
            top_complex_keywords = sorted(complex_keywords.items(), key=lambda x: x[1]['positive'] + x[1]['negative'], reverse=True)[:3]
            for rank, (keyword, scores) in enumerate(top_complex_keywords, start=1):
                file.write(f"{rank}. {keyword}: Positive: {scores['positive']}, Negative: {scores['negative']}\n")

        # Section 3: Bad Keywords
        file.write("\nSection 3: Bad Keywords\n")
        # Filter out top scenes and keywords
        top_scenes_and_keywords = set([item[0] for item in best_scenes + top_keywords])
        filtered_scenes = {k: v for k, v in scenes.items() if k not in top_scenes_and_keywords}
        filtered_structure = {category: {k: v for k, v in structure[category].items() if k not in top_scenes_and_keywords} for category in structure}

        # Report table 1: Top Bad Scenes
        file.write("Report table 1: Top Bad Scenes\n")
        bad_scenes = sorted(filtered_scenes.items(), key=lambda x: x[1]['negative'], reverse=True)[:5]
        for rank, (scene, scores) in enumerate(bad_scenes, start=1):
            file.write(f"{rank}. {scene}: {scores['negative']}\n")

        # Report table 2: Top Bad Keywords All Dictionary
        file.write("Report table 2: Top Bad Keywords All Dictionary\n")
        all_bad_keywords = [(keyword, score['negative']) for category in filtered_structure for keyword, score in filtered_structure[category].items()]
        top_bad_keywords = sorted(all_bad_keywords, key=lambda x: x[1], reverse=True)[:5]
        for rank, (keyword, score) in enumerate(top_bad_keywords, start=1):
            file.write(f"{rank}. {keyword}: {score}\n")

        # Report table 3: Top 3 Bad Keywords by Dictionary
        file.write("Report table 3: Top 3 Bad Keywords by Dictionary\n")
        for category in filtered_structure:
            file.write(f"Category: {category}\n")
            top_category_bad_keywords = sorted(filtered_structure[category].items(), key=lambda x: x[1]['negative'], reverse=True)[:3]
            for rank, (keyword, scores) in enumerate(top_category_bad_keywords, start=1):
                file.write(f"{rank}. {keyword}: {scores['negative']}\n")

    # Print the report to the console (or you can decide to print specific parts only)
    with open('report.txt', 'r', encoding='utf-8') as file:
        print(file.read())

    print("Report generation completed.")


def save_optimized_csvs(scenes, structure, include_all_positive=False):
    """
    Creates and saves 'scene-optimized.csv' and 'structure-optimized.csv' files.
    Can optionally include all scenes with a positive score instead of the top 10.

    Parameters:
    - scenes: Dictionary of scenes with their scores.
    - structure: Dictionary of structure categories and keywords with their scores.
    - include_all_positive: Boolean flag to include all scenes with a positive score. Defaults to False.
    """
    # Save optimized scene CSV
    with open('config-files/scene-optimized.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Scene Description'])
        if include_all_positive:
            positive_scenes = sorted([scene for scene, scores in scenes.items() if scores['positive'] > 0],
                                     key=lambda x: scenes[x]['positive'], reverse=True)
            for scene in positive_scenes:
                writer.writerow([scene])
        else:
            top_scenes = sorted(scenes.items(), key=lambda x: x[1]['positive'], reverse=True)[:10]
            for scene, _ in top_scenes:
                writer.writerow([scene])

    # Save optimized structure CSV
    with open('config-files/structure-optimized.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        headers = list(structure.keys())
        writer.writerow(headers)

        # Determine the maximum number of keywords for any category to ensure alignment
        max_keywords = max(len(structure[category]) for category in structure)

        # Initialize a matrix to hold all rows of data to be written
        data_matrix = [["" for _ in range(len(headers))] for _ in range(max_keywords)]

        for col_index, category in enumerate(headers):
            sorted_keywords = sorted(structure[category].items(), key=lambda x: x[1]['positive'], reverse=True)
            for row_index, (keyword, _) in enumerate(sorted_keywords):
                if row_index < max_keywords:
                    data_matrix[row_index][col_index] = keyword

        for row in data_matrix:
            writer.writerow(row)

    print("Optimized CSV files saved.")


def main():
    start_time = time.time()  # Start the timer

    # Log that the script has started
    print("Script started.")

    # Preparation Phase
    print("Starting data preparation...")
    good_files, bad_files, scenes, structure = prepare_data()
    print("Data preparation completed.")

    # Processing Phase
    print("Starting image metadata processing...")
    process_image_prompts(good_files, bad_files, scenes, structure)
    print("Image metadata processing completed.")

    # Reporting Phase
    # print("Generating report...")
    # generate_report(scenes, structure)
    # print("Report generated.")

    # Saving Optimized CSVs
    print("Saving optimized CSV files...")
    save_optimized_csvs(scenes, structure)
    print("Optimized CSV files saved.")

    # Calculate elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)

    # Log the report as completed
    print("Report generation and optimization process completed successfully.")
    print(f"Report generated in {int(hours)} hours {int(minutes)} minutes and {int(seconds)} seconds.")

if __name__ == "__main__":
    main()