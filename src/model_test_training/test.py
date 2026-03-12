# ==============================
# IMPORT LIBRARIES
# ==============================

import cv2
import numpy as np
import mediapipe as mp

import tensorflow as tf
from tensorflow.keras.models import load_model # type: ignore
import h5py
import json

# ==============================
# LOAD TRAINED MODELS
# ==============================

EYE_MODEL_PATH  = "./src/model/eye_state_model.h5"
YAWN_MODEL_PATH = "./src/model/yawn_model.h5"

def load_model_compatible(path):
    """Load .h5 model while patching InputLayer config for Keras 2.15 compatibility."""
    with h5py.File(path, 'r+') as f:
        model_config = f.attrs.get('model_config')
        if model_config:
            if isinstance(model_config, bytes):
                model_config = model_config.decode('utf-8')
            config = json.loads(model_config)

            def patch_config(obj):
                if isinstance(obj, dict):
                    if obj.get('class_name') == 'InputLayer':
                        cfg = obj.get('config', {})
                        if 'batch_shape' in cfg:
                            cfg['batch_input_shape'] = cfg.pop('batch_shape')
                        elif 'shape' in cfg:
                            cfg['batch_input_shape'] = cfg.pop('shape')
                        cfg.pop('sparse', None)
                        cfg.pop('ragged', None)

                    if 'config' in obj:
                        cfg = obj['config']
                        if isinstance(cfg, dict) and 'dtype' in cfg:
                            dtype_val = cfg['dtype']
                            if isinstance(dtype_val, dict) and dtype_val.get('class_name') == 'DTypePolicy':
                                cfg['dtype'] = dtype_val.get('config', {}).get('name', 'float32')

                    for v in obj.values():
                        patch_config(v)
                elif isinstance(obj, list):
                    for item in obj:
                        patch_config(item)

            patch_config(config)
            f.attrs['model_config'] = json.dumps(config).encode('utf-8')

    return load_model(path, compile=False)

eye_model  = load_model_compatible(EYE_MODEL_PATH)
yawn_model = load_model_compatible(YAWN_MODEL_PATH)

# ==============================
# IMAGE PREPROCESSING
# ==============================

def preprocess_image(img):
    img = cv2.resize(img, (64, 64))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# ==============================
# BOUNDING BOX CROP
# ==============================

def crop_region(points, frame, padding=10):
    h, w = frame.shape[:2]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x1 = max(min(xs) - padding, 0)
    x2 = min(max(xs) + padding, w)
    y1 = max(min(ys) - padding, 0)
    y2 = min(max(ys) + padding, h)
    return frame[y1:y2, x1:x2]

# ==============================
# INITIALIZE MEDIAPIPE
# ==============================

mp_face_mesh = mp.solutions.face_mesh # type: ignore

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ==============================
# FACIAL LANDMARK INDEXES
# ==============================

LEFT_EYE  = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
MOUTH     = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409,
             291, 375, 321, 405, 314, 17, 84, 181, 91, 146]

# ==============================
# FRAME COUNTERS & THRESHOLDS
# ==============================

eye_closed_frames = 0
yawn_frames       = 0
DROWSY_THRESHOLD  = 4
YAWN_THRESHOLD    = 20

# ==============================
# START WEBCAM
# ==============================

cap = cv2.VideoCapture(0)

while cap.isOpened():

    ret, frame = cap.read()
    if not ret:
        break

    frame   = cv2.flip(frame, 1)
    rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:

        for face_landmarks in results.multi_face_landmarks:

            h, w, _ = frame.shape

            # LEFT EYE
            left_eye_points = []
            for idx in LEFT_EYE:
                lm = face_landmarks.landmark[idx]
                left_eye_points.append((int(lm.x * w), int(lm.y * h)))

            # RIGHT EYE
            right_eye_points = []
            for idx in RIGHT_EYE:
                lm = face_landmarks.landmark[idx]
                right_eye_points.append((int(lm.x * w), int(lm.y * h)))

            # MOUTH
            mouth_points = []
            for idx in MOUTH:
                lm = face_landmarks.landmark[idx]
                mouth_points.append((int(lm.x * w), int(lm.y * h)))

            # ==============================
            # CROP REGIONS
            # ==============================

            left_eye_crop  = crop_region(left_eye_points, frame, padding=10)
            right_eye_crop = crop_region(right_eye_points, frame, padding=10)
            mouth_crop     = crop_region(mouth_points, frame, padding=15)

            # ==============================
            # MODEL PREDICTIONS
            # ==============================

            eye_closed = False
            yawning    = False

            # LEFT EYE MODEL (0 = closed, 1 = open)
            if left_eye_crop.size != 0 and right_eye_crop.size != 0:
                left_pred  = eye_model(preprocess_image(left_eye_crop),  training=False)
                right_pred = eye_model(preprocess_image(right_eye_crop), training=False)
                avg_pred   = (left_pred[0][0] + right_pred[0][0]) / 2
                eye_closed = avg_pred < 0.5

            elif left_eye_crop.size != 0:
                pred = eye_model(preprocess_image(left_eye_crop), training=False)
                eye_closed = pred[0][0] < 0.5

            elif right_eye_crop.size != 0:
                pred = eye_model(preprocess_image(right_eye_crop), training=False)
                eye_closed = pred[0][0] < 0.5

            # MOUTH MODEL (0 = yawning, 1 = not yawning)
            if mouth_crop.size != 0:
                pred = yawn_model(preprocess_image(mouth_crop), training=False)
                yawning = pred[0][0] > 0.35  # strict: only confident yawns

            # ==============================
            # FRAME COUNTERS
            # ==============================

            eye_closed_frames = eye_closed_frames + 1 if eye_closed else 0
            yawn_frames       = yawn_frames + 1       if yawning    else 0

            # ==============================
            # DISPLAY ALERTS
            # ==============================

            if eye_closed_frames > DROWSY_THRESHOLD:
                cv2.putText(frame, "DROWSINESS ALERT", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            if yawn_frames > YAWN_THRESHOLD:
                cv2.putText(frame, "YAWNING DETECTED", (30, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)

    cv2.imshow("Driver Monitor", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()