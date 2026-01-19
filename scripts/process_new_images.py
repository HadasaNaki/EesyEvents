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

# Process new images
images_path = 'backend/static/images/'

# Convert and remove white background from ball.jpeg
ball_input = os.path.join(images_path, 'ball.jpeg')
ball_output = os.path.join(images_path, 'ball.png')
if os.path.exists(ball_input):
    remove_white_background(ball_input, ball_output)

# Convert and remove white background from tfilin.jpeg
tfilin_input = os.path.join(images_path, 'tfilin.jpeg')
tfilin_output = os.path.join(images_path, 'tfilin.png')
if os.path.exists(tfilin_input):
    remove_white_background(tfilin_input, tfilin_output)

print('\n✓ New images processed!')
