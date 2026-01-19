from PIL import Image
import os

# Path to the image
image_path = 'backend/static/images/fireworks.png'

# Check if file exists
if os.path.exists(image_path):
    # Open the image
    img = Image.open(image_path)
    print(f'Image mode: {img.mode}, Size: {img.size}')
    
    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Get image data
    data = img.getdata()
    
    # Create new image data with transparent background
    new_data = []
    for item in data:
        # If pixel is white or very light (close to white)
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            # Make it transparent
            new_data.append((255, 255, 255, 0))
        else:
            # Keep original
            new_data.append(item)
    
    # Update image
    img.putdata(new_data)
    
    # Save the image
    img.save(image_path, 'PNG')
    print(f'✓ Saved: {image_path}')
else:
    print(f'❌ File not found: {image_path}')
    print('Please save the fireworks image first')
