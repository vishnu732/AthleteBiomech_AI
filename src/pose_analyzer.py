import cv2
import uuid
import math
from pathlib import Path

from ultralytics import YOLO

from src.joint_angle_calculator import calculate_angle, calculate_spine_tilt


# YOLO Pose COCO keypoint indexes
NOSE = 0
LEFT_EYE = 1
RIGHT_EYE = 2
LEFT_EAR = 3
RIGHT_EAR = 4
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


SKELETON_CONNECTIONS = [
    (LEFT_SHOULDER, RIGHT_SHOULDER),
    (LEFT_SHOULDER, LEFT_ELBOW),
    (LEFT_ELBOW, LEFT_WRIST),
    (RIGHT_SHOULDER, RIGHT_ELBOW),
    (RIGHT_ELBOW, RIGHT_WRIST),
    (LEFT_SHOULDER, LEFT_HIP),
    (RIGHT_SHOULDER, RIGHT_HIP),
    (LEFT_HIP, RIGHT_HIP),
    (LEFT_HIP, LEFT_KNEE),
    (LEFT_KNEE, LEFT_ANKLE),
    (RIGHT_HIP, RIGHT_KNEE),
    (RIGHT_KNEE, RIGHT_ANKLE)
]


def get_point(keypoints, index):
    return (
        float(keypoints[index][0]),
        float(keypoints[index][1])
    )


def calculate_pose_angles_from_yolo(keypoints):
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

    return {
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


def select_target_player(boxes, frame_width, frame_height, target_mode):
    """
    Selects one target player from multiple detected people.
    """
    if boxes is None or len(boxes) == 0:
        return None

    best_index = 0

    if target_mode == "Largest Player":
        max_area = -1

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box
            area = max(0, x2 - x1) * max(0, y2 - y1)

            if area > max_area:
                max_area = area
                best_index = i

    elif target_mode == "Center Player":
        frame_center_x = frame_width / 2
        frame_center_y = frame_height / 2
        min_distance = float("inf")

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box
            player_center_x = (x1 + x2) / 2
            player_center_y = (y1 + y2) / 2

            distance = math.sqrt(
                (player_center_x - frame_center_x) ** 2
                + (player_center_y - frame_center_y) ** 2
            )

            if distance < min_distance:
                min_distance = distance
                best_index = i

    return best_index


def draw_target_skeleton(frame, keypoints, box):
    """
    Draws skeleton only for the selected target player.
    """
    annotated = frame.copy()

    x1, y1, x2, y2 = [int(v) for v in box]

    cv2.rectangle(
        annotated,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        3
    )

    cv2.putText(
        annotated,
        "TARGET PLAYER",
        (x1, max(y1 - 10, 30)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    for start_idx, end_idx in SKELETON_CONNECTIONS:
        x_start, y_start = keypoints[start_idx]
        x_end, y_end = keypoints[end_idx]

        if x_start > 0 and y_start > 0 and x_end > 0 and y_end > 0:
            cv2.line(
                annotated,
                (int(x_start), int(y_start)),
                (int(x_end), int(y_end)),
                (255, 255, 0),
                3
            )

    for point in keypoints:
        x, y = point

        if x > 0 and y > 0:
            cv2.circle(
                annotated,
                (int(x), int(y)),
                5,
                (0, 0, 255),
                -1
            )

    return annotated


def generate_pose_risk_flags(average_angles):
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


def analyze_video_pose(
    video_path,
    output_dir,
    target_mode="Largest Player",
    analysis_fps=2,
    max_analysis_seconds=10
):
    """
    Runs YOLOv8 pose detection on one targeted player only.
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

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if frame_count == 0 or video_fps == 0:
        cap.release()
        return {
            "success": False,
            "error": "Video has no readable frames."
        }

    total_duration = frame_count / video_fps
    analysis_duration = min(total_duration, max_analysis_seconds)

    frame_interval = max(int(video_fps / analysis_fps), 1)
    max_frames_to_process = int(analysis_duration * analysis_fps)

    analyzed_frames = []
    all_angles = []

    frame_index = 0
    processed_count = 0
    target_detected_count = 0

    while cap.isOpened() and processed_count < max_frames_to_process:
        ret, frame = cap.read()

        if not ret:
            break

        if frame_index % frame_interval == 0:
            results = model.predict(frame, conf=0.3, verbose=False)

            annotated_frame = frame.copy()

            if results and len(results) > 0:
                result = results[0]

                if (
                    result.keypoints is not None
                    and result.keypoints.xy is not None
                    and result.boxes is not None
                ):
                    keypoints_data = result.keypoints.xy.cpu().numpy()
                    boxes_data = result.boxes.xyxy.cpu().numpy()

                    if len(keypoints_data) > 0 and len(boxes_data) > 0:
                        target_index = select_target_player(
                            boxes=boxes_data,
                            frame_width=frame_width,
                            frame_height=frame_height,
                            target_mode=target_mode
                        )

                        if target_index is not None:
                            target_keypoints = keypoints_data[target_index]
                            target_box = boxes_data[target_index]

                            annotated_frame = draw_target_skeleton(
                                frame=frame,
                                keypoints=target_keypoints,
                                box=target_box
                            )

                            try:
                                angles = calculate_pose_angles_from_yolo(target_keypoints)
                                all_angles.append(angles)
                                target_detected_count += 1

                                cv2.putText(
                                    annotated_frame,
                                    f"Target Mode: {target_mode}",
                                    (30, frame_height - 40),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.8,
                                    (0, 255, 0),
                                    2
                                )
                            except Exception:
                                cv2.putText(
                                    annotated_frame,
                                    "Angle calculation failed",
                                    (30, 40),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.8,
                                    (0, 255, 255),
                                    2
                                )
                    else:
                        cv2.putText(
                            annotated_frame,
                            "No target keypoints detected",
                            (30, 40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 0, 255),
                            2
                        )
                else:
                    cv2.putText(
                        annotated_frame,
                        "No pose detected",
                        (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 0, 255),
                        2
                    )

            frame_filename = f"target_pose_frame_{processed_count + 1}_{uuid.uuid4().hex[:6]}.jpg"
            frame_path = output_dir / frame_filename

            cv2.imwrite(str(frame_path), annotated_frame)
            analyzed_frames.append(frame_path)

            processed_count += 1

        frame_index += 1

    cap.release()

    if not all_angles:
        return {
            "success": False,
            "error": "No usable target player pose was detected.",
            "analyzed_frames": analyzed_frames,
            "processed_frames": processed_count,
            "target_detected_frames": target_detected_count
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
        "risk_flags": risk_flags,
        "processed_frames": processed_count,
        "target_detected_frames": target_detected_count,
        "analysis_fps": analysis_fps,
        "target_mode": target_mode
    }