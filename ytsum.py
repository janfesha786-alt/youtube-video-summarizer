import streamlit as st
import base64
from pathlib import Path

from transcript import get_transcript
from summarizer import summarize
from pdf_generator import create_pdf
from video_downloader import get_video_formats, download_video


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="YouTube Video Summarizer",
    page_icon="youtube.png",
    layout="centered"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       REMOVE DEFAULT STREAMLIT BACKGROUND
       ===================================================== */

    .stApp {
        background: transparent !important;
    }

    [data-testid="stAppViewContainer"] {
        background: transparent !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }


    /* =====================================================
       VIDEO BACKGROUND
       ===================================================== */

    .video-background {
        position: fixed;
        top: 0;
        left: 0;

        width: 100vw;
        height: 100vh;

        overflow: hidden;

        z-index: -10;

        pointer-events: none;
    }

    .video-background video {
        position: absolute;

        top: 50%;
        left: 50%;

        min-width: 100%;
        min-height: 100%;

        width: auto;
        height: auto;

        transform: translate(-50%, -50%);

        object-fit: cover;

        filter: brightness(0.55);

        pointer-events: none;
    }


    /* =====================================================
       DARK OVERLAY
       ===================================================== */

    .video-overlay {
        position: fixed;

        top: 0;
        left: 0;

        width: 100vw;
        height: 100vh;

        background: rgba(0, 0, 0, 0.35);

        z-index: -5;

        pointer-events: none;
    }


    /* =====================================================
       MAIN CONTENT
       ===================================================== */

    [data-testid="stAppViewContainer"] > .main {
        position: relative;

        z-index: 1;

        background: transparent !important;
    }

    .block-container {
        position: relative;

        z-index: 2;

        padding-top: 40px;
        padding-bottom: 50px;
    }


    /* =====================================================
       LOGO
       ===================================================== */

    .logo-container {
        text-align: center;

        margin-top: 10px;
        margin-bottom: 10px;
    }


    /* =====================================================
       TITLE
       ===================================================== */

    .main-title {
        text-align: center;

        font-size: 42px;
        font-weight: 700;

        color: white;

        margin-top: 5px;
        margin-bottom: 8px;

        text-shadow:
            0px 3px 8px rgba(0,0,0,0.8);
    }


    .subtitle {
        text-align: center;

        font-size: 17px;

        color: #f1f5f9;

        margin-bottom: 30px;

        text-shadow:
            0px 2px 6px rgba(0,0,0,0.8);
    }


    /* =====================================================
       SECTION TITLE
       ===================================================== */

    .section-title {
        font-size: 24px;

        font-weight: 700;

        margin-bottom: 15px;

        color: white;

        text-shadow:
            0px 2px 6px rgba(0,0,0,0.8);
    }


    /* =====================================================
       SUMMARY BOX
       ===================================================== */

    .summary-box {
        padding: 20px;

        border-radius: 12px;

        margin-top: 20px;

        background: rgba(255,255,255,0.12);

        backdrop-filter: blur(8px);

        border: 1px solid rgba(255,255,255,0.25);
    }


    /* =====================================================
       CONTAINERS
       ===================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255,255,255,0.12) !important;

        backdrop-filter: blur(8px);

        border: 1px solid rgba(255,255,255,0.25) !important;

        border-radius: 15px !important;
    }


    /* =====================================================
       LABELS
       ===================================================== */

    label {
        color: white !important;

        font-weight: 500 !important;
    }


    /* =====================================================
       INPUT BOXES
       ===================================================== */

    input {
        background-color: rgba(255,255,255,0.92) !important;

        color: #111827 !important;

        border-radius: 10px !important;
    }


    /* =====================================================
       SELECT BOX
       ===================================================== */

    [data-baseweb="select"] > div {
        background-color: rgba(255,255,255,0.92) !important;

        color: #111827 !important;

        border-radius: 10px !important;
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        background-color: #ff0000 !important;

        color: white !important;

        border: none !important;

        border-radius: 10px !important;

        font-weight: 600 !important;

        min-height: 45px;
    }


    .stButton > button:hover {
        background-color: #cc0000 !important;

        color: white !important;
    }


    /* =====================================================
       DOWNLOAD BUTTONS
       ===================================================== */

    .stDownloadButton > button {
        background-color: #ff0000 !important;

        color: white !important;

        border: none !important;

        border-radius: 10px !important;

        font-weight: 600 !important;

        min-height: 45px;

        opacity: 1 !important;
    }


    .stDownloadButton > button:hover {
        background-color: #cc0000 !important;

        color: white !important;
    }


    .stDownloadButton > button p,
    .stDownloadButton > button span {
        color: white !important;
    }


    .stDownloadButton > button * {
        color: white !important;
    }


    /* =====================================================
       NORMAL TEXT
       ===================================================== */

    .stMarkdown,
    .stCaption,
    p {
        color: white;
    }


    /* =====================================================
       EXPANDER
       ===================================================== */

    [data-testid="stExpander"] {
        background: rgba(255,255,255,0.10) !important;

        border: 1px solid rgba(255,255,255,0.25) !important;

        border-radius: 12px !important;
    }


    /* =====================================================
       DIVIDER
       ===================================================== */

    hr {
        border-color: rgba(255,255,255,0.35) !important;
    }


    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# VIDEO BACKGROUND
# =========================================================

# Locate the video inside the project's static folder

video_path = (
    Path(__file__).parent
    / "static"
    / "bg_video.mp4"
)


# Read the video file

with open(video_path, "rb") as video_file:

    video_base64 = base64.b64encode(
        video_file.read()
    ).decode()


# Display the background video

st.html(
    f"""
    <div class="video-background">

        <video
            autoplay
            muted
            playsinline
            loop
        >

            <source
                src="data:video/mp4;base64,{video_base64}"
                type="video/mp4"
            >

        </video>

    </div>

    <div class="video-overlay"></div>
    """
)


# =========================================================
# LOGO
# =========================================================

col1, col2, col3 = st.columns(
    [1, 1, 1]
)

with col2:

    st.image(
        "youtube.png",
        width=90
    )


# =========================================================
# TITLE
# =========================================================

st.markdown(
    """
    <div class="main-title">
        YouTube Video Summarizer
    </div>

    <div class="subtitle">
        Transform any YouTube video into a concise AI-powered summary.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# INPUT SECTION
# =========================================================

with st.container(border=True):

    st.markdown(
        "### 🎬 Enter your YouTube video"
    )


    youtube_url = st.text_input(
        "YouTube Video URL",
        placeholder="Paste a YouTube video URL here..."
    )


    # -----------------------------------------------------
    # SUMMARY OPTIONS
    # -----------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        summary_length = st.selectbox(
            "Choose summary length",
            [
                "Short",
                "Medium",
                "Detailed"
            ]
        )


    with col2:

        summary_format = st.selectbox(
            "Choose summary format",
            [
                "Paragraph",
                "Bullet Points",
                "Study Notes"
            ]
        )


# =========================================================
# GENERATE BUTTON
# =========================================================

left, center, right = st.columns(
    [1, 2, 1]
)


with center:

    generate = st.button(
        "Generate summary...",
        use_container_width=True
    )


# =========================================================
# GENERATE SUMMARY
# =========================================================

if generate:

    if not youtube_url.strip():

        st.warning(
            "Please enter a YouTube URL."
        )

    else:

        try:

            # =================================================
            # FETCH TRANSCRIPT
            # =================================================

            with st.spinner(
                "Fetching transcript..."
            ):

                transcript = get_transcript(
                    youtube_url
                )


            st.success(
                "Transcript fetched successfully!"
            )


            # =================================================
            # GENERATE AI SUMMARY
            # =================================================

            with st.spinner(
                "Generating AI Summary..."
            ):

                summary = summarize(
                    transcript,
                    summary_length,
                    summary_format
                )


            # =================================================
            # DISPLAY SUMMARY
            # =================================================

            st.markdown(
                """
                <div class="summary-box">
                """,
                unsafe_allow_html=True
            )


            st.markdown(
                """
                <div class="section-title">
                    ✨ AI Summary
                </div>
                """,
                unsafe_allow_html=True
            )


            st.write(summary)


            st.markdown(
                """
                </div>
                """,
                unsafe_allow_html=True
            )


            # =================================================
            # DOWNLOAD SUMMARY
            # =================================================

            st.download_button(
                label="📥 Download Summary",
                data=summary,
                file_name="youtube_summary.txt",
                mime="text/plain"
            )


            # =================================================
            # VIEW TRANSCRIPT
            # =================================================

            with st.expander(
                "📜 View Transcript"
            ):

                st.write(transcript)


            # =================================================
            # DOWNLOAD TRANSCRIPT
            # =================================================

            st.download_button(
                label="📥 Download Transcript",
                data=transcript,
                file_name="youtube_transcript.txt",
                mime="text/plain"
            )


            # =================================================
            # GENERATE PDF
            # =================================================

            try:

                with st.spinner(
                    "Creating PDF..."
                ):

                    pdf_data = create_pdf(
                        summary
                    )


                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_data,
                    file_name="youtube_summary.pdf",
                    mime="application/pdf"
                )


            except Exception as pdf_error:

                st.error(
                    f"PDF generation error: {pdf_error}"
                )


            # =================================================
            # VIDEO DOWNLOAD SECTION
            # =================================================

            st.markdown("---")


            st.markdown(
                """
                <div class="section-title">
                    🎥 Download Video
                </div>
                """,
                unsafe_allow_html=True
            )


            st.write(
                "Download the YouTube video in your preferred quality."
            )


            # =================================================
            # GET VIDEO FORMATS
            # =================================================

            try:

                with st.spinner(
                    "Finding available video qualities..."
                ):

                    video_data = get_video_formats(
                        youtube_url
                    )


                # -------------------------------------------------
                # EXTRACT ALL VIDEO FORMATS
                # -------------------------------------------------

                formats = video_data.get(
                    "formats",
                    []
                )


                # -------------------------------------------------
                # KEEP ONLY VIDEO FORMATS
                # -------------------------------------------------

                video_formats = [
                    fmt
                    for fmt in formats
                    if fmt.get("type") == "video"
                    and fmt.get("url")
                ]


                if not video_formats:

                    st.warning(
                        "No downloadable video qualities were found."
                    )


                else:

                    # =================================================
                    # SORT VIDEO QUALITIES
                    # =================================================

                    def get_quality_number(fmt):

                        label = str(
                            fmt.get(
                                "label",
                                "0"
                            )
                        )


                        try:

                            return int(
                                label.replace(
                                    "p",
                                    ""
                                )
                            )

                        except ValueError:

                            return 0


                    video_formats.sort(
                        key=get_quality_number,
                        reverse=True
                    )


                    # =================================================
                    # CREATE QUALITY OPTIONS
                    # =================================================

                    quality_options = []


                    for fmt in video_formats:

                        # GenDownload uses "label"
                        # such as "2160p", "1440p", "1080p"

                        quality = fmt.get(
                            "label",
                            "Unknown quality"
                        )


                        filesize = fmt.get(
                            "filesize"
                        )


                        # -------------------------------------------------
                        # CALCULATE FILE SIZE
                        # -------------------------------------------------

                        if filesize:

                            size_mb = (
                                filesize
                                / (1024 * 1024)
                            )


                            display_label = (
                                f"{quality} "
                                f"({size_mb:.1f} MB)"
                            )

                        else:

                            display_label = str(
                                quality
                            )


                        # -------------------------------------------------
                        # STORE LABEL + COMPLETE FORMAT
                        # -------------------------------------------------

                        quality_options.append(
                            (
                                display_label,
                                fmt
                            )
                        )


                    # =================================================
                    # QUALITY SELECTOR
                    # =================================================

                    selected_label = st.selectbox(
                        "Choose video quality",
                        [
                            item[0]
                            for item in quality_options
                        ],
                        key="video_quality"
                    )


                    # =================================================
                    # FIND SELECTED FORMAT
                    # =================================================

                    selected_format = None


                    for label, fmt in quality_options:

                        if label == selected_label:

                            selected_format = fmt

                            break


                    # =================================================
                    # PREPARE DOWNLOAD
                    # =================================================

                    prepare_video = st.button(
                        "⬇️ Prepare Video Download",
                        use_container_width=True,
                        key="prepare_video"
                    )


                    if prepare_video:

                        if selected_format is None:

                            st.error(
                                "Invalid video quality selected."
                            )

                        else:

                            try:

                                # -------------------------------------------------
                                # GET DOWNLOAD URL
                                # -------------------------------------------------

                                video_url = selected_format.get(
                                    "url"
                                )


                                if not video_url:

                                    raise Exception(
                                        "No download URL was returned "
                                        "for this quality."
                                    )


                                # -------------------------------------------------
                                # GET QUALITY
                                # -------------------------------------------------

                                selected_quality = selected_format.get(
                                    "label",
                                    "video"
                                )


                                # -------------------------------------------------
                                # DOWNLOAD VIDEO
                                # -------------------------------------------------

                                with st.spinner(
                                    f"Preparing {selected_quality} video..."
                                ):

                                    video_bytes = download_video(
                                        video_url
                                    )


                                st.success(
                                    "Video prepared successfully!"
                                )


                                # =================================================
                                # SAFE FILE NAME
                                # =================================================

                                video_title = video_data.get(
                                    "title",
                                    "YouTube Video"
                                )


                                safe_title = "".join(
                                    c
                                    for c in video_title
                                    if c.isalnum()
                                    or c in " -_"
                                ).strip()


                                if not safe_title:

                                    safe_title = (
                                        "youtube_video"
                                    )


                                file_name = (
                                    f"{safe_title}_"
                                    f"{selected_quality}.mp4"
                                )


                                # =================================================
                                # DOWNLOAD BUTTON
                                # =================================================

                                st.download_button(
                                    label="⬇️ Download Video",
                                    data=video_bytes,
                                    file_name=file_name,
                                    mime="video/mp4",
                                    use_container_width=True,
                                    key="download_video"
                                )


                            except Exception as video_error:

                                st.error(
                                    f"Video preparation error: "
                                    f"{video_error}"
                                )


            except Exception as format_error:

                st.error(
                    f"Could not retrieve video qualities: "
                    f"{format_error}"
                )


        # =====================================================
        # MAIN ERROR
        # =====================================================

        except Exception as e:

            st.error(
                f"Error: {e}"
            )


# =========================================================
# HOW IT WORKS
# =========================================================

st.markdown("---")


st.markdown(
    """
    <div class="section-title">
        ✨ How it works
    </div>
    """,
    unsafe_allow_html=True
)


col1, col2, col3 = st.columns(3)


with col1:

    st.markdown(
        "**🎬 1. Paste URL**"
    )

    st.caption(
        "Enter any supported YouTube video link."
    )


with col2:

    st.markdown(
        "**🤖 2. Generate**"
    )

    st.caption(
        "AI reads the transcript and creates a summary."
    )


with col3:

    st.markdown(
        "**📥 3. Download**"
    )

    st.caption(
        "Download your summary, transcript, PDF, or video."
    )