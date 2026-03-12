# AI-Based Driver Alertness Monitoring System

A real-time driver safety monitoring system that detects driver fatigue and unsafe driving conditions using computer vision and behavioral analysis.

The system uses a smartphone camera to monitor driver facial features and detect signs of drowsiness such as eye closure and yawning. It also integrates additional indicators such as vehicle speed and simulated wearable health data (SpO₂ and heart rate) to evaluate driver alertness.

This project demonstrates how low-cost consumer devices such as smartphones and wearable devices can be used to build an intelligent driver monitoring system without requiring expensive automotive hardware.

---

# Project Overview

Driver fatigue is one of the leading causes of road accidents worldwide, particularly in long-distance transportation and logistics industries.

Many commercial driver monitoring systems require specialized cameras and embedded hardware, which can be expensive and difficult to deploy for small-scale transport companies.

This project proposes a **low-cost AI-based driver alertness monitoring system** that works using:

- Smartphone camera
- Computer vision algorithms
- Behavioral fatigue indicators
- Optional wearable health data
- Real-time monitoring dashboard

The goal is to provide an **accessible and scalable driver safety solution**.

---

# Key Features

- Real-time driver monitoring using a smartphone camera
- Eye closure detection using Eye Aspect Ratio (EAR)
- Yawning detection using Mouth Aspect Ratio (MAR)
- Speed monitoring using GPS data
- Simulated smartwatch health monitoring (SpO₂ and heart rate)
- Multi-factor fatigue risk scoring system
- Real-time alerts and notifications
- Emergency hazard detection
- Interactive Streamlit dashboard
- Event logging for safety monitoring

---

# System Architecture

The system processes live video from a camera and analyzes driver facial landmarks to detect fatigue indicators.

Additional safety signals such as speed and health indicators are combined with vision-based detection to determine driver risk levels.

Architecture documentation is available here:

docs/system_architecture.md

Architecture diagram:

![Architecture](architecture.png)

---

# Methodology

The system follows a multi-stage pipeline:

1. Video capture from smartphone camera
2. Face landmark detection using MediaPipe
3. Eye Aspect Ratio (EAR) calculation for eye closure detection
4. Mouth Aspect Ratio (MAR) calculation for yawning detection
5. Multi-factor fatigue risk scoring
6. Alert generation and dashboard monitoring

Full methodology documentation:

docs/methodology.md

---

# Technology Stack

Programming Language  
Python

Computer Vision  
OpenCV  
MediaPipe Face Mesh

Machine Learning  
TensorFlow / Keras (used during model experimentation)

Web Application  
Streamlit  
Streamlit WebRTC

Notifications  
Plyer

Data Handling  
NumPy  
Pandas

Other Tools  
Ngrok (remote access for mobile devices)

---

# Project Structure
Adaptive_DriverAlterness

docs/
system_architecture.md
methodology.md
screenshots/

src/
app.py
model_test_training/
test/

architecture.png
README.md
requirements.txt
setup_instructions.md
demo_video_link.txt


---

# How to Run the Project

See detailed instructions:

setup_instructions.md

Quick start:

```
pip install -r requirements.txt

streamlit run src/app.py
```


Then open the Streamlit dashboard in your browser.

---

# Dashboard Features

The monitoring dashboard provides:

- Live driver camera feed
- Eye and yawning detection
- Driver alertness status
- Danger score
- Speed monitoring
- Health indicators
- Alert notifications
- Emergency event logs

---

# Screenshots

Screenshots of the system interface are available in:

docs/screenshots/

Examples include:

- Live driver monitoring
- Fatigue detection alerts
- Speed monitoring dashboard
- Health monitoring display

---

# Demo Video

Demo video link:

See file: demo_video_link.txt

---

# Project Outcomes

- Real-time driver fatigue detection system
- Integration of computer vision and behavioral monitoring
- Low-cost driver monitoring architecture
- Interactive safety dashboard

---

# Future Improvements

- Integration with real smartwatch APIs
- Mobile application interface
- Improved fatigue detection models
- Vehicle control integration for automatic safety response

---

# Authors

Alliance University
Raj Kumar Sharma  
M. Deekshitha Chowdary
Kaushik Choudhary

---

# Academic Project

This project was developed as part of the **Design Project – Alliance School of Advanced Computing, Alliance University**.