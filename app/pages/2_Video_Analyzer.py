import streamlit as st
import pandas as pd
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

from src.pose_analyzer import analyze_video_pose


st.set_page_config(
    page_title="Video Biomechanics Analyzer",
    page_icon="🎥",
    layout="wide"
)

st.title("🎥 Video Biomechanics Analyzer")

st.write(
    """
    Upload a sports movement video to extract video metadata, sample frames,
    pose skeleton overlays, joint angles, and early movement-risk indicators.
    """
)

st.warning(
    "Prototype note: This is an AI movement-analysis demo and not a medical diagnosis tool."
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

    tab1, tab2 = st.tabs(["Frame Extraction", "Pose Skeleton Analysis"])

    with tab1:
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
            else:
                st.error("No frames could be extracted from this video.")

    with tab2:
        st.markdown("### Run Pose Skeleton Analysis")

        st.write(
            """
            This uses MediaPipe Pose to detect body landmarks, draw skeleton overlays,
            calculate joint angles, and flag risky movement patterns.
            """
        )

        if st.button("Analyze Pose Skeleton"):
            pose_result = analyze_video_pose(
                video_path=video_path,
                output_dir=screenshot_output_dir,
                max_frames=6
            )

            if not pose_result["success"]:
                st.error(pose_result["error"])

                if "analyzed_frames" in pose_result:
                    st.markdown("### Frames Checked")
                    checked_cols = st.columns(3)

                    for index, frame_path in enumerate(pose_result["analyzed_frames"]):
                        with checked_cols[index % 3]:
                            st.image(
                                str(frame_path),
                                caption=f"Checked Frame {index + 1}",
                                use_container_width=True
                            )
            else:
                st.success("Pose analysis completed successfully.")

                metric_col1, metric_col2, metric_col3 = st.columns(3)

                with metric_col1:
                    st.metric(
                        "Movement Risk Score",
                        f"{pose_result['movement_risk_score']}%"
                    )

                with metric_col2:
                    st.metric(
                        "Movement Risk Level",
                        pose_result["movement_risk_level"]
                    )

                with metric_col3:
                    st.metric("Sport", sport)

                st.markdown("### Skeleton Overlay Frames")

                pose_cols = st.columns(3)

                for index, frame_path in enumerate(pose_result["analyzed_frames"]):
                    with pose_cols[index % 3]:
                        st.image(
                            str(frame_path),
                            caption=f"Pose Frame {index + 1}",
                            use_container_width=True
                        )

                st.markdown("---")

                st.markdown("### Average Joint Angles")

                angle_df = pd.DataFrame({
                    "Joint / Movement Metric": list(pose_result["average_angles"].keys()),
                    "Average Angle": list(pose_result["average_angles"].values())
                })

                st.dataframe(angle_df, use_container_width=True)

                st.bar_chart(
                    angle_df,
                    x="Joint / Movement Metric",
                    y="Average Angle"
                )

                st.markdown("---")

                st.markdown("### Risky Movement Flags")

                for flag in pose_result["risk_flags"]:
                    st.write(f"- {flag}")

                st.markdown("### Sport-Specific Interpretation")

                if sport == "Cricket":
                    st.info(
                        """
                        Cricket focus:
                        - Shoulder and elbow loading during bowling/throwing
                        - Spine tilt during delivery
                        - Front knee stability
                        - Ankle and landing balance
                        """
                    )

                elif sport == "Basketball":
                    st.info(
                        """
                        Basketball focus:
                        - Knee valgus during jump landing
                        - Ankle roll risk
                        - Hip-knee alignment
                        - Landing balance
                        """
                    )

                elif sport == "Soccer":
                    st.info(
                        """
                        Soccer focus:
                        - Hip rotation during kicking
                        - Knee loading
                        - Ankle stability
                        - Sprint posture and hamstring load
                        """
                    )

                elif sport == "Tennis":
                    st.info(
                        """
                        Tennis focus:
                        - Shoulder load during serve
                        - Elbow and wrist stress
                        - Spine rotation
                        - Knee bend during serve
                        """
                    )

                elif sport == "Running":
                    st.info(
                        """
                        Running focus:
                        - Hip drop
                        - Knee angle
                        - Ankle landing position
                        - Stride imbalance
                        """
                    )

                elif sport == "Weightlifting":
                    st.info(
                        """
                        Weightlifting focus:
                        - Spine/back angle
                        - Knee collapse
                        - Hip alignment
                        - Shoulder stability
                        """
                    )

else:
    st.info("Upload a video to begin analysis.")