from PIL import Image, ImageDraw, ImageFont
import os


def load_font(size):
    # Try common CJK fonts on Windows
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/msgothic.ttc",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


FONT_TITLE = load_font(22)
FONT_FOOTER = load_font(18)
FONT_LABEL = load_font(18)

HEADER_H = 48
FOOTER_H = 60
HEADER_BG = (37, 99, 235)  # blue-600
HEADER_FG = (255, 255, 255)
FOOTER_BG = (248, 250, 252)  # slate-50
FOOTER_FG = (15, 23, 42)  # slate-900
FOOTER_BORDER = (226, 232, 240)  # slate-200

PALETTE = {
    "red": (239, 68, 68),
    "orange": (249, 115, 22),
    "amber": (245, 158, 11),
    "green": (34, 197, 94),
    "teal": (20, 184, 166),
    "blue": (59, 130, 246),
    "purple": (168, 85, 247),
}


def add_header(draw, w, title):
    draw.rectangle([0, 0, w - 1, HEADER_H - 1], fill=HEADER_BG)
    bbox = draw.textbbox((0, 0), title, font=FONT_TITLE)
    th = bbox[3] - bbox[1]
    draw.text((12, (HEADER_H - th) // 2), title, fill=HEADER_FG, font=FONT_TITLE)


def add_footer(draw, y0, w, lines):
    draw.rectangle([0, y0, w - 1, y0 + FOOTER_H - 1], fill=FOOTER_BG, outline=FOOTER_BORDER)
    y = y0 + 8
    for line in lines:
        draw.text((12, y), line, fill=FOOTER_FG, font=FONT_FOOTER)
        y += 22


def draw_arrow(draw, x1, y1, x2, y2, color, width=2):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    # arrow head at (x2, y2) pointing left
    draw.polygon([(x2, y2), (x2 - 8, y2 - 5), (x2 - 8, y2 + 5)], fill=color)


def draw_label_with_arrow(draw, img_w, y_target, text, color_name, x_dot=None):
    color = PALETTE.get(color_name, PALETTE["blue"])
    # label on the right
    bbox = draw.textbbox((0, 0), text, font=FONT_LABEL)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = 8
    label_h = th + 2 * pad
    label_w = tw + 2 * pad
    x_label = img_w - label_w - 16
    y_label = max(HEADER_H + 8, min(y_target - label_h // 2, HEADER_H + 500))
    # keep label within reasonable vertical bounds
    # draw rounded-ish rect
    draw.rounded_rectangle(
        [x_label, y_label, x_label + label_w, y_label + label_h],
        radius=6,
        fill=color,
    )
    draw.text((x_label + pad, y_label + pad - 2), text, fill=(255, 255, 255), font=FONT_LABEL)
    # arrow from label to target
    x_arrow_end = x_label - 10
    y_arrow_end = y_target
    x_arrow_start = x_label
    y_arrow_start = y_label + label_h // 2
    draw_arrow(draw, x_arrow_start, y_arrow_start, x_arrow_end, y_arrow_end, color, width=2)
    # dot at target
    if x_dot is None:
        x_dot = x_arrow_end - 40
    r = 5
    draw.ellipse([x_dot - r, y_target - r, x_dot + r, y_target + r], fill=(255, 255, 255), outline=color, width=2)


def process(src, dst, title, footer_lines, labels):
    """
    labels: list of dicts with keys:
        y: target y (relative to original image, before header)
        text: label text
        color: color name
        x_dot: optional x of the dot
    """
    img = Image.open(src).convert("RGB")
    w, h = img.size
    new_h = h + HEADER_H + FOOTER_H
    canvas = Image.new("RGB", (w, new_h), (255, 255, 255))
    canvas.paste(img, (0, HEADER_H))
    draw = ImageDraw.Draw(canvas)
    add_header(draw, w, title)
    add_footer(draw, HEADER_H + h, w, footer_lines)
    for lab in labels:
        y = HEADER_H + lab["y"]
        draw_label_with_arrow(draw, w, y, lab["text"], lab["color"], lab.get("x_dot"))
    canvas.save(dst, "PNG")
    print(f"Saved {dst}")


if __name__ == "__main__":
    OUT = r"E:\project\team-share-public\worklog-2026-07-15"

    # WAKE_CS_SEL1 第二张：POFF_DRA_CH 细节
    process(
        src=r"C:\Users\xiapeng2\AppData\Local\Temp\screenshot-20260715-111039.png",
        dst=os.path.join(OUT, "t_8b2lane_WAKE_CS_SEL1_2.png"),
        title="t_8b2lane_WAKE_CS_SEL1 截图 2",
        footer_lines=[
            "WAKE_CS_SEL=01(HAVDD)",
            "预期：sim_out=0xAA(HAVDD); reg_lane_pd 拉高; CS_HVDDA 拉高; SD 关断信号拉高",
        ],
        labels=[
            {"y": 145, "text": "SD 关断信号 1→0", "color": "teal"},
        ],
    )

    # XON 第一张
    process(
        src=r"C:\Users\xiapeng2\AppData\Local\Temp\screenshot-20260715-173516.png",
        dst=os.path.join(OUT, "t_8b2lane_XON_1.png"),
        title="t_8b2lane_XON 截图 1",
        footer_lines=[
            "XON 拉低后再拉高",
            "预期：XON=0 期间 sim_out 输出为 0（含 data chopper polarity）",
        ],
        labels=[
            {"y": 95, "text": "XON 拉低再拉高", "color": "red", "x_dot": 1100},
            {"y": 175, "text": "sim_out=0", "color": "purple", "x_dot": 1100},
        ],
    )
