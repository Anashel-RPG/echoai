from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import piexif
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(essage)s')

def download_image(image_url, local_path, job_id, prompt, additional_metadata):
    logging.info(f"Initiating download: URL {image_url}, Local Path {local_path}, Job ID {job_id}, Prompt {prompt[:30]}...")

    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        # Read image from response
        image_data = response.content
        image = Image.open(BytesIO(image_data))

        # Draw text on the image
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(size=28)  # Specifying font size
        text = prompt.split(',')[0]  # Extract first part of the prompt

        # Positioning the text at top left (10, 10)
        # draw.text((20, 10), text, font=font)

        # Prepare metadata (EXIF) with additional fields
        exif_dict = {
            "0th": {},
            "Exif": {},
            "1st": {},
            "thumbnail": None,
            "GPS": {}  # Optional, if you want to include GPS-related tags
        }
        exif_dict["0th"][piexif.ImageIFD.Artist] = job_id
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = prompt

        # Concatenate additional metadata into a single string
        user_comment = "; ".join([f"{key}: {value}" for key, value in additional_metadata.items()])

        # Encode user comment with ASCII prefix
        encoded_comment = b"ASCII\x00\x00" + user_comment.encode("utf-8")

        # Assign encoded user comment to EXIF
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = encoded_comment

        # Generate EXIF bytes
        exif_bytes = piexif.dump(exif_dict)

        # Save image with metadata and added text
        image.save(local_path, "jpeg", exif=exif_bytes)
        logging.info(f"Image downloaded successfully and saved to {local_path}, with embedded text and metadata")

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred while downloading the image: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.ConnectionError as e:
        logging.error("Connection error occurred while downloading the image.")
    except requests.exceptions.Timeout as e:
        logging.error("Timeout error occurred while downloading the image.")
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while downloading the image: {e}")
    except IOError as e:
        logging.error(f"I/O error occurred while saving the image to {local_path}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while downloading the image: {e}")
