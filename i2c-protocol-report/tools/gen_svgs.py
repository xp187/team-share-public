#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate all SVG figures for the I2C protocol web report.

Style: fireworks-tech-graph Style 1 (Flat Icon).
All figures are emitted with the Python list method to keep the SVG
syntactically valid and easy to review.
"""

import os
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

FONT = ("'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei',"
        " 'Microsoft JhengHei', 'SimHei', sans-serif")

INK = "#111827"       # gray-900, primary text
MUTE = "#6b7280"      # gray-500, secondary text
LINE = "#d1d5db"      # gray-300, box stroke
BLUE = "#2563eb"
RED = "#dc2626"
GREEN = "#16a34a"
ORANGE = "#ea580c"
PURPLE = "#9333ea"
BLUE_T = "#eff6ff"    # tints
BLUE_T2 = "#bfdbfe"
GREEN_T = "#f0fdf4"
GREEN_T2 = "#86efac"
RED_T = "#fef2f2"
RED_T2 = "#fca5a5"
ORANGE_T = "#fff7ed"
ORANGE_T2 = "#fdba74"
GRAY_T = "#f9fafb"


def header(w, h):
    return [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        "  <style>text { font-family: %s; }</style>" % FONT,
        "  <defs>",
        '    <marker id="ar-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="%s"/></marker>' % BLUE,
        '    <marker id="ar-red" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="%s"/></marker>' % RED,
        '    <marker id="ar-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="%s"/></marker>' % GREEN,
        '    <marker id="ar-orange" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="%s"/></marker>' % ORANGE,
        '    <marker id="ar-mute" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="%s"/></marker>' % MUTE,
        "  </defs>",
        '  <rect width="%d" height="%d" fill="#ffffff"/>' % (w, h),
    ]


def text(x, y, s, size=13, fill=INK, anchor="start", weight=400, style=""):
    st = ' font-style="%s"' % style if style else ""
    return ('<text x="%s" y="%s" fill="%s" font-size="%d" font-weight="%d" text-anchor="%s"%s>%s</text>'
            % (x, y, fill, size, weight, anchor, st, xml_escape(s)))


def box(x, y, w, h, fill="#ffffff", stroke=LINE, rx=8, sw=1.5, dash=""):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    return ('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" ry="%s" fill="%s" stroke="%s" stroke-width="%s"%s/>'
            % (x, y, w, h, rx, rx, fill, stroke, sw, d))


def line(x1, y1, x2, y2, stroke=INK, sw=1.5, dash="", marker=""):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    m = ' marker-end="url(#%s)"' % marker if marker else ""
    return '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"%s%s/>' % (x1, y1, x2, y2, stroke, sw, d, m)


def path(d, stroke=INK, sw=1.5, dash="", marker="", fill="none"):
    da = ' stroke-dasharray="%s"' % dash if dash else ""
    m = ' marker-end="url(#%s)"' % marker if marker else ""
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%s"%s%s/>' % (d, fill, stroke, sw, da, m)


def title(t, sub, w):
    return [
        text(40, 42, t, 17, INK, "start", 600),
        text(40, 64, sub, 12, MUTE),
        line(40, 76, w - 40, 76, LINE, 1),
    ]


def save(name, lines):
    svg = "\n".join(lines) + "\n</svg>\n"
    path_out = os.path.join(OUT, name)
    with open(path_out, "w", encoding="utf-8") as f:
        f.write(svg)
    ET.parse(path_out)  # raises on invalid XML
    print("OK", name)


# ---------------------------------------------------------------- bus topology
def bus_topology():
    L = header(960, 430)
    L += title("I2C 总线拓扑：开漏 + 上拉", "SDA/SCL 只能被拉低或释放（高阻）；释放后由上拉电阻拉高 —— 线与逻辑的基础", 960)
    # VDD rail
    L.append(text(60, 108, "VDD", 13, INK, "start", 600))
    L.append(line(100, 104, 880, 104, INK, 2))
    # pull-up resistors (rect symbol) down to bus lines
    for rx, name in ((340, "Rp"), (620, "Rp")):
        L.append(line(rx, 104, rx, 122, INK, 2))
        L.append(box(rx - 16, 122, 32, 44, "#ffffff", INK, 2, 1.5))
        L.append(text(rx, 149, name, 12, INK, "middle", 600))
        L.append(line(rx, 166, rx, 186, INK, 2))
    L.append(text(280, 92, "上拉电阻（典型 1k~10k，速率/总线电容折中）", 11, MUTE))
    # bus lines
    L.append(line(60, 186, 900, 186, BLUE, 2.5))
    L.append(text(64, 178, "SCL", 13, BLUE, "start", 600))
    L.append(line(60, 246, 900, 246, GREEN, 2.5))
    L.append(text(64, 238, "SDA", 13, GREEN, "start", 600))
    # devices
    devs = [(150, "Master", "产生时钟/发起传输", BLUE_T, BLUE_T2),
            (400, "Slave #1", "地址 0x33", GREEN_T, GREEN_T2),
            (610, "Slave #2", "地址 0x34", GREEN_T, GREEN_T2),
            (800, "Slave #N", "…", GREEN_T, GREEN_T2)]
    for cx, name, sub, fill, stroke in devs:
        L.append(line(cx, 186, cx, 246, MUTE, 1.5, dash="4,3"))
        L.append(line(cx, 246, cx, 286, MUTE, 1.5))
        L.append(box(cx - 75, 286, 150, 74, fill, stroke))
        L.append(text(cx, 316, name, 14, INK, "middle", 600))
        L.append(text(cx, 338, sub, 11, MUTE, "middle"))
    # open-drain note
    L.append(box(60, 386, 560, 30, ORANGE_T, ORANGE_T2, 6, 1))
    L.append(text(72, 406, "每个引脚 = 开漏输出：只能【拉低】或【释放为高阻】，不能主动输出高电平", 12, "#9a3412"))
    L.append(text(660, 406, "线与：任一设备拉低 → 总线为低", 12, RED, "start", 600))
    return L


# ------------------------------------------------------- start/stop conditions
def start_stop():
    L = header(960, 330)
    L += title("START / STOP 条件与数据有效窗口", "S 与 P 只在 SCL 高电平期间由 SDA 跳变产生；数据位期间 SCL 高时 SDA 必须保持稳定", 960)
    yh, yl = 110, 150      # SCL levels
    dh, dl = 210, 250      # SDA levels
    # grid labels
    L.append(text(48, 136, "SCL", 13, INK, "start", 600))
    L.append(text(48, 236, "SDA", 13, INK, "start", 600))
    # window shadings first (z-order below the waveforms)
    L.append(box(306, 196, 108, 68, GREEN_T, GREEN_T2, 4, 1, dash="4,3"))
    L.append(box(426, 196, 68, 68, BLUE_T, BLUE_T2, 4, 1, dash="4,3"))
    # SCL: idle high -> fall after START -> one data clock -> rise and stay high
    scl = [(100, yh), (210, yh), (210, yl), (300, yl), (300, yh), (420, yh),
           (420, yl), (500, yl), (500, yh), (640, yh), (640, yl), (720, yl), (720, yh), (900, yh)]
    # SDA: START fall at x=170 (SCL high); changes only in SCL-low windows (240/440);
    # stable during SCL-high plateaus; STOP rise at x=760 (SCL high)
    sda = [(100, dh), (170, dh), (170, dl), (240, dl), (260, dh),
           (440, dh), (460, dl), (760, dl), (760, dh), (900, dh)]
    L.append(path("M " + " L ".join("%s,%s" % p for p in scl), INK, 2))
    L.append(path("M " + " L ".join("%s,%s" % p for p in sda), BLUE, 2.5))
    # START / STOP markers
    L.append(box(150, 168, 44, 22, RED_T, RED_T2, 4, 1))
    L.append(text(172, 184, "S", 12, RED, "middle", 600))
    L.append(box(738, 168, 44, 22, GREEN_T, GREEN_T2, 4, 1))
    L.append(text(760, 184, "P", 12, GREEN, "middle", 600))
    L.append(text(150, 286, "START：SCL=1 时 SDA 高→低", 12, RED))
    L.append(text(700, 286, "STOP：SCL=1 时 SDA 低→高", 12, GREEN, "start"))
    # window labels on top of the shadings
    L.append(text(360, 232, "SCL=1：SDA 稳定", 10, GREEN, "middle"))
    L.append(text(460, 226, "SCL=0", 10, BLUE, "middle"))
    L.append(text(460, 242, "允许变化", 10, BLUE, "middle"))
    return L


# ------------------------------------------------------------- byte + ack wave
def byte_ack():
    L = header(960, 360)
    L += title("一字节传输与 ACK（第 9 拍）", "MSB first；发送方在第 9 拍释放 SDA，由接收方拉低产生 ACK", 960)
    yh, yl = 100, 138
    dh, dl = 200, 238
    x0, cell = 110, 84
    bits = [1, 0, 1, 1, 0, 0, 1, 0]   # sample byte 0xB2
    # SCL: 9 pulses
    pts = [(x0, yl)]
    for i in range(9):
        bx = x0 + i * cell
        pts += [(bx + 12, yl), (bx + 12, yh), (bx + cell - 16, yh), (bx + cell - 16, yl)]
    pts += [(x0 + 9 * cell + 20, yl)]
    L.append(path("M " + " L ".join("%s,%s" % p for p in pts), INK, 2))
    # SDA data bits: value per cell, transitions inside low windows (cell start area)
    spts = []
    cur_y = dh if bits[0] else dl
    spts.append((x0 + 6, cur_y))
    for i, b in enumerate(bits):
        tgt = dh if b else dl
        bx = x0 + i * cell
        if tgt != cur_y:
            spts += [(bx + 4, cur_y), (bx + 12, tgt)]
            cur_y = tgt
        spts.append((bx + cell, cur_y))
    # ACK cell: sender releases (dashed) then receiver pulls low
    bx = x0 + 8 * cell
    spts += [(bx + 4, cur_y), (bx + 12, dh)]
    L.append(path("M " + " L ".join("%s,%s" % p for p in spts), BLUE, 2.5))
    L.append(line(bx + 12, dh, bx + 30, dh, MUTE, 1.5, dash="4,3"))
    L.append(path("M %s,%s L %s,%s L %s,%s" % (bx + 30, dh, bx + 40, dl, x0 + 9 * cell + 6, dl), GREEN, 2.5))
    # bit labels
    for i, b in enumerate(bits):
        L.append(text(x0 + i * cell + cell / 2, 172, "D%d" % (7 - i), 12, INK, "middle", 600))
    L.append(text(x0 + 8 * cell + cell / 2, 172, "ACK", 12, GREEN, "middle", 600))
    # annotations
    L.append(text(x0 + 8 * cell + cell / 2, 268, "接收方拉低 = ACK（保持高 = NACK）", 11, GREEN, "middle"))
    L.append(text(110, 296, "发送方驱动 D7..D0（蓝）", 12, BLUE))
    L.append(text(340, 296, "第 9 拍发送方释放 SDA（灰虚线）", 12, MUTE))
    L.append(text(680, 296, "接收方拉低 SDA（绿）", 12, GREEN))
    L.append(text(110, 326, "规则：SDA 只在 SCL=0 期间允许变化；每字节固定 9 个 SCL 周期", 12, INK))
    L.append(text(620, 90, "示例字节 0xB2（MSB first）", 11, MUTE))
    return L


# ------------------------------------------------------------- address byte
def addr_byte():
    L = header(960, 320)
    L += title("7 位地址字节结构", "bit7..bit1 为设备地址，bit0 为 R/W；软件常用 8 位形式 (addr<<1)|R/W", 960)
    x0, cw, y0, hh = 120, 88, 110, 56
    names = ["A6", "A5", "A4", "A3", "A2", "A1", "A0", "R/W"]
    for i, n in enumerate(names):
        last = i == 7
        L.append(box(x0 + i * cw, y0, cw, hh, ORANGE_T if last else BLUE_T, ORANGE_T2 if last else BLUE_T2, 0 if i else 8, 1.5))
        L.append(text(x0 + i * cw + cw / 2, y0 + 34, n, 14, "#9a3412" if last else "#1e40af", "middle", 600))
        L.append(text(x0 + i * cw + cw / 2, y0 - 10, "bit%d" % (7 - i), 10, MUTE, "middle"))
    L.append(text(x0 + 3 * cw + 20, y0 + 84, "7 位设备地址", 12, "#1e40af"))
    L.append(text(x0 + 7 * cw + cw / 2, y0 + 84, "0=写 1=读", 12, "#9a3412", "middle"))
    # example
    L.append(text(120, 250, "例：设备地址 0x33", 13, INK, "start", 600))
    L.append(line(300, 244, 360, 244, MUTE, 1.5, marker="ar-mute"))
    L.append(text(330, 236, "左移1位", 10, MUTE, "middle"))
    L.append(box(380, 222, 170, 40, "#ffffff", LINE, 8, 1.5))
    L.append(text(395, 247, "写：0x66  (0x33<<1|0)", 12, INK))
    L.append(box(570, 222, 170, 40, "#ffffff", LINE, 8, 1.5))
    L.append(text(585, 247, "读：0x67  (0x33<<1|1)", 12, INK))
    L.append(text(120, 292, "10 位寻址：首字节 11110XX+R/W，第二字节为地址低 8 位（挂大量设备时使用）", 11, MUTE))
    return L


# ------------------------------------------------------- read / write flow
def rw_flow():
    L = header(960, 400)
    L += title("寄存器读写流程（最常见场景）", "读必须先用写方向发寄存器地址，再用 Repeated START(SR) 切到读方向；最后一个读字节由 master 回 NACK", 960)
    x0 = 40
    yw, yr = 130, 280

    def chip(x, y, t, kind):
        colors = {"S": (RED_T, RED_T2, RED), "P": (RED_T, RED_T2, RED),
                  "SR": (ORANGE_T, ORANGE_T2, ORANGE),
                  "A": (GREEN_T, GREEN_T2, GREEN), "N": (RED_T, RED_T2, RED)}
        if kind in colors:
            f, s, tc = colors[kind]
            L.append("<circle cx='%s' cy='%s' r='13' fill='%s' stroke='%s'/>" % (x, y, f, s))
            L.append(text(x, y + 4, t, 11, tc, "middle", 600))
        return

    def stepbox(x, y, w, label, sub="", fill="#ffffff", stroke=LINE, tc=INK):
        L.append(box(x, y, w, 52, fill, stroke))
        L.append(text(x + w / 2, y + 24, label, 12, tc, "middle", 600))
        if sub:
            L.append(text(x + w / 2, y + 41, sub, 10, MUTE, "middle"))

    def flow(y, items, lane_color):
        x = x0
        for i, it in enumerate(items):
            w = it[1]
            stepbox(x, y, w, it[0], it[2] if len(it) > 2 else "",
                    lane_color[0], lane_color[1], lane_color[2])
            x += w
            if i < len(items) - 1:
                ack = it[3] if len(it) > 3 else "A"
                L.append(line(x + 2, y + 26, x + 30, y + 26, MUTE, 1.5, marker="ar-mute"))
                chip(x + 16, y - 2, ack, ack)
                x += 32
        return x

    L.append(text(x0, yw - 18, "写（W）：S → ADR+W → REG → DATA×n → P", 13, "#1e40af", "start", 600))
    flow(yw, [("S", 46, "START", None), ("ADR+W", 92, "地址+写"), ("REG", 86, "寄存器地址"),
              ("DATA0", 84, "数据"), ("…", 40, "", None), ("DATAn", 84, "数据"), ("P", 46, "STOP", None)],
         (BLUE_T, BLUE_T2, "#1e40af"))
    L.append(text(x0, yr - 18, "读（R）：S → ADR+W → REG → SR → ADR+R → DATA×n（末字节 NACK）→ P", 13, "#166534", "start", 600))
    flow(yr, [("S", 46, "START", None), ("ADR+W", 92, "地址+写"), ("REG", 86, "寄存器地址"),
              ("SR", 46, "重启动", None), ("ADR+R", 92, "地址+读"), ("DATA0", 84, "数据"),
              ("…", 40, "", None), ("DATAn", 84, "末字节", "N"), ("P", 46, "STOP", None)],
         (GREEN_T, GREEN_T2, "#166534"))
    # legend
    L.append("<circle cx='52' cy='368' r='10' fill='%s' stroke='%s'/>" % (GREEN_T, GREEN_T2))
    L.append(text(52, 372, "A", 10, GREEN, "middle", 600))
    L.append(text(68, 372, "ACK（接收方拉低 SDA）", 11, MUTE))
    L.append("<circle cx='240' cy='368' r='10' fill='%s' stroke='%s'/>" % (RED_T, RED_T2))
    L.append(text(240, 372, "N", 10, RED, "middle", 600))
    L.append(text(256, 372, "NACK（保持高，读末尾/异常）", 11, MUTE))
    L.append(text(460, 372, "SR = Repeated START：不发 STOP 直接再次 START，切方向并占住总线", 11, ORANGE))
    return L


# ------------------------------------------------------- clock stretching
def clock_stretch():
    L = header(960, 330)
    L += title("时钟拉伸（Clock Stretching）", "slave 在任意 SCL 低电平后继续拉低 SCL，强制 master 等待；常见于 ACK 之后", 960)
    yh, yl = 110, 150
    dh, dl = 210, 250
    L.append(text(48, 136, "SCL", 13, INK, "start", 600))
    L.append(text(48, 236, "SDA", 13, INK, "start", 600))
    # SCL: two normal pulses, then long held-low stretch, then resume
    pts = [(100, yl), (112, yl), (112, yh), (168, yh), (168, yl),
           (200, yl), (212, yh), (268, yh), (268, yl),
           (640, yl), (652, yh), (708, yh), (708, yl),
           (740, yl), (752, yh), (808, yh), (808, yl), (880, yl)]
    L.append(path("M " + " L ".join("%s,%s" % p for p in pts), INK, 2))
    # stretch shading
    L.append(box(268, 92, 384, 176, RED_T, RED_T2, 4, 1, dash="5,3"))
    L.append(text(460, 108, "slave 保持拉低 SCL（时钟拉伸）", 12, RED, "middle", 600))
    # SDA: stable through stretch
    sda = [(100, dh), (150, dh), (160, dl), (230, dl), (240, dh), (660, dh), (670, dl), (740, dl), (750, dh), (880, dh)]
    L.append(path("M " + " L ".join("%s,%s" % p for p in sda), BLUE, 2.5))
    L.append(text(460, 236, "传输暂停，SDA 保持", 11, MUTE, "middle"))
    # master intent dashed (what master wanted to do)
    L.append(path("M 290,%s L 300,%s L 350,%s L 360,%s" % (yl, yh, yh, yl), MUTE, 1.5, dash="3,3"))
    L.append(text(326, 92, "master 本想继续打钟（虚线），检测到 SCL 未释放则等待", 11, MUTE, "middle"))
    L.append(text(100, 296, "DV：master 必须有等待/超时逻辑（DW_apb_i2c 有 tx/rx 超时）；case 覆盖 ACK 后拉伸、地址后拉伸", 11, INK))
    return L


# ------------------------------------------------------- arbitration
def arbitration():
    L = header(960, 360)
    L += title("多主机仲裁（线与回读）", "每个 master 发位同时回读 SDA：发 1 却读到 0 → 仲裁失败立即退出；数据不丢失", 960)
    rows = [("Master A 想发", 120, "#1e40af"), ("Master B 想发", 190, "#166534"), ("总线 SDA 实际", 260, RED)]
    for name, y, c in rows:
        L.append(text(40, y + 5, name, 12, c, "start", 600))
    x0, cw = 200, 90
    bits = [("A", 0, 0), ("B", 0, 0), ("C", 1, 0), ("D", None, 0)]
    # bit frames
    for i in range(4):
        bx = x0 + i * cw
        L.append(line(bx, 96, bx, 300, LINE, 1, dash="3,3"))
        L.append(text(bx + cw / 2, 88, "bit%d" % (7 - i), 10, MUTE, "middle"))
    # highlight losing bit first (z-order below the column texts)
    L.append(box(x0 + 2 * cw + 4, 98, cw - 8, 210, RED_T, RED_T2, 6, 1))
    va = [0, 0, 1, None]
    vb = [0, 0, 0, 0]
    for i in range(4):
        bx = x0 + i * cw
        # A row
        if va[i] is None:
            L.append(box(bx + 6, 106, cw - 12, 28, GRAY_T, LINE, 4, 1, dash="4,3"))
            L.append(text(bx + cw / 2, 125, "退出驱动", 10, MUTE, "middle"))
        else:
            L.append(text(bx + cw / 2, 125, str(va[i]), 14, "#1e40af", "middle", 600))
        L.append(text(bx + cw / 2, 195, str(vb[i]), 14, "#166534", "middle", 600))
        bus = 0 if (vb[i] == 0 or va[i] in (0, None)) else 1
        L.append(text(bx + cw / 2, 265, str(bus), 14, RED, "middle", 600))
    L.append(text(x0 + 2 * cw + cw / 2, 330, "A 发 1 却回读到 0 → 仲裁失败，立即停止驱动", 12, RED, "middle", 600))
    L.append(text(200 + 4 * cw + 20, 125, "失败方可稍后重试，获胜方数据不受影响", 11, MUTE))
    return L


# ------------------------------------------------------- reserved addresses
def main():
    os.makedirs(OUT, exist_ok=True)
    save("bus-topology.svg", bus_topology())
    save("start-stop.svg", start_stop())
    save("byte-ack.svg", byte_ack())
    save("addr-byte.svg", addr_byte())
    save("rw-flow.svg", rw_flow())
    save("clock-stretch.svg", clock_stretch())
    save("arbitration.svg", arbitration())


if __name__ == "__main__":
    main()
