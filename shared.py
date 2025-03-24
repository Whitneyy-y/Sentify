import re

def extract_video_id(url):
    pattern = (
        r"(?:https?://)?(?:www\.)?"
        r"(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)"
        r"([^\"&?/ ]{11})"
    )
    match = re.search(pattern, url)
    return match.group(1) if match else None