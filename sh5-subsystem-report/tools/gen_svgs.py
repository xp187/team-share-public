#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Flat Icon style SVG diagrams for the SH5 subsystem report.

Outputs (into ../assets/):
  sh5-architecture.svg   - three power domains and SH5 module map
  power-mode-fsm.svg     - Active / Standby / OFF state machine
  i2c-family.svg         - five I2C-related modules and their data paths
  dbgi2c-unlock.svg      - DBGI2C password-unlock and access sequence
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

FONT = ("'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei',"
        " 'Microsoft JhengHei', 'SimHei', sans-serif")

# style-1-flat-icon tokens
INK = "#111827"
GRAY = "#6b7280"
BOX_STROKE = "#d1d5db"
BLUE = "#2563eb"
RED = "#dc2626"
GREEN = "#16a34a"
PURPLE = "#9333ea"
ORANGE = "#ea580c"
BLUE_TINT = "#eff6ff"
BLUE_TINT2 = "#dbeafe"
GREEN_TINT = "#f0fdf4"
PURPLE_TINT = "#faf5ff"
ORANGE_TINT = "#fff7ed"
TEAL_TINT = "#f0fdfa"
RED_TINT = "#fef2f2"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_open(w, h):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        f'  <style>text {{ font-family: {FONT}; }}</style>',
        '  <defs>',
        '    <marker id="ar-b" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/></marker>',
        '    <marker id="ar-o" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#ea580c"/></marker>',
        '    <marker id="ar-g" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#16a34a"/></marker>',
        '    <marker id="ar-p" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#9333ea"/></marker>',
        '    <marker id="ar-gr" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#6b7280"/></marker>',
        '  </defs>',
        f'  <rect width="{w}" height="{h}" fill="#ffffff"/>',
    ]


def container(x, y, w, h, label, sub=""):
    lines = [
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#fafafa" stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="6,4"/>',
        f'  <text x="{x + 14}" y="{y + 24}" font-size="15" font-weight="600" fill="{INK}">{esc(label)}</text>',
    ]
    if sub:
        lines.append(f'  <text x="{x + 14}" y="{y + 41}" font-size="11" fill="{GRAY}">{esc(sub)}</text>')
    return lines


def box(x, y, w, h, label, sub="", fill="#ffffff", stroke=BOX_STROKE, tfill=INK, fs=13):
    lines = [
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>',
    ]
    if sub:
        lines.append(f'  <text x="{x + w / 2}" y="{y + h / 2 - 4}" font-size="{fs}" font-weight="600" fill="{tfill}" text-anchor="middle">{esc(label)}</text>')
        lines.append(f'  <text x="{x + w / 2}" y="{y + h / 2 + 13}" font-size="11" fill="{GRAY}" text-anchor="middle">{esc(sub)}</text>')
    else:
        lines.append(f'  <text x="{x + w / 2}" y="{y + h / 2 + 4}" font-size="{fs}" font-weight="600" fill="{tfill}" text-anchor="middle">{esc(label)}</text>')
    return lines


def arrow(x1, y1, x2, y2, color, marker, dash=None, width=1.5, label=None, lx=0, ly=0, lfill=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    lines = [f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{d} marker-end="url(#{marker})"/>']
    if label:
        lines.append(f'  <text x="{lx}" y="{ly}" font-size="11" fill="{lfill or color}" text-anchor="middle">{esc(label)}</text>')
    return lines


def path(d, color, marker, dash=None, width=1.5):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return f'  <path d="{d}" stroke="{color}" stroke-width="{width}" fill="none"{dd} marker-end="url(#{marker})"/>'


def save(name, lines):
    lines.append('</svg>')
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote", p)


# ---------------------------------------------------------------- SVG 1: architecture
def gen_architecture():
    L = svg_open(960, 660)
    L.append(f'  <text x="480" y="30" font-size="17" font-weight="600" fill="{INK}" text-anchor="middle">SH5（SH5_STBY）待机子系统 —— 三电源域架构（AOSHAN）</text>')

    # ---- AON domain (left), container 36..246
    L += container(36, 56, 210, 470, "AON 域", "常开电 · 永不掉电")
    L += box(56, 108, 170, 44, "Bandgap + OSC", "27 MHz 晶振", TEAL_TINT, "#99f6e4")
    L += box(56, 166, 170, 52, "PMU 状态机", "27MHz · 与APB异步", ORANGE_TINT, "#fdba74")
    L += box(56, 238, 170, 44, "Power Key", "整机电源键输入", RED_TINT, "#fca5a5")
    L += box(56, 302, 170, 40, "PMU 寄存器", "APB 27/166MHz")
    L += box(56, 364, 170, 62, "电源/复位生成", "stb_pwr_on / power_on")
    L += box(56, 450, 170, 56, "Boot Status 寄存器", "看门狗/SW/LVR 启动原因")

    # ---- STBY domain (center), container 262..682
    L += container(262, 56, 420, 470, "STBY 域 —— SH5_STBY", "常开电 · OFF 态无 OSC CLK")
    L += box(372, 108, 200, 66, "LEON3 CPU", "SPARC V8 · 27/600MHz", BLUE_TINT, "#93c5fd")
    L.append(f'  <text x="472" y="166" font-size="10.5" fill="{GRAY}" text-anchor="middle">I/D-Cache 4KB · DSU · 8 寄存器窗口</text>')
    L += box(322, 190, 320, 30, "AHB / APB 总线架构（含 int_misc 中断汇聚）", "", "#f3f4f6", BOX_STROKE, INK, 12)

    px = [302, 422, 542]
    pw, ph = 108, 46
    row1_y, row2_y, row3_y = 240, 296, 352
    per1 = [("GPIO ×34", "输入/输出/中断"), ("SAR-ADC ×4", "按键电压检测"), ("PWM", "呼吸灯")]
    per2 = [("Cable 检测 ×5", "HDMI/DP/VGA 插拔"), ("CEC ×2 / AUX ×2", "指令唤醒"), ("Type-C ×2", "插入唤醒")]
    per3 = [("DDC ×3 (EDDC)", "VGA×1 HDMI×2"), ("MI2C", "master I2C"), ("DBGI2C / DBGSPI", "调试桥")]
    for i, (t, s) in enumerate(per1):
        L += box(px[i], row1_y, pw, ph, t, s)
    for i, (t, s) in enumerate(per2):
        L += box(px[i], row2_y, pw, ph, t, s)
    for i, (t, s) in enumerate(per3):
        L += box(px[i], row3_y, pw, ph, t, s, PURPLE_TINT, "#d8b4fe")

    L += box(302, 414, 216, 40, "Pwr_ctrl / Level Shift / RX_SHORT_STB", "iso · rst_n · power_on 输出", "#f3f4f6", BOX_STROKE, INK, 11)
    L += box(532, 414, 108, 40, "Standby reg", "寄存器堆", "#f3f4f6", BOX_STROKE, INK, 11)

    # wake interrupt consolidated arrow: peripherals -> bus bar (gutter at x=416)
    L.append(path("M 416 348 L 416 226", BLUE, "ar-b"))
    L.append(f'  <text x="330" y="232" font-size="11" fill="{BLUE}">唤醒中断（Cable/CEC/AUX/ADC/DDC…）</text>')

    # ---- MAIN domain (right), container 718..924
    L += container(718, 56, 206, 470, "MAIN 域", "外部 DCDC 供电 · 可断电")
    L += box(744, 108, 154, 44, "Video Path", "显示主链路")
    L += box(744, 166, 154, 44, "Audio Path", "")
    L += box(744, 224, 154, 44, "DDR 控制", "")
    L += box(744, 282, 154, 44, "PLL / 高速时钟", "")
    L += box(744, 340, 154, 62, "APB_MAIN 外设", "I2C0/I2C1 · UART …")
    L += box(744, 424, 154, 62, "供电开关", "POWER_ON → 外部 DCDC", RED_TINT, "#fca5a5")

    # ---- inter-domain arrows
    L += arrow(226, 192, 258, 192, ORANGE, "ar-o", width=2)
    L.append(f'  <text x="242" y="180" font-size="10.5" fill="{ORANGE}" text-anchor="middle">CLK/RST</text>')
    # power key -> PMU FSM (directly below it now)
    L += arrow(141, 238, 141, 222, ORANGE, "ar-o", label="脉冲", lx=120, ly=232)
    # 电源/复位生成 -> STBY
    L.append(path("M 226 396 C 244 380, 250 340, 268 320", ORANGE, "ar-o", dash="4,3"))
    # LEON -> MAIN control
    L += arrow(572, 141, 740, 141, ORANGE, "ar-o", width=2, label="power_on / iso / rst_n", lx=656, ly=129)
    # Pwr_ctrl -> MAIN supply
    L.append(path("M 640 434 C 690 440, 700 448, 740 452", ORANGE, "ar-o", dash="4,3"))
    # MAIN clocks to STBY (mcu clk switch)
    L.append(path("M 821 282 C 830 230, 700 160, 578 148", GRAY, "ar-gr", dash="4,3"))
    L.append(f'  <text x="712" y="206" font-size="11" fill="{GRAY}" text-anchor="middle">mcu_clk / apb_clk（Active 时切高速）</text>')

    # external below STBY: EEPROM + Host
    L += box(302, 566, 140, 52, "外部 EEPROM", "保存待机/OFF 状态", GREEN_TINT, "#86efac")
    L += box(492, 566, 200, 52, "整机主机 / 调试主机", "DDC · DBGI2C · DBGSPI", PURPLE_TINT, "#d8b4fe")
    L += arrow(356, 566, 356, 402, GREEN, "ar-g", width=2, label="E2P 读写", lx=330, ly=480)
    L += arrow(592, 566, 592, 402, PURPLE, "ar-p", dash="5,3", width=2, label="烧录 / 调试（密码握手）", lx=592, ly=480)

    # legend
    L.append('  <g>')
    L += arrow(46, 580, 78, 580, ORANGE, "ar-o", width=2)
    L.append(f'  <text x="84" y="584" font-size="11" fill="{GRAY}">电源/时钟/复位控制</text>')
    L += arrow(46, 602, 78, 602, BLUE, "ar-b")
    L.append(f'  <text x="84" y="606" font-size="11" fill="{GRAY}">唤醒中断</text>')
    L += arrow(46, 624, 78, 624, GREEN, "ar-g")
    L.append(f'  <text x="84" y="628" font-size="11" fill="{GRAY}">数据（E2P）</text>')
    L += arrow(190, 580, 222, 580, PURPLE, "ar-p", dash="5,3")
    L.append(f'  <text x="228" y="584" font-size="11" fill="{GRAY}">调试/烧录通道</text>')
    L += arrow(190, 602, 222, 602, GRAY, "ar-gr", dash="4,3")
    L.append(f'  <text x="228" y="606" font-size="11" fill="{GRAY}">时钟切换路径</text>')
    L.append('  </g>')
    save("sh5-architecture.svg", L)


# ---------------------------------------------------------------- SVG 2: power mode FSM
def gen_fsm():
    def state(x, name, sub1, sub2, fill, stroke):
        lines = [
            f'  <rect x="{x}" y="190" width="200" height="96" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>',
            f'  <text x="{x + 100}" y="222" font-size="15" font-weight="600" fill="{INK}" text-anchor="middle">{esc(name)}</text>',
            f'  <text x="{x + 100}" y="246" font-size="11" fill="{GRAY}" text-anchor="middle">{esc(sub1)}</text>',
            f'  <text x="{x + 100}" y="263" font-size="11" fill="{GRAY}" text-anchor="middle">{esc(sub2)}</text>',
        ]
        return lines

    L = svg_open(960, 500)
    L.append(f'  <text x="480" y="30" font-size="17" font-weight="600" fill="{INK}" text-anchor="middle">SH5 电源状态机 —— Active / Standby / OFF</text>')

    L += state(90, "ACTIVE", "AON / STBY / MAIN 全上电", "LEON 27/600MHz 高速运行", GREEN_TINT, "#86efac")
    L += state(380, "STANDBY", "STBY 有电有时钟 · MAIN 断电", "LEON 值守，监控唤醒源", BLUE_TINT, "#93c5fd")
    L += state(670, "OFF", "STBY 无 OSC CLK · MAIN 断电", "仅 PMU 状态机工作", "#f3f4f6", BOX_STROKE)

    # initial marker -> STANDBY
    L.append('  <circle cx="330" cy="238" r="7" fill="#111827"/>')
    L += arrow(337, 238, 374, 238, INK, "ar-gr")
    L.append(f'  <text x="330" y="262" font-size="10.5" fill="{GRAY}" text-anchor="middle">上电 boot</text>')

    # ACTIVE -> STANDBY (top)
    L.append(path("M 260 190 C 300 130, 340 130, 400 186", ORANGE, "ar-o", width=2))
    L.append(f'  <text x="330" y="128" font-size="11.5" fill="{ORANGE}" text-anchor="middle" font-weight="600">无信号超时</text>')
    L.append(f'  <text x="330" y="144" font-size="10.5" fill="{GRAY}" text-anchor="middle">MAIN 切 OSC 时钟 → 关时钟 → 拉复位 → 开 iso → 断电</text>')

    # STANDBY -> ACTIVE (bottom)
    L.append(path("M 400 292 C 360 350, 320 350, 264 290", GREEN, "ar-g", width=2))
    L.append(f'  <text x="330" y="342" font-size="11.5" fill="{GREEN}" text-anchor="middle" font-weight="600">唤醒中断（Cable/CEC/AUX/ADC/DDC）</text>')
    L.append(f'  <text x="330" y="358" font-size="10.5" fill="{GRAY}" text-anchor="middle">POWER_ON → 关 iso → 放复位 → 切高速时钟</text>')

    # STANDBY -> OFF (top)
    L.append(path("M 550 190 C 590 130, 630 130, 690 186", RED, "ar-o", width=2))
    L.append(f'  <text x="620" y="128" font-size="11.5" fill="{RED}" text-anchor="middle" font-weight="600">Power Key</text>')
    L.append(f'  <text x="620" y="144" font-size="10.5" fill="{GRAY}" text-anchor="middle">LEON 记 EEPROM → reg_pmu_mcu_off_req=1 → 关 OSC CLK</text>')

    # OFF -> STANDBY (bottom)
    L.append(path("M 690 292 C 650 350, 610 350, 554 290", BLUE, "ar-b", width=2))
    L.append(f'  <text x="620" y="342" font-size="11.5" fill="{BLUE}" text-anchor="middle" font-weight="600">Power Key 脉冲</text>')
    L.append(f'  <text x="620" y="358" font-size="10.5" fill="{GRAY}" text-anchor="middle">开 OSC CLK → 释放 pmu_stby_rstn → LEON boot</text>')

    # ACTIVE -> OFF (outer top)
    L.append(path("M 190 186 C 240 70, 720 70, 770 186", RED, "ar-o", width=1.5))
    L.append(f'  <text x="480" y="76" font-size="11.5" fill="{RED}" text-anchor="middle" font-weight="600">Power Key（Active 直接进 OFF）</text>')
    L.append(f'  <text x="480" y="92" font-size="10.5" fill="{GRAY}" text-anchor="middle">先执行 ACTIVE→STANDBY 的降级 sequence，再按 STANDBY→OFF 关断</text>')

    # note
    L += box(90, 410, 780, 60, "", "", "#fafafa", BOX_STROKE)
    L.append(f'  <text x="110" y="434" font-size="11.5" fill="{INK}">假 OFF 变体（ADC 复用 Power Key）：不写 reg_pmu_mcu_off_req，仅关闭 STBY 域内除 ADC/LEON 外的时钟与复位，状态机停在 STBY 态。</text>')
    L.append(f'  <text x="110" y="454" font-size="11.5" fill="{INK}">状态回读：regr_stb_pwr_on / regr_stb_rst_n / regr_power_on / regr_stb_sw_rst_n / regr_stby_iso；启动原因：regr_boot_status[1:0]。</text>')
    save("power-mode-fsm.svg", L)


# ---------------------------------------------------------------- SVG 3: I2C family
def gen_i2c_family():
    L = svg_open(960, 640)
    L.append(f'  <text x="480" y="30" font-size="17" font-weight="600" fill="{INK}" text-anchor="middle">SH5 的 I2C 家族 —— 五个模块的角色与数据通路</text>')

    # left column: external
    L += container(30, 56, 210, 540, "芯片外部")
    L += box(56, 104, 158, 58, "整机主机 / PC", "经 HDMI / VGA 线材 DDC", PURPLE_TINT, "#d8b4fe")
    L += box(56, 192, 158, 52, "调试主机", "DBGI2C 引脚（AON_GP0/1）", PURPLE_TINT, "#d8b4fe")
    L += box(56, 272, 158, 52, "SPI 主机", "DBGSPI 引脚", PURPLE_TINT, "#d8b4fe")
    L += box(56, 352, 158, 52, "外部 EEPROM", "待机/状态数据", GREEN_TINT, "#86efac")

    # center column: SH5 STBY
    L += container(280, 56, 400, 540, "SH5（STBY 域）")
    L += box(310, 104, 160, 52, "DDC / EDDC 从机", "VGA×1 · HDMI×2")
    L += box(500, 104, 150, 52, "DDC access 开关", "0xFC 密码握手")
    L += box(310, 196, 160, 66, "DBGI2C 桥", "PWD 0x33 → SLV 0x34")
    L.append(f'  <text x="390" y="252" font-size="10.5" fill="{GRAY}" text-anchor="middle">外部 I2C → AHB / APB</text>')
    L += box(500, 196, 150, 52, "DBGSPI 桥", "SPI → AHB")
    L += box(310, 300, 160, 52, "MI2C（master）", "LEON 控制")
    L += box(310, 390, 340, 54, "LEON3（待机固件）", "中断响应 · 电源切换 · E2P 状态管理", BLUE_TINT, "#93c5fd")
    L += box(310, 478, 340, 80, "", "", ORANGE_TINT, "#fdba74")
    L.append(f'  <text x="480" y="501" font-size="13" font-weight="600" fill="{INK}" text-anchor="middle">系统控制寄存器</text>')
    L.append(f'  <text x="480" y="523" font-size="11" fill="{GRAY}" text-anchor="middle">0x80 控制字（WatchDog / CPU_RST_N / BUS_RST_N）</text>')
    L.append(f'  <text x="480" y="540" font-size="11" fill="{GRAY}" text-anchor="middle">+ 0x88/0x89 = 0xCBDC 秘钥；Device 0x32（DDC 通路 0x64）</text>')

    # right column
    L += container(720, 56, 210, 300, "内部总线（STBY 域）")
    L += box(746, 104, 158, 52, "STBY AHB", "全局地址空间")
    L += box(746, 182, 158, 52, "HOST_APB_STBY", "PAGE 0x110b_0000~ffff")
    L += container(720, 376, 210, 220, "MAIN 域")
    L += box(746, 424, 158, 62, "I2C0 / I2C1", "DW_apb_i2c 控制器")
    L.append(f'  <text x="825" y="502" font-size="10.5" fill="{GRAY}" text-anchor="middle">0x110A_3000 / 0x110A_4000</text>')
    L.append(f'  <text x="825" y="518" font-size="10.5" fill="{GRAY}" text-anchor="middle">APB_MAIN · SS/FS 模式</text>')
    L += box(746, 532, 158, 44, "通用 I2C 外设", "传感器/EEPROM 等")

    # arrows
    L += arrow(214, 133, 306, 130, PURPLE, "ar-p", width=2, label="DDC(I2C)", lx=258, ly=118)
    L += arrow(470, 130, 496, 130, BLUE, "ar-b")
    L.append(path("M 575 156 C 575 176, 540 188, 474 198", BLUE, "ar-b"))
    L.append(f'  <text x="522" y="180" font-size="10.5" fill="{BLUE}" text-anchor="middle">密码 0x31393639 导通</text>')
    L += arrow(214, 218, 306, 224, PURPLE, "ar-p", width=2)
    L.append(path("M 214 298 C 330 290, 420 260, 496 232", PURPLE, "ar-p", width=1.5))
    # DBGI2C -> buses (labels placed in clear corridors)
    L.append(path("M 470 214 C 570 200, 660 160, 742 136", BLUE, "ar-b", width=2))
    L.append(f'  <text x="618" y="164" font-size="11" fill="{BLUE}" text-anchor="middle">AHB 读写</text>')
    L.append(path("M 470 240 C 570 236, 660 222, 742 212", BLUE, "ar-b", width=2))
    L.append(f'  <text x="640" y="256" font-size="11" fill="{BLUE}" text-anchor="middle">APB 读写</text>')
    # DBGSPI -> AHB
    L.append(path("M 650 222 C 700 210, 712 170, 742 140", BLUE, "ar-b", dash="4,3"))
    # DBGI2C -> system control regs
    L.append(path("M 352 262 C 340 330, 380 440, 448 474", ORANGE, "ar-o", dash="4,3"))
    # EEPROM <-> MI2C
    L += arrow(214, 378, 306, 322, GREEN, "ar-g", width=2, label="读写", lx=246, ly=340)
    # LEON controls (route around MI2C box right side)
    L += arrow(390, 390, 390, 356, ORANGE, "ar-o", dash="4,3")
    L.append(path("M 600 390 C 560 336, 505 296, 432 264", ORANGE, "ar-o", dash="4,3"))
    L.append(f'  <text x="530" y="330" font-size="10.5" fill="{ORANGE}" text-anchor="middle">固件控制/中断</text>')
    # MAIN domain I2C
    L += arrow(825, 532, 825, 490, GRAY, "ar-gr")

    # note + legend rows
    L.append(f'  <text x="480" y="626" font-size="11" fill="{GRAY}" text-anchor="middle">注：I2C0/I2C1 位于 MAIN 域，由主系统使用；其余四个模块在 STBY 域（SH5）。</text>')
    L += arrow(300, 596, 332, 596, PURPLE, "ar-p", width=2)
    L.append(f'  <text x="338" y="600" font-size="11" fill="{GRAY}">外部 I2C/SPI 激励</text>')
    L += arrow(452, 596, 484, 596, BLUE, "ar-b", width=2)
    L.append(f'  <text x="490" y="600" font-size="11" fill="{GRAY}">内部总线访问</text>')
    L += arrow(592, 596, 624, 596, GREEN, "ar-g", width=2)
    L.append(f'  <text x="630" y="600" font-size="11" fill="{GRAY}">E2P 数据</text>')
    save("i2c-family.svg", L)


# ---------------------------------------------------------------- SVG 4: DBGI2C sequence
def gen_dbgi2c_seq():
    W, H = 960, 640
    L = svg_open(W, H)
    L.append(f'  <text x="480" y="30" font-size="17" font-weight="600" fill="{INK}" text-anchor="middle">DBGI2C 密码解锁与寄存器访问时序</text>')

    actors = [
        (150, "外部主机", "I2C master"),
        (400, "I2C_PWD_Slave", "Device ID 0x33"),
        (620, "I2C_SLV_Slave", "Device ID 0x34"),
        (840, "内部 AHB/APB", "地址空间"),
    ]
    top_y, bot_y = 70, 540
    for x, name, sub in actors:
        L += box(x - 80, top_y - 24, 160, 44, name, sub, BLUE_TINT if x == 150 else "#ffffff", "#93c5fd" if x == 150 else BOX_STROKE)
        L.append(f'  <line x1="{x}" y1="{top_y + 20}" x2="{x}" y2="{bot_y}" stroke="{BOX_STROKE}" stroke-width="1.5" stroke-dasharray="5,4"/>')

    def msg(y, x1, x2, text, color=INK, marker="ar-gr", dash=None):
        L.append(f'  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="1.5"' + (f' stroke-dasharray="{dash}"' if dash else "") + f' marker-end="url(#{marker})"/>')
        L.append(f'  <text x="{(x1 + x2) / 2}" y="{y - 7}" font-size="11.5" fill="{color}" text-anchor="middle">{esc(text)}</text>')

    def activation(x, y1, y2):
        L.append(f'  <rect x="{x - 5}" y="{y1}" width="10" height="{y2 - y1}" fill="{BLUE_TINT2}" stroke="#93c5fd"/>')

    y = 120
    msg(y, 150, 400, "① 写密码：S · 0x33+W · Pwd地址 · 密码ID 0x78 · 32bit 密码", BLUE, "ar-b")
    activation(400, y + 6, y + 40)
    L.append(f'  <text x="412" y="{y + 32}" font-size="11" fill="{GRAY}">校验通过 → 解锁 SLV，regr_dbgi2c_on=1</text>')

    y = 186
    msg(y, 150, 620, "② DATA 写：S · 0x34+W · 32bit 寄存器地址 · 32bit 数据 · P", BLUE, "ar-b")
    activation(620, y + 6, y + 40)
    msg(y + 34, 620, 840, "AHB/APB 写事务", ORANGE, "ar-o")

    y = 252
    msg(y, 150, 620, "③ DATA 读：S · 0x34+W · 32bit 地址 · RS · 0x34+R", BLUE, "ar-b")
    activation(620, y + 6, y + 40)
    msg(y + 34, 840, 620, "读回 32bit 数据", ORANGE, "ar-o")

    y = 322
    msg(y, 620, 150, "④ 返回 4 字节数据 · 末字节 NACK · STOP", GREEN, "ar-g")

    # alt frame: system control
    fy = 376
    L.append(f'  <rect x="90" y="{fy}" width="780" height="116" rx="8" fill="none" stroke="{GRAY}" stroke-width="1.2" stroke-dasharray="6,4"/>')
    L.append(f'  <rect x="90" y="{fy - 9}" width="150" height="18" fill="#f3f4f6" stroke="{BOX_STROKE}"/>')
    L.append(f'  <text x="100" y="{fy + 4}" font-size="11" font-weight="600" fill="{INK}">系统控制（可选）</text>')
    msg(fy + 40, 150, 620, "Device 0x32（DDC 通路 0x64）· 写 0x80 控制字", BLUE, "ar-b")
    L.append(f'  <text x="385" y="{fy + 62}" font-size="10.5" fill="{GRAY}" text-anchor="middle">0x80[0]=WatchDog 关闭 · [1]=CPU_RST_N · [4]=BUS_RST_N</text>')
    msg(fy + 92, 150, 620, "写秘钥：0x88=0xDC，0x89=0xCB（组合 0xCBDC 才生效）", BLUE, "ar-b")

    # note box: DDC passthrough
    L += box(90, 522, 780, 44, "", "", PURPLE_TINT, "#d8b4fe")
    L.append(f'  <text x="110" y="541" font-size="11.5" fill="{INK}">DDC 直通握手：向 base 0xFC / sub 0x0 写 0x31393639（"1969"）开启，DDC 通道切换到 debug I2C；</text>')
    L.append(f'  <text x="110" y="559" font-size="11.5" fill="{INK}">向 base 0xFC / sub 0x1 写 0x414f5348（"AOSH"）关闭。速率 100/400 KHz；reg_scl_stretch_en=0 可兼容不持 stretch 的主机。</text>')

    # legend
    L += arrow(90, 600, 122, 600, BLUE, "ar-b")
    L.append(f'  <text x="128" y="604" font-size="11" fill="{GRAY}">I2C 交易</text>')
    L += arrow(210, 600, 242, 600, ORANGE, "ar-o")
    L.append(f'  <text x="248" y="604" font-size="11" fill="{GRAY}">内部总线事务</text>')
    L += arrow(360, 600, 392, 600, GREEN, "ar-g")
    L.append(f'  <text x="398" y="604" font-size="11" fill="{GRAY}">返回数据</text>')
    save("dbgi2c-unlock.svg", L)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    gen_architecture()
    gen_fsm()
    gen_i2c_family()
    gen_dbgi2c_seq()
    print("all done")
