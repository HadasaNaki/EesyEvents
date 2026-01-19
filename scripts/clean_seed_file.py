#!/usr/bin/env python3
import re

with open('backend/seed_large_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the line with "All venue images: UNIQUE"
match = re.search(r"print\(f\"✨ All venue images:.*?\n", content)
if match:
    # Keep everything up to the end of that print statement
    end_pos = match.end()
    new_content = content[:end_pos]
    
    # Add the final lines
    new_content += '\nif __name__ == \'__main__\':\n    seed_data()\n'
    
    with open('backend/seed_large_data.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('✅ File cleaned successfully!')
    print(f'Removed {len(content) - len(new_content)} characters')
else:
    print('❌ Could not find the target line')
