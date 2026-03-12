# Methodology

## Overview

The methodology of the AI-Based Driver Alertness Monitoring System focuses on detecting driver fatigue using computer vision techniques and behavioral indicators. The system processes real-time video data from a smartphone camera and analyzes facial features to detect signs of drowsiness.

The methodology consists of several stages including video acquisition, facial landmark detection, feature extraction, fatigue detection, and alert generation.

---

## Step 1: Video Capture

The system captures live video using the device camera.

Video frames are streamed to the application in real time using WebRTC through the Streamlit interface.

Each frame is processed individually to detect facial landmarks and analyze driver behavior.

---

## Step 2: Face Detection and Landmark Extraction

MediaPipe Face Mesh is used to detect facial landmarks in each frame.

The model identifies facial structures including:

- Eyes
- Mouth
- Nose
- Face contour

From these landmarks, the system extracts specific points that correspond to the eye and mouth regions.

---

## Step 3: Eye Aspect Ratio (EAR) Calculation

The Eye Aspect Ratio (EAR) is used to determine whether the driver's eyes are open or closed.

EAR is calculated using distances between specific eye landmarks.

If the EAR value remains below a predefined threshold for a certain number of frames, the system detects possible drowsiness.

---

## Step 4: Mouth Aspect Ratio (MAR) Calculation

The Mouth Aspect Ratio (MAR) is used to detect yawning behavior.

MAR is computed using the distance between upper and lower lip landmarks.

If MAR exceeds a threshold for several frames, the system identifies a yawning event.

---

## Step 5: Multi-Factor Risk Analysis

The system combines multiple indicators to evaluate driver safety.

The following factors are considered:

- Eye closure duration
- Yawning frequency
- Vehicle speed
- Blood oxygen level (SpO₂)

Each detected risk contributes to a **danger score**.

---

## Step 6: Alert Scoring Mechanism

The system assigns alert levels based on the number of detected hazards.

| Condition | Alert Type |
|----------|-----------|
| Eye closure | Drowsiness alert |
| Yawning | Fatigue alert |
| Overspeed | Speed warning |
| Low SpO₂ | Health alert |

The combined alerts produce an overall **danger score**.

---

## Step 7: Emergency Detection Logic

If multiple hazards occur simultaneously and persist for a specified duration, the system triggers an emergency alert.

This helps prevent false alarms and ensures alerts are generated only during sustained hazardous conditions.

---

## Step 8: Alert and Notification System

The system generates alerts through:

- Visual notifications on the dashboard
- Audio alerts
- System notifications

These warnings inform the driver and encourage immediate corrective action.

---

## Step 9: Data Logging

Emergency events and alerts are recorded for monitoring and analysis.

This data can be used to evaluate driver behavior and improve safety strategies.

---

## Summary

The proposed methodology combines computer vision techniques with behavioral analysis and sensor data to detect driver fatigue. By integrating multiple risk indicators, the system provides a more reliable driver monitoring solution compared to single-factor fatigue detection systems.