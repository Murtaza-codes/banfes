from django import template
from urllib.parse import urlparse, parse_qs
register = template.Library()


@register.filter
def youtube_embed(url):
    """
    Converts a YouTube URL into an embeddable iframe URL.
    """
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            query = parse_qs(parsed_url.query)
            video_id = query.get('v')
            if video_id:
                return f"https://www.youtube.com/embed/{video_id[0]}"
        elif parsed_url.hostname == 'youtu.be':
            video_id = parsed_url.path.lstrip('/')
            return f"https://www.youtube.com/embed/{video_id}"
    except Exception:
        pass
    return url  # Return the original URL if parsing fails


@register.filter
def has_submission(assignment, user):
    return assignment.submissions.filter(student=user).exists()


@register.filter
def submission_limit(assignment, user):
    return assignment.submissions.filter(student=user).count() >= assignment.allowed_submissions
