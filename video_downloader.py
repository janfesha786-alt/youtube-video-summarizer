import requests
import time


# =========================================================
# GEN DOWNLOAD API
# =========================================================

API_URL = "https://gendownload.com/api/extract"


# =========================================================
# HEADERS
# =========================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
}


# =========================================================
# GET VIDEO FORMATS
# =========================================================

def get_video_formats(youtube_url):

    """
    Get available video download formats
    from GenDownload.
    """

    response = requests.post(
        API_URL,

        json={
            "url": youtube_url
        },

        headers={
            "Content-Type": "application/json",
            "User-Agent": HEADERS["User-Agent"]
        },

        timeout=60
    )


    response.raise_for_status()


    data = response.json()


    if "formats" not in data:

        raise Exception(
            data.get(
                "error",
                "No downloadable formats were returned."
            )
        )


    return data


# =========================================================
# DOWNLOAD VIDEO
# =========================================================

def download_video(video_url):

    """
    Download selected video stream into memory.

    Uses streaming and retries because some
    GenDownload URLs can terminate prematurely.
    """

    max_retries = 3

    last_error = None


    for attempt in range(max_retries):

        try:

            response = requests.get(
                video_url,

                headers=HEADERS,

                stream=True,

                timeout=300
            )


            response.raise_for_status()


            chunks = []


            # -------------------------------------------------
            # DOWNLOAD IN SMALL CHUNKS
            # -------------------------------------------------

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):

                if chunk:

                    chunks.append(chunk)


            response.close()


            # -------------------------------------------------
            # COMBINE CHUNKS
            # -------------------------------------------------

            video_bytes = b"".join(chunks)


            # -------------------------------------------------
            # CHECK DOWNLOAD
            # -------------------------------------------------

            if not video_bytes:

                raise Exception(
                    "The video server returned an empty file."
                )


            return video_bytes


        except (
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout
        ) as error:

            last_error = error


            # -------------------------------------------------
            # RETRY
            # -------------------------------------------------

            if attempt < max_retries - 1:

                time.sleep(2)

                continue


            raise Exception(
                f"Video download failed after "
                f"{max_retries} attempts: {last_error}"
            )


        except requests.exceptions.HTTPError as error:

            raise Exception(
                f"Video server returned HTTP error: "
                f"{error}"
            )


        except Exception as error:

            raise Exception(
                f"Unable to download video: "
                f"{error}"
            )


    raise Exception(
        f"Video download failed: {last_error}"
    )