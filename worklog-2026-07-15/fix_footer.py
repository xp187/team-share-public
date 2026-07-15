from PIL import Image, ImageDraw, ImageFont
import os


def load_font(size):
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


FONT_FOOTER = load_font(18)
FOOTER_H = 60
FOOTER_BG = (248, 250, 252)
FOOTER_FG = (15, 23, 42)
FOOTER_BORDER = (226, 232, 240)


def fix_footer(path, lines):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    # crop off existing footer
    cropped = img.crop((0, 0, w, h - FOOTER_H))
    new = Image.new("RGB", (w, h), (255, 255, 255))
    new.paste(cropped, (0, 0))
    draw = ImageDraw.Draw(new)
    y0 = h - FOOTER_H
    draw.rectangle([0, y0, w - 1, h - 1], fill=FOOTER_BG, outline=FOOTER_BORDER)
    y = y0 + 8
    for line in lines:
        draw.text((12, y), line, fill=FOOTER_FG, font=FONT_FOOTER)
        y += 22
    new.save(path, "PNG")
    print(f"Fixed {path}")


OUT = r"E:\project\team-share-public\worklog-2026-07-15"
fix_footer(
    os.path.join(OUT, "t_8b2lane_WAKE_PD_OPT1_1.png"),
    ["WAKE_PD_OPT=01(CDR lane 掉电)", "预期：sim_out 保持原值; reg_lane_pd 拉高; SD 关断信号不变"],
)
fix_footer(
    os.path.join(OUT, "t_8b2lane_WAKE_PD_OPT1_2.png"),
    ["WAKE_PD_OPT=01(CDR lane 掉电)", "预期：sim_out 保持原值; reg_lane_pd 拉高; SD 关断信号不变"],
)
