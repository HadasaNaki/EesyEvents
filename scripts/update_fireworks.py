from PIL import Image
import base64
from io import BytesIO

# The image data from the attachment (I'll process the uploaded image)
# This script will handle the image processing

def process_fireworks_image(input_path, output_path):
    """
    Remove white background from fireworks image and save with transparency
    """
    try:
        # Open the image
        img = Image.open(input_path)
        print(f'✓ Opened image: {input_path}')
        print(f'  Image mode: {img.mode}, Size: {img.size}')
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Get image data
        data = img.getdata()
        
        # Create new image data with transparent background
        new_data = []
        for item in data:
            # If pixel is white or very light (close to white)
            # Adjust threshold (240) if needed for your image
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                # Make it transparent
                new_data.append((255, 255, 255, 0))
            else:
                # Keep original color but preserve alpha
                new_data.append(item)
        
        # Update image
        img.putdata(new_data)
        
        # Save the image
        img.save(output_path, 'PNG')
        print(f'✓ Processed and saved: {output_path}')
        
    except Exception as e:
        print(f'❌ Error: {e}')

# Process the fireworks image
if __name__ == '__main__':
    process_fireworks_image(
        'backend/static/images/fireworks.png',
        'backend/static/images/fireworks.png'
    )
