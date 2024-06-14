import cv2
import os

def extract_key_frames(video_path, output_folder, num_frames=10):
    # Open the video file
    vidcap = cv2.VideoCapture(video_path)
    length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = length // num_frames
    success, image = vidcap.read()
    count = 0
    frame_count = 0

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    while success:
        if count % interval == 0:
            cv2.imwrite(os.path.join(output_folder, f"frame{frame_count}.jpg"), image)
            frame_count += 1
        success, image = vidcap.read()
        count += 1

    vidcap.release()
    return frame_count

from PIL import Image

def stitch_images(image_folder, output_image):
    images = [Image.open(os.path.join(image_folder, img)) for img in sorted(os.listdir(image_folder))]
    
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    stitched_image = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for img in images:
        stitched_image.paste(img, (x_offset, 0))
        x_offset += img.width

    stitched_image.save(output_image)


import requests

def get_description(image_url, api_key):
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a cool image analyst. Your goal is to describe what is in this image."}]
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is in the image?"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        "max_tokens": 500
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=payload)
    
    if response.status_code == 200:
        r = response.json()
        return r["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")


def main(video_path, output_folder, stitched_image_path, image_url, openai_api_key):
    print("Extracting key frames...")
    extract_key_frames(video_path, output_folder)
    print("Stitching images...")
    stitch_images(output_folder, stitched_image_path)
    print("Getting description from ChatGPT API...")
    description = get_description(image_url, openai_api_key)
    print("Description:", description)

if __name__ == "__main__":
    video_path = "forest.mp4"
    output_folder = "output2"
    stitched_image_path = "output2/stitched_image.jpg"
    image_url = "https://i.ibb.co/LQ13fx4/stitched-image.jpg"  # You need to upload the stitched image and provide the URL
    openai_api_key = ""
    
    main(video_path, output_folder, stitched_image_path, image_url, openai_api_key)

