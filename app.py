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
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title="ATS Proof of Concept", page_icon="🫀", layout="wide")

FACES_DIR = Path(__file__).resolve().parent / "assets" / "faces"

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

# Bounded action set, consistent with the guardrail-restricted action space
# described in the accompanying manuscript (Sections 2.6 and 3.5): the demo
# may only ever select among these six pre-approved actions.
ACTION_LEAD_INS = {
    "rest": "Recommend a rest day",
    "recover": "Extend recovery",
    "maintain": "Maintain current plan",
    "decrease": "Decrease intensity",
    "increase": "Increase intensity",
    "regulate": "Provide a regulation prompt",
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


def pick_face_photo() -> tuple:
    """Pick a random real stock portrait as an illustrative placeholder.

    These are real photographs (see assets/faces/ATTRIBUTION.md for source
    and license), but they are NOT real study participants and are NOT
    connected to any camera or facial-analysis model. One is simply chosen
    at random each time "Simulate Data" is clicked.
    """
    candidates = sorted(FACES_DIR.glob("*.jpg"))
    if not candidates:
        return None, "No placeholder photos found."
    chosen = random.choice(candidates)
    return Image.open(chosen), chosen.name


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


def generate_recommendation(hrv: dict, affect: dict, self_report: dict, readiness: float):
    """Rule-based recommendation engine (illustrative only).

    Mirrors, at a much simplified scale, the Phase A rule-based decision
    layer described in the manuscript (Section 3.5): a small, auditable,
    priority-ordered set of if-then rules that considers multiple simulated
    signals jointly, rather than readiness alone, and always resolves to one
    of six pre-approved actions (Sections 2.6, 3.5). No machine learning or
    LLM component is used here; a single deterministic function decides the
    action, and a short natural-language rationale is generated by citing
    the specific simulated inputs that drove that decision, so the logic
    remains fully inspectable.
    """
    factors = []

    if self_report["Soreness"] >= 8 and hrv["RMSSD (ms)"] < 30:
        key = "decrease"
        factors.append(f"high reported muscle soreness ({self_report['Soreness']}/10)")
        factors.append(f"reduced parasympathetic recovery (RMSSD = {hrv['RMSSD (ms)']} ms)")

    elif readiness < 35:
        key = "rest"
        factors.append(f"low composite readiness ({readiness}/100)")
        if self_report["Stress"] >= 7:
            factors.append(f"elevated self-reported stress ({self_report['Stress']}/10)")
        if hrv["RMSSD (ms)"] < 30:
            factors.append(f"low RMSSD ({hrv['RMSSD (ms)']} ms) relative to typical resting range")

    elif readiness < 50 or (self_report["Stress"] >= 7 and self_report["Sleep Quality"] <= 4):
        key = "recover"
        factors.append(f"readiness below target ({readiness}/100)")
        if self_report["Sleep Quality"] <= 4:
            factors.append(f"poor reported sleep quality ({self_report['Sleep Quality']}/10)")

    elif affect["gesture"] in ("Restless", "Fidgety", "Slouched") and affect["sentiment"] < 0:
        key = "regulate"
        factors.append(f"{affect['gesture'].lower()} body-language cue")
        factors.append(f"negative speech sentiment ({affect['sentiment']})")

    elif readiness >= 80 and affect["affect"] >= 7 and affect["control"] >= 6:
        key = "increase"
        factors.append(f"high composite readiness ({readiness}/100)")
        factors.append(f"positive affect and sense of control ({affect['affect']}/10, {affect['control']}/10)")

    elif readiness < 65:
        key = "decrease"
        factors.append(f"moderately reduced readiness ({readiness}/100)")

    else:
        key = "maintain"
        factors.append(f"readiness within the expected range ({readiness}/100)")

    # Illustrative confidence heuristic: more corroborating factors and a
    # readiness value further from ambiguous mid-range thresholds both raise
    # confidence. Not a calibrated probability, purely for demonstration.
    distance_from_midline = abs(readiness - 50) / 50
    confidence = round(min(97, max(55, 60 + 20 * distance_from_midline + 5 * len(factors))), 0)

    action = ACTION_LEAD_INS[key]
    factor_text = "; ".join(factors)
    rationale = (
        f"Based on {factor_text}, the system recommends this action for the upcoming session. "
        f"This recommendation reflects a fixed, auditable rule (not a machine learning or "
        f"LLM output) and remains within the bounded action set described in the manuscript."
    )
    return action, rationale, confidence, factors


def run_simulation():
    hrv = simulate_hrv()
    affect = simulate_affect()
    self_report = simulate_self_report()
    readiness = compute_readiness(hrv, affect, self_report)
    action, rationale, confidence, factors = generate_recommendation(hrv, affect, self_report, readiness)
    face_img, face_filename = pick_face_photo()

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hrv": hrv,
        "affect": affect,
        "self_report": self_report,
        "readiness": readiness,
        "action": action,
        "rationale": rationale,
        "confidence": confidence,
        "factors": factors,
        "face_img": face_img,
        "face_filename": face_filename,
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
        st.markdown("**Simulated Facial Capture (stock placeholder photo)**")
        st.image(
            latest["face_img"],
            caption="Real stock photo used as a placeholder \u2014 not an actual "
            "study participant, and not connected to any camera or model. "
            "See assets/faces/ATTRIBUTION.md.",
            width=200,
        )

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
    st.caption(f"Illustrative confidence score: {latest['confidence']:.0f}%")
    with st.expander("Contributing factors considered by the rule engine"):
        for f in latest["factors"]:
            st.markdown(f"- {f}")

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
