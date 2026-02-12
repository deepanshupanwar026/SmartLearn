from django import template
import re

register = template.Library()

@register.filter
def youtube_id(url):
    """
    Extract YouTube video ID from all common URL formats.
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID&t=30s
    """
    if not url:
        return ""

    patterns = [
        r'youtube\.com/watch\?v=([^&]+)',
        r'youtu\.be/([^?&]+)',
        r'youtube\.com/embed/([^?&]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return ""
