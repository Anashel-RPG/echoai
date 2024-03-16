# config_check.py
import os
import logging
import time
from tkinter import ttk
from tkinter import Tk, messagebox, Toplevel
from tkinter.ttk import Progressbar


# Import your config module
import config as config_module

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_file_existence(file_path):
    return os.path.exists(file_path)

def check_config_values():
    required_config_keys = [
        "CONVERSATION_MODE", "AUDIO_MODE", "RANDOM_READ", "FORCE_UNIVERSE",
        "NUM_ITERATIONS", "MAX_CONCURRENT_JOBS", "IMAGE_WIDTH", "IMAGE_HEIGHT",
        "API_BASE_URL", "AUTHORIZATION_TOKEN", "OPENAI_API_KEY"
    ]
    missing_or_invalid = []
    for key in required_config_keys:
        value = getattr(config_module, key, None)
        if key == 'FORCE_UNIVERSE' and value == "":
            continue  # Allow FORCE_UNIVERSE to be an empty string
        if value in [None, 'TURE', 'FALSE']:
            missing_or_invalid.append(key)
    return missing_or_invalid

def check_override_values(override_path):
    required_override_keys = [
        "OVERRIDE", "STYLE", "REALISTIC_MODE", "SCENE",
        "REALISTIC_MODEL", "CREATIVE_MODEL"
    ]
    missing_or_invalid = []
    for key in required_override_keys:
        if not os.path.exists(override_path):
            missing_or_invalid.append("Override file missing")
            break
        with open(override_path, 'r') as file:
            lines = file.readlines()
        settings = {line.split('=')[0].strip(): line.split('=')[1].strip().strip('"') for line in lines if '=' in line}
        value = settings.get(key)
        if value in [None, 'TURE', 'FALSE']:
            missing_or_invalid.append(key)
    return missing_or_invalid

def run_checks():
    errors = []
    total_checks = 7
    check_count = 0

    # File existence checks
    file_paths = [
        config_module.TRIGGER_FILE_PATH, config_module.IMAGE_FOLDER_PATH,
        config_module.STRUCTURE_CSV_PATH, config_module.SCENES_FILE_PATH,
        config_module.CONFIG_FILE_PATH, config_module.CONVERSATION_FILE_PATH,
        config_module.INPUT_PATH
    ]
    for path in file_paths:
        if not check_file_existence(path):
            errors.append(f"Missing file: {path}")
        check_count += 1

    # Config value checks
    config_errors = check_config_values()
    errors.extend([f"Invalid config value: {error}" for error in config_errors])
    check_count += 1

    # Override value checks
    override_errors = check_override_values(config_module.OVERRIDE_PATH)
    errors.extend([f"Invalid override value: {error}" for error in override_errors])
    check_count += 1

    return errors

def show_results(errors, parent):
    if errors:
        error_message = "\n".join(errors)
        messagebox.showerror("Configuration Errors", error_message, parent=parent)
        parent.destroy()
        return False
    else:
        time.sleep(1)  # Additional 1 second delay for successful completion
        parent.destroy()
        return True

def create_progress_bar():
    # Create a root window and hide it
    root = Tk()
    root.withdraw()

    # Create a top-level window for the progress bar
    top = Toplevel(root)
    top.geometry("250x20")  # Adjust size as needed
    screen_width = top.winfo_screenwidth()
    screen_height = top.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (250 / 2))
    y_coordinate = int((screen_height / 2) - (20 / 2))
    top.geometry(f"+{x_coordinate}+{y_coordinate}")
    top.resizable(False, False)
    top.overrideredirect(True)  # No window border and title bar

    # Style the progress bar
    style = ttk.Style(top)
    style.theme_use('clam')  # 'classic' theme for better control
    style.configure("custom.Horizontal.TProgressbar", background='black', troughcolor='black')

    # Create and pack the progress bar
    progress = Progressbar(top, orient='horizontal', length=250, mode='determinate',
                           style="black.Horizontal.TProgressbar")
    progress.pack(expand=True, fill='both', pady=(0, 0))

    top.update()  # Initial update to draw the window

    for i in range(101):
        progress['value'] = i
        top.update()
        time.sleep(0.005)

    # Run checks and show results
    errors = run_checks()
    result = show_results(errors, top)
    root.destroy()
    return result

if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Hide the root window
    create_progress_bar()
    root.mainloop()
