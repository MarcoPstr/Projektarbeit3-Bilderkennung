import numpy as np

def find_depth(right_point, left_point, frame_right, frame_left, baseline, f, alpha):

    height_right, width_right, _ = frame_right.shape
    height_left, width_left, _ = frame_left.shape

    # Winkel in Pixelbrennweite umrechnen
    f_pixel = (width_right * 0.5) / np.tan(alpha * 0.5 * np.pi / 180)

    x_right = right_point[0]
    x_left = left_point[0]

    disparity = np.linalg.norm(np.array(left_point) - np.array(right_point))

    zDepth = (baseline * f_pixel) / disparity

    return abs(zDepth)
