import cv2
import uuid
from pathlib import Path

from ultralytics import YOLO

from src.joint_angle_calculator import calculate_angle, calculate_spine_tilt


# COCO keypoint indexes used by YOLO pose models
LEFT_SHOULDER = 5
RIGHT_SHOULDER = 6
LEFT_ELBOW = 7
RIGHT_ELBOW = 8
LEFT_WRIST = 9
RIGHT_WRIST = 10
LEFT_HIP = 11
RIGHT_HIP = 12
LEFT_KNEE = 13
RIGHT_KNEE = 14
LEFT_ANKLE = 15
RIGHT_ANKLE = 16


def get_point(keypoints, index):
    """
    Returns x, y point from YOLO keypoints.
    """
    return (
        float(keypoints[index][0]),
        float(keypoints[index][1])
    )


def calculate_pose_angles_from_yolo(keypoints):
    """
    Calculates major joint angles from YOLO pose keypoints.
    """
    left_shoulder = get_point(keypoints, LEFT_SHOULDER)
    right_shoulder = get_point(keypoints, RIGHT_SHOULDER)

    left_elbow = get_point(keypoints, LEFT_ELBOW)
    right_elbow = get_point(keypoints, RIGHT_ELBOW)

    left_wrist = get_point(keypoints, LEFT_WRIST)
    right_wrist = get_point(keypoints, RIGHT_WRIST)

    left_hip = get_point(keypoints, LEFT_HIP)
    right_hip = get_point(keypoints, RIGHT_HIP)

    left_knee = get_point(keypoints, LEFT_KNEE)
    right_knee = get_point(keypoints, RIGHT_KNEE)

    left_ankle = get_point(keypoints, LEFT_ANKLE)
    right_ankle = get_point(keypoints, RIGHT_ANKLE)

    angles = {
        "left_elbow_angle": calculate_angle(left_shoulder, left_elbow, left_wrist),
        "right_elbow_angle": calculate_angle(right_shoulder, right_elbow, right_wrist),
        "left_knee_angle": calculate_angle(left_hip, left_knee, left_ankle),
        "right_knee_angle": calculate_angle(right_hip, right_knee, right_ankle),
        "left_shoulder_angle": calculate_angle(left_elbow, left_shoulder, left_hip),
        "right_shoulder_angle": calculate_angle(right_elbow, right_shoulder, right_hip),
        "spine_tilt_angle": calculate_spine_tilt(
            left_shoulder,
            right_shoulder,
            left_hip,
            right_hip
        )
    }

    return angles


def generate_pose_risk_flags(average_angles):
    """
    Simple prototype risk rules based on average joint angles.
    """
    flags = []

    left_knee = average_angles.get("left_knee_angle", 0)
    right_knee = average_angles.get("right_knee_angle", 0)
    spine_tilt = average_angles.get("spine_tilt_angle", 0)
    left_elbow = average_angles.get("left_elbow_angle", 0)
    right_elbow = average_angles.get("right_elbow_angle", 0)
    left_shoulder = average_angles.get("left_shoulder_angle", 0)
    right_shoulder = average_angles.get("right_shoulder_angle", 0)

    if left_knee > 165 or right_knee > 165:
        flags.append("Possible stiff knee or hyperextension pattern detected.")

    if left_knee < 90 or right_knee < 90:
        flags.append("Deep knee flexion detected; monitor landing or squat load.")

    if spine_tilt > 20:
        flags.append("Excessive spine tilt detected; possible lower-back load risk.")

    if left_elbow > 165 or right_elbow > 165:
        flags.append("High elbow extension detected; monitor throwing or striking mechanics.")

    if left_shoulder > 150 or right_shoulder > 150:
        flags.append("High shoulder elevation detected; possible shoulder overload risk.")

    if not flags:
        flags.append("No major risky posture pattern detected in sampled frames.")

    movement_risk_score = 20 + (len(flags) * 15)
    movement_risk_score = min(movement_risk_score, 100)

    if movement_risk_score <= 35:
        movement_risk_level = "LOW"
    elif movement_risk_score <= 65:
        movement_risk_level = "MEDIUM"
    else:
        movement_risk_level = "HIGH"

    return movement_risk_score, movement_risk_level, flags


def analyze_video_pose(video_path, output_dir, max_frames=6):
    """
    Runs YOLOv8 pose detection on sampled video frames.
    Saves skeleton-overlay frames and returns joint-angle summary.
    """
    video_path = str(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO("yolov8n-pose.pt")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return {
            "success": False,
            "error": "Unable to open video for pose analysis."
        }

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if frame_count == 0:
        cap.release()
        return {
            "success": False,
            "error": "Video has no frames."
        }

    interval = max(frame_count // max_frames, 1)

    analyzed_frames = []
    all_angles = []

    frame_index = 0
    saved_count = 0

    while cap.isOpened() and saved_count < max_frames:
        ret, frame = cap.read()

        if not ret:
            break

        if frame_index % interval == 0:
            results = model.predict(frame, conf=0.3, verbose=False)

            if results and len(results) > 0:
                result = results[0]
                annotated_frame = result.plot()

                if result.keypoints is not None and result.keypoints.xy is not None:
                    keypoints_data = result.keypoints.xy.cpu().numpy()

                    if len(keypoints_data) > 0:
                        person_keypoints = keypoints_data[0]

                        try:
                            angles = calculate_pose_angles_from_yolo(person_keypoints)
                            all_angles.append(angles)

                            cv2.putText(
                                annotated_frame,
                                "YOLO Pose Detected",
                                (30, 40),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 255, 0),
                                2
                            )
                        except Exception:
                            cv2.putText(
                                annotated_frame,
                                "Pose Detected - Angle Error",
                                (30, 40),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 255, 255),
                                2
                            )
                    else:
                        cv2.putText(
                            annotated_frame,
                            "No Person Keypoints",
                            (30, 40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 0, 255),
                            2
                        )
                else:
                    cv2.putText(
                        annotated_frame,
                        "No Pose Keypoints",
                        (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2
                    )
            else:
                annotated_frame = frame
                cv2.putText(
                    annotated_frame,
                    "No Pose Detected",
                    (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

            frame_filename = f"pose_frame_{saved_count + 1}_{uuid.uuid4().hex[:6]}.jpg"
            frame_path = output_dir / frame_filename

            cv2.imwrite(str(frame_path), annotated_frame)
            analyzed_frames.append(frame_path)

            saved_count += 1

        frame_index += 1

    cap.release()

    if not all_angles:
        return {
            "success": False,
            "error": "No usable human pose keypoints were detected in sampled frames.",
            "analyzed_frames": analyzed_frames
        }

    average_angles = {}

    for key in all_angles[0].keys():
        values = [frame_angles[key] for frame_angles in all_angles]
        average_angles[key] = round(sum(values) / len(values), 2)

    movement_risk_score, movement_risk_level, risk_flags = generate_pose_risk_flags(
        average_angles
    )

    return {
        "success": True,
        "analyzed_frames": analyzed_frames,
        "average_angles": average_angles,
        "movement_risk_score": movement_risk_score,
        "movement_risk_level": movement_risk_level,
        "risk_flags": risk_flags
    }