# screen.py
import os
import pygame
import time
import config
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ImageWatcher(FileSystemEventHandler):
    def __init__(self, display_function):
        self.display_function = display_function

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.jpg') or event.src_path.endswith('.png'):
            print(f"New image detected: {event.src_path}")
            # Wait a bit for the file to be fully written
            time.sleep(1)  # Adjust the delay as needed
            self.display_function(event.src_path)

def display_image(screen, image_path):
    try:
        image = pygame.image.load(image_path)
        iw, ih = image.get_size()
        sw, sh = screen.get_size()

        # Calculate scaling factor while maintaining aspect ratio
        scale_factor = max(sw / iw, sh / ih)

        # Calculate new image dimensions
        new_size = (int(iw * scale_factor), int(ih * scale_factor))
        image = pygame.transform.smoothscale(image, new_size)

        # Center the image on the screen
        x = (sw - new_size[0]) // 2
        y = (sh - new_size[1]) // 2

        image.set_alpha(255)  # Set initial alpha value for the image
        # print(f"Displaying image: {image_path}")
        return image, (x, y)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None, (0, 0)

def fade_from_black(screen, image, image_pos):
    print("Fading in from black")
    for alpha in range(0, 255, 5):
        screen.fill((0, 0, 0))  # Fill screen with black
        image.set_alpha(alpha)
        screen.blit(image, image_pos)
        pygame.display.flip()
        time.sleep(config.FADE_SPEED)
    # print("Fade from black completed")

def fade_in(screen, current_image, current_pos, next_image, next_pos):
    # print("Starting fade transition")
    for alpha in range(0, 255, 5):
        screen.fill((0, 0, 0))
        current_image.set_alpha(255 - alpha)
        next_image.set_alpha(alpha)
        screen.blit(current_image, current_pos)
        screen.blit(next_image, next_pos)
        pygame.display.flip()
        time.sleep(config.FADE_SPEED)
    # print("Fade transition completed")

class ImageScreen:
    def __init__(self, image_folder):
        self.image_folder = image_folder
        self.image_files = []
        self.current_image_index = -1
        self.screen = None
        self.running = True
        self.load_images()
        self.setup_screen()

    def load_images(self):
        self.image_files = [os.path.join(self.image_folder, f) for f in os.listdir(self.image_folder) if
                            f.endswith(('.jpg', '.png'))]
        self.image_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        print(f"Loaded images: {self.image_files}")

    def setup_screen(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        screen_size = self.screen.get_size()

    def update_display(self, new_image_path, is_next=True):
        if new_image_path not in self.image_files:
            self.image_files.append(new_image_path)

        new_image_index = self.image_files.index(new_image_path)
        new_image, new_image_pos = display_image(self.screen, new_image_path)

        # Determine which image to fade from based on arrow key pressed
        if is_next and new_image_index == 0 and len(self.image_files) > 1:
            # Special case for the first image with right arrow
            other_image_index = len(self.image_files) - 1
        elif not is_next and new_image_index == len(self.image_files) - 1:
            # Special case for the last image with left arrow
            other_image_index = 0
        else:
            # Normal operation for all other cases
            other_image_index = (new_image_index - 1 if is_next else (new_image_index + 1) % len(self.image_files))

        other_image_path = self.image_files[other_image_index]
        other_image, other_image_pos = display_image(self.screen, other_image_path)
        if other_image and new_image:
            fade_in(self.screen, other_image, other_image_pos, new_image, new_image_pos)
        else:
            if new_image:
                self.screen.blit(new_image, new_image_pos)
                pygame.display.flip()

        self.current_image_index = new_image_index

    def start(self):
        if self.image_files:
            self.current_image_index = 0
            first_image, first_image_pos = display_image(self.screen, self.image_files[self.current_image_index])
            fade_from_black(self.screen, first_image, first_image_pos)

        observer = Observer()
        event_handler = ImageWatcher(self.update_display)
        observer.schedule(event_handler, self.image_folder, recursive=True)
        observer.start()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.running = False
                elif event.type == pygame.KEYDOWN and len(self.image_files) > 1:
                    if event.key == pygame.K_LEFT:
                        next_index = (self.current_image_index - 1) % len(self.image_files)
                    elif event.key == pygame.K_RIGHT:
                        next_index = (self.current_image_index + 1) % len(self.image_files)
                    else:
                        continue

                    print(f"Current index: {self.current_image_index}, Next index: {next_index}")
                    self.current_image_index = next_index
                    self.update_display(self.image_files[next_index], event.key == pygame.K_RIGHT)

        observer.stop()
        observer.join()
