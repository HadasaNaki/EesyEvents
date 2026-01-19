from PIL import Image
import os

# Function to remove white background from image
def remove_white_background(image_path, output_path):
    # Open the image
    img = Image.open(image_path)
    
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
    img.save(output_path, 'PNG')
    print(f"✓ Saved: {output_path}")

# Remove background from bride-groom illustration
print("Processing bride-groom-illustration.png...")
remove_white_background(
    'backend/static/images/bride-groom-illustration.png',
    'backend/static/images/bride-groom-illustration.png'
)

# Remove background from wedding rings
print("Processing wedding-rings.png...")
remove_white_background(
    'backend/static/images/wedding-rings.png',
    'backend/static/images/wedding-rings.png'
)

print("\n✓ All backgrounds removed successfully!")
