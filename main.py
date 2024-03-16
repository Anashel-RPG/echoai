# main.py
import config
import os
import sys
import time
import platform
from process import start_process, read_structure_parameters
from colorama import init, Fore, Style
from audio2txt import process_audio2txt
from datetime import datetime
import time  # Assuming wait_time() uses time.sleep() under the hood

def wizard():

    #### WIZARD STEP 1 : SCENE SOURCE ####
    print(Fore.GREEN + Style.BRIGHT + "1 - Use your prompt to create your scene (/config-files/scene.csv)")
    print("2 - Use a .wav audio file to create your scene (/input/*.wav)")
    # print(Fore.GREEN + Style.BRIGHT + "3 - Use a story to create your scene (/config-files/conversation-capture.txt)")
    choice = input(Style.RESET_ALL + "Enter your choice (1 to 2): ")

    if choice == "3":
        choice = "1"  # Force to use the first option

    # Choice Feedbacks
    print(Style.RESET_ALL + "")
    if choice == "1":
        config.CONVERSATION_MODE = False
        config.AUDIO_MODE = False
        # Read the number of lines from config-files/scene.csv except the header
        with open('config-files/scene.csv', 'r') as file:
            lines = file.readlines()[1:]  # Skip the header
            number_of_lines = len(lines)
        s = "s" if number_of_lines > 1 else ""
        s2 = "s" if config.NUM_ITERATIONS > 1 else ""
        print(f"A total of {number_of_lines} scene{s} will be rendered with {config.NUM_ITERATIONS} iteration{s2}")
    elif choice == "2":
        config.CONVERSATION_MODE = True
        config.AUDIO_MODE = True
        # Assuming 'config.INPUT_PATH' and other variables like 'file_path', 'model', 'language' are defined correctly
        # Here you should process the audio file as needed; the example below may not directly apply to your logic.
        print("A total of 1 file will be processed by ChatGPT to create your scenes")
    elif choice == "3":
        config.CONVERSATION_MODE = True
        config.AUDIO_MODE = False
        # Read the number of lines from /config-files/conversation-capture.txt
        with open('config-files/conversation-capture.txt', 'r') as file:
            lines = file.readlines()
            number_of_lines = len(lines)
        s = "s" if number_of_lines > 1 else ""
        s2 = "s" if config.NUM_ITERATIONS > 1 else ""
        print(f"A total of {number_of_lines} scene{s} will be rendered with {config.NUM_ITERATIONS} iteration{s2}")
    else:
        print("Invalid selection.")
        exit(1)
    s3 = "s" if config.RPS_Sleep > 1 else ""
    s4 = "s" if config.MAX_CONCURRENT_JOBS > 1 else ""
    print(f"We will wait {config.RPS_Sleep} second{s3} between API call")
    print(f"And render {config.MAX_CONCURRENT_JOBS} scene{s4} at the same time")

    wait_time(2)


    #### WIZARD STEP 2 : SCENE RENDER VARIABLES ####
    print(Fore.GREEN + Style.BRIGHT + "1 - Randomly combine suffix to research a style (/config-files/structure.csv)")
    print("2 - Use a set prefix and suffix (/config-files/config.py)")
    choice = input(Style.RESET_ALL + "Enter your choice (1 or 2): ")

    # Choice Feedbacks
    print(Style.RESET_ALL + "")
    if choice == "1":
        config.OVERRIDE_MODE = False
        structure_params = read_structure_parameters(config.STRUCTURE_CSV_PATH)
        print(f"A total of {len(structure_params)} dictionaries have been loaded.")
        # Calculate the total number of unique combinations
        total_combinations = 1  # Start with 1 since we're multiplying
        for category in structure_params:
            total_combinations *= len(structure_params[category])
        print(f"This represents a total of {format_number(total_combinations)} unique possible combinations.")
    elif choice == "2":
        config.OVERRIDE_MODE = True
        prefix = config.SCENE.split("<SCENE>")[0]
        suffix = config.SCENE.split("<SCENE>")[1]
        print("The scene will be rendered using your Override Value")
        print("Prefix: " + prefix + " ...")
        print("Suffix: ..." + suffix)
        if config.REALISTIC_MODE == 1:
            print("The scene will be rendered using the Realistic Model")
            print("Model ID: " + config.OVERRIDE_MODEL)
        else:
            print("The scene will be rendered using the Creative Model")
            print("Model ID: " + config.OVERRIDE_MODEL)
        print("The render style " + config.OVERRIDE_STYLE + " will be apply to your scene")
    else:
        print("Invalid selection.")
        exit(1)

    wait_time(2)


    print(Fore.GREEN + Style.BRIGHT + "1 - Render Scene in Landscape Format (16:9)")
    print("2 - Render Scene in Portrait Format (3:4)")
    choice = input(Style.RESET_ALL + "Enter your choice (1 or 2): ")

    # Choice Feedbacks
    print(Style.RESET_ALL + "")
    if choice == "1":
        config.IMAGE_WIDTH = 1360
        config.IMAGE_HEIGHT = 768
    elif choice == "2":
        config.IMAGE_WIDTH = 768
        config.IMAGE_HEIGHT = 1024
    else:
        print(Fore.LIGHTBLACK_EX + Style.BRIGHT + "")
        print("Invalid selection.")
        exit(1)

    print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "Configuration Completed" + Style.RESET_ALL)
    if config.IMAGE_WIDTH == 768:
        print("Render Mode = " + config.RENDER_MODE + " in Portrait Format (3:4)")
    else:
        print("Render Mode = " + config.RENDER_MODE + " in Landscape Format (16:9)")

    # press_any_key_to_continue()

# Function to check for missing configuration variables
def check_config_vars(module, vars_list):
    missing_vars = []

    # Check if RENDER_MODE is set and then call load_override_settings to initialize dynamic variables
    if hasattr(module, 'RENDER_MODE'):
        # Since load_override_settings updates module-level variables, ensure it's called before checking variables
        config.load_override_settings(config.RENDER_MODE)
    else:
        # If RENDER_MODE itself is missing, add it to missing_vars
        missing_vars.append('RENDER_MODE')

    # Now check for both static and dynamic variables presence
    for var in vars_list:
        if not hasattr(module, var):
            missing_vars.append(var)

    return missing_vars

def format_number(num):
    if num >= 1e9:  # Billions
        return f"{num / 1e9:.1f} billion"
    elif num >= 1e6:  # Millions
        return f"{num / 1e6:.1f} million"
    elif num >= 1e3:  # Thousands
        return f"{num / 1e3:.1f} thousand"
    else:
        return str(num)

# Clear console text
def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def press_any_key_to_continue():
    """Pause the program until the user presses any key, handling different OSes."""
    print("")
    try:
        if platform.system() == "Windows":
            # For Windows
            import msvcrt
            print(Fore.LIGHTBLACK_EX + Style.BRIGHT + "Press enter to start your EchoAI render...")
            msvcrt.getch()
        else:
            # For Unix/Linux/Mac
            print(Fore.LIGHTBLACK_EX + Style.BRIGHT + "Press enter to start your EchoAI render...")
            os.system("read -n 1 -s -r")
    except Exception as e:
        print(f"Error waiting for key press: {e}")

    print(Style.RESET_ALL + "")

def wait_time(seconds):
    spinner = ['🌑 ', '🌒 ', '🌓 ', '🌔 ', '🌕 ', '🌖 ', '🌗 ', '🌘 ']
    end_time = time.time() + seconds
    idx = 0  # Index for the spinner animation frame

    while time.time() < end_time:
        # Print the current spinner frame followed by a carriage return to overwrite it on the next print
        sys.stdout.write('\r' + spinner[idx % len(spinner)])
        sys.stdout.flush()
        idx += 1
        time.sleep(0.3)  # Adjust for desired spinner speed

    # Overwrite the spinner with a space to remove it, then return to the start of the line
    sys.stdout.write('\r' + ' ' * len(spinner[idx % len(spinner)]) + '\r')
    sys.stdout.flush()

    print("")

def main():
    #### SETTING UP ####
    init()  # Initialize colorama
    os.environ['TERM'] = 'xterm-256color'

    # Usage of clear_screen
    clear_screen()

    print(Fore.GREEN + Style.BRIGHT + "WELCOME TO ECHOAI" + Fore.LIGHTBLACK_EX)

    # Checking that default config file exist
    # Import the config module
    try:
        import config
    except ImportError as e:
        print("The config file cannot be found or has an error.")
        raise

    # List of required configuration variables
    required_vars = [
        "LEONARDO_TOKEN",
        "OPENAI_API_KEY",
        "RANDOM_MODE",
        "BROADCAST_MODE",
        "RENDER_MODE",
        "NUM_ITERATIONS",
        "MAX_CONCURRENT_JOBS",
        "IMAGE_WIDTH",
        "IMAGE_HEIGHT",
        "CONVERSATION_MODE",
        "AUDIO_MODE",
        "RANDOM_READ",
        "FORCE_UNIVERSE",
        "NEGATIVE",
        "SLIDESHOW_ENABLED",
        "OVERRIDE_MODE",
        "OVERRIDE_STRING",
        "OVERRIDE_STYLE",
        "OVERRIDE_MODEL",
        "SCENE"
    ]

    # Check for missing variables
    missing = check_config_vars(config, required_vars)

    # Notify the user if any variables are missing
    if missing:
        missing_str = ", ".join(missing)
        print(f"The following configuration variables are missing: {missing_str}")
        exit(0)
    else:
        print("All required configuration variables are set.")

    print("Process Started")

    if config.WIZARD:
        wizard()

    clear_screen()

    # Start time tracker
    start_time = datetime.now()
    print(Fore.GREEN + Style.BRIGHT + "START TIME: " + start_time.strftime('%I:%M %p') + Fore.LIGHTBLACK_EX)

    scenes = []
    if config.AUDIO_MODE:
        scenes = process_audio2txt()
        print(scenes)
        wait_time(3)
        clear_screen()

    start_process(scenes)

    # End time tracker and calculate duration
    end_time = datetime.now()
    duration = end_time - start_time
    # Format the duration in a readable format (e.g., "1h20 min" or "30 sec")
    if duration.seconds >= 3600:
        # More than an hour
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        duration_str = f"{hours}h{minutes} min"
    elif duration.seconds >= 60:
        # More than a minute but less than an hour
        minutes = duration.seconds // 60
        seconds = duration.seconds % 60
        duration_str = f"{minutes} min {seconds} sec" if seconds > 0 else f"{minutes} min"
    else:
        # Less than a minute
        duration_str = f"{duration.seconds} sec"

    print(Fore.GREEN + Style.BRIGHT + "TOTAL DURATION: " + duration_str + Fore.LIGHTBLACK_EX)

if __name__ == "__main__":
    main()
