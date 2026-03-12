# System Architecture

## Overview

The AI-Based Driver Alertness Monitoring System is designed to detect driver fatigue and unsafe driving behavior using computer vision and sensor data. The system operates using a smartphone camera, optional wearable device data, and a web-based monitoring dashboard.

The architecture focuses on creating a low-cost driver monitoring system that does not require specialized automotive hardware. Instead, it uses commonly available devices such as smartphones and smartwatches.

---

## Architecture Components

The system consists of the following major components:

### 1. Smartphone Device

The smartphone acts as the primary sensing device and provides:

- Camera for driver face monitoring
- Internet connectivity for dashboard access
- GPS data for vehicle speed and location tracking

The camera captures the driver's face and streams video frames to the processing pipeline.

---

### 2. Frame Preprocessing (OpenCV)

Incoming video frames are processed using OpenCV.

Key operations include:

- Frame extraction from video stream
- Image enhancement
- Conversion to grayscale (if required)
- Preparation of frames for landmark detection

---

### 3. Face Landmark Detection (MediaPipe)

MediaPipe Face Mesh is used to detect facial landmarks.

The model identifies **468 facial landmarks** and allows the system to locate important regions such as:

- Eyes
- Mouth

These landmarks are used to extract features required for fatigue detection.

---

### 4. Feature Extraction

After detecting facial landmarks, the system extracts regions of interest including:

- Left eye region
- Right eye region
- Mouth region

These regions are used to compute fatigue indicators such as:

- Eye Aspect Ratio (EAR)
- Mouth Aspect Ratio (MAR)

---

### 5. Fatigue Detection

Driver fatigue is detected using the following indicators:

#### Eye Aspect Ratio (EAR)

EAR measures eye openness based on facial landmark distances.

If EAR remains below a threshold for several frames, the system detects possible drowsiness.

#### Mouth Aspect Ratio (MAR)

MAR measures mouth opening.

If MAR remains above a threshold for multiple frames, the system detects yawning behavior.

---

### 6. Additional Monitoring Modules

The system also monitors additional risk indicators.

#### GPS Monitoring

The system uses GPS data to determine:

- Vehicle speed
- Driver location

If speed exceeds a predefined limit, an overspeed alert is triggered.

#### Wearable Health Monitoring (Simulated)

A smartwatch or fitness band can provide:

- Heart rate
- SpO₂ (blood oxygen level)

In the prototype, these values are simulated to demonstrate system functionality.

Low SpO₂ values may indicate driver fatigue or health issues.

---

### 7. Fatigue Analysis Engine

All detected signals are combined to calculate a **danger score**.

Signals include:

- Eye closure detection
- Yawning detection
- Overspeed detection
- Low SpO₂ detection

Multiple simultaneous alerts increase the overall risk score.

---

### 8. Alert Decision System

Based on the danger score, the system determines the driver’s safety status.

Possible alert levels include:

| Alert Score | Status |
|-------------|--------|
| 0 | Normal |
| 1 | Warning |
| 2 | High Risk |
| 3+ | Emergency |

If multiple hazards persist for a predefined duration, an emergency alert is triggered.

---

### 9. Notification System

When hazardous conditions are detected, the system generates:

- Visual alerts on the dashboard
- Audio warning signals
- System notifications

These alerts help the driver respond quickly to unsafe conditions.

---

### 10. Driver Monitoring Dashboard

The dashboard is built using **Streamlit** and provides real-time monitoring features including:

- Live camera feed
- Driver alertness status
- Danger score
- GPS speed monitoring
- Health indicators
- Alert notifications
- Emergency event logs

The dashboard allows users to monitor driver safety in real time.

---

## Architecture Diagram

The overall system architecture is illustrated in the following diagram.

![System Architecture](../architecture.png)

---

## Summary

The proposed architecture integrates computer vision, physiological monitoring, and vehicle telemetry to create a comprehensive driver alertness monitoring system. By using widely available consumer devices such as smartphones and wearables, the system provides a scalable and cost-effective safety solution for transportation environments.