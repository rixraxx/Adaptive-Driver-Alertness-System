import streamlit as st
import cv2
import numpy as np
from scipy.spatial import distance as dist
import mediapipe as mp
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import threading
import time
import random
import math
from datetime import datetime
from plyer import notification
import pandas as pd

try:
    from streamlit_js_eval import get_geolocation
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False

st.set_page_config(page_title="Driver Safety System", page_icon="🚗", layout="wide")

st.markdown("""
<style>
.stApp { background: #0d0f14; color: #e0e6f0; }
.emergency-banner {
    background: linear-gradient(135deg,#ff0000,#cc0000); color:white;
    padding:18px 24px; border-radius:12px; text-align:center;
    font-size:1.4rem; font-weight:800; letter-spacing:0.05em;
    animation:pulse-red 0.8s infinite; box-shadow:0 0 30px rgba(255,0,0,0.7); margin-bottom:12px;
}
.emergency-banner-active {
    background:linear-gradient(135deg,#ff6600,#cc4400); color:white;
    padding:14px 20px; border-radius:10px; text-align:center;
    font-size:1.1rem; font-weight:700; animation:pulse-orange 1s infinite;
    box-shadow:0 0 20px rgba(255,102,0,0.6); margin-bottom:8px;
}
.alert-single {
    background:#2a1f00; border:1px solid #ffab00; color:#ffab00;
    padding:10px 16px; border-radius:8px; text-align:center;
    font-size:1rem; font-weight:700; margin-bottom:8px;
}
@keyframes pulse-red   { 0%,100%{box-shadow:0 0 30px rgba(255,0,0,0.7);} 50%{box-shadow:0 0 60px rgba(255,0,0,1);} }
@keyframes pulse-orange { 0%,100%{opacity:1;} 50%{opacity:0.75;} }
.watch-face {
    background:radial-gradient(ellipse at 30% 30%,#1e2535,#0d0f14);
    border:3px solid #2e3a55; border-radius:28px; padding:14px 10px;
    text-align:center; max-width:190px; margin:0 auto;
    box-shadow:0 6px 30px rgba(0,0,0,0.7);
}
.watch-strap-t,.watch-strap-b { background:#1a1f2e; height:22px; width:70%; margin:0 auto; }
.watch-strap-t { border-radius:4px 4px 0 0; }
.watch-strap-b { border-radius:0 0 4px 4px; }
.watch-time  { font-size:1.5rem; font-weight:700; font-family:'Courier New',monospace; color:#e0e6f0; }
.watch-date  { font-size:0.6rem; color:#6a7a99; margin-bottom:8px; letter-spacing:0.1em; text-transform:uppercase; }
.spo2-label  { font-size:0.58rem; color:#7a8aaa; letter-spacing:0.15em; text-transform:uppercase; margin-bottom:2px; }
.spo2-value-normal { font-size:1.9rem; font-weight:900; color:#00bcd4; text-shadow:0 0 12px rgba(0,188,212,0.6); }
.spo2-value-low    { font-size:1.9rem; font-weight:900; color:#ff5722; text-shadow:0 0 12px rgba(255,87,34,0.6); }
.spo2-pct    { font-size:0.8rem; color:#7a8aaa; }
.watch-status-ok   { font-size:0.62rem; color:#00e676; margin-top:4px; }
.watch-status-warn { font-size:0.62rem; color:#ff5722; margin-top:4px; animation:pulse-orange 1s infinite; }
.alert-score-container {
    background:linear-gradient(145deg,#1a1d26,#12151e); border:2px solid #2a3050;
    border-radius:16px; padding:14px; text-align:center; margin-top:10px;
}
.alert-score-title { font-size:0.72rem; color:#7a8aaa; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:6px; }
.alert-score-0 { font-size:1.9rem; font-weight:900; color:#00e676; }
.alert-score-1 { font-size:1.9rem; font-weight:900; color:#ffab00; }
.alert-score-2 { font-size:1.9rem; font-weight:900; color:#ff6d00; }
.alert-score-3 { font-size:1.9rem; font-weight:900; color:#ff1744; animation:pulse-red 0.8s infinite; }
.trigger-item-active   { background:#3a1414; border-left:4px solid #ff1744; padding:5px 10px; border-radius:6px; margin:3px 0; font-size:0.82rem; }
.trigger-item-inactive { background:#141a14; border-left:4px solid #00e676; padding:5px 10px; border-radius:6px; margin:3px 0; font-size:0.82rem; color:#4a6a4a; }
.hazard-timer { background:#1e1400; border:2px solid #ff6d00; padding:10px 14px; border-radius:10px; text-align:center; margin-bottom:8px; }
.hazard-timer-label { font-size:0.65rem; color:#ff6d00; letter-spacing:0.12em; text-transform:uppercase; }
.hazard-timer-val   { font-size:2rem; font-weight:900; color:#ff6d00; }
</style>
""", unsafe_allow_html=True)

def _beep_html(fn_body):
    uid = int(time.time() * 1000) % 999999
    return f"""<script id="beep{uid}">
(function(){{
  try{{
    var AC=window.AudioContext||window.webkitAudioContext;
    if(!AC)return;
    var ctx=new AC();
    function tone(freq,start,dur,vol){{
      var o=ctx.createOscillator(),g=ctx.createGain();
      o.connect(g);g.connect(ctx.destination);
      o.frequency.value=freq;
      g.gain.setValueAtTime(vol,ctx.currentTime+start);
      g.gain.exponentialRampToValueAtTime(0.001,ctx.currentTime+start+dur);
      o.start(ctx.currentTime+start);
      o.stop(ctx.currentTime+start+dur+0.05);
    }}
    {fn_body}
    setTimeout(function(){{try{{ctx.close();}}catch(e){{}}}},3000);
  }}catch(e){{}}
}})();
</script>"""

def trigger_sound(kind):
    if kind=="drowsy":
        body="tone(1000,0.00,0.15,0.5);tone(1000,0.22,0.15,0.5);tone(1000,0.44,0.15,0.5);"
    elif kind=="yawn":
        body="tone(700,0.00,0.20,0.45);tone(700,0.30,0.20,0.45);"
    elif kind=="emergency":
        body="".join(f"tone({'1200' if i%2==0 else '900'},{i*0.35:.2f},0.28,0.6);" for i in range(7))
    else:
        body="tone(880,0,0.2,0.4);"
    st.markdown(_beep_html(body), unsafe_allow_html=True)

RTC_CONFIGURATION = RTCConfiguration({"iceServers":[
    {"urls":["stun:stun.l.google.com:19302","stun:stun1.l.google.com:19302"]},
    {"urls":["turn:openrelay.metered.ca:80","turn:openrelay.metered.ca:443","turns:openrelay.metered.ca:443"],
     "username":"openrelayproject","credential":"openrelayproject"},
],"iceTransportPolicy":"all"})

def eye_aspect_ratio(eye_landmarks):
    A=dist.euclidean(eye_landmarks[1],eye_landmarks[5])
    B=dist.euclidean(eye_landmarks[2],eye_landmarks[4])
    C=dist.euclidean(eye_landmarks[0],eye_landmarks[3])
    return (A+B)/(2.0*C)

def get_eye_landmarks(landmarks,eye_indices,fw,fh):
    return np.array([[int(landmarks[i].x*fw),int(landmarks[i].y*fh)] for i in eye_indices])

def lip_distance(landmarks,fw,fh):
    top=landmarks[13];bottom=landmarks[14];left=landmarks[78];right=landmarks[308]
    v=abs((bottom.y-top.y)*fh);h=abs((right.x-left.x)*fw)
    return v/h if h>0 else 0

class SpO2Simulator:
    def __init__(self):
        self._spo2=98.0; self._hr=72
        self._lock=threading.Lock(); self._running=True
        self.drowsy_signal=False   # set BEFORE thread starts
        self._thread=threading.Thread(target=self._simulate,daemon=True)
        self._thread.start()

    def _simulate(self):
        while self._running:
            with self._lock:
                noise=random.gauss(0,0.15)
                trend,hr_target=(-0.06,88) if self.drowsy_signal else (0.04,72)
                self._spo2=max(88.0,min(100.0,self._spo2+trend+noise))
                self._hr=int(max(50,min(130,self._hr+(hr_target-self._hr)*0.05+random.gauss(0,1))))
            time.sleep(0.5)

    def set(self,spo2,hr):
        with self._lock:
            self._spo2=float(spo2); self._hr=int(hr)

    def get(self):
        with self._lock:
            return round(self._spo2,1),self._hr

    def stop(self):
        self._running=False

class VideoProcessor:
    def __init__(self):
        self.mp_face_mesh=mp.solutions.face_mesh
        self.face_mesh=self.mp_face_mesh.FaceMesh(max_num_faces=1,refine_landmarks=True,
            min_detection_confidence=0.5,min_tracking_confidence=0.5)
        self.LEFT_EYE=[33,160,158,133,153,144]
        self.RIGHT_EYE=[362,385,387,263,373,380]
        self.lock=threading.Lock()
        self.counter=0;self.yawn_counter=0
        self.ear_value=0.0;self.mar_value=0.0
        self.alert_status=[];self.face_detected=False
        self.last_drowsy_alert=0;self.last_yawn_alert=0

    def get_metrics(self):
        with self.lock:
            return {'ear':self.ear_value,'mar':self.mar_value,
                    'counter':self.counter,'yawn_counter':self.yawn_counter,
                    'alerts':self.alert_status.copy(),'face_detected':self.face_detected}

    def recv(self,frame,ear_thresh,ear_frames,yawn_thresh,yawn_frames):
        img=frame.to_ndarray(format="bgr24")
        fh,fw=img.shape[:2]
        results=self.face_mesh.process(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
        # Build alerts in a LOCAL list first — only write to self.alert_status
        # atomically at the end, so get_metrics() never reads a half-empty list.
        new_alerts=[]
        face_found=False
        if results.multi_face_landmarks:
            face_found=True
            for fl in results.multi_face_landmarks:
                lm=fl.landmark
                le=get_eye_landmarks(lm,self.LEFT_EYE,fw,fh)
                re=get_eye_landmarks(lm,self.RIGHT_EYE,fw,fh)
                ear=(eye_aspect_ratio(le)+eye_aspect_ratio(re))/2.0
                mar=lip_distance(lm,fw,fh)
                cv2.drawContours(img,[cv2.convexHull(le)],-1,(0,255,0),2)
                cv2.drawContours(img,[cv2.convexHull(re)],-1,(0,255,0),2)
                lp=np.array([[int(lm[i].x*fw),int(lm[i].y*fh)] for i in [61,146,91,181,84,17,314,405,321,375,291,61]])
                cv2.drawContours(img,[lp],-1,(0,255,0),2)
                now_t=time.time()
                # ── Eye / drowsiness ──────────────────────────────────────
                with self.lock:
                    self.ear_value=ear; self.mar_value=mar
                    if ear<ear_thresh:
                        self.counter+=1
                    else:
                        self.counter=0
                    counter_now=self.counter
                    if mar>yawn_thresh:
                        self.yawn_counter+=1
                    else:
                        self.yawn_counter=0
                    yawn_counter_now=self.yawn_counter
                if counter_now>=ear_frames:
                    new_alerts.append("DROWSY")
                    cv2.putText(img,"DROWSINESS ALERT!",(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,0,255),3)
                    cv2.rectangle(img,(5,5),(fw-5,fh-5),(0,0,255),3)
                    with self.lock:
                        if now_t-self.last_drowsy_alert>2.0:
                            try: notification.notify(title="⚠️ DROWSINESS!",message=f"EAR:{ear:.3f}",timeout=5)
                            except: pass
                            self.last_drowsy_alert=now_t
                if yawn_counter_now>=yawn_frames:
                    new_alerts.append("YAWN")
                    cv2.putText(img,"YAWN ALERT!",(10,70),cv2.FONT_HERSHEY_SIMPLEX,0.9,(255,165,0),3)
                    with self.lock:
                        if now_t-self.last_yawn_alert>2.0:
                            try: notification.notify(title="😮 YAWN!",message=f"MAR:{mar:.3f}",timeout=5)
                            except: pass
                            self.last_yawn_alert=now_t
                cv2.putText(img,f"EAR:{ear:.2f}",(10,fh-60),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)
                cv2.putText(img,f"MAR:{mar:.2f}",(10,fh-30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)
        # Commit atomically — get_metrics() always sees a consistent snapshot
        with self.lock:
            self.face_detected=face_found
            self.alert_status=new_alerts
        return av.VideoFrame.from_ndarray(img,format="bgr24")

def render_speedometer(speed_val,speed_limit,speed_unit,max_speed=220):
    if speed_val is None: speed_val=0
    frac=min(speed_val/max_speed,1.0)
    angle=-135+frac*270; rad=math.radians(angle)
    cx=cy=110; r=90
    nx=cx+r*0.82*math.cos(rad); ny=cy+r*0.82*math.sin(rad)
    if speed_val==0:                 nc=ac=dc="#4a5568"
    elif speed_val<speed_limit*0.8:  nc=ac=dc="#00e676"
    elif speed_val<speed_limit:      nc=ac=dc="#ffab00"
    else:                             nc=ac=dc="#ff1744"
    def ap(s,e,rd,col,w=10):
        sr=math.radians(s);er=math.radians(e)
        x1=cx+rd*math.cos(sr);y1=cy+rd*math.sin(sr)
        x2=cx+rd*math.cos(er);y2=cy+rd*math.sin(er)
        lg=1 if abs(e-s)>180 else 0
        return f'<path d="M{x1:.1f} {y1:.1f} A{rd} {rd} 0 {lg} 1 {x2:.1f} {y2:.1f}" stroke="{col}" stroke-width="{w}" fill="none" stroke-linecap="round"/>'
    bg=ap(-135,135,90,"#1e2535",12)
    fe=-135+frac*270
    fill=ap(-135,max(-134.9,fe),90,ac,12) if frac>0 else ""
    ticks=""
    for i in range(12):
        ta=math.radians(-135+i*(270/11));ro=82;ri=74 if i%2==0 else 78
        x1=cx+ro*math.cos(ta);y1=cy+ro*math.sin(ta)
        x2=cx+ri*math.cos(ta);y2=cy+ri*math.sin(ta)
        c="#4a5568" if i%2!=0 else "#6a7a99"
        ticks+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="2"/>'
    la=math.radians(-135+(speed_limit/max_speed)*270)
    lx=cx+90*math.cos(la);ly=cy+90*math.sin(la)
    return f"""<svg width="200" height="200" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
<defs>
  <radialGradient id="bg" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#1a1d26"/><stop offset="100%" stop-color="#0d0f14"/>
  </radialGradient>
  <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<circle cx="{cx}" cy="{cy}" r="108" fill="#12151e" stroke="#2a3050" stroke-width="2"/>
<circle cx="{cx}" cy="{cy}" r="100" fill="url(#bg)"/>
{bg}{fill}{ticks}
<circle cx="{lx:.1f}" cy="{ly:.1f}" r="5" fill="#ff1744" filter="url(#glow)"/>
<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{nc}" stroke-width="3" stroke-linecap="round" filter="url(#glow)"/>
<circle cx="{cx}" cy="{cy}" r="8" fill="{nc}" filter="url(#glow)"/>
<circle cx="{cx}" cy="{cy}" r="3" fill="#0d0f14"/>
<text x="{cx}" y="{cy+32}" text-anchor="middle" font-family="Courier New,monospace" font-size="32" font-weight="900" fill="{dc}" filter="url(#glow)">{int(round(speed_val))}</text>
<text x="{cx}" y="{cy+50}" text-anchor="middle" font-family="Arial" font-size="10" fill="#6a7a99" letter-spacing="2">{speed_unit.upper()}</text>
<text x="{cx}" y="{cy+68}" text-anchor="middle" font-family="Arial" font-size="9" fill="#4a5568">LIMIT {int(speed_limit)}</text>
</svg>"""

def render_watch(spo2,hr,is_low):
    now=datetime.now()
    beat_s=round(60.0/max(hr,30),2)
    hb_color="#ff1744" if is_low else "#ef5350"
    ecg_col="#ff5722" if is_low else "#00bcd4"
    spo2_cls="spo2-value-low" if is_low else "spo2-value-normal"
    status='<div class="watch-status-warn">⚠️ LOW SpO₂</div>' if is_low else '<div class="watch-status-ok">● Normal</div>'
    ecg_pts="0,22 10,22 14,18 18,22 22,22 26,22 28,4 30,38 32,22 36,22 40,16 44,22 54,22"
    tiles="".join(f'''<polyline fill="none" stroke="{ecg_col}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" points="{ecg_pts}" transform="translate({i*54},0)">
      <animateTransform attributeName="transform" type="translate" from="{i*54},0" to="{(i-1)*54},0" dur="{beat_s}s" repeatCount="indefinite"/>
    </polyline>''' for i in range(4))
    return f"""
<div class="watch-strap-t"></div>
<div class="watch-face">
  <div class="watch-time">{now.strftime("%H:%M")}</div>
  <div class="watch-date">{now.strftime("%a %d %b").upper()}</div>
  <div style="text-align:center;margin:4px 0 1px">
    <svg width="32" height="30" viewBox="0 0 36 34" xmlns="http://www.w3.org/2000/svg">
      <defs><filter id="hg"><feGaussianBlur stdDeviation="2" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
      <path d="M18 30 C18 30 4 20 4 11 C4 6 8 3 12 3 C14.5 3 16.5 4.5 18 6.5
               C19.5 4.5 21.5 3 24 3 C28 3 32 6 32 11 C32 20 18 30 18 30Z"
            fill="{hb_color}" filter="url(#hg)">
        <animateTransform attributeName="transform" type="scale"
          values="1;1.22;1;1.08;1" keyTimes="0;0.12;0.25;0.35;1"
          dur="{beat_s}s" repeatCount="indefinite" additive="sum" transformOrigin="18 17"/>
      </path>
      <ellipse cx="13" cy="10" rx="3" ry="2" fill="rgba(255,255,255,0.2)" transform="rotate(-30,13,10)"/>
    </svg>
  </div>
  <div style="font-size:1.2rem;font-weight:900;color:{hb_color};text-shadow:0 0 10px rgba(239,83,80,0.5);line-height:1">{hr}</div>
  <div style="font-size:0.58rem;color:#7a8aaa;letter-spacing:0.12em;margin-bottom:6px">BPM</div>
  <svg width="150" height="38" viewBox="0 0 160 42" style="display:block;margin:0 auto 6px;overflow:hidden">
    <rect width="160" height="42" rx="4" fill="#0d1018"/>
    <defs><clipPath id="ec"><rect x="0" y="0" width="160" height="42"/></clipPath>
      <filter id="eg"><feGaussianBlur stdDeviation="1.5" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
    <g clip-path="url(#ec)"><g filter="url(#eg)">{tiles}</g></g>
    <rect width="3" height="42" rx="1" fill="{ecg_col}" opacity="0.35">
      <animateTransform attributeName="transform" type="translate" from="-3,0" to="160,0" dur="{beat_s}s" repeatCount="indefinite"/>
    </rect>
  </svg>
  <div class="spo2-label">SpO₂ Blood Oxygen</div>
  <div class="{spo2_cls}">{spo2:.1f}<span class="spo2-pct"> %</span></div>
  {status}
</div>
<div class="watch-strap-b"></div>"""

ALERT_LABELS={"DROWSY":(1,"Eyes closing"),"YAWN":(1,"Repeated yawning"),
              "SPEED":(1,"Speed exceeded"),"LOW_SPO2":(1,"Low blood oxygen")}

def compute_score(alerts):
    return sum(ALERT_LABELS[a][0] for a in alerts if a in ALERT_LABELS)

def send_emergency_notification(alerts,loc_str,spo2,speed,unit):
    detail="\n".join(f"• {ALERT_LABELS[a][1]}" for a in alerts if a in ALERT_LABELS)
    try: notification.notify(title="🚨🚨 EMERGENCY — CALLING 112/911 🚨🚨",
        message=f"Time:{datetime.now().strftime('%H:%M:%S')}\n{detail}\nSpO2:{spo2:.1f}%  Speed:{speed:.1f}{unit}\n{loc_str}",
        timeout=10)
    except: pass

def main():
    st.title("🚗 Driver Safety System")
    st.markdown("### Real-time Drowsiness · Speed · Blood Oxygen Monitoring")
    st.markdown("---")

    defaults={
        'processor':VideoProcessor(),'spo2_sim':SpO2Simulator(),
        'last_speed_alert':0.0,'cached_location':None,
        'last_emergency_alert':0.0,'emergency_log':[],
        'hazard_start':None,
        'last_beep_drowsy':0.0,'last_beep_yawn':0.0,'last_beep_emergency':0.0,
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v

    processor=st.session_state.processor
    spo2_sim=st.session_state.spo2_sim

    if GPS_AVAILABLE:
        raw=get_geolocation()
        if raw and isinstance(raw,dict) and 'coords' in raw:
            st.session_state.cached_location=raw

    location=st.session_state.cached_location
    speed_kmh=latitude=longitude=None
    if location and 'coords' in location:
        c=location['coords']
        latitude=c.get('latitude');longitude=c.get('longitude')
        ms=c.get('speed')
        if ms is not None and ms>=0: speed_kmh=ms*3.6

    # ── SIDEBAR ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Detection Settings")
        ear_thresh =st.slider("EAR Threshold",  0.1,0.5,0.25,0.01)
        ear_frames =st.slider("Drowsiness frames",10,50,20,5)
        yawn_thresh=st.slider("Yawn MAR Threshold",0.3,1.0,0.6,0.05)
        yawn_frames=st.slider("Yawn frames",3,15,5,1)

        st.markdown("---")
        st.header("🛰️ GPS")
        speed_unit =st.radio("Speed Unit",["km/h","mph"],horizontal=True)
        speed_limit=st.slider(f"Speed Alert ({speed_unit})",20,
                              200 if speed_unit=="km/h" else 124,
                              80 if speed_unit=="km/h" else 50,5)

        st.markdown("---")
        st.header("🩺 Health")
        spo2_threshold=st.slider("Low SpO₂ Alert (%)",88,96,94,1)

        st.markdown("---")
        st.header("🚨 Emergency")
        hazard_hold_s=st.slider("Sustained hazard before emergency (s)",2,15,5,1,
            help="All 3+ alerts must stay active this long before emergency fires")
        st.info(f"Fires after **{hazard_hold_s}s** of 3+ simultaneous alerts")

        st.markdown("---")
        st.header("🧪 Manual Overrides")
        st.caption("Tweak values for testing without real sensors")

        override_speed=st.checkbox("Override speed")
        manual_speed=st.slider("Manual speed",0,200 if speed_unit=="km/h" else 124,0,1,
                               disabled=not override_speed)

        st.markdown("---")
        override_health=st.checkbox("Override SpO₂ / HR")
        manual_spo2=st.slider("Manual SpO₂ (%)",85.0,100.0,98.0,0.5,disabled=not override_health)
        manual_hr  =st.slider("Manual Heart Rate",40,150,72,1,   disabled=not override_health)

        st.markdown("---")
        override_alerts=st.checkbox("Force alert flags")
        force_drowsy =st.checkbox("Force DROWSY",  disabled=not override_alerts)
        force_yawn   =st.checkbox("Force YAWN",    disabled=not override_alerts)
        force_spo2low=st.checkbox("Force LOW_SPO2",disabled=not override_alerts)
        force_speed  =st.checkbox("Force SPEED",   disabled=not override_alerts)

        st.markdown("---")
        col_t1,col_t2=st.columns(2)
        with col_t1:
            if st.button("🔊 Test Beep"):  trigger_sound("emergency")
        with col_t2:
            if st.button("🚨 Force Emergency"):
                st.session_state.last_emergency_alert=0.0
                st.session_state.hazard_start=time.time()-hazard_hold_s-1

        st.markdown("---")
        st.success("✅ Optimised for mobile via ngrok")

    # ── Apply overrides ────────────────────────────────────────────────────────
    if override_health:
        spo2_sim.set(manual_spo2,manual_hr)

    if override_speed:
        display_speed=float(manual_speed)
    elif speed_kmh is not None:
        display_speed=speed_kmh if speed_unit=="km/h" else speed_kmh/1.60934
    else:
        display_speed=None

    metrics_now=processor.get_metrics()
    spo2_sim.drowsy_signal="DROWSY" in metrics_now['alerts']
    spo2_val,hr_val=spo2_sim.get()
    spo2_low=spo2_val<spo2_threshold

    # ── Active alerts ──────────────────────────────────────────────────────────
    active_alerts=[]
    if force_drowsy  or "DROWSY" in metrics_now['alerts']: active_alerts.append("DROWSY")
    if force_yawn    or "YAWN"   in metrics_now['alerts']: active_alerts.append("YAWN")
    if force_speed   or (display_speed is not None and display_speed>speed_limit): active_alerts.append("SPEED")
    if force_spo2low or spo2_low: active_alerts.append("LOW_SPO2")

    alert_score=compute_score(active_alerts)
    now_t=time.time()

    # ── Sustained hazard timer ─────────────────────────────────────────────────
    if alert_score>=3:
        if st.session_state.hazard_start is None:
            st.session_state.hazard_start=now_t
        hazard_elapsed=now_t-st.session_state.hazard_start
    else:
        st.session_state.hazard_start=None
        hazard_elapsed=0.0

    is_emergency=(alert_score>=3 and hazard_elapsed>=hazard_hold_s)

    # ── Speed notification ─────────────────────────────────────────────────────
    if "SPEED" in active_alerts and now_t-st.session_state.last_speed_alert>5.0:
        loc_str=f"\nLocation:{latitude:.5f},{longitude:.5f}" if latitude else ""
        try: notification.notify(title="🚨 SPEED!",
            message=f"Speed:{display_speed:.1f}{speed_unit} Limit:{speed_limit}{speed_unit}{loc_str}",
            timeout=5)
        except: pass
        st.session_state.last_speed_alert=now_t

    # ── Emergency notification ─────────────────────────────────────────────────
    if is_emergency and now_t-st.session_state.last_emergency_alert>15.0:
        loc_str=f"Location:{latitude:.5f},{longitude:.5f}" if latitude else "Location:Unknown"
        send_emergency_notification(active_alerts,loc_str,spo2_val,display_speed or 0,speed_unit)
        st.session_state.emergency_log.insert(0,{
            'time':datetime.now().strftime("%H:%M:%S"),
            'alerts':", ".join(active_alerts),
            'spo2':f"{spo2_val:.1f}%",
            'speed':f"{display_speed or 0:.1f} {speed_unit}",
            'held_s':f"{hazard_elapsed:.1f}s",
            'location':loc_str
        })
        st.session_state.emergency_log=st.session_state.emergency_log[:10]
        st.session_state.last_emergency_alert=now_t

    # ── Audio beeps ────────────────────────────────────────────────────────────
    if "DROWSY" in active_alerts and now_t-st.session_state.last_beep_drowsy>3.0:
        trigger_sound("drowsy"); st.session_state.last_beep_drowsy=now_t
    if "YAWN" in active_alerts and now_t-st.session_state.last_beep_yawn>4.0:
        trigger_sound("yawn"); st.session_state.last_beep_yawn=now_t
    if is_emergency and now_t-st.session_state.last_beep_emergency>5.0:
        trigger_sound("emergency"); st.session_state.last_beep_emergency=now_t

    # ── Banners ────────────────────────────────────────────────────────────────
    if is_emergency:
        st.markdown('<div class="emergency-banner">🚨 EMERGENCY — CALLING 112 / 911 🚨<br>'
            '<span style="font-size:0.85rem;font-weight:400">Multiple sustained danger signals · Emergency services notified</span></div>',
            unsafe_allow_html=True)
    elif alert_score>=3:
        remaining=max(0,hazard_hold_s-hazard_elapsed)
        st.markdown(f'<div class="hazard-timer"><div class="hazard-timer-label">⚠️ 3 HAZARDS ACTIVE — Emergency in</div>'
            f'<div class="hazard-timer-val">{remaining:.1f}s</div></div>',unsafe_allow_html=True)
    elif alert_score==2:
        st.markdown(f'<div class="emergency-banner-active">⚠️ WARNING — {alert_score} simultaneous alerts · 1 more triggers emergency</div>',
            unsafe_allow_html=True)
    # Prominent banners for individual alerts (if/if not elif — both can show)
    if "DROWSY" in active_alerts:
        st.markdown('''<div style="background:linear-gradient(135deg,#cc0000,#880000);
            color:white;padding:18px 24px;border-radius:12px;text-align:center;
            font-size:1.5rem;font-weight:900;letter-spacing:0.05em;
            animation:pulse-red 0.7s infinite;
            box-shadow:0 0 40px rgba(255,0,0,0.85);margin-bottom:8px;">
            &#128065;&#65039; DROWSINESS DETECTED &#8212; WAKE UP!<br>
            <span style="font-size:0.85rem;font-weight:500">Eyes closing detected &#8212; pull over safely</span>
            </div>''', unsafe_allow_html=True)
    if "YAWN" in active_alerts:
        st.markdown('''<div style="background:linear-gradient(135deg,#e65100,#bf360c);
            color:white;padding:14px 24px;border-radius:12px;text-align:center;
            font-size:1.25rem;font-weight:800;
            box-shadow:0 0 25px rgba(255,100,0,0.7);margin-bottom:8px;">
            &#128558; YAWNING DETECTED &#8212; Driver Fatigue Warning<br>
            <span style="font-size:0.8rem;font-weight:400">Consider taking a break soon</span>
            </div>''', unsafe_allow_html=True)

    # ── Main layout ────────────────────────────────────────────────────────────
    col_cam,col_right=st.columns([2,1])

    with col_cam:
        st.subheader("🎥 Live Camera Feed")

        def video_frame_callback(frame):
            return processor.recv(frame,ear_thresh,ear_frames,yawn_thresh,yawn_frames)

        ctx=webrtc_streamer(key="drowsiness-detection",mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIGURATION,
            video_frame_callback=video_frame_callback,
            media_stream_constraints={"video":True,"audio":False},
            async_processing=True)

        sc=min(alert_score,3)
        st.markdown(f"""<div class="alert-score-container">
  <div class="alert-score-title">⚡ Danger Score</div>
  <div class="alert-score-{sc}">{alert_score} / 4</div>
  <div style="font-size:0.7rem;color:#4a5568;margin-top:4px">
    {"🚨 EMERGENCY" if is_emergency else ("⏳ HOLD…" if alert_score>=3 else ("⚠️ HIGH RISK" if alert_score==2 else ("⚡ ELEVATED" if alert_score==1 else "✅ SAFE")))}
  </div></div>""",unsafe_allow_html=True)

        if alert_score>=3 and not is_emergency:
            pct=min(int(hazard_elapsed/hazard_hold_s*100),100)
            st.markdown(f"""<div style="margin-top:8px">
  <div style="font-size:0.65rem;color:#ff6d00;margin-bottom:3px">Emergency countdown: {hazard_elapsed:.1f}s / {hazard_hold_s}s</div>
  <div style="background:#1e1400;border-radius:6px;height:10px;overflow:hidden">
    <div style="background:linear-gradient(90deg,#ff6d00,#ff1744);height:100%;width:{pct}%;border-radius:6px"></div>
  </div></div>""",unsafe_allow_html=True)

    with col_right:
        sp_col,wt_col=st.columns(2)
        with sp_col:
            st.markdown("**🏎️ Speed**")
            svg=render_speedometer(display_speed or 0,speed_limit,speed_unit,
                                   200 if speed_unit=="km/h" else 124)
            st.markdown(f'<div style="text-align:center">{svg}</div>',unsafe_allow_html=True)
            if override_speed:    st.caption(f"🧪 Manual: {manual_speed} {speed_unit}")
            elif display_speed is None: st.caption("📡 Awaiting GPS…")
            elif display_speed>speed_limit: st.error(f"🚨 {display_speed:.1f} {speed_unit}")
            else: st.success(f"✅ {display_speed:.1f} {speed_unit}")

        with wt_col:
            st.markdown("**⌚ Smartwatch**")
            st.markdown(render_watch(spo2_val,hr_val,spo2_low),unsafe_allow_html=True)
            if override_health:   st.caption(f"🧪 {manual_spo2}% / {manual_hr}bpm")
            elif spo2_low:        st.error(f"💙 SpO₂ {spo2_val:.1f}%")

        st.markdown("---")
        st.subheader("🚨 Alert Triggers")
        for key,label in [("DROWSY","👁️ Eyes Closing"),("YAWN","😮 Yawning"),
                          ("SPEED","🏎️ Over Speed"),("LOW_SPO2","💙 Low SpO₂")]:
            cls="trigger-item-active" if key in active_alerts else "trigger-item-inactive"
            ico="🔴" if key in active_alerts else "🟢"
            st.markdown(f'<div class="{cls}">{ico} {label}</div>',unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📊 Metrics")
        metrics_ph=st.empty()
        alert_ph=st.empty()

        if latitude is not None and longitude is not None:
            st.markdown("---")
            maps_url=f"https://www.google.com/maps?q={latitude:.6f},{longitude:.6f}"
            st.caption(f"📍 [{latitude:.5f},{longitude:.5f}]({maps_url})")
            st.map(pd.DataFrame({'lat':[latitude],'lon':[longitude]}),zoom=15)

    if st.session_state.emergency_log:
        st.markdown("---")
        st.subheader("📋 Emergency Event Log")
        st.dataframe(pd.DataFrame(st.session_state.emergency_log),use_container_width=True)

    # ── Live metrics via st.fragment so ONLY this block reruns — camera is never disturbed ──
    @st.fragment(run_every=0.5)
    def live_metrics():
        m = processor.get_metrics()
        is_playing = ctx.state.playing
        if not is_playing:
            with metrics_ph.container():
                if override_alerts:
                    st.info("🧪 Manual override active — camera optional")
                else:
                    st.info("🎥 Click START to begin camera detection")
            return
        with metrics_ph.container():
            if m['face_detected']:
                c1,c2 = st.columns(2)
                with c1:
                    st.metric("EAR",f"{m['ear']:.3f}",
                        delta="⚠️ Alert" if m['ear']<ear_thresh else "Normal",
                        delta_color="normal" if m['ear']>=ear_thresh else "inverse")
                    st.metric("Drowsy frames",f"{m['counter']}/{ear_frames}")
                with c2:
                    st.metric("MAR",f"{m['mar']:.3f}",
                        delta="😮 Yawn!" if m['mar']>yawn_thresh else "Normal",
                        delta_color="normal" if m['mar']<=yawn_thresh else "inverse")
                    st.metric("Yawn frames",f"{m['yawn_counter']}/{yawn_frames}")
                st.progress(min(m['ear']/0.4,1.0),text="Eye Openness")
            else:
                st.info("👤 Waiting for face detection…")
        with alert_ph.container():
            if "DROWSY" in m['alerts']: st.error("⚠️ DROWSINESS DETECTED!")
            if "YAWN"   in m['alerts']: st.warning("😮 YAWN DETECTED!")
            if not m['alerts'] and m['face_detected']: st.success("✅ Driver is alert")

    live_metrics()

    if not ctx.state.playing and not override_alerts:
        st.markdown("---")
        st.markdown("### 📱 Using with ngrok")
        st.code("ngrok http 8501")

if __name__=="__main__":
    main()