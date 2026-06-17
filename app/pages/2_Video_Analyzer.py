import streamlit as st
import sys
from pathlib import Path

# Add project root folder to Python path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from src.video_processor import (
    save_uploaded_video,
    get_video_metadata,
    extract_sample_frames
)

st.set_page_config(
    page_title="Video Biomechanics Analyzer",
    page_icon="🎥",
    layout="wide"
)

st.title("🎥 Video Biomechanics Analyzer")
st.write(
    """
    Upload a sports movement video to extract metadata and sample frames.
    This module is the foundation for pose estimation, joint-angle tracking,
    and body-load analysis.
    """
)

st.markdown("---")

sport = st.selectbox(
    "Select Sport",
    ["Cricket", "Soccer", "Basketball", "Tennis", "Running", "Weightlifting"]
)

movement_type = st.selectbox(
    "Select Movement Type",
    [
        "Bowling / Throwing",
        "Running / Sprinting",
        "Jump Landing",
        "Kicking",
        "Tennis Serve",
        "Squat / Deadlift",
        "General Movement"
    ]
)

uploaded_video = st.file_uploader(
    "Upload a sports video",
    type=["mp4", "mov", "avi", "mkv"]
)

if uploaded_video is not None:
    st.success("Video uploaded successfully.")

    video_output_dir = ROOT_DIR / "outputs" / "processed_videos"
    screenshot_output_dir = ROOT_DIR / "outputs" / "screenshots"

    video_path = save_uploaded_video(uploaded_video, video_output_dir)

    st.markdown("### Video Preview")
    st.video(str(video_path))

    st.markdown("---")

    st.markdown("### Video Metadata")

    metadata = get_video_metadata(video_path)

    if not metadata["success"]:
        st.error(metadata["error"])
    else:
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("FPS", metadata["fps"])

        with col2:
            st.metric("Frames", metadata["frame_count"])

        with col3:
            st.metric("Duration", f"{metadata['duration_seconds']} sec")

        with col4:
            st.metric("Width", metadata["width"])

        with col5:
            st.metric("Height", metadata["height"])

        st.markdown("---")

        st.markdown("### Extract Sample Frames")

        if st.button("Extract Frames"):
            frames = extract_sample_frames(
                video_path=video_path,
                output_dir=screenshot_output_dir,
                max_frames=6
            )

            if frames:
                st.success(f"Extracted {len(frames)} sample frames.")

                frame_cols = st.columns(3)

                for index, frame_path in enumerate(frames):
                    with frame_cols[index % 3]:
                        st.image(
                            str(frame_path),
                            caption=f"Frame {index + 1}",
                            use_container_width=True
                        )

                st.markdown("---")

                st.markdown("### Initial Biomechanics Analysis Status")

                st.info(
                    f"""
                    Sport Selected: {sport}

                    Movement Type: {movement_type}

                    Current Module Status:
                    - Video upload: Completed
                    - Metadata extraction: Completed
                    - Frame extraction: Completed
                    - Pose estimation: Coming next
                    - Joint-angle calculation: Coming next
                    - Injury risk from movement: Coming next
                    """
                )

                st.markdown("### Next Planned Detection")

                if sport == "Cricket":
                    st.write("- Bowling shoulder alignment")
                    st.write("- Elbow angle during release")
                    st.write("- Spine tilt during delivery")
                    st.write("- Front knee landing stability")
                    st.write("- Ankle and foot landing position")

                elif sport == "Basketball":
                    st.write("- Knee valgus during landing")
                    st.write("- Ankle roll risk")
                    st.write("- Hip-knee alignment")
                    st.write("- Jump landing balance")

                elif sport == "Soccer":
                    st.write("- Hip rotation during kicking")
                    st.write("- Knee loading")
                    st.write("- Ankle stability")
                    st.write("- Sprint posture and hamstring load")

                elif sport == "Tennis":
                    st.write("- Shoulder load during serve")
                    st.write("- Elbow and wrist stress")
                    st.write("- Spine rotation")
                    st.write("- Knee bend during serve")

                elif sport == "Running":
                    st.write("- Hip drop")
                    st.write("- Knee angle")
                    st.write("- Ankle landing position")
                    st.write("- Stride imbalance")

                elif sport == "Weightlifting":
                    st.write("- Spine/back angle")
                    st.write("- Knee collapse")
                    st.write("- Hip alignment")
                    st.write("- Shoulder stability")

            else:
                st.error("No frames could be extracted from this video.")
else:
    st.info("Upload a video to begin analysis.")