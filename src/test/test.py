# ==============================
# IMPORT LIBRARIES
# ==============================

import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import time
import pandas as pd

from keras.models import load_model

# ==============================
# LOAD TRAINED MODELS
# ==============================

EYE_MODEL_PATH = "model/eye_state_model.h5"
YAWN_MODEL_PATH = "model/yawn_model.h5"

eye_model = load_model(EYE_MODEL_PATH, compile=False)
yawn_model = load_model(YAWN_MODEL_PATH, compile=False)

# ==============================
# IMAGE PREPROCESSING
# ==============================

def preprocess_image(img):

    img = cv2.resize(img, (64, 64))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    return img

# ==============================
# INITIALIZE MEDIAPIPE
# ==============================

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)