"""
Adaptive Training Systems (ATS) - Public Proof-of-Concept Demo
=================================================================

This is a SIMULATION-ONLY front-end demo. No real sensors, cameras,
microphones, or AI/ML models are used anywhere in this app. Every value
shown is randomly generated within physiologically plausible ranges for
illustrative purposes only.

This demo exists solely to give reviewers and the public a concrete,
interactive sense of the *type* of outputs the full research platform
produces (described in the accompanying book chapter). It intentionally
does not include the underlying data pipelines, model code, or
infrastructure of the full system.

Run locally with:
    pip install -r requirements.txt
    streamlit run app.py
"""

import random
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw

st.set_page_config(page_title="ATS Proof of Concept", page_icon="🫀", layout="wide")

EMOTION_LABELS = ["Calm", "Joy", "Stress", "Fatigue", "Frustration", "Neutral"]
GESTURE_LABELS = ["Engaged", "Restless", "Still", "Slouched", "Fidgety"]
TRANSCRIPT_SNIPPETS = [
    "I'm feeling pretty good today, ready to train.",
    "A bit tired from yesterday, but okay overall.",
    "Honestly kind of stressed about work right now.",
    "Feeling calm and focused before this session.",
    "My legs are a little sore, but I'm motivated.",
    "Not sure I have much energy today.",
]
RECOMMENDATION_ACTIONS = {
    "rest": ("Recommend a rest day", "Readiness is low and recovery markers suggest the body needs a break."),
    "recover": ("Extend recovery", "Readiness is below target; adding recovery time should help restore balance."),
    "maintain": ("Maintain current plan", "Readiness is within the expected range for the planned session."),
    "decrease": ("Decrease intensity", "Some indicators suggest reducing load slightly today."),
    "increase": ("Increase intensity", "Readiness and recovery markers are strong; the body can handle more today."),
    "regulate": ("Provide a regulation prompt", "Affective signals suggest a brief mindset or breathing cue before training."),
}


def simulate_hrv():
    hr = round(np.random.normal(68, 8), 1)
    rmssd = round(np.random.normal(45, 15), 1)
    sdnn = round(np.random.normal(55, 12), 1)
    hf_power = round(np.random.normal(600, 200), 1)
    lf_hf_ratio = round(np.random.normal(1.5, 0.5), 2)
    signal_quality = round(np.random.uniform(85, 100), 1)
    return {
        "Heart Rate (bpm)": hr,
        "RMSSD (ms)": max(rmssd, 5),
        "SDNN (ms)": max(sdnn, 5),
        "HF Power (ms^2)": max(hf_power, 50),
        "LF/HF Ratio": max(lf_hf_ratio, 0.1),
        "Signal Quality (%)": signal_quality,
    }


def simulate_affect():
    affect = round(np.random.uniform(1, 10), 1)
    energy = round(np.random.uniform(1, 10), 1)
    control = round(np.random.uniform(1, 10), 1)
    raw = np.random.dirichlet(np.ones(len(EMOTION_LABELS)) * 2)
    distribution = {label: round(float(p) * 100, 1) for label, p in zip(EMOTION_LABELS, raw)}
    gesture = random.choice(GESTURE_LABELS)
    sentiment = round(np.random.uniform(-1, 1), 2)
    transcript = random.choice(TRANSCRIPT_SNIPPETS)
    return {
        "affect": affect,
        "energy": energy,
        "control": control,
        "distribution": distribution,
        "gesture": gesture,
        "sentiment": sentiment,
        "transcript": transcript,
    }


def simulate_self_report():
    fields = ["Energy", "Motivation", "Stress", "Mood", "Soreness", "Sleep Quality", "Hydration"]
    return {f: round(np.random.uniform(1, 10), 1) for f in fields}


def simulate_facial_snapshot(affect_score: float) -> Image.Image:
    """Draw a simple synthetic face placeholder. NOT a real photo or camera capture."""
    size = 200
    img = Image.new("RGB", (size, size), (245, 247, 250))
    draw = ImageDraw.Draw(img)

    face_color = (255, 224, 189)
    draw.ellipse([20, 20, size - 20, size - 20], fill=face_color, outline=(120, 90, 60), width=2)

    eye_y = size * 0.4
    draw.ellipse([60, eye_y - 8, 76, eye_y + 8], fill=(60, 40, 30))
    draw.ellipse([size - 76, eye_y - 8, size - 60, eye_y + 8], fill=(60, 40, 30))

    mouth_y = size * 0.65
    curve = int((affect_score - 5.5) * 6)
    bbox = [size * 0.3, mouth_y - 20 - curve, size * 0.7, mouth_y + 20 - curve]
    if affect_score >= 5.5:
        draw.arc(bbox, start=0, end=180, fill=(150, 50, 50), width=4)
    else:
        draw.arc(bbox, start=180, end=360, fill=(150, 50, 50), width=4)

    return img


def compute_readiness(hrv, affect, self_report):
    hrv_component = np.clip((hrv["RMSSD (ms)"] / 80) * 100, 0, 100)
    affect_component = np.clip((affect["affect"] + affect["control"]) / 20 * 100, 0, 100)
    self_report_component = np.clip(
        np.mean([self_report["Energy"], self_report["Motivation"], 10 - self_report["Stress"],
                 self_report["Mood"], 10 - self_report["Soreness"], self_report["Sleep Quality"]]) / 10 * 100,
        0, 100,
    )
    readiness = round(0.4 * hrv_component + 0.3 * affect_component + 0.3 * self_report_component, 1)
    return readiness


def generate_recommendation(readiness: float, affect: dict):
    if readiness < 35:
        key = "rest"
    elif readiness < 50:
        key = "recover"
    elif readiness < 65:
        key = "maintain" if affect["affect"] >= 4 else "regulate"
    elif readiness < 80:
        key = "maintain"
    else:
        key = "increase"
    action, rationale = RECOMMENDATION_ACTIONS[key]
    return action, rationale


def run_simulation():
    hrv = simulate_hrv()
    affect = simulate_affect()
    self_report = simulate_self_report()
    readiness = compute_readiness(hrv, affect, self_report)
    action, rationale = generate_recommendation(readiness, affect)
    face_img = simulate_facial_snapshot(affect["affect"])

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hrv": hrv,
        "affect": affect,
        "self_report": self_report,
        "readiness": readiness,
        "action": action,
        "rationale": rationale,
        "face_img": face_img,
    }


if "history" not in st.session_state:
    st.session_state.history = []

st.title("🫀 Adaptive Training Systems — Proof of Concept")
st.warning(
    "**All data on this page is synthetically simulated.** No cameras, microphones, "
    "wearables, or AI models are connected in this demo. This app illustrates the "
    "*type* of profile and recommendation the full research platform generates, "
    "described in the accompanying book chapter. Underlying model, pipeline, and "
    "infrastructure code are intentionally not included in this public repository."
)

col_btn, _ = st.columns([1, 4])
with col_btn:
    simulate_clicked = st.button("🎲 Simulate Data", type="primary", use_container_width=True)

if simulate_clicked:
    st.session_state.history.append(run_simulation())

if not st.session_state.history:
    st.info("Click **Simulate Data** above to generate a simulated pre-session profile.")
else:
    latest = st.session_state.history[-1]
    st.caption(f"Simulated session generated at {latest['timestamp']}")

    st.subheader("Simulated Psychophysiological Status Profile")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Cardiovascular (simulated HRV)**")
        for k, v in latest["hrv"].items():
            st.metric(k, v)

    with c2:
        st.markdown("**Multimodal Affective Signals (simulated)**")
        st.metric("Affect (valence)", latest["affect"]["affect"])
        st.metric("Energy (arousal)", latest["affect"]["energy"])
        st.metric("Control", latest["affect"]["control"])
        st.metric("Gesture", latest["affect"]["gesture"])
        st.metric("Speech Sentiment", latest["affect"]["sentiment"])
        st.caption(f"Simulated transcript snippet: \u201c{latest['affect']['transcript']}\u201d")

    with c3:
        st.markdown("**Simulated Facial Capture (synthetic placeholder)**")
        st.image(latest["face_img"], caption="Not a real photo \u2014 synthetically drawn", width=200)

    st.markdown("**Simulated Emotion Label Distribution**")
    dist_df = pd.DataFrame.from_dict(latest["affect"]["distribution"], orient="index", columns=["% of frames"])
    st.bar_chart(dist_df)

    st.markdown("**Simulated Self-Report Profile**")
    sr_df = pd.DataFrame.from_dict(latest["self_report"], orient="index", columns=["Rating (1-10)"])
    st.bar_chart(sr_df)

    st.subheader("Composite Readiness Score")
    st.progress(int(latest["readiness"]))
    st.metric("Readiness (0-100)", latest["readiness"])

    st.subheader("Simulated Recommendation (rule-based, illustrative only)")
    st.success(f"**{latest['action']}**\n\n{latest['rationale']}")

    if len(st.session_state.history) > 1:
        st.subheader("Simulated Session History (this browser session only)")
        hist_df = pd.DataFrame(
            {
                "Session": list(range(1, len(st.session_state.history) + 1)),
                "Readiness": [h["readiness"] for h in st.session_state.history],
            }
        ).set_index("Session")
        st.line_chart(hist_df)

st.divider()
st.caption(
    "Adaptive Training Systems (ATS) \u2014 Proof-of-Concept Demo. "
    "Companion repository to a manuscript chapter on adaptive training and "
    "psychophysiological profiling. Simulated data only; no real participant "
    "data, sensors, or production models are used in this repository."
)
