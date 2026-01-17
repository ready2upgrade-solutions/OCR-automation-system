import re

def basic_cleanup(lines):
    cleaned = []
    for line in lines:
        line = re.sub(r'\s+', ' ', line).strip()
        if len(line) > 1:
            cleaned.append(line)
    return cleaned
