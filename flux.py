import fal_client
import requests
from PIL import Image
from io import BytesIO

# API Key and configuration
API_KEY = "71ff3a2a-cc06-499f-afbf-d603b8fdf737:42ee72e6fd9691f2e5ce630ac19bf3e7"
fal_client.api_key = API_KEY

# Image URLs
image_urls = [
    "https://i.ebayimg.com/images/g/A38AAOSwhYNkPFL9/s-l1600.webp",  # Top image
    "https://i.ebayimg.com/images/g/FO4AAOSwIw5mYXrz/s-l960.webp",  # Bottom image
    "https://i.ebayimg.com/images/g/ViIAAOSwrFVmKSAk/s-l1600.webp"   # Shoes image
]

# Unified prompt for better outfit generation
prompt = "Combine the top, bottom, and shoes into a single cohesive and stylish outfit, ensuring a seamless fit."

# Step 1: Generate each outfit piece
def generate_outfit_piece(image_url, prompt):
    result = fal_client.subscribe(
        "fal-ai/flux/dev/image-to-image",
        arguments={
            "image_url": image_url,
            "prompt": prompt,
            "strength": 0.85,
            "num_inference_steps": 50,
            "guidance_scale": 7.5,
            "num_images": 1,
            "enable_safety_checker": True,
        },
        with_logs=True,
    )
    
    # Get generated image URL
    return result['images'][0]['url']

# Step 2: Download and combine images
def download_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

# Step 3: Combine the images
def combine_images(images):
    widths, heights = zip(*(i.size for i in images))
    total_width = max(widths)
    total_height = sum(heights)
    
    new_image = Image.new('RGB', (total_width, total_height))
    y_offset = 0
    
    for img in images:
        new_image.paste(img, (0, y_offset))
        y_offset += img.height
        
    return new_image

# Process all images and generate the final outfit
generated_images = []
for image_url in image_urls:
    generated_image_url = generate_outfit_piece(image_url, prompt)
    print(f"Generated Image URL: {generated_image_url}")
    generated_images.append(download_image(generated_image_url))

# Combine the generated pieces into one image
final_outfit_image = combine_images(generated_images)
final_outfit_image.show()  # Display the final combined outfit
final_outfit_image.save("final_outfit.jpg")  # Save the final outfit image
