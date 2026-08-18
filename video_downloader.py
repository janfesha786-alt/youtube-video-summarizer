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
    "Referer": "https://www.youtube.com/",
}


# =========================================================
# GET VIDEO FORMATS
# =========================================================

def get_video_formats(youtube_url):

    """
    Get available video download formats from GenDownload.

    Returns the complete GenDownload response.

    Only actual video formats are kept.
    Audio-only formats are removed because this
    application is designed to download videos.
    """

    if not youtube_url:
        raise Exception("YouTube URL is empty.")

    # -----------------------------------------------------
    # REQUEST EXTRACTION
    # -----------------------------------------------------

    try:

        response = requests.post(
            API_URL,
            json={
                "url": youtube_url.strip()
            },
            headers={
                "Content-Type": "application/json",
                "User-Agent": HEADERS["User-Agent"],
                "Referer": HEADERS["Referer"],
            },
            timeout=60,
        )

    except requests.exceptions.Timeout:

        raise Exception(
            "GenDownload took too long to respond."
        )

    except requests.exceptions.ConnectionError as error:

        raise Exception(
            f"Could not connect to GenDownload: {error}"
        )

    except requests.exceptions.RequestException as error:

        raise Exception(
            f"GenDownload request failed: {error}"
        )


    # -----------------------------------------------------
    # CHECK HTTP RESPONSE
    # -----------------------------------------------------

    try:

        response.raise_for_status()

    except requests.exceptions.HTTPError as error:

        try:
            error_data = response.json()

            error_message = error_data.get(
                "error",
                str(error)
            )

        except Exception:

            error_message = str(error)

        raise Exception(
            f"GenDownload returned an HTTP error: "
            f"{error_message}"
        )


    # -----------------------------------------------------
    # PARSE JSON
    # -----------------------------------------------------

    try:

        data = response.json()

    except ValueError:

        raise Exception(
            "GenDownload returned an invalid JSON response."
        )


    # -----------------------------------------------------
    # CHECK API ERROR
    # -----------------------------------------------------

    if data.get("error"):

        raise Exception(
            str(data.get("error"))
        )


    # -----------------------------------------------------
    # GET FORMATS
    # -----------------------------------------------------

    formats = data.get(
        "formats",
        []
    )


    if not isinstance(formats, list):

        raise Exception(
            "GenDownload returned an invalid formats list."
        )


    # =====================================================
    # KEEP ONLY VIDEO FORMATS
    # =====================================================

    video_formats = []


    for fmt in formats:

        if not isinstance(fmt, dict):
            continue


        # -------------------------------------------------
        # DOWNLOAD URL
        # -------------------------------------------------

        video_url = fmt.get("url")

        if not video_url:
            continue


        # -------------------------------------------------
        # FORMAT TYPE
        # -------------------------------------------------

        format_type = str(
            fmt.get(
                "type",
                ""
            )
        ).lower()


        # -------------------------------------------------
        # EXTENSION
        # -------------------------------------------------

        extension = str(
            fmt.get(
                "ext",
                ""
            )
        ).lower()


        # -------------------------------------------------
        # LABEL
        # -------------------------------------------------

        label = str(
            fmt.get(
                "label",
                ""
            )
        ).strip()


        # -------------------------------------------------
        # REMOVE AUDIO-ONLY FORMATS
        # -------------------------------------------------

        if format_type == "audio":
            continue


        if extension in (
            "mp3",
            "m4a",
            "aac",
            "opus",
            "wav",
            "ogg",
        ):
            continue


        if not label:

            label = "Unknown quality"


        # -------------------------------------------------
        # COPY FORMAT
        # -------------------------------------------------

        clean_format = dict(fmt)

        clean_format["label"] = label

        clean_format["url"] = video_url


        video_formats.append(
            clean_format
        )


    # =====================================================
    # REMOVE DUPLICATE QUALITIES
    # =====================================================

    unique_formats = []

    seen = set()


    for fmt in video_formats:

        label = str(
            fmt.get(
                "label",
                "Unknown quality"
            )
        )

        extension = str(
            fmt.get(
                "ext",
                ""
            )
        ).lower()


        # -------------------------------------------------
        # USE LABEL + EXTENSION AS UNIQUE KEY
        # -------------------------------------------------

        unique_key = (
            label.lower(),
            extension
        )


        if unique_key in seen:
            continue


        seen.add(
            unique_key
        )


        unique_formats.append(
            fmt
        )


    # =====================================================
    # SORT BY RESOLUTION
    # =====================================================

    def resolution_number(fmt):

        label = str(
            fmt.get(
                "label",
                ""
            )
        ).lower()


        # -------------------------------------------------
        # FIND NUMBER BEFORE "P"
        # -------------------------------------------------

        import re


        match = re.search(
            r"(\d{3,4})p",
            label
        )


        if match:

            try:

                return int(
                    match.group(1)
                )

            except ValueError:

                pass


        return 0


    unique_formats.sort(
        key=resolution_number,
        reverse=True
    )


    # =====================================================
    # REPLACE FORMATS WITH CLEAN VIDEO FORMATS
    # =====================================================

    data["formats"] = unique_formats


    # =====================================================
    # FINAL CHECK
    # =====================================================

    if not unique_formats:

        raise Exception(
            "GenDownload did not return any "
            "downloadable video formats."
        )


    return data


# =========================================================
# DOWNLOAD VIDEO
# =========================================================

def download_video(video_url):

    """
    Download the selected video stream into memory.

    Uses streaming and retries because GenDownload
    download URLs can occasionally terminate early.
    """

    if not video_url:

        raise Exception(
            "Video download URL is empty."
        )


    max_retries = 3

    last_error = None


    # =====================================================
    # RETRY LOOP
    # =====================================================

    for attempt in range(
        max_retries
    ):

        try:

            # -------------------------------------------------
            # REQUEST VIDEO
            # -------------------------------------------------

            response = requests.get(
                video_url,
                headers=HEADERS,
                stream=True,
                timeout=300,
            )


            # -------------------------------------------------
            # CHECK RESPONSE
            # -------------------------------------------------

            response.raise_for_status()


            chunks = []


            # -------------------------------------------------
            # DOWNLOAD IN CHUNKS
            # -------------------------------------------------

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):

                if chunk:

                    chunks.append(
                        chunk
                    )


            response.close()


            # -------------------------------------------------
            # COMBINE CHUNKS
            # -------------------------------------------------

            video_bytes = b"".join(
                chunks
            )


            # -------------------------------------------------
            # CHECK FILE
            # -------------------------------------------------

            if not video_bytes:

                raise Exception(
                    "The video server returned "
                    "an empty file."
                )


            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            return video_bytes


        # =====================================================
        # RETRYABLE ERRORS
        # =====================================================

        except (
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
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
                f"{max_retries} attempts: "
                f"{last_error}"
            )


        # =====================================================
        # HTTP ERROR
        # =====================================================

        except requests.exceptions.HTTPError as error:

            raise Exception(
                f"Video server returned HTTP error: "
                f"{error}"
            )


        # =====================================================
        # OTHER ERROR
        # =====================================================

        except Exception as error:

            raise Exception(
                f"Unable to download video: "
                f"{error}"
            )


    # =====================================================
    # FINAL FAILURE
    # =====================================================

    raise Exception(
        f"Video download failed: {last_error}"
    )