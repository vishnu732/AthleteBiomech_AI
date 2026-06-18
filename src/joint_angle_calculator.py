import numpy as np


def calculate_angle(point_a, point_b, point_c):
    """
    Calculates the angle at point_b using three 2D points.
    Each point should be a tuple: (x, y)
    """
    a = np.array(point_a)
    b = np.array(point_b)
    c = np.array(point_c)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (
        np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8
    )

    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

    angle = np.degrees(np.arccos(cosine_angle))

    return round(angle, 2)


def calculate_spine_tilt(left_shoulder, right_shoulder, left_hip, right_hip):
    """
    Estimates spine tilt angle using shoulder midpoint and hip midpoint.
    0 degrees means more vertical posture.
    Higher values mean more side/back tilt.
    """
    shoulder_mid = (
        (left_shoulder[0] + right_shoulder[0]) / 2,
        (left_shoulder[1] + right_shoulder[1]) / 2
    )

    hip_mid = (
        (left_hip[0] + right_hip[0]) / 2,
        (left_hip[1] + right_hip[1]) / 2
    )

    dx = hip_mid[0] - shoulder_mid[0]
    dy = hip_mid[1] - shoulder_mid[1]

    angle_from_vertical = abs(np.degrees(np.arctan2(dx, dy + 1e-8)))

    return round(angle_from_vertical, 2)