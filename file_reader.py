# file_reader.py
import csv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_structure_parameters(csv_file):
    # Initialize a dictionary to store unique values for each header
    param_dict = {}

    # Try-except block to handle file reading exceptions
    try:
        # Open the CSV file and create a reader object
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader, None)  # First row as headers

            if not headers:
                raise ValueError("CSV file is empty or headers are missing")

            num_columns = len(headers)
            param_dict = {header: [] for header in headers}

            for row in reader:
                if not any(row):  # Skip empty rows
                    continue

                # Truncate or extend the row to match the header length
                row = row[:num_columns] + [''] * (num_columns - len(row))

                for header, value in zip(headers, row):
                    if value and value not in param_dict[header]:
                        param_dict[header].append(value)

            # Log the successful reading of the file
            # logging.info(f"Structure parameters read successfully from {csv_file}")
            print(f"Structure parameters read successfully from {csv_file}")

    except Exception as e:
        # Log any exceptions that occur during file reading
        logging.error(f"An error occurred while reading the structure parameters from {csv_file}: {e}")

    # Return the dictionary of parameters
    return param_dict


def read_scene_descriptions(file_path):
    # Initialize a list to store scene descriptions
    descriptions = []

    # Try-except block to handle file reading exceptions
    try:
        # Open the text file and read lines
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read the first line as the title, removing commas and extra whitespace
            title = next(file).replace(',', '').strip()

            # Read the rest of the lines, stripping whitespace, removing commas, and ignoring empty lines
            descriptions = [line.replace(',', '').strip() for line in file if line.strip()]

            # Log the successful reading of the file
            logging.info(f"Scene descriptions read successfully from {file_path}")

    except Exception as e:
        # Log any exceptions that occur during file reading
        logging.error(f"An error occurred while reading scene descriptions from {file_path}: {e}")

    # Return the list of descriptions
    return {title: descriptions}
