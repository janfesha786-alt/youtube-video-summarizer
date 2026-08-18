from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(url):

    url = url.strip()
    parsed_url = urlparse(url)

    # Extract video ID
    if parsed_url.netloc in ["youtu.be", "www.youtu.be"]:
        video_id = parsed_url.path.lstrip("/")

    elif parsed_url.netloc in [
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com"
    ]:
        video_id = parse_qs(parsed_url.query).get("v", [None])[0]

    else:
        raise ValueError("Invalid YouTube URL")

    if not video_id:
        raise ValueError("Could not extract video ID")

    try:
        # New youtube-transcript-api syntax
        ytt_api = YouTubeTranscriptApi()

        transcript = ytt_api.fetch(video_id)

        # Convert transcript snippets into plain text
        text = " ".join(snippet.text for snippet in transcript)

        return text

    except Exception as e:
        raise Exception(f"Could not fetch transcript: {e}")