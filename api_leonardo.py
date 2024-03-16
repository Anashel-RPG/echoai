# api_leonardo.py
from api_base import APIBase
import requests
import logging
import json

class LeonardoAPI(APIBase):
    def start_job(self, data):
        url = self.base_url + 'generations'
        payload = json.dumps(data)
        try:
            response = requests.post(url, headers=self.headers, data=payload)
            response.raise_for_status()
            job_response = response.json()
            return job_response
        except Exception as e:
            logging.error(f"Error starting job in Leonardo API: {e}")
            return None

    def check_job_status(self, job_id):
        url = self.base_url + f'generations/{job_id}'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            job_status_response = response.json()
            return job_status_response
        except Exception as e:
            logging.error(f"Error checking job status in Leonardo API: {e}")
            return 'UNKNOWN'

    def download_job_content(self, job_id):
        url = self.base_url + f'generations/{job_id}'
        try:
            logging.info(f"Calling Leonardo CDN DOWNLOAD")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            job_content_response = response.json()
            generated_images = job_content_response.get('generations_by_pk', {}).get('generated_images', [])

            additional_metadata = {
                "inferenceSteps": job_content_response.get('generations_by_pk', {}).get('inferenceSteps'),
                "seed": job_content_response.get('generations_by_pk', {}).get('seed'),
                "presetStyle": job_content_response.get('generations_by_pk', {}).get('presetStyle'),
                "initStrength": job_content_response.get('generations_by_pk', {}).get('initStrength'),
                "guidanceScale": job_content_response.get('generations_by_pk', {}).get('guidanceScale'),
                "promptMagic": job_content_response.get('generations_by_pk', {}).get('promptMagic'),
                "promptMagicVersion": job_content_response.get('generations_by_pk', {}).get('promptMagicVersion'),
                "promptMagicStrength": job_content_response.get('generations_by_pk', {}).get('promptMagicStrength'),
                "photoReal": job_content_response.get('generations_by_pk', {}).get('photoReal'),
                "photoRealStrength": job_content_response.get('generations_by_pk', {}).get('photoRealStrength')
            }

            job_data = get_job_data(job_id)  # Retrieve job data

            if job_data:
                for image in generated_images:
                    image_url = image.get('url')
                    if image_url:
                        local_path = os.path.join("downloaded_images", f"{job_id}_{image.get('id', 'unknown')}.jpg")
                        logging.info(f"Downloading image: {image_url}")
                        download_image(image_url, local_path, job_id, job_data['prompt'], additional_metadata)
                        print(f"NOW SHOWING: {job_data}")
        except Exception as e:
            logging.error(f"Error downloading content for job ID {job_id}: {e}")
