# MIPI DSI v1.1 规范技术总结（数字验证视角）

> 来源：`C:\Users\xiapeng2\Desktop\MIPI\mipi-DSI-specification-v1.1.pdf`（全文 5323 行已通读；ECC/CRC 示例数值均经 Python 独立复算验证）。
> 面向数字 IC 验证工程师，聚焦协议与数字逻辑，不含电气特性。

## 1. 文档整体结构

- 文档标题：MIPI Alliance Specification for Display Serial Interface (DSI)，Version 1.1 — 22 November 2011；MIPI Board Approved 14-Mar-2012；首页标注发布日期 6-Apr-2012。
- 正文章节（除标注 informative 外均为 normative）：
  - §1 Overview：定义 host processor 与 peripheral（显示模组）间的协议与信号时序关系；电气/物理规格、DPI-2/DBI-2 legacy 接口、I2C/SPI 辅助总线均不在范围内。
  - §2 Terminology：Forward/Reverse Direction、Half duplex、Lane、Link（1 条 Clock Lane + 至少 1 条 Data Lane）、HS/LP Transmission（均以 LP-11 界定起止）、Virtual Channel（最多 4 个）、Word Count。
  - §3 References：DCS、DBI-2、DPI-2、D-PHY v1.1、SDF、CEA-861-E、ITU-R BT.601/656/709。Video Mode 像素格式取自 DPI-2；Command Mode 命令集取自 DCS。
  - §4 DSI Introduction（分层定义、Command/Video Mode、Virtual Channel）。
  - §5 DSI Physical Layer（数据流控、双向策略、Command/Video Mode 接口最低要求、BTA、Clock 管理、系统上电初始化）。
  - §6 Multi-Lane Distribution and Merging。
  - §7 Low-Level Protocol Errors and Contention（6 类低层错误、争用检测/恢复、定时器）。
  - §8 DSI Protocol（包结构、Data Type、双向传输、Video Mode 时序、TE）——全文核心。
  - §9 ECC and Checksum（Hamming 修改码、CRC-16）。
  - §10 Compliance, Interoperability, and Optional Capabilities。
  - Annex A 争用检测/恢复；Annex B CRC 计算 C 代码；Annex C 隔行视频传输。
- 全文共 41 张图、28 张表。

## 2. DSI 总体架构

### 2.1 协议分层

- **PHY Layer**：传输介质、I/O 电路、时钟捕获机制；SoT/EoT 带外信令、比特/字节级同步。SLVS 有 HS/LP 两种电气模式。PHY 层规范在 D-PHY 中定义，DSI 只引用。
- **Lane Management Layer**：DSI 是 lane 可扩展接口（1/2/3/4 条 Data Lane）。发送端 distributor 把输出字节流分发到 N 条 lane；接收端 merger 合并恢复原始字节序。
- **Protocol Layer（PLI）**：定义线上比特/字节顺序与取值、packet 组成、header 生成与解析、ECC/Checksum 添加与校验、用 Virtual Channel 标签交织多路数据流。
- **Application Layer**：像素格式（Video Mode 取 DPI-2）或命令与参数（Command Mode 取 DCS）到 packet 字节的映射。

### 2.2 DSI 与 D-PHY 的关系

- DSI 是协议层规范，D-PHY 提供物理层。DSI 中 SoT/EoT 序列、Escape Mode、LPDT、Trigger Message、LP High/Low Fault、TINIT、ULPS 等均引用 D-PHY。
- D-PHY 低层协议最小数据单位为 1 字节，一次 transmission 含整数个字节。
- 与 CSI-2 对比：CSI-2 HS 单向、控制走 I2C 旁路、数据方向 peripheral→host；DSI 半双工双向、主方向 host→peripheral。

### 2.3 两种基本工作模式

- **Command Mode**：transaction 以向带 display controller（含本地寄存器与 frame buffer）的 peripheral 发命令/参数为主，host 可读写寄存器与 frame memory。要求双向接口。
- **Video Mode**：host→peripheral 为实时像素流，只能用 HS mode 传视频；仅 Video Mode 的系统可用单向数据路径。部分 Video Mode 模组带 timing controller + 局部 frame buffer，可低功耗自刷新。
- Virtual Channel：DI[7:6] 两位，最多 4 个虚拟通道，以 packet 为单位交织服务多个外设（多 driver IC 拼大屏、一路 Command + 一路 Video、隔行视频两个 field 各用一个 VC）。

## 3. 数据通道与 Lane 分配

- 物理组成：1–4 条 Data Lane + 1 条 Clock Lane。Command Mode 系统中 Data Lane 0 必须双向，其余 lane 必须单向；Video Mode 系统中 Lane 0 可双向可单向，其余单向。Clock Lane 只能由 host 驱动。
- LP 信令策略：前向 LP 传输只能用 Lane 0；反向（peripheral→host）传输只能用 Lane 0 的 LP Mode。多 lane 系统反向也只用 Lane 0。
- Lane 分发规则（Lane Distributor）：
  - 缓冲 N 字节（N=lane 数），按 round-robin 并行发出：2 lane 时 byte0→Lane0、byte1→Lane1、byte2→Lane0……
  - 所有 lane 同时并行执行 SoT；但各 lane 独立结束——总字节数不是 lane 数整数倍时，先耗尽数据的 lane 提前一个字节发 EoT 进入 LPS。
  - 末尾不足 N 字节时 Lane Management layer 对无数据的 lane 撤销 "valid data"。
- Lane 数为静态参数，设计/初始配置时固定，不得动态改变；N-lane 能力的 host 必须能用 1…N 中任意 lane 数工作；多 lane 共用单一公共 clock。
- Lane 模块最低要求（D-PHY CIL 代码）：
  - Command Mode host：Data Lane CIL-MFAA（HS-TX, LP-TX, LP-RX, LP-CD），Clock CIL-MCNN（HS-TX, LP-TX）；
  - Command Mode peripheral：CIL-SFAA（HS-RX, LP-RX, LP-TX, LP-CD），Clock CIL-SCNN；
  - Video Mode host/peripheral：CIL-MFAN（HS-TX, LP-TX）/ CIL-SFAN（HS-RX, LP-RX）。
  - 双向 Link 的 Lane 0 必须支持反向 Escape Mode（LPDT、ACK、TE Trigger）；所有 Trigger message 走 Lane 0。

## 4. 包结构（核心）

### 4.1 总体规则

- Short Packet 固定 4 字节；Long Packet 6 ~ 65,541 字节（payload 0 ~ 65535 字节）。
- 字节序：每个字节 LSB 先发送；多字节字段（WC、Checksum）低字节先发。示例：DI=0x29、WC=0x0001、ECC=0x06、Data=0x01、CRC=0x1E0E（线上字节序 29 01 00 06 01 0E 1E）。
- 一次 HS/LP transmission 可级联多个 packet；HS 模式下 packet 间若有时间空隙则必须拆成独立 transmission（各带 SoT/EoT）；LP transmission 无此限制。

### 4.2 Long Packet

```
| DI (1B) | WC LSB (1B) | WC MSB (1B) | ECC (1B) | Data 0 … Data WC-1 (WC B) | CRC LSB (1B) | CRC MSB (1B) |
|<------ 32-bit Packet Header (PH) ------>|<-- Payload WC bytes -->|<- 16-bit Packet Footer ->|
```

- DI：DI[7:6]=Virtual Channel（0–3），DI[5:0]=Data Type。
- WC（16-bit）：payload 字节数；接收端靠 WC 数到 packet 结束——协议无 start/end 同步码，header 必须显式给出长度。
- ECC（8-bit）：保护整个 4 字节 header，可纠 1 bit、检 2 bit。
- Checksum（16-bit CRC）：host 发送 Long packet 必须计算并发送；peripheral 可选——不支持时反向必须发 0x0000 占位；payload 长度为 0 时 Checksum=0xFFFF。

### 4.3 Short Packet

```
| DI (1B) | Data 0 (1B) | Data 1 (1B) | ECC (1B) |     （无 Packet Footer，共 4 字节）
```

用于大多数 Command Mode 命令及 H/V Sync 等事件。单参数命令参数放 Data 0，Data 1 置 0x00。

### 4.4 ECC（Hamming-modified code）

- 5+1 bit Hamming 修改码 (30,24)：纠 1 bit + 检 2 bit；保护 24 bit header 数据。header 固定 24 bit，P7=P6=0。
- 发送端 parity 方程（D0=header 第 0 bit=DI 的 LSB；已用规范示例逐一复算验证）：

```
P7 = 0
P6 = 0
P5 = D10^D11^D12^D13^D14^D15^D16^D17^D18^D19^D21^D22^D23
P4 = D4^D5^D6^D7^D8^D9^D16^D17^D18^D19^D20^D22^D23
P3 = D1^D2^D3^D7^D8^D9^D13^D14^D15^D19^D20^D21^D23
P2 = D0^D2^D3^D5^D6^D9^D11^D12^D15^D18^D20^D21^D22
P1 = D0^D1^D3^D4^D6^D8^D10^D12^D14^D17^D20^D21^D22^D23
P0 = D0^D1^D2^D4^D5^D7^D10^D11^D13^D16^D20^D21^D22^D23
```

- 接收端：syndrome S = 收到的 ECC ^ 对收到 24bit 重算的 ECC；S=0 无错；S 命中 syndrome 矩阵（64 项，D0→0x07、D1→0x0B、D2→0x0D、D3→0x0E、D4→0x13、D5→0x15、D6→0x16、D7→0x19、…）则对应数据位取反纠正；S 为单位矩阵行则错在 parity 位本身；S 无法识别 → multi-bit error，置 Multi-bit Error Flag。
- 验证过的规范示例：DI=0x37、WC=0x01F0 → ECC=0x3F；DI=0x29/WC=0x0001 → 0x06；EoTp（08 0F 0F）→ 0x01；0x0D/0x0001 → 0x1E；0x1D/0x0001 → 0x0D。
- ECC 义务：host 永远生成并发送 ECC；peripheral 两个方向都要支持；host 还须能针对旧版不支持 ECC 的 peripheral 关闭 ECC 检查。

### 4.5 Checksum（CRC-16）

- 16-bit CRC，生成多项式 x^16 + x^12 + x^5 + x^0（0x1021，反射实现 0x8408），初值 0xFFFF，payload 按 LSB first 逐比特进入，算完后 CRC 低字节先发。只检错不纠错。
- 测试向量（已复算吻合）：`00`→0x0F87；`01`→0x1E0E；24 字节流 `FF 00 00 00 1E F0 1E C7 4F 82 78 C5 82 E0 8C 70 D2 3C 78 E9 FF 00 00 01`→0xE569。
- 规范编辑瑕疵（引用时加校注）：① Annex B 代码注释把多项式写成 x^16+x^15+x^5+x^0，与正文矛盾，实测 x^12 版才能复现全部向量；② §8.8.18 的 36-bit 示例 packet CRC 印为 0x1C4C，实算为 0xC1C4，疑为排版错误。

## 5. Data Type 完整列表

### 5.1 DT 编码约束

- DT[3:0]=0000 或 1111（0xX0、0xXF）禁止使用；编码保证每个 packet 前 4 bit 内至少有一次跳变——EoT 序列是全 1 或全 0，接收端可据此在 4 bit 内区分"新 packet 开始"与"EoT"。

### 5.2 Processor-sourced（host→peripheral）

Video Mode 同步/控制（均 Short）：

| DT (hex) | DT (binary) | 含义 |
|---|---|---|
| 0x01 | 00 0001 | Sync Event, V Sync Start (VSS) |
| 0x11 | 01 0001 | Sync Event, V Sync End (VSE) |
| 0x21 | 10 0001 | Sync Event, H Sync Start (HSS) |
| 0x31 | 11 0001 | H Sync End (HSE) |
| 0x08 | 00 1000 | End of Transmission packet (EoTp) |
| 0x02 | 00 0010 | Color Mode (CM) Off Command |
| 0x12 | 01 0010 | Color Mode (CM) On Command |
| 0x22 | 10 0010 | Shut Down Peripheral Command |
| 0x32 | 11 0010 | Turn On Peripheral Command |

Command Mode 通用/DCS：

| DT (hex) | 含义 | 长度 |
|---|---|---|
| 0x03 / 0x13 / 0x23 | Generic Short WRITE，0/1/2 参数 | Short |
| 0x04 / 0x14 / 0x24 | Generic READ，0/1/2 参数 | Short |
| 0x05 / 0x15 | DCS Short WRITE，0/1 参数 | Short |
| 0x06 | DCS READ，无参数 | Short |
| 0x37 | Set Maximum Return Packet Size | Short |
| 0x09 | Null Packet, no data | Long |
| 0x19 | Blanking Packet, no data | Long |
| 0x29 | Generic Long Write | Long |
| 0x39 | DCS Long Write / write_LUT | Long |

像素流（均 Long，Video Mode）：

| DT (hex) | 格式 |
|---|---|
| 0x0C | Loosely Packed Pixel Stream, 20-bit YCbCr 4:2:2 |
| 0x1C | Packed Pixel Stream, 24-bit YCbCr 4:2:2（每分量 12 bit） |
| 0x2C | Packed Pixel Stream, 16-bit YCbCr 4:2:2 |
| 0x0D | Packed Pixel Stream, 30-bit RGB 10-10-10 |
| 0x1D | Packed Pixel Stream, 36-bit RGB 12-12-12 |
| 0x3D | Packed Pixel Stream, 12-bit YCbCr 4:2:0 |
| 0x0E | Packed Pixel Stream, 16-bit RGB 5-6-5 |
| 0x1E | Packed Pixel Stream, 18-bit RGB 6-6-6（packed） |
| 0x2E | Loosely Packed Pixel Stream, 18-bit RGB 6-6-6（3 字节/像素） |
| 0x3E | Packed Pixel Stream, 24-bit RGB 8-8-8 |

注意：v1.1 中 0x3E=24-bit RGB888、0x2E=18-bit loosely packed、RGB565 是 0x0E。

### 5.3 EoTp（DT=0x08）

- 固定格式：DT=0b001000、VC 固定 0b00、Payload=0x0F0F、ECC=0x01；多 lane 时 EoTp 字节同样按 lane 分发。
- 作用：协议层标示 HS transmission 结束，与 PHY 层 EoT 序列解耦，增强鲁棒性；代价是每次 transmission 多 4 字节。
- 兼容性：v1.1 设备必须具备 EoTp 生成/检测能力，同时必须提供 enable/disable 手段兼容旧设备。HS 模式 shall 发送；LP 模式 should not 发送；接收端 HS/LP 都 shall 检测。

### 5.4 Peripheral-sourced（peripheral→host）

| DT (hex) | 含义 | 长度 |
|---|---|---|
| 0x02 | Acknowledge and Error Report | Short |
| 0x08 | EoTp | Short |
| 0x11 / 0x12 | Generic Short READ Response，返回 1/2 字节 | Short |
| 0x1A | Generic Long READ Response | Long |
| 0x1C | DCS Long READ Response | Long |
| 0x21 / 0x22 | DCS Short READ Response，返回 1/2 字节 | Short |

（§8.10.5 正文把 DCS Short Read Response 的 DT 误印为 01 0001/01 0010，应为 10 0001/10 0010，系规范笔误。）

## 6. Video Mode 操作（核心）

### 6.1 三种 packet sequence

host 必须全部支持；Video Mode peripheral 至少支持一种。

- **Non-Burst Mode with Sync Pulses**：精确重建 DPI 型时序——像素按 DPI 速率发送，sync 脉宽精确传递（每个 sync 发 Start+End 一对短包）。HSA/HBP/HFP 用 Blanking Packet（0x19）填充；若时间充裕也可用定时 LP-11 代替 Blanking Packet 省电。
- **Non-Burst Mode with Sync Events**：简化版——每个 sync 只发 Start（单个 Sync Event），peripheral 自行重建脉宽；像素仍按 DPI 速率发。
- **Burst Mode**：RGB 像素时间压缩成高速 burst 发出（peripheral 需 line buffer），每行腾出更多时间进 LP 省电或复用链路；burst 后总线可留 HS 发 blanking packet 或进 LP。若 peripheral 借此时段反向 LP 发送，其时长必须受限以免 line buffer underflow。

### 6.2 帧/行结构与消隐规则

- 一帧时间 = tL × (VSA + VBP + VACT + VFP)，tL 为行时间（= tHSA + tHBP + tHACT + tHFP）。
- 每帧第一行以 VSS 开始；其余所有行以 VSE 或 HSS 开始。VSS 隐含"VSA 第一行的 HSS"；VSE 隐含"VSA 最后一行的 HSS"。
- 正常一行 RGB 用一个 packet 发完整 scanline；必要时一行可拆多个 packet，但单个像素不得跨包拆分。
- BLLP（Blanking or Low-Power Interval）期间链路可做：① 保持 Idle（LP-11）；② Escape Mode 发非视频 packet；③ HS Mode 发非视频 packet；④ 前次传输以 BTA 结束时 peripheral 用 Escape Mode 回传；⑤ 用不同 VC ID 向另一 peripheral 发 packet。
- host 每帧至少应结束一次 HS 传输并回到 LP（LPM）；推荐每行水平消隐期都回一次 LP。
- HBP/HFP：peripheral 时序规格最小值为 0 时 Blanking Packet may 省略；最大值为 0 时 shall 省略。

### 6.3 时序参数（peripheral 厂商必须填写，host 必须满足）

| 参数 | 含义 | 单位 |
|---|---|---|
| brPHY | 所有 lane 总比特率 | Mbps |
| tL | 行时间 | s |
| tHSA / tHBP / tHACT / tHFP | 行同步/后沿/图像数据/前沿时间 | s |
| HACT | 每行有效像素数 | pixels |
| VSA / VBP / VACT / VFP | 场同步/后沿/有效行/前沿行数 | lines |

## 7. Command Mode 与双向传输

### 7.1 关键命令细节

- Generic Short WRITE (0x03/0x13/0x23)：DT[5:4] 表参数个数；单参数时 Data1=0x00。
- Generic READ (0x04/0x14/0x24)：必须是 transmission 中唯一或最后一个 packet，之后 host 发 BTA。peripheral 响应：无错→返回 READ 数据；有错→Acknowledge and Error Report；单 bit ECC 错已纠正→READ 数据 + 追加 Error Report。返回数据超过 Set Maximum Return Packet Size 时须多次传输。
- DCS Short WRITE (0x05/0x15)：DI 后第一字节即 DCS Command Byte。后随 BTA 时，双向 peripheral 无错回 ACK Trigger Message，有错回 Error Report；单向 Video Mode 模组忽略 BTA。
- DCS READ (0x06)：规则同 Generic READ。
- DCS Long Write/write_LUT (0x39)：DI + 2B WC + ECC + DCS Command Byte + (WC−1) 字节 payload + 2B Checksum。
- Set Maximum Return Packet Size (0x37)：限定回传 Long packet 最大 payload；上电/Reset 后默认值为 1；单向 peripheral 忽略。
- Null Packet (0x09, Long)：让 Data Lane 保持 HS 发哑数据，peripheral 不捕获 payload，但 ECC/Checksum 照常生成。
- Blanking Packet (0x19, Long)：承载消隐期时序；payload 可为任意数据。
- Color Mode On/Off (0x12/0x02)：Video Mode 模组进入/退出低色彩省电模式。Shutdown Peripheral (0x22)：关显示省电（接口保持供电）；Turn On Peripheral (0x32)：恢复正常显示。

### 7.2 BTA

- BTA 是 token-passing：host 在 transmission 最后一个 packet 期间向 PHY 置 TurnRequest，PHY 在 EoT 后发 BTA；peripheral 获得总线后发一个或多个 packet，再以自己的 TurnRequest 还权。每次 peripheral→host transaction 之后都必须 BTA 还权。
- 反向只用 Lane 0 + LP Mode；反向 packet 结构与正向相同（peripheral 不算 Checksum 时 PF=0x0000）。
- host 一次 transmission 中最多只能有一个需要 peripheral 响应的 packet；带 BTA 的非 READ 命令 → 无错回 ACK Trigger（单字节 00100001，first-bit→last-bit），有错回 4 字节 Acknowledge and Error Report。
- peripheral→host 四类传输：TE Trigger、ACK Trigger、Acknowledge and Error Report、READ Response。
- Acknowledge and Error Report 固定打 VC=0b00。

## 8. Tearing Effect (TE) 报告

- DSI 无 peripheral→host 中断能力，host 要么轮询（DCS get_scan_line），要么长期让出总线等 TE。
- TE 由 DCS 命令 set_tear_on / set_tear_scanline / set_tear_off 控制。set_tear_on 以 DT=0x15 发送，set_tear_scanline 以 DT=0x39 发送；该 transmission 以 BTA 结束，模组回普通 ACK 还权。
- 要使能 TE 上报，host 必须在不附带任何 DSI 命令的情况下再次 BTA 让出总线，然后最多等待一个视频帧周期——期间 host 不能发任何新命令。
- TE 事件发生时模组流程：发 LP Escape Mode 序列 → 发 TE Trigger message 字节 01011101（first-bit→last-bit）→ 还权 host。该 Trigger 为 TE 专用。

## 9. 电源管理

- DSI v1.1 本身不定义 ULPS 进入/退出流程（属 D-PHY）。
- 系统上电初始化（§5.7）：上电后 host 必须在 TINIT 期间向所有 Lane 持续驱动 LP-11；peripheral 检测到至少 TINIT 长的 LP-11 之前忽略一切链路状态。peripheral 可用 ±30% 精度 R-C timer 检测。host 的 tINIT_MASTER 应编程为 > tINIT_SLAVE + tINTERNAL_DELAY。
- Clock 管理（§5.6）：所有 DSI 收发器必须支持 continuous clock，可选 non-continuous；由 host 控制。
- 省电命令：Color Mode On/Off、Shutdown/Turn On Peripheral、局部 frame buffer 自刷新、Burst Mode 腾出 LP 时间、BLLP 进 LP-11。
- Peripheral Reset：host 发 Reset Entry command 后用可选 PR_TO 定时器等待复位完成。

## 10. Error 报告

### 10.1 低层协议错误（PHY 检测，peripheral 存为状态位）

1. SoT Error：前导序列单 bit 错容错，检出后可继续但数据可信度降低；
2. SoT Sync Error：前导损坏到无法同步，不得执行任何 WRITE；
3. EoT Sync Error：EoT 时最后一字节不对齐字节边界；
4. Escape Mode Entry Command Error：Escape 进入命令不被识别；
5. LP Transmission Sync Error：LP 传输结束数据未对齐字节边界；
6. False Control Error：LP-10 后无合法 escape/turnaround 序列，或 LP-01 后无 LP-00 bridge。

### 10.2 争用与定时器

- LP-CD 检测 LP High Fault / LP Low Fault（双方同时驱动）；common-mode fault 只能靠定时器恢复。
- 必需定时器：HRX_TO（peripheral HS RX 超时）、HTX_TO（host HS TX 超时，应比 HRX_TO 长）、LTX-P_TO（peripheral LP TX 占线超时）、LRX-H_TO（host LP RX 超时，须 > LTX-P_TO）。
- 可选定时器：TA_TO、PR_TO、PRESP_TO（分 BTA / LPDT READ / LPDT WRITE / HS READ / HS WRITE 五种取值）。
- peripheral 检出 HRX_TO 或 LTX-P_TO 超时 → Error Report 置 Peripheral Timeout Error（bit 5）；检出 LP High/Low Fault → 置 Contention Detected（bit 7）。

### 10.3 Acknowledge and Error Report packet（DT=0x02，4 字节 Short）

- 格式：Byte0=DI（VC + 0x02）、Byte1=Error Report bits 0–7、Byte2=bits 8–15、Byte3=ECC。
- Error Report 位定义：

| Bit | 含义 | Bit | 含义 |
|---|---|---|---|
| 0 | SoT Error | 8 | ECC Error, single-bit（已纠正） |
| 1 | SoT Sync Error | 9 | ECC Error, multi-bit |
| 2 | EoT Sync Error | 10 | Checksum Error（仅 Long packet） |
| 3 | Escape Mode Entry Command Error | 11 | DSI Data Type Not Recognized |
| 4 | Low-Power Transmit Sync Error | 12 | DSI VC ID Invalid |
| 5 | Peripheral Timeout Error | 13 | Invalid Transmission Length |
| 6 | False Control Error | 14 | Reserved |
| 7 | Contention Detected | 15 | DSI Protocol Violation |

- 错误跨多次传输累积，直到某次 BTA 统一上报，上报后 Error Register 全部清零；每次 BTA 只回一个 ACK 或一个 Error Report。
- 响应规则：单 bit ECC 错已纠正 → READ 照常回数据 + 追加 Error Report（bit 8）；multi-bit ECC 错 → 不执行命令只回 Error Report（bit 9）；SoT/SoT Sync/VC invalid/协议违规/命令不识别 → 只回 Error Report；EoT Sync/LP Sync/Checksum 错 → 只回 Error Report。
- 遇到不识别 Data Type 或 multi-bit ECC 错后，接收端失去包界，从出错点丢弃该次 transmission 剩余全部内容。

## 11. 像素数据格式（字节排列）

通用规则：分量顺序 R→G→B（YCbCr 按 BT.656：Cb、Y、Cr、Y）；分量内 LSB 先发；标清 BT.601、高清 BT.709。

| DT | 格式 | 字节排列要点 | WC 约束 |
|---|---|---|---|
| 0x0E | RGB 5-6-5（16bpp） | 2 字节/像素：byte0={G[2:0],R[4:0]}、byte1={B[4:0],G[5:3]} | 行宽 2 字节倍数 |
| 0x1E | RGB 6-6-6 packed（18bpp） | 4 像素=9 字节紧凑位流 | 行宽 4 像素倍数，不足补 fill pixel |
| 0x2E | RGB 6-6-6 loosely packed | 3 字节/像素，每字节有效位 [7:2]，[1:0] 忽略 | 行宽 3 字节倍数 |
| 0x3E | RGB 8-8-8（24bpp） | 3 字节/像素：byte0=R、byte1=G、byte2=B | 行宽 3 字节倍数 |
| 0x0D | RGB 10-10-10（30bpp） | 4 像素=15 字节；示例单像素全 1 packet = `0D 01 00 1E FF FF FF 3F B4 36` | 行宽 15 字节倍数 |
| 0x1D | RGB 12-12-12（36bpp） | 2 像素=9 字节 | — |
| 0x0C | YCbCr 4:2:2 20bpp loosely | 每分量 10 bit 放 12 bit 字段；2 像素=6 字节 | WC 必须非零且 6 的倍数 |
| 0x1C | YCbCr 4:2:2 24bpp | 每分量 12 bit；2 像素=6 字节 | WC 6 的倍数 |
| 0x2C | YCbCr 4:2:2 16bpp | 每分量 8 bit；2 像素=4 字节，Cb0 Y0 Cr0 Y1 | WC 4 的倍数 |
| 0x3D | YCbCr 4:2:0 12bpp | 奇数行发 Cb+Y、偶数行发 Cr+Y；2 像素=3 字节 | WC 3 的倍数 |

合规要求：Video Mode host 必须实现 16bpp、18bpp packed、18bpp loosely packed、24bpp 四种；peripheral 至少一种。30/36 bpp 用 sRGB 色彩空间。

## 12. 时序与性能参数

- LP 时钟匹配：host 与 peripheral 的 Escape Mode 频率比不得超过 3:2；host LP 时钟频率须为 peripheral 的 67% ~ 150%。
- TINIT：上电初始化期（定义在 D-PHY）；peripheral 用 ±30% RC timer 检测。
- 帧周期 = tL×(VSA+VBP+VACT+VFP)；每帧至少一次回 LP（LPM），推荐每行消隐期回 LP。
- 超时定时器：HRX_TO、HTX_TO、LTX-P_TO、LRX-H_TO、TA_TO、PR_TO、PRESP_TO。
- 合规分辨率清单：QQVGA 160×120、QCIF 176×144、QCIF+ 176×208/220、QVGA 320×240、CIF 352×288、CIF+ 352×416/440、(1/2)VGA 320×480、(2/3)VGA 640×320、VGA 640×480、WVGA 800×480、SVGA 800×600、XVGA 1024×768。
- 数据流控：协议层与 PHY 之间无握手反压，packet 一旦开始必须完整不间断发完；两端协议层与缓冲带宽须 ≥ PHY 带宽。

## 13. v1.1 相对旧版的新增内容

| 日期 | 版本 | 变更 |
|---|---|---|
| 2006-04-19 | v1.00a | 首个 MIPI Board 批准发布 |
| 2008-02-21 | v1.01.00 | 大改：新增系统上电初始化、EoTp、Short Write、DCS Write、Generic Read/Long Write、Color Mode Command、ECC 要求 |
| 2010-06-28 | v1.02.00 | 新增 30bpp/36bpp、隔行视频 VC 用法澄清、可上报错误更新 |
| 2012-04-06 | v1.1 | 新增立体显示格式（SDF）支持 |

- 3D 支持落点：帧首 VSS 短包携带 payload——Data 0 bit3=1 表示存在 3D Control payload；Data 1 内含 3DMODE[1:0]、3DFMT[1:0]、3DVSYNC、3DL/R。
- 隔行视频：建议第一 field VC=0b00、第二 field VC=0b01。

## 附：关键验证锚点

- EoTp 固定字节 `08 0F 0F 01`；TE Trigger `01011101`；ACK Trigger `00100001`。
- ECC 测试向量：DI=0x37/WC=0x01F0→0x3F；DI=0x29/WC=0x0001→0x06；EoTp header→0x01；0x0D/0x0001→0x1E；0x1D/0x0001→0x0D。
- CRC 测试向量：`00`→0x0F87；`01`→0x1E0E；24 字节流→0xE569。
- 30bpp 完整示例包 `0D 01 00 1E FF FF FF 3F B4 36`。
- 提醒：① Annex B 注释多项式笔误（应为 x^16+x^12+x^5+x^0）；② §8.8.18 示例 CRC 疑误（实算 0xC1C4，规范印 0x1C4C）；③ ULPS 流程不在 DSI v1.1 范围（属 D-PHY）。
