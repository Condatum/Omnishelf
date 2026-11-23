import re


def increment_chapter_label(label: str) -> str:
    """Smart-increment the trailing number in a chapter label (e.g. 'Ch. 41' -> 'Ch. 42')."""
    cleaned = (label or '').strip()
    if not cleaned:
        return 'Ch. 1'

    match = re.search(r'(\d+)(?!.*\d)', cleaned)
    if not match:
        return f'{cleaned} 2'

    num_str = match.group(1)
    width = len(num_str)
    next_num = int(num_str) + 1
    formatted = str(next_num).zfill(width) if num_str.startswith('0') and width > 1 else str(next_num)
    return f'{cleaned[:match.start()]}{formatted}{cleaned[match.end():]}'
