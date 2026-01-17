import re

def normalize_text(raw_text: str) -> str:
    if not raw_text or not isinstance(raw_text, str):
        return ""

    lines = [l.strip() for l in raw_text.splitlines()]
    output = []

    buffer = ""
    upper_buffer = []

    for line in lines:
        if not line:
            continue

        # Merge uppercase headings split across lines
        if line.isupper() and len(line.split()) <= 5:
            upper_buffer.append(line)
            continue

        if upper_buffer:
            output.append(" ".join(upper_buffer))
            upper_buffer = []

        # Merge broken sentences
        if buffer:
            if not buffer.endswith((".", ":", ";")):
                buffer += " " + line
            else:
                output.append(buffer)
                buffer = line
        else:
            buffer = line

    if upper_buffer:
        output.append(" ".join(upper_buffer))

    if buffer:
        output.append(buffer)

    # Final cleanup
    cleaned = []
    for line in output:
        line = re.sub(r"\s+", " ", line)
        cleaned.append(line.strip())

    return "\n".join(cleaned)
