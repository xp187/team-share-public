from pathlib import Path
from xml.sax.saxutils import escape


REPORT_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = REPORT_DIR / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 960
INK = "#111827"
MUTE = "#6b7280"
LINE = "#d1d5db"
BLUE = "#2563eb"
BLUE_TINT = "#eff6ff"
BLUE_LINE = "#bfdbfe"
GREEN = "#16a34a"
GREEN_TINT = "#f0fdf4"
GREEN_LINE = "#bbf7d0"
RED = "#dc2626"
RED_TINT = "#fef2f2"
RED_LINE = "#fecaca"
ORANGE = "#ea580c"
ORANGE_TINT = "#fff7ed"
ORANGE_LINE = "#fed7aa"


def text(
    value: str,
    x: float,
    y: float,
    size: int = 13,
    fill: str = INK,
    weight: str = "400",
    anchor: str = "start",
    family: str = "sans",
) -> str:
    font_family = (
        "'SFMono-Regular', Consolas, 'Liberation Mono', monospace"
        if family == "mono"
        else "'Helvetica Neue', Helvetica, Arial, 'PingFang SC', "
        "'Microsoft YaHei', sans-serif"
    )
    return (
        f'<text x="{x}" y="{y}" font-family="{font_family}" '
        f'font-size="{size}px" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}">{escape(value)}</text>'
    )


def header(title: str, subtitle: str, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}">',
        "  <defs>",
        f'    <marker id="ar-blue" markerWidth="8" markerHeight="6" refX="7" '
        f'orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="{BLUE}"/></marker>',
        f'    <marker id="ar-green" markerWidth="8" markerHeight="6" refX="7" '
        f'orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="{GREEN}"/></marker>',
        f'    <marker id="ar-red" markerWidth="8" markerHeight="6" refX="7" '
        f'orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="{RED}"/></marker>',
        f'    <marker id="ar-mute" markerWidth="8" markerHeight="6" refX="7" '
        f'orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="{MUTE}"/></marker>',
        "  </defs>",
        f'<rect width="{WIDTH}" height="{height}" fill="#ffffff"/>',
        text(title, 40, 40, 20, INK, "700"),
        text(subtitle, 40, 63, 12, MUTE),
        f'<line x1="40" y1="78" x2="920" y2="78" stroke="{LINE}"/>',
    ]


def rect(
    x: float,
    y: float,
    width: float,
    height: float,
    fill: str,
    stroke: str,
    radius: int = 12,
    stroke_width: float = 1.2,
    dash: str = "",
) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        f'rx="{radius}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{stroke_width}"{dash_attr}/>'
    )


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str = BLUE,
    marker: str = "ar-blue",
    width: float = 1.8,
    dash: str = "",
) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="{width}" marker-end="url(#{marker})"'
        f'{dash_attr}/>'
    )


def path(
    d: str,
    color: str = BLUE,
    marker: str = "ar-blue",
    width: float = 1.8,
    dash: str = "",
) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'marker-end="url(#{marker})"{dash_attr}/>'
    )


def state_card(
    parts: list[str],
    center_x: float,
    center_y: float,
    width: float = 128,
    fill: str = BLUE_TINT,
    stroke: str = BLUE_LINE,
    title_color: str = BLUE,
) -> list[str]:
    height = 62
    left = center_x - width / 2
    top = center_y - height / 2
    return [
        rect(left, top, width, height, fill, stroke),
        text(parts[0], center_x, center_y - 4, 14, title_color, "700", "middle", "mono"),
        text(parts[1], center_x, center_y + 18, 11, MUTE, "400", "middle"),
    ]


def label_box(
    value: str,
    center_x: float,
    baseline_y: float,
    color: str = BLUE,
    fill: str = "#ffffff",
    width: float = 86,
) -> list[str]:
    height = 22
    return [
        rect(center_x - width / 2, baseline_y - 17, width, height, fill, color, 6, 1),
        text(value, center_x, baseline_y - 2, 11, color, "600", "middle"),
    ]


def note_card(
    title: str,
    detail: str,
    x: float,
    y: float,
    width: float,
    fill: str = BLUE_TINT,
    stroke: str = BLUE_LINE,
    title_color: str = BLUE,
) -> list[str]:
    return [
        rect(x, y, width, 60, fill, stroke, 10),
        text(title, x + 14, y + 23, 12, title_color, "700"),
        text(detail, x + 14, y + 44, 11, MUTE),
    ]


def save_svg(filename: str, lines: list[str]) -> None:
    lines.append("</svg>")
    (ASSETS_DIR / filename).write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_write_svg() -> None:
    lines = header(
        "I2C Slave 写操作状态机",
        "RTL 实际路径：地址不匹配进入 devid_error；写数据完成后由 ACK 回到下一个 data 字节",
        520,
    )

    centers = [100, 238, 388, 538, 688, 838]
    names = [
        ("idle", "等待 START"),
        ("slave_ack", "地址 ACK"),
        ("get_address", "接收寄存器地址"),
        ("gma_ack", "寄存器地址 ACK"),
        ("data", "接收写数据"),
        ("data_ack", "数据 ACK"),
    ]
    widths = [92, 120, 142, 126, 112, 120]
    for index in range(len(centers) - 1):
        start = centers[index] + widths[index] / 2 + 7
        end = centers[index + 1] - widths[index + 1] / 2 - 7
        lines.append(line(start, 188, end, 188))

    lines.extend(
        [
            line(42, 188, centers[0] - widths[0] / 2 - 7, 188, INK, "ar-mute"),
            '<circle cx="36" cy="188" r="6" fill="#111827"/>',
        ]
    )
    for index, (name, detail) in enumerate(names):
        lines.extend(state_card([name, detail], centers[index], 188, widths[index]))
    lines.extend(
        state_card(
            ["devid_error", "地址不匹配后锁死"],
            238,
            316,
            142,
            RED_TINT,
            RED_LINE,
            RED,
        )
    )

    for value, center_x, width in [
        ("my_adr=1", 169, 72),
        ("rw=0", 313, 60),
        ("8 bit", 463, 58),
        ("ld=1", 613, 58),
        ("8 bit", 763, 58),
    ]:
        lines.extend(label_box(value, center_x, 145, BLUE, "#ffffff", width))

    lines.extend(
        [
            path("M 838,219 C 838,270 688,270 688,219", GREEN, "ar-green"),
            *label_box("rw=0 → data", 763, 268, GREEN, GREEN_TINT, 96),
            path("M 688,219 C 688,370 100,370 100,219", MUTE, "ar-mute", 1.4, "6 5"),
            *label_box("sta / sto → idle", 500, 362, MUTE, "#ffffff", 112),
            path("M 100,219 C 100,278 238,278 238,285", RED, "ar-red"),
            *label_box("my_adr=0", 156, 266, RED, RED_TINT, 76),
            path("M 309,300 C 360,300 360,332 309,332", RED, "ar-red", 1.5),
            *label_box("锁死", 360, 316, RED, RED_TINT, 52),
        ]
    )

    lines.append(
        text(
            "ACK=0：从机拉低 SDA，继续进入下一字节；ACK=1：结束当前写事务",
            480,
            400,
            12,
            MUTE,
            "400",
            "middle",
        )
    )
    lines.extend(
        [
            *note_card(
                "地址阶段",
                "匹配设备地址后，rw=0 才进入写路径",
                40,
                424,
                270,
            ),
            *note_card(
                "数据阶段",
                "每收到 8 bit 数据，就产生一次 ACK",
                330,
                424,
                270,
            ),
            *note_card(
                "RTL 对齐",
                "状态名与 RTL parameter 保持一致",
                620,
                424,
                300,
                ORANGE_TINT,
                ORANGE_LINE,
                ORANGE,
            ),
        ]
    )
    save_svg("i2c_slave_write_state_machine.svg", lines)


def build_read_svg() -> None:
    lines = header(
        "I2C Slave 读操作状态机",
        "以 RTL 为准：rw=1 时 slave_ack 没有跳转到 data；下方虚线为文档描述的预期路径",
        500,
    )

    centers = [112, 322, 532, 742]
    names = [
        ("idle", "等待 START"),
        ("slave_ack", "地址 ACK"),
        ("data", "发送读数据"),
        ("data_ack", "采样主机响应"),
    ]
    widths = [92, 120, 112, 132]
    for index in range(len(centers) - 1):
        start = centers[index] + widths[index] / 2 + 7
        end = centers[index + 1] - widths[index + 1] / 2 - 7
        if index == 0:
            lines.append(line(start, 188, end, 188))
        else:
            lines.append(line(start, 188, end, 188, MUTE, "ar-mute", 1.5, "6 5"))
    lines.extend(
        [
            line(54, 188, centers[0] - widths[0] / 2 - 7, 188, INK, "ar-mute"),
            '<circle cx="48" cy="188" r="6" fill="#111827"/>',
        ]
    )
    for index, (name, detail) in enumerate(names):
        if index < 2:
            lines.extend(state_card([name, detail], centers[index], 188, widths[index]))
        else:
            lines.extend(
                state_card(
                    [name, detail],
                    centers[index],
                    188,
                    widths[index],
                    "#f9fafb",
                    LINE,
                    MUTE,
                )
            )
    for value, center_x, width in [
        ("my_adr=1", 217, 72),
        ("rw=1：缺 state<=data", 427, 132),
        ("8 bit", 637, 58),
    ]:
        lines.extend(label_box(value, center_x, 145, BLUE, "#ffffff", width))

    lines.extend(
        [
            path("M 400,219 C 460,302 200,302 260,219", RED, "ar-red"),
            *label_box("RTL 自循环：rw=1", 330, 296, RED, RED_TINT, 116),
            path("M 742,219 C 742,286 532,286 532,219", GREEN, "ar-green", 1.5, "6 5"),
            *label_box("预期 ACK", 637, 282, GREEN, GREEN_TINT, 76),
            path("M 742,219 C 742,346 112,346 112,219", RED, "ar-red", 1.5, "6 5"),
            *label_box("预期 NACK", 430, 342, RED, RED_TINT, 84),
        ]
    )
    lines.append(
        text(
            "实线 = RTL 当前可达路径；虚线 = 文档/设计意图。当前 slave_ack 的 rw=1 分支未赋值 state，读数据阶段不会被进入。",
            480,
            366,
            11,
            MUTE,
            "400",
            "middle",
        )
    )
    lines.extend(
        [
            *note_card(
                "ACK 分支",
                "主机继续接收：data_ack → data",
                40,
                394,
                270,
                GREEN_TINT,
                GREEN_LINE,
                GREEN,
            ),
            *note_card(
                "NACK 分支",
                "主机结束读取：data_ack → idle",
                330,
                394,
                270,
                RED_TINT,
                RED_LINE,
                RED,
            ),
            *note_card(
                "协议要点",
                "SDA 在 ACK 位由接收方控制",
                620,
                394,
                300,
                ORANGE_TINT,
                ORANGE_LINE,
                ORANGE,
            ),
        ]
    )
    save_svg("i2c_slave_read_state_machine.svg", lines)


if __name__ == "__main__":
    build_write_svg()
    build_read_svg()
    print("Generated optimized I2C state-machine diagrams:")
    print(ASSETS_DIR / "i2c_slave_write_state_machine.svg")
    print(ASSETS_DIR / "i2c_slave_read_state_machine.svg")
