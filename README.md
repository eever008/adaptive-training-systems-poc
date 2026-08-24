# Adaptive Training Systems (ATS) — Proof of Concept

A minimal, public **proof-of-concept demo** accompanying a book chapter on
adaptive training and psychophysiological profiling.

## What this is

A single-page app with one button, **Simulate Data**, that generates a
randomly simulated pre-session profile (heart rate variability, multimodal
affective signals, a self-report survey, and a facial-capture placeholder
photo) and displays an illustrative, rule-based training recommendation
derived jointly from those simulated signals.

The facial-capture placeholder uses real stock portrait photos (see
[`assets/faces/ATTRIBUTION.md`](assets/faces/ATTRIBUTION.md) for source and
license) rather than an actual camera capture. A different photo is chosen
at random on each simulation.

The recommendation engine is a small, transparent, priority-ordered set of
if-then rules (see `generate_recommendation()` in `app.py`) that jointly
considers readiness, HRV recovery markers, self-reported stress/soreness/
sleep, and affective/behavioral cues (gesture, speech sentiment) before
selecting one of six pre-approved actions, along with an illustrative
confidence score and a plain-language list of the specific factors that
drove the decision.

## What this is not

- No cameras, microphones, or wearable devices are connected.
- No real AI/ML or LLM models are called anywhere in this repository; the
  recommendation logic is a simple, fully transparent rule engine for
  illustration only.
- No participant data of any kind is collected, stored, or transmitted.
- The facial-capture photos are stock placeholder images, not photos of
  real study participants, and are not analyzed by any model.
- This repository does not include the data pipelines, model training
  code, or infrastructure of the full research platform.

Every value shown is generated with a random-number generator, within
plausible physiological ranges, purely to illustrate the *type* of output
the full system produces.

## Preview

![Simulated results screenshot](screenshots/02_simulated_results.png)

## Running the demo

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints in your terminal, and click
**Simulate Data**.

## License

MIT — see [LICENSE](LICENSE).
