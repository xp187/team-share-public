# MIPI 协议网页报告 — 构建计划

## 项目

- 输出目录：`E:\mipi-dsi-report\`
- 交付物：`index.html`（单页报告，内联 CSS/JS）+ `assets/*.svg`（14 张图示，HTML 用 `<img src="assets/xxx.svg">` 引用）
- 语言：报告正文与图示标注全部使用**中文**（技术术语/信号名/代码保留英文）
- 读者：数字 IC 验证工程师。**不写电气特性**（电压/阻抗/抖动/眼图一律不出现），聚焦协议、状态机、时序参数、包结构、错误处理、验证检查点。
- 资料：`E:\mipi-dsi-report\docs-src\dsi-summary.md`（DSI v1.1 总结）、`E:\mipi-dsi-report\docs-src\dphy-summary.md`（D-PHY v2.0 总结）。所有技术内容以这两份文件为准，数值不得编造。
- 图示风格：遵循 `E:\skills\fireworks-tech-graph\SKILL.md` 与 `E:\skills\fireworks-tech-graph\references\style-1-flat-icon.md`（Style 1 Flat Icon，白底）。SVG 内字体栈：`"Microsoft YaHei","Segoe UI",sans-serif`，等宽处用 `Consolas,monospace`。

## index.html 页面结构（单页、固定左侧目录）

视觉基调：白底、Flat Icon 风格配色（蓝 #2563eb 主、橙 #ea580c 控制、绿 #059669、紫 #7c3aed、灰 #6b7280）；左侧固定目录（桌面），移动端折叠为顶部汉堡；章节卡片式排版；表格斑马纹；关键数值用 `<code>` 高亮。目录项点击平滑滚动，滚动时当前章节高亮（scrollspy）。页首 Hero：标题「MIPI 协议技术报告 — DSI v1.1 / D-PHY v2.0（数字验证视角）」+ 规范徽标 + 阅读说明（读者定位、不含电气内容、资料来源声明）。

### 章节清单（id / 标题 / 内容要求）

1. `overview` 概述
   - MIPI Alliance 与协议族定位（DSI/CSI-2/DPI/DBI/DCS/D-PHY/C-PHY/M-PHY 关系一句话表）
   - 本报告依据：DSI v1.1（2012-04-06 Board approved）、D-PHY v2.0（2016-03-08 adopted）
   - DSI 版本历史表（v1.00a→v1.01→v1.02→v1.1 变更）
   - 两种基本工作模式（Command Mode / Video Mode）与 Virtual Channel（4 个 VC）概念
   - 图：`assets/dsi-layers.svg`
2. `link` 链路架构
   - Link = 1 Clock Lane + 1~4 Data Lane；HS 单向 Forward、LP 可双向、反向只用 Lane0 LP；Clock Lane 永远 host 驱动
   - Lane Module 组成（HS-TX/RX、LP-TX/RX/CD、CIL）与 CIL 类型表（MFAA/SFAA/MFAN/SFAN/MCNN/SCNN）
   - Command/Video Mode 对 Lane 的最低要求
   - 图：`assets/dphy-lane-module.svg`
3. `phy-state` D-PHY 线状态与模式
   - Lane 状态编码表（HS-0/1、LP-00/01/10/11 × Burst/Control/Escape 含义）
   - Stop 中心地位、TLPX≥50ns、Dp⊕Dn 重建 LP 时钟
   - 三种请求序列（HS / Escape / Turnaround）
   - 图：`assets/dphy-line-states.svg`、`assets/dphy-state-machine.svg`
4. `phy-xfer` D-PHY 传输流程
   - SoT/EoT 序列（TX/RX 两侧步骤、Sync `00011101`、RX 锁定 `011101` 容忍单比特错）
   - Escape Mode：进入序列、Spaced-One-Hot 编码、8 个 entry command 表（LPDT 0x87 / ULPS 0x78 / Reset-Trigger 0x46 / HS Test 0xBA…）
   - ULPS 进入/退出（TWAKEUP=1ms）、Clock Lane ULPS
   - BTA 握手时序（TTA-GO=4·TLPX、TTA-GET=5·TLPX、TTA-SURE∈[1,2]·TLPX）
   - Clock Lane 启动/停止（TCLK-PRE≥8UI、TCLK-POST≥60ns+52UI、TCLK-MISS≤60ns）、连续/非连续时钟
   - 全局时序参数表（Table 14 全表照录）
   - 初始化 TINIT≥100µs
   - Deskew 校准（>1.5G 必须：sync 全 1 16UI + 0101… pattern，initial ≥2¹⁵UI/≤100µs，periodic ≥2¹⁰UI/≤10µs）与速率档位（80M~1.5G / 2.5G / 4.5G）及版本互操作矩阵
   - 图：`assets/dphy-sot-eot.svg`、`assets/dphy-escape.svg`、`assets/dphy-bta-ulps.svg`、`assets/dphy-clock-deskew.svg`
5. `packet` DSI 包协议
   - Short/Long packet 结构、DI=VC[7:6]+DT[5:0]、WC、ECC、CRC footer
   - 字节序规则（LSB first、LS byte first）+ 示例 `29 01 00 06 01 0E 1E`
   - 无包同步码、靠 WC 定界；HS transmission 级联规则
   - ECC：P0~P5 生成方程、syndrome 纠错流程、P7=P6=0、纠 1 检 2
   - CRC-16：多项式 x^16+x^12+x^5+x^0（0x1021/反射 0x8408）、初值 0xFFFF、低字节先发；payload 长度 0 时 0xFFFF；规范 Annex B 注释笔误与 §8.8.18 CRC 疑误校注
   - 黄金测试向量表（ECC 5 组、CRC 3 组、30bpp 示例包、EoTp 字节）
   - 图：`assets/dsi-packet.svg`、`assets/dsi-ecc-crc.svg`
6. `datatype` Data Type 编码
   - DT 编码约束（低 4 位禁 0000/1111 的原因——与 EoT 区分）
   - Processor-sourced 全表（同步控制 / Command-DCS / 像素流 三组）
   - Peripheral-sourced 全表
   - EoTp（固定字节 08 0F 0F 01、VC=0、HS shall / LP should not / 双向兼容）
   - 常见误传校注：v1.1 中 RGB888=0x3E、RGB565=0x0E、18-bit loosely=0x2E
7. `video` Video Mode
   - 帧/行结构：帧=tL×(VSA+VBP+VACT+VFP)、行=tHSA+tHBP+tHACT+tHFP；VSS 起始帧、VSE/HSS 起始行、VSS/VSE 隐含 HSS
   - 三种模式对比（Non-Burst Sync Pulses / Sync Events / Burst Mode）特点与外设要求（line buffer）
   - BLLP 期间可做的 5 件事；每帧至少一次回 LP、推荐每行回 LP
   - 行拆分规则（单像素不跨包）；HBP/HFP blanking packet 省略条件
   - 外设时序参数表（brPHY/tL/tHSA…/HACT/VSA…）
   - 图：`assets/dsi-video-frame.svg`、`assets/dsi-video-modes.svg`
8. `command` Command Mode 与双向传输
   - Generic/DCS 读写规则（READ 必须是唯一或最后一个 packet + BTA；一次 transmission 最多一个需响应 packet）
   - Set Maximum Return Packet Size（上电默认 1）；Null/Blanking packet；Color Mode / Shutdown / Turn On
   - BTA 令牌机制（TurnRequest、必须还权）、反向四类传输（TE Trigger / ACK Trigger / Error Report / READ Response）
   - TE 上报完整流程（set_tear_on→BTA→无条件 BTA→等一帧→TE Trigger `01011101`）
   - 图：`assets/dsi-te-flow.svg`
9. `error` 错误处理与争用
   - 6 类低层协议错误（SoT / SoT Sync / EoT Sync / Escape Entry / LP Sync / False Control）
   - Error Report 16bit 位定义表（DT=0x02 包结构）
   - 错误累积-上报-清零机制；响应规则矩阵（单 bit ECC 纠正仍回数据+上报、multi-bit 只上报…）
   - 定时器表（HRX_TO/HTX_TO/LTX-P_TO/LRX-H_TO/TA_TO/PR_TO/PRESP_TO 及相对大小约束）
   - 争用（LP High/Low Fault、common-mode fault）与恢复
10. `pixel` 像素格式
    - 通用规则（R→G→B、LSB 先发、BT.601/709、Cb Y Cr Y 顺序）
    - 打包表：RGB565/666p/666lp/888/101010/121212、YUV422 20/24/16、YUV420（WC 约束列）
    - 合规要求（host 必须 4 种、peripheral ≥1 种）；fill pixel 规则
11. `dv` 数字验证视角（ checklist ）
    - Monitor/checker 检查点清单：SoT/EoT 序列与 sync 字、ECC 复算与 syndrome、CRC 复算、WC 定界、DT 合法性与 VC、lane 分发/合并、BTA 还权、时序参数（Table 14 全集）、TINIT/TWAKEUP、EoTp 存在性
    - 错误注入场景矩阵：6 类低层错误 × 期望上报 bit；ECC 单/多 bit 注入；CRC 错；非法 DT；VC invalid；超时场景
    - 覆盖率建议：DT 全编码 × VC × 包长边界（0/1/65535）、三种 video mode、lane 数 1/2/3/4、像素格式全集、BTA 回环、ULPS 进出、deskew 序列
    - 黄金参考模型要点：ECC P0~P5 方程 + syndrome 表、CRC-16 反射算法、lane 分发 round-robin
12. `appendix` 附录
    - 术语表（HS/LP/SoT/EoT/BTA/ULPS/LPDT/EoTp/BLLP/DCS/DPI/DBI/TE/VC/PLL/PPI/CIL…）
    - 规范引用清单
    - 资料来源声明：本报告内容来自 `C:\Users\xiapeng2\Desktop\MIPI` 中两份可读规范（mipi-DSI-specification-v1.1.pdf、mipi_d-phy_specification_v2-0.pdf）；目录中另有 7 份文件（JD9165BA 数据手册、MIPI DSI 相关协议介绍.pptx、MIPI High speed interface.ppt、MIPI_DBI_Specification_v2.pdf、D-PHY v1.0/v1.2、mipi_dsi_svt_uvm_user_guide.pdf）因企业透明加密无法读取，未纳入本报告。

## SVG 清单（14 张，全部中文标注、Flat Icon 白底）

### A 组（D-PHY，7 张）

1. `dphy-lane-module.svg`（架构图，960×640）
   左侧 Host（Master）：Protocol Layer 方块 → PPI → Lane Module ×5（1 Clock Lane MCNN + 4 Data Lane MFAA）；每个 Lane Module 内画 HS-TX、LP-TX、LP-RX、LP-CD 小方块；右侧 Peripheral（Slave）镜像。中间连线标注 Dp/Dn 差分对；HS 箭头单向（Host→Periph，蓝），LP 箭头双向（绿，仅 Lane0 标注双向）。底部图例。
2. `dphy-line-states.svg`（编码图，960×600）
   4 组 mini 波形（Dp/Dn 两条线）分别展示 LP-11/LP-10/LP-01/LP-00 电平组合 + 一组 HS 差分（HS-0/HS-1）；右侧对照表：状态码 × Burst/Control/Escape 含义。配色：Control 橙、Escape 紫、Burst 蓝。
3. `dphy-state-machine.svg`（状态机图，960×700）
   中心 Stop(LP-11) 大圆角框；三条出边：→HS-Rqst(LP-01)→Bridge(LP-00)→HS Burst（蓝）；→LP-Rqst(LP-10)→LP-00→LP-01→Space(LP-00)→Escape Mode（紫，内含 LPDT/ULPS/Trigger 子框）；→BTA 序列→Turnaround（绿）。所有状态标注"任意状态见 Stop ≥T\_MIN 回 Stop"虚线回流。逃逸中止规则注记。
4. `dphy-sot-eot.svg`（时序波形图，1200×640）
   两条波形轨（Dp、Dn 或单轨差分标注）：LP-11 → LP-01(TLPX) → LP-00(THS-PREPARE) → HS-0(THS-ZERO) → Sync `00011101` → Data(8 个 UI 方波，标注 DDR 时钟正交采样) → 翻转末位(THS-TRAIL) → LP-11(THS-EXIT)。下方第三轨画 DDR Clock，标注 TCLK-PRE/TCLK-POST。时序参数用大括号+文字标注（40ns+4UI 等数值写在括号旁）。图下注：RX 侧 TD-TERM-EN/THS-SETTLE/THS-SKIP。
5. `dphy-escape.svg`（时序+表，1200×680）
   上半：Escape 进入序列波形 LP-11→LP-10→LP-00→LP-01→LP-00，标注 Spaced-One-Hot（Mark-0=LP-01、Mark-1=LP-10、Space=LP-00）与 EXOR 时钟轨；演示一个字节（如 0x87 LPDT）的逐位波形。下半：8 个 entry command 表格（名称/类型/位模式/hex：0x87/0x78/0xF9/0x7B/0x46/0xBA/0x84/0x05）。
6. `dphy-bta-ulps.svg`（时序图组，1200×720）
   上半 BTA：Host 侧波形 LP-11→LP-10→LP-00→LP-10→LP-00(TTA-GO=4TLPX)→高阻观察；Periph 侧 TTA-SURE→LP-00(TTA-GET=5TLPX)→LP-10→LP-11；标注令牌移交方向箭头与 TLPX 比值 [2/3,3/2]。
   下半 ULPS：进入（Escape 序列+0x78 命令→Space 保持）与退出（Mark-1 持续 TWAKEUP=1ms→LP-11）两段波形，含 Clock Lane ULPS 注记。
7. `dphy-clock-deskew.svg`（时序+流程，1200×720）
   上半：Clock Lane HS 启动/停止波形：LP-11→LP-01→LP-00(TCLK-PREPARE)→HS-0(TCLK-ZERO)→DDR clk 先跑 TCLK-PRE≥8UI→Data Lane 才启动…最后 Data Lane 结束后时钟续跑 TCLK-POST≥60ns+52UI→TCLK-TRAIL→LP-11；TCLK-MISS≤60ns 标注。
   下半：deskew 校准 burst：SoT→Sync 全 1(16UI)→0101… pattern（initial ≥2¹⁵UI ≤100µs / periodic ≥2¹⁰UI ≤10µs），与普通 burst 对比小图；速率档阶梯条（80M~1.5G 无需 deskew / ≤2.5G 需 deskew / ≤4.5G 需 deskew+均衡+SSC）。

### B 组（DSI，7 张）

8. `dsi-layers.svg`（分层架构图，960×720）
   左右双列（Host / Peripheral）各 4 层：Application（像素格式 DPI-2 / 命令 DCS）→ PLI（packet 组成、ECC/CRC、VC 交织）→ Lane Management（distributor/merger）→ PHY（D-PHY，SoT/EoT、HS/LP）。层间箭头标数据形态（像素/命令→packet 字节→N lane 字节流→串行比特）。底部注：DSI 规范覆盖上三层，PHY 属 D-PHY。
9. `dsi-packet.svg`（比特布局图，1200×720）
   上：Long Packet 横向字节条：DI | WC LSB | WC MSB | ECC || Data0…DataN || CRC LSB | CRC MSB，标注 32-bit PH / Payload / 16-bit PF；DI 字节展开 VC[7:6]+DT[5:0]。
   下：Short Packet：DI | Data0 | Data1 | ECC。右侧字节序示意：单字节 LSB first（bit0→bit7 时间轴）、多字节 LS byte first；实例 `29 01 00 06 01 0E 1E` 逐字节标注。
10. `dsi-ecc-crc.svg`（算法流程图，1200×720）
    左：ECC 发送端（24-bit header → P0~P5 异或方程 → 8-bit ECC{0,0,P5..P0}）与接收端（重算→Syndrome S→分支：S=0 无错 / 命中矩阵纠 1bit / 命中 I 纠 parity / 其他多 bit 报错）流程图；示例 0x37/0x01F0→0x3F。
    右：CRC-16 LFSR 示意（16 级寄存器、抽头 x^16+x^12+x^5+x^0、初值 0xFFFF、LSB first 输入、低字节先发）+ 测试向量 `01`→0x1E0E。
11. `dsi-lane-dist.svg`（分发图，1200×680）
    上：Lane Distributor 概念：字节流 byte0..byte7 → round-robin → Lane0/1（2-lane 例）。
    下：三种结束情形横条图（N%2==0 同时 EoT / N%2==1 Lane0 晚 1 字节；3-lane 同理两例），每 lane 画 SoT…Data…EoT 横条，错位处用红色标注"多 1 字节"。
12. `dsi-video-frame.svg`（帧结构图，1200×760）
    二维帧图：纵轴 VSA/VBP/VACT/VFP（行数），横轴一行内部 HSA→HBP→HACT(像素包)→HFP；每个区域用不同色块+标注该区可发内容（VSS/VSE/HSS 短包、RGB 长包、BLLP）。公式条：帧周期=tL×(VSA+VBP+VACT+VFP)。标注"每帧第一行 VSS 开始、其余行 VSE/HSS 开始"、"每帧至少一次回 LP(LPM)"。
13. `dsi-video-modes.svg`（三模式对比时序，1200×760）
    三条横向时序带：(a) Non-Burst Sync Pulses：HSS…HSE 对 + 像素按 DPI 速率 + blanking packet 填充；(b) Non-Burst Sync Events：只有 HSS + 像素按 DPI 速率；(c) Burst Mode：像素压缩高速 burst + 大段 BLLP/LP。每带标注外设要求与特点，右侧对比小结表（sync 精度/line buffer/省电）。
14. `dsi-te-flow.svg`（序列图，960×760）
    双生命线（Host / Peripheral）时序：set_tear_on(0x15) → BTA → ACK Trigger(00100001) → Host 无条件 BTA（让出总线）→ 等待≤1 帧 → Periph Escape+TE Trigger(01011101) → BTA 还权。用 alt/loop 框标注"期间 Host 不得发任何命令"、"最多等待一个视频帧"。下方注 set_tear_scanline(0x39)/set_tear_off。

## 质量要求

- 每张 SVG：XML 校验通过（`E:\.venv\Scripts\python.exe -c "import xml.etree.ElementTree as ET;ET.parse('f.svg')"`）；文字不溢出（中文按 14px≈14px 宽估算）、箭头不穿框、留白充足、viewBox 与内容匹配。
- index.html：UTF-8；无外部依赖（不引 CDN）；`<img>` 引用 14 张 SVG 全部存在；目录 scrollspy；桌面/移动两态可用；HTML 注释用英文。
- 所有中文标点正确，数值与 docs-src 总结一致。
