"""Generate a simple box-and-arrow diagram of the POC's internal pipeline.

This is a documentation asset only (used for the manuscript figure), not
part of the running app. Uses PIL only, no extra dependencies.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_PATH = Path(__file__).resolve().parent.parent / "screenshots" / "04_architecture_diagram.png"

W, H = 1500, 700
BG = (255, 255, 255)
BOX_FILL = (235, 244, 250)
BOX_EDGE = (40, 80, 120)
ARROW_COLOR = (60, 60, 60)
TEXT_COLOR = (20, 20, 20)
TITLE_COLOR = (10, 10, 10)


def get_font(size, bold=False):
    candidates = (
        ["/System/Library/Fonts/Supplemental/Arial Bold.ttf"]
        if bold
        else ["/System/Library/Fonts/Supplemental/Arial.ttf"]
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_box(draw, xy, text, font, fill=BOX_FILL, edge=BOX_EDGE, text_color=TEXT_COLOR):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=14, fill=fill, outline=edge, width=2)
    lines = text.split("\n")
    line_height = font.size + 4
    total_h = line_height * len(lines)
    ty = (y0 + y1) / 2 - total_h / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        tx = (x0 + x1) / 2 - tw / 2
        draw.text((tx, ty), line, font=font, fill=text_color)
        ty += line_height


def h_arrow(draw, x0, x1, y, color=ARROW_COLOR, width=3):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)
    draw.polygon([(x1, y - 6), (x1, y + 6), (x1 + 10, y)], fill=color)


def v_arrow(draw, x, y0, y1, color=ARROW_COLOR, width=3):
    draw.line([(x, y0), (x, y1)], fill=color, width=width)
    draw.polygon([(x - 6, y1), (x + 6, y1), (x, y1 + 10)], fill=color)


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    title_font = get_font(24, bold=True)
    box_font = get_font(15)
    small_font = get_font(13)

    draw.text((30, 20), "Proof-of-Concept Demo — Internal Pipeline (simulated data only)", font=title_font, fill=TITLE_COLOR)

    # Stage 1: trigger
    b1 = (40, 140, 220, 260)
    draw_box(draw, b1, "User clicks\n\u201cSimulate Data\u201d", box_font)

    # Stage 2: four parallel simulated generators
    gen_y0, gen_y1 = 90, 310
    gens = [
        ("Simulated HRV\n(HR, RMSSD, SDNN,\nHF, LF/HF, quality)", 280, 460),
        ("Simulated Multimodal\nAffect (valence, arousal,\ngesture, sentiment)", 480, 660),
        ("Simulated Self-Report\n(energy, motivation,\nstress, sleep, etc.)", 680, 860),
        ("Stock Placeholder Photo\n(real photo, random pick,\nnot a live capture)", 880, 1080),
    ]
    for text, x0, x1 in gens:
        draw_box(draw, (x0, gen_y0, x1, gen_y1), text, small_font)

    # Route the connector from stage 1 to the four generator boxes via a bus
    # line ABOVE the boxes (bus_y < gen_y0), so it never crosses box interiors.
    riser_x = 250
    bus_y = 65
    b1_cx_y = (b1[1] + b1[3]) // 2  # 200
    draw.line([(b1[2], b1_cx_y), (riser_x, b1_cx_y)], fill=ARROW_COLOR, width=2)
    draw.line([(riser_x, b1_cx_y), (riser_x, bus_y)], fill=ARROW_COLOR, width=2)
    last_cx = max((x0 + x1) // 2 for _, x0, x1 in gens)
    draw.line([(riser_x, bus_y), (last_cx, bus_y)], fill=ARROW_COLOR, width=2)
    for text, x0, x1 in gens:
        cx = (x0 + x1) // 2
        v_arrow(draw, cx, bus_y, gen_y0)

    # Stage 3: composite readiness score. Only HRV, affect, and self-report
    # feed the readiness score (the photo is illustrative only and is not
    # used in any computation); converge those three via a bus placed just
    # below the generator boxes so lines never cross box interiors.
    b3 = (480, 380, 860, 460)
    b3_cx = (b3[0] + b3[2]) // 2
    converge_y = 345
    scoring_cxs = [(x0 + x1) // 2 for _, x0, x1 in gens[:3]]
    for cx in scoring_cxs:
        draw.line([(cx, gen_y1), (cx, converge_y)], fill=ARROW_COLOR, width=2)
    draw.line([(min(scoring_cxs), converge_y), (max(scoring_cxs), converge_y)], fill=ARROW_COLOR, width=2)
    v_arrow(draw, b3_cx, converge_y, b3[1])
    draw_box(draw, b3, "Composite Readiness Score\n(weighted combination, 0\u2013100)", box_font)

    # Stage 4: rule-based recommendation engine
    b4 = (480, 500, 860, 600)
    v_arrow(draw, (b3[0] + b3[2]) // 2, b3[3], b4[1])
    draw_box(draw, b4, "Rule-Based Recommendation Engine\n(priority-ordered if\u2013then rules;\nbounded action set)", box_font)

    # Stage 5: display output
    b5 = (1080, 380, 1460, 600)
    h_arrow(draw, b4[2], 1070, (b4[1] + b4[3]) // 2)
    draw_box(
        draw,
        b5,
        "Display Output:\nProfile + Readiness Score +\nRecommendation + Confidence +\nContributing Factors",
        box_font,
    )

    # Stock photo bypasses scoring/recommendation entirely and routes
    # straight to the display stage, since it is illustrative only.
    photo_cx = (gens[3][1] + gens[3][2]) // 2
    b5_cy = (b5[1] + b5[3]) // 2
    draw.line([(photo_cx, gen_y1), (photo_cx, b5_cy)], fill=ARROW_COLOR, width=2)
    h_arrow(draw, photo_cx, b5[0] - 10, b5_cy)

    # Note box
    note_font = get_font(13)
    draw.rectangle((40, 630, 1460, 680), outline=(180, 60, 60), width=2)
    draw.text(
        (55, 640),
        "No camera, microphone, wearable device, or trained ML/LLM model is used anywhere in this pipeline; all inputs are pseudo-randomly generated.",
        font=note_font,
        fill=(150, 30, 30),
    )

    OUT_PATH.parent.mkdir(exist_ok=True)
    img.save(OUT_PATH)
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
