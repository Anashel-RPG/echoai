# file_reader.py
import csv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_structure_parameters(csv_file):
    """
    Reads a CSV file containing structure parameters and builds a dictionary from it.

    Parameters:
    csv_file (str): Path to the CSV file containing structure parameters.

    The function performs the following steps:
    1. Opens the CSV file using the csv.DictReader, which reads the file into a dictionary.
    2. Iterates over the rows of the CSV, collecting unique values for each header.
    3. Logs the results, showing how many unique values were found for each header.
    4. Returns the dictionary containing the unique values for each parameter.

    Returns:
    dict: A dictionary where each key corresponds to a header in the CSV and each value is a list of unique values for that header.
    """
    # Initialize a dictionary to store unique values for each header
    param_dict = {}

    # Try-except block to handle file reading exceptions
    try:
        # Open the CSV file and create a DictReader object
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Initialize the dictionary with empty lists for each header
            param_dict = {header: [] for header in reader.fieldnames}

            # Loop over each row in the CSV file
            for row in reader:
                # For each header, add the value to the corresponding list in the dictionary if it's not already present
                for header in reader.fieldnames:
                    if row[header] not in param_dict[header]:
                        param_dict[header].append(row[header])

            # Log the successful reading of the file
            logging.info(f"Structure parameters read successfully from {csv_file}")

    except Exception as e:
        # Log any exceptions that occur during file reading
        logging.error(f"An error occurred while reading the structure parameters from {csv_file}: {e}")

    # Return the dictionary of parameters
    return param_dict


def read_scene_descriptions(file_path):
    """
    Reads a text file containing scene descriptions line by line.

    Parameters:
    file_path (str): Path to the text file containing scene descriptions.

    The function performs the following steps:
    1. Opens the text file and reads lines one by one.
    2. Ignores empty lines and trims whitespace from each line.
    3. Collects non-empty lines in a list as scene descriptions.
    4. Logs the number of descriptions read.
    5. Returns the list of scene descriptions.

    Returns:
    list: A list of scene descriptions.
    """
    # Initialize a list to store scene descriptions
    descriptions = []

    # Try-except block to handle file reading exceptions
    try:
        # Open the text file and read lines
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read the first line as the title
            title = next(file).strip()
            # Read the rest of the lines, stripping whitespace and ignoring empty lines
            descriptions = [line.strip() for line in file if line.strip()]

            # Log the successful reading of the file
            logging.info(f"Scene descriptions read successfully from {file_path}")

    except Exception as e:
        # Log any exceptions that occur during file reading
        logging.error(f"An error occurred while reading scene descriptions from {file_path}: {e}")

    # Return the list of descriptions
    return {title: descriptions}
