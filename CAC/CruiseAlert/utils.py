from scipy.spatial import distance
import dlib
import cv2
import numpy as np
import base64
import io
from PIL import Image

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r'C:\Users\Ram\PycharmProjects\Cruise-Alert\models\shape_predictor_68_face_landmarks.dat')

LEFT_EYE = list(range(36, 42))
RIGHT_EYE = list(range(42, 48))
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 48
counter = 0

def calculate_eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

left_eye = None
right_eye = None
ear = 0

def detect_sleep_from_frame(image_data):
    global counter
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)
    status = "Awake"
    left_eye_coords = []
    right_eye_coords = []
    ear = 0

    if len(faces) == 0:
        print("No faces detected.")
        return {
            "status": status,
            "ear": ear,
            "left_eye": left_eye_coords,
            "right_eye": right_eye_coords,
        }

    for face in faces:
        landmarks = predictor(gray, face)
        landmarks = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(68)])
        left_eye = landmarks[LEFT_EYE]
        right_eye = landmarks[RIGHT_EYE]
        left_ear = calculate_eye_aspect_ratio(left_eye)
        right_ear = calculate_eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0

        print(f"Left EAR: {left_ear}, Right EAR: {right_ear}, Combined EAR: {ear}")

        if ear < EYE_AR_THRESH:
            counter += 1
            if counter >= EYE_AR_CONSEC_FRAMES:
                status = "Sleeping"
        else:
            counter = 0

        # Store eye coordinates for the response
        left_eye_coords = left_eye
        right_eye_coords = right_eye

    return {
        "status": status,
        "ear": ear,  # Eye Aspect Ratio
        "left_eye": left_eye_coords.tolist(),  # Convert to list for JSON
        "right_eye": right_eye_coords.tolist(),  # Convert to list for JSON
    }
