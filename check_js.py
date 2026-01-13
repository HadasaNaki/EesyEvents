import re
from collections import Counter

with open('backend/templates/results.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find script section
script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
if script_match:
    script = script_match.group(1)
    
    # Count function definitions
    funcs = re.findall(r'function (\w+)', script)
    print(f'Total functions found: {len(funcs)}')
    
    # Check for duplicate function names
    dups = [k for k, v in Counter(funcs).items() if v > 1]
    if dups:
        print(f'DUPLICATE FUNCTIONS: {dups}')
    else:
        print('No duplicate functions')
    
    # Print all function names
    print('\nAll functions:')
    for f in sorted(set(funcs)):
        print(f'  - {f}')
else:
    print('No script found')
