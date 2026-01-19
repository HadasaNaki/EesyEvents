from PIL import Image, ImageDraw
import os

def remove_white_background(input_path, output_path):
    """Remove white background from image"""
    img = Image.open(input_path)
    print(f'Processing: {input_path} - Mode: {img.mode}, Size: {img.size}')
    
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    data = img.getdata()
    new_data = []
    for item in data:
        # If pixel is white or very light
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    
    img.putdata(new_data)
    img.save(output_path, 'PNG')
    print(f'✓ Saved: {output_path}')

def create_bar_mitzvah_icon(output_path):
    """Create a simple bar mitzvah icon - Star of David style"""
    size = 200
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple celebratory figure with confetti
    center = size // 2
    color = (76, 43, 8, 255)  # Espresso color
    
    # Draw person silhouette (simplified)
    # Head
    draw.ellipse([(center-15, 30), (center+15, 60)], fill=color)
    # Body
    draw.polygon([(center, 65), (center-30, 140), (center+30, 140)], fill=color)
    # Arms up (celebrating)
    draw.line([(center-25, 80), (center-45, 50)], fill=color, width=8)
    draw.line([(center+25, 80), (center+45, 50)], fill=color, width=8)
    # Legs
    draw.line([(center-15, 140), (center-25, 180)], fill=color, width=8)
    draw.line([(center+15, 140), (center+25, 180)], fill=color, width=8)
    
    # Add confetti dots
    confetti_colors = [(171, 119, 67, 255), (132, 89, 61, 255), (215, 189, 166, 255)]
    import random
    random.seed(42)
    for _ in range(15):
        x = random.randint(10, size-10)
        y = random.randint(10, size-10)
        r = random.randint(3, 6)
        c = random.choice(confetti_colors)
        draw.ellipse([(x-r, y-r), (x+r, y+r)], fill=c)
    
    img.save(output_path, 'PNG')
    print(f'✓ Created bar mitzvah icon: {output_path}')

def create_pool_party_icon(output_path):
    """Create a pool party icon - waves with sun"""
    size = 200
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    color = (76, 43, 8, 255)  # Espresso color
    light_color = (171, 119, 67, 255)  # Caramel
    
    # Draw sun
    sun_center = (size//2, 50)
    draw.ellipse([(sun_center[0]-25, sun_center[1]-25), 
                  (sun_center[0]+25, sun_center[1]+25)], fill=light_color)
    # Sun rays
    for i in range(8):
        import math
        angle = i * (math.pi / 4)
        x1 = sun_center[0] + 30 * math.cos(angle)
        y1 = sun_center[1] + 30 * math.sin(angle)
        x2 = sun_center[0] + 45 * math.cos(angle)
        y2 = sun_center[1] + 45 * math.sin(angle)
        draw.line([(x1, y1), (x2, y2)], fill=light_color, width=4)
    
    # Draw waves
    for wave_y in [110, 140, 170]:
        points = []
        for x in range(0, size+20, 10):
            import math
            y = wave_y + 15 * math.sin(x * 0.1)
            points.append((x, y))
        for i in range(len(points)-1):
            draw.line([points[i], points[i+1]], fill=color, width=5)
    
    # Draw beach ball
    ball_center = (size//2, 130)
    draw.ellipse([(ball_center[0]-20, ball_center[1]-20),
                  (ball_center[0]+20, ball_center[1]+20)], outline=color, width=3)
    
    img.save(output_path, 'PNG')
    print(f'✓ Created pool party icon: {output_path}')

# Main execution
if __name__ == '__main__':
    images_path = 'backend/static/images/'
    
    # Remove white background from corporate toast
    corporate_path = os.path.join(images_path, 'corporate-toast-icon.png')
    if os.path.exists(corporate_path):
        remove_white_background(corporate_path, corporate_path)
    
    # Create bar mitzvah icon
    create_bar_mitzvah_icon(os.path.join(images_path, 'bar-mitzvah-icon.png'))
    
    # Create pool party icon
    create_pool_party_icon(os.path.join(images_path, 'pool-party-icon.png'))
    
    print('\n✓ All icons processed!')
