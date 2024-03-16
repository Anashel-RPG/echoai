import tkinter as tk
from PIL import Image, ImageTk
import threading

# Global variables
taskbar_window = None
taskbar_content = None
taskbar_ready_event = threading.Event()

def create_taskbar():
    global taskbar_window, taskbar_content, taskbar_ready_event

    taskbar_window = tk.Tk()
    taskbar_window.geometry(f"{taskbar_window.winfo_screenwidth()}x30+0+0")  # Width 100%, height 75px, top of screen
    taskbar_window.configure(background='#040c3a')
    taskbar_window.overrideredirect(True)  # Remove window decoration
    taskbar_window.attributes('-topmost', True)  # Always on top

    # Label for displaying text or images
    taskbar_content = tk.Label(taskbar_window, background='#040c3a', fg='white')
    taskbar_content.pack(expand=True, fill='both')

    # Bind Escape key to close the taskbar window
    taskbar_window.bind("<Escape>", lambda e: taskbar_window.destroy())

    taskbar_ready_event.set()  # Signal that the taskbar is ready

    return taskbar_window

def update_taskbar(content, is_image=False):
    global taskbar_content, taskbar_ready_event

    taskbar_ready_event.wait()  # Wait until the taskbar is ready

    if is_image:
        # If content is an image
        img = Image.open(content)
        img.thumbnail((75, 75), Image.Resampling.LANCZOS)  # Resize to fit in taskbar
        photo = ImageTk.PhotoImage(img)
        taskbar_content.config(image=photo)
        taskbar_content.image = photo  # Keep a reference
    else:
        # If content is text
        taskbar_content.config(text=content, image='')

def main():
    create_taskbar()
    taskbar_window.mainloop()

if __name__ == "__main__":
    main()
