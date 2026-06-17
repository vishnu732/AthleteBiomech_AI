import cv2
import uuid
from pathlib import Path


def save_uploaded_video(uploaded_file, output_dir):
    """
    Saves uploaded Streamlit video file to local outputs folder.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_extension = Path(uploaded_file.name).suffix
    unique_filename = f"uploaded_video_{uuid.uuid4().hex[:8]}{file_extension}"
    video_path = output_dir / unique_filename

    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return video_path


def get_video_metadata(video_path):
    """
    Extracts basic metadata from a video using OpenCV.
    """
    video_path = str(video_path)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return {
            "success": False,
            "error": "Unable to open video file."
        }

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    duration = frame_count / fps if fps > 0 else 0

    cap.release()

    return {
        "success": True,
        "fps": round(fps, 2),
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "duration_seconds": round(duration, 2)
    }


def extract_sample_frames(video_path, output_dir, max_frames=6):
    """
    Extracts sample frames from the video and saves them as images.
    """
    video_path = str(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return []

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if frame_count == 0:
        cap.release()
        return []

    interval = max(frame_count // max_frames, 1)

    saved_frames = []
    frame_index = 0
    saved_count = 0

    while cap.isOpened() and saved_count < max_frames:
        ret, frame = cap.read()

        if not ret:
            break

        if frame_index % interval == 0:
            frame_filename = f"frame_{saved_count + 1}_{uuid.uuid4().hex[:6]}.jpg"
            frame_path = output_dir / frame_filename

            cv2.imwrite(str(frame_path), frame)

            saved_frames.append(frame_path)
            saved_count += 1

        frame_index += 1

    cap.release()

    return saved_frames