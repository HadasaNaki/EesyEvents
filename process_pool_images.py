from PIL import Image
import os

def remove_white_background(input_path, output_path, threshold=240):
    """Remove white/light background from image"""
    img = Image.open(input_path)
    print(f'Processing: {input_path} - Mode: {img.mode}, Size: {img.size}')
    
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    data = img.getdata()
    new_data = []
    for item in data:
        # If pixel is white or very light
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    
    img.putdata(new_data)
    img.save(output_path, 'PNG')
    print(f'✓ Saved: {output_path}')

# Process summer and pool images
images_path = 'backend/static/images/'

# Convert and remove white background from summer.jpeg
summer_input = os.path.join(images_path, 'summer.jpeg')
summer_output = os.path.join(images_path, 'summer.png')
if os.path.exists(summer_input):
    remove_white_background(summer_input, summer_output)

# Convert and remove white background from pool.jpeg
pool_input = os.path.join(images_path, 'pool.jpeg')
pool_output = os.path.join(images_path, 'pool.png')
if os.path.exists(pool_input):
    remove_white_background(pool_input, pool_output)

print('\n✓ Pool party images processed!')
