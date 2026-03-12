# Setup Instructions

This document explains how to install and run the **AI-Based Driver Alertness Monitoring System**.

The system is implemented using Python and Streamlit and can run on a local computer with a webcam.

---

# 1. System Requirements

Minimum requirements:

- Python 3.9 or higher
- Webcam or smartphone camera
- Internet connection (optional for GPS features)
- Modern web browser (Chrome recommended)

Recommended:

- Python 3.10+
- 8 GB RAM
- GPU optional (not required)

---

# 2. Clone the Repository

Clone the project repository from GitHub.

```bash
git clone https://github.com/YOUR_USERNAME/Adaptive_DriverAlterness.git
cd Adaptive_DriverAlterness
3. Create Virtual Environment (Recommended)

Create a Python virtual environment.

Windows:

python -m venv .venv

Activate the environment:

.venv\Scripts\activate

Mac / Linux:

python3 -m venv .venv
source .venv/bin/activate
4. Install Dependencies

Install all required libraries using the requirements file.

pip install -r requirements.txt

This installs:

Streamlit

OpenCV

MediaPipe

Streamlit WebRTC

NumPy

Pandas

Plyer

SciPy

Other dependencies

5. Run the Application

Start the Streamlit application.

streamlit run src/app.py

After running this command, Streamlit will start a local server.

You will see something like:

Local URL: http://localhost:8501

Open this URL in your browser.

6. Starting Camera Monitoring

Open the dashboard in your browser.

Click the START button in the camera section.

Allow camera permissions when prompted.

The system will begin analyzing the video feed for:

Eye closure

Yawning

Driver fatigue

7. GPS Location and Speed Monitoring

The system can access browser geolocation data.

Steps:

Allow location access in the browser.

The dashboard will display:

Current GPS location

Vehicle speed

Overspeed alerts

Note:

GPS speed may not work on desktop systems without movement. For demonstration purposes, manual overrides are available in the sidebar.

8. Simulated Smartwatch Health Monitoring

The system includes a simulated wearable health monitor.

The dashboard displays:

Heart Rate

Blood Oxygen Level (SpO₂)

These values are simulated to demonstrate integration with wearable devices.

9. Manual Testing Controls

The dashboard includes testing controls in the sidebar.

These allow you to simulate different scenarios such as:

Driver drowsiness

Yawning detection

Overspeed condition

Low SpO₂ levels

These controls are useful for demonstration purposes.

10. Running the System on a Mobile Device (Optional)

To access the dashboard from a smartphone, you can use ngrok.

Install ngrok and run:

ngrok http 8501

This will generate a public URL such as:

https://xxxx.ngrok-free.app

Open this link on your smartphone to access the dashboard.

11. Troubleshooting

Camera not detected:

Check camera permissions in your browser

Try using Google Chrome

Ensure no other application is using the camera

Dependencies installation issues:

Update pip and retry installation.

pip install --upgrade pip
pip install -r requirements.txt
12. Stopping the Application

Press:

CTRL + C

in the terminal to stop the Streamlit server.

13. Project Documentation

Additional documentation is available in the docs folder.

docs/system_architecture.md
docs/methodology.md

These documents explain the system design and implementation in detail.


---
