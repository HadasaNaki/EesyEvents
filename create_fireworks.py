from PIL import Image, ImageDraw
import math

# Create a new image with transparent background
width, height = 400, 400
img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw fireworks - golden colored bursts
center_x, center_y = width // 2, height // 2
num_bursts = 40
radius = 150
color = (218, 165, 32, 255)  # Goldenrod color

for i in range(num_bursts):
    angle = (i / num_bursts) * 2 * math.pi
    
    # Draw burst lines
    x1 = center_x
    y1 = center_y
    x2 = center_x + radius * math.cos(angle)
    y2 = center_y + radius * math.sin(angle)
    
    # Draw line
    draw.line([(x1, y1), (x2, y2)], fill=color, width=3)
    
    # Draw dots at end of lines
    dot_radius = 5
    draw.ellipse(
        [(x2 - dot_radius, y2 - dot_radius), (x2 + dot_radius, y2 + dot_radius)],
        fill=color
    )

# Save the image
img.save('backend/static/images/fireworks.png', 'PNG')
print('✓ Fireworks image created: backend/static/images/fireworks.png')
