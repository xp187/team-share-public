# MIPI D-PHY v2.0 规范技术总结（数字验证视角）

> 来源：`C:\Users\xiapeng2\Desktop\MIPI\mipi_d-phy_specification_v2-0.pdf`（全文 7939 行已通读：正文 12 章、3 附录、80 图、46 表）。
> 面向数字 IC 验证工程师：报告只使用协议/状态机/时序参数/编码内容；电气特性（电压、阻抗、抖动预算等）不需要，仅在本总结末尾归档备查。

## 1. 文档结构

- 文档全称：Specification for D-PHY, Version 2.0，23 November 2015，MIPI Board Adopted 08 March 2016。v2.0 为首个 Board adopted v2.0 release。
- 正文 12 章：1 Introduction；2 Terminology；3 References（D-PHY v1.0、C-PHY v1.0）；4 D-PHY Overview；5 Architecture；6 Global Operation（SoT/EoT、Turnaround、Escape、时钟、时序参数、校准、初始化——核心协议章）；7 Fault Detection；8 Interconnect and Lane Configuration；9 Electrical Characteristics；10 High-Speed Data-Clock Timing；11 Regulatory；12 Built-In HS Test Mode（informative）。
- 附录：A 逻辑 PPI 接口；B 互连设计指南；C 8b9b 线路编码（normative）。
- 目标 BER < 10⁻¹²。

## 2. 总体定位与架构

- D-PHY 是源同步、高速、低功耗 PHY，"D" 来自罗马数字 500（早期约 500 Mbit/s 量级）。主要用于移动端摄像头/显示屏互连。
- PHY Configuration = 1 条 Clock Lane + 1 条或多条 Data Lane；最少 4 根线，N 条 Data Lane 需要 2*(N+1) 根线。
- 每条 Lane 两侧 Lane Module 经两线点对点互连。Lane Module 内含：HS-TX/HS-RX（差分）、LP-TX/LP-RX/LP-CD（单端、竞争检测）、CIL（Control and Interface Logic，与协议层 PPI 对接）。
- HS 信号摆幅约 200 mV，LP 约 1.2 V（电气仅作背景，报告不展开）。含 HS-TX 必含 LP-TX，含 HS-RX 必含 LP-RX。LP-RX 上电即常开监听；LP-CD 仅双向 Lane 需要。
- 主从关系：Master 发送 HS DDR 时钟并作为主要数据源（Forward 方向 = 时钟方向）；Slave 可反向发送。**HS 单向（仅 Forward）、LP 可双向**；反向 HS 带宽为正向 1/4；方向控制用令牌传递（token passing）。Clock Lane 永远 Forward。
- Lane 类型（CIL 命名）：Unidirectional Data Lane（CIL-MFXN/SFXN）、Bi-directional Data Lane（无 HS 反向 MFXY/SFXY；含 HS 反向 MRXX/SRXX）、Clock Lane（MCNN/SCNN，仅支持 ULPS，无常规 Escape mode）。
- 所有 Data Lane 必须支持 Forward HS 与 Forward Escape（至少 ULPS+Trigger）；反向 Escape、反向 HS、LPDT 均为可选。
- 高频时钟由 PHY 外部 Clock Multiplier Unit（PLL）产生。

## 3. Lane 状态与线状态

### 3.1 状态编码（Table 2）

| 状态码 | Dp 电平 | Dn 电平 | HS Burst Mode | Control Mode | Escape Mode |
|---|---|---|---|---|---|
| HS-0 | HS Low | HS High | Differential-0 | N/A | N/A |
| HS-1 | HS High | HS Low | Differential-1 | N/A | N/A |
| LP-00 | LP Low | LP Low | N/A | Bridge | Space |
| LP-01 | LP Low | LP High | N/A | HS-Rqst | Mark-0 |
| LP-10 | LP High | LP Low | N/A | LP-Rqst | Mark-1 |
| LP-11 | LP High | LP High | N/A | Stop | N/A（出现即返回 Control Stop） |

- HS 传输期间 LP 接收器始终把差分 HS 状态看作 LP-00。
- Stop 状态（LP-11）具有中心地位：线上出现 Stop 达到最小要求时间，PHY 状态机无论之前处于何状态都必须回到 Stop。
- 所有 LP 状态持续期 ≥ TLPX（min 50 ns）；Dp/Dn 异或可重建 LP 时钟。

### 3.2 状态转换（Control mode 下从 Stop 出发的三种请求）

- 进入 HS：LP-11 → LP-01（HS-Rqst）→ LP-00（Bridge），随后进入 HS 模式，直到收到 LP-11。
- 进入 Escape：LP-11 → LP-10（LP-Rqst）→ LP-00 → LP-01 → LP-00，最后 Bridge 后进入 Escape（Space 态）。
- Turnaround：LP-11 → LP-10 → LP-00 → LP-10 → LP-00。
- 任一序列中若在最终 Bridge 前检测到 LP-11，则中止并回到/等待 Stop。

## 4. High-Speed（HS）模式

### 4.1 数据速率档位（v2.0 核心扩展）

- 基础范围 80 Mbps ~ 1.5 Gbps/lane（无需 deskew）；
- 支持 deskew 校准后可达 2.5 Gbps；
- 再加均衡（de-emphasis）可达 4.5 Gbps。
- 强制要求：>1.5 Gbps 必须支持 deskew；>2.5 Gbps 必须支持均衡且 SSC 必须可用。LP 模式最大 10 Mbps。

### 4.2 DDR 时钟与数据关系

- Clock Lane 发送 DDR（半速率）时钟，与数据成正交相位：时钟上升沿位于数据比特中心，数据在时钟上升沿和下降沿均被采样。1 个 DDR 时钟周期 = 2 个瞬时 UI。
- TX 必须保证 burst 第一个 payload bit 期间出现时钟上升沿。
- UIINST max = 12.5 ns（对应最低 80 Mbps）；ΔUI = ±10%。

### 4.3 SoT / EoT 序列

**SoT（TX 侧）**：
1. 驱动 Stop（LP-11）；
2. 驱动 HS-Rqst（LP-01）持续 TLPX；
3. 驱动 Bridge（LP-00）持续 THS-PREPARE；
4. 使能 HS 驱动器、关闭 LP 驱动器，驱动 HS-0 持续 THS-ZERO；
5. 在时钟上升沿插入 HS Sync 序列 `00011101`；
6. 继续发送 payload。

**SoT（RX 侧）**：观察 LP-11→LP-01→LP-00；经 TD-TERM-EN 使能端接；等待 THS-SETTLE 忽略过渡；搜索并锁定 Leader 序列 `011101`（允许任意单比特错误），之后接收 payload。

**EoT（TX 侧）**：发完 payload 后立即翻转差分状态并保持 THS-TRAIL，然后关 HS-TX、开 LP-TX，驱动 Stop（LP-11）持续 THS-EXIT。
**EoT（RX 侧）**：检测线离开 LP-00 进入 LP-11 并断开端接；用 THS-SKIP 忽略末段过渡比特，回溯确定最后一个有效字节。
- HS burst 期间 Clock Lane 必须处于 HS 模式提供 DDR 时钟；burst 载荷为整数个字节、最少 1 字节、无 PHY 级上限。

## 5. Low-Power（LP）模式与 Escape Mode

### 5.1 Escape Mode

- 进入序列：LP-11 → LP-10 → LP-00 → LP-01 → LP-00；最终 Bridge 后进入 Escape（Space 态）。随后 TX 必须发送 8-bit entry command。
- 位编码：Spaced-One-Hot——每个 Mark（Mark-0=LP-01 表 0，Mark-1=LP-10 表 1）后必须跟一个 Space（LP-00）；退出前最后一个相位必须是不带 Space 的 Mark-1。时钟 = Dp ⊕ Dn。Escape mode 不依赖 Clock Lane。Stop（LP-11）立即退出 Escape 回到 Control mode；不识别的命令被忽略并等待 Stop。
- Escape Entry Codes（Table 8）：

| 命令 | 类型 | 位模式（发送顺序） | 常用十六进制（先发位=LSB） |
|---|---|---|---|
| Low-Power Data Transmission (LPDT) | mode | 11100001 | 0x87 |
| Ultra-Low Power State (ULPS) | mode | 00011110 | 0x78 |
| Undefined-1 | mode | 10011111 | 0xF9 |
| Undefined-2 | mode | 11011110 | 0x7B |
| Reset-Trigger [Remote Application] | Trigger | 01100010 | 0x46 |
| Entry sequence for HS Test Mode | Trigger | 01011101 | 0xBA |
| Unknown-4 | Trigger | 00100001 | 0x84 |
| Unknown-5 | Trigger | 10100000 | 0x05 |

- LPDT：入口命令后跟 Spaced-One-Hot 数据，自定时、可变速率；Space 态可暂停；Mark-1 + Stop 结束。
- ULPS：发送 ULPS 命令后 Lane 进入超低功耗态，线保持 Space（LP-00）；退出 = Mark-1 持续 TWAKEUP（1 ms）+ Stop（LP-11）。

### 5.2 Bus Turnaround（BTA，双向 Lane）

原 TX 侧流程（令牌移交）：
1. LP-11（Stop）→ 2. LP-10 持续 TLPX → 3. LP-00 持续 TLPX → 4. LP-10 持续 TLPX → 5. LP-00（Bridge）持续 TTA-GO = 4·TLPX → 6. 停止驱动，用 LP-RX 观察确认。
原 RX 侧（接管方）：观察到 Bridge 后等待 TTA-SURE（TLPX ~ 2·TLPX），然后驱动 LP-00 持续 TTA-GET = 5·TLPX，再驱动 LP-10 持续 TLPX，最后 LP-11 持续 TLPX 完成。
两侧 TLPX 之比约束：TLPX(MASTER)/TLPX(SLAVE) ∈ [2/3, 3/2]。Master/Slave 身份不因 Turnaround 改变。

## 6. Clock Lane

- 仅支持 Stop / HS 时钟发送 / ULPS 三种主状态，无常规 Escape mode。
- Clock Lane ULPS 进入：LP-11 → LP-10（TX-ULPS-Rqst，TLPX）→ LP-00（TX-ULPS）。退出：Mark-1（LP-10，TX-ULPS-Exit）持续 TWAKEUP = 1 ms → LP-11。
- HS 时钟启动：LP-11 → LP-01（TLPX）→ LP-00（TCLK-PREPARE）→ HS-0（TCLK-ZERO）→ DDR 时钟先跑 TCLK-PRE（≥8 UI）才允许任何 Data Lane 启动。
- HS 时钟停止：最后一个 Data Lane 转入 LP 后，时钟继续 TCLK-POST（≥60 ns+52·UI）并以 HS-0 结束，再驱动 HS-0 持续 TCLK-TRAIL（≥60 ns），然后 LP-11（THS-EXIT）。RX 侧以 TCLK-MISS（≤60 ns）超时检测时钟消失。
- 规范允许 Clock Lane 在两次 burst 之间回到 LP 模式（非连续时钟用法）；协议只能在所有 Data Lane 都无 HS 活动时停时钟。连续与非连续时钟均通过同一套启动/停止过程实现。

## 7. 全局时序参数表（Table 14，数字验证必查）

| 参数 | 定义 | Min | Max | 单位 | 侧 |
|---|---|---|---|---|---|
| TCLK-MISS | RX 检测时钟消失并关闭 HS-RX 的超时 | — | 60 | ns | RX |
| TCLK-POST | 最后 Data Lane 转 LP 后 TX 继续发 HS 时钟的时间 | 60 ns + 52·UI | — | ns | TX |
| TCLK-PRE | 任何 Data Lane 启动前 TX 先驱动 HS 时钟的时间 | 8 | — | UI | TX |
| TCLK-PREPARE | HS 传输前驱动 Clock Lane LP-00 的时间 | 38 | 95 | ns | TX |
| TCLK-SETTLE | HS RX 忽略时钟跳变的窗口 | 95 | 300 | ns | RX |
| TCLK-TERM-EN | Clock Lane RX 使能端接的时间 | Dn 达 VTERM-EN | 38 | ns | RX |
| TCLK-TRAIL | 最后 payload 时钟位后驱动 HS-0 的时间 | 60 | — | ns | TX |
| TCLK-PREPARE+TCLK-ZERO | LP-00 + 启动时钟前 HS-0 的总时间 | 300 | — | ns | TX |
| TD-TERM-EN | Data Lane RX 使能端接的时间 | Dn 达 VTERM-EN | 35 ns + 4·UI | ns | RX |
| TEOT | THS-TRAIL 起点到 HS burst 后 LP-11 起点 | — | 105 ns + n·12·UI | ns | n=1 正向 / n=4 反向 |
| THS-EXIT | HS burst 后驱动 LP-11 的时间 | 100 | — | ns | TX |
| THS-PREPARE | HS 传输前驱动 Data Lane LP-00 的时间 | 40 ns + 4·UI | 85 ns + 6·UI | ns | TX |
| THS-PREPARE+THS-ZERO | LP-00 + 发 Sync 前 HS-0 的总时间 | 145 ns + 10·UI | — | ns | TX |
| THS-SETTLE | HS RX 忽略数据跳变的窗口 | 85 ns + 6·UI | 145 ns + 10·UI | ns | RX |
| THS-SKIP | RX burst 后回溯忽略的窗口 | 40 | 55 ns + 4·UI | ns | RX |
| THS-TRAIL | 最后 payload 位后驱动翻转差分态的时间 | max(n·8·UI, 60 ns + n·4·UI) | — | ns | TX |
| TINIT | 初始化 Stop 时长 | 100 | — | µs | TX/RX |
| TLPX | 任一 LP 状态周期长度 | 50 | — | ns | TX |
| TLPX 比值 | TLPX(MASTER)/TLPX(SLAVE) | 2/3 | 3/2 | — | — |
| TTA-GET | Turnaround 中新 TX 驱动 Bridge 的时间 | 5·TLPX | — | ns | — |
| TTA-GO | Turnaround 中释放控制前驱动 Bridge 的时间 | 4·TLPX | — | ns | — |
| TTA-SURE | 新 TX 在 LP-10 后、驱动 Bridge 前的等待 | TLPX | 2·TLPX | ns | — |
| TWAKEUP | ULPS 退出时 Mark-1 的驱动时长 | 1 | — | ms | TX |

- Lane 间静态 skew：≤1.5 Gbps 时 Data Lane 与 Clock Lane 延迟差 < UI/50。

## 8. v2.0 新特性

规范明确点名的新增能力：SSC（扩频时钟）、Transmit Equalization（de-emphasis）、Deskew。

1. **速率档位提升**：≤2.5 Gbps → 4.5 Gbps/lane；>1.5 Gbps 必须 deskew、>2.5 Gbps 必须均衡+SSC。
2. **HS Skew Calibration（deskew，Section 6.12）**：
   - >1.5 Gbps 时正常 HS 传输前必须先发送 initial deskew 序列；≤1.5 Gbps 时 initial deskew 可选；periodic deskew 任何速率均可选。
   - 序列结构：SoT 同普通 burst，但 Sync pattern = 全 1（16'hFFFF），持续 TSKEWCAL-SYNC = 16 UI；随后 payload 为 `01010101…` 时钟 pattern：initial ≥ 2¹⁵ UI 且 ≤ 100 µs；periodic ≥ 2¹⁰ UI 且 ≤ 10 µs。
   - 所有活跃 Lane 同时发送；RX 检测全 1 sync 后启动 clock-data deskew。从 ULPS 切回 HS 且此前已做过 initial deskew 时，deskew 可选。
3. **Half Swing 模式**（可选省电）与 RX 非端接模式。
4. **Built-In HS Test Mode**（第 12 章）：经 Escape Trigger `01011101`（0xBA）进入；sync word `00011101`；优选 PRBS9（x⁰+x⁵+x⁹，16-bit 种子 Lane0=0xFF、Lane1=0xFE…）；退出条件为 ≥500 ms LP-11 或重新上电。
5. **互操作矩阵（Table 19）**：v1.0/v1.1/v1.2/v2.0 TX×RX 组合的最大速率与 deskew 需求（v2.0↔v2.0 达 4.5 Gbps 需 deskew 初始化；v2.0 TX + v1.2 RX 至 1.5 Gbps 无需 deskew、至 2.5 Gbps 需 deskew 初始化）。
6. LP 时钟失配约束即 TLPX 比值 [2/3, 3/2]。

## 9. 多 Lane 数据分发

- 规范不限定 Data Lane 数量，各 Lane 由协议层独立控制；各 Lane 可独立开始/结束传输；多数应用各 Lane 同步开始但因字节数不同可在不同时间结束。
- 字节如何在 Lane 间分配不在 PHY 规范内（属上层协议如 DSI 的 PHY Adapter）；PHY 层只规定每条 Lane payload 为整数字节（≥1）、LSB 先传、不支持数据节流。
- PPI 数据通路宽度可选 8/16/32 bit。
- 反向传输：Slave 比特周期 = 4·UIINST，即反向速率 = 正向 1/4。

## 10. 初始化

- TINIT ≥ 100 µs：上电后 TX 驱动 Stop（LP-11）；RX 在检测到 Stop 前忽略线上一切状态（Table 15 Initialization States）。

## 11. 附录要点（数字相关）

- Annex A 逻辑 PPI 接口信号（TxDataHS/RxDataHS、TxReadyHS、TxRequestHS、TurnRequest、RxUlpsEsc 等）。
- Annex C 可选 8b9b 线路编码：9 bit 码字、12.5% 开销、4 个 Type A Comma 码（C600 Protocol、C611 EoT、C610/C601 Idle/Sync）。
- 光互连扩展：TWAIT-OPTICAL ≥ 150,000 UI；光链路不支持 BTA。

## 12. 电气规格归档（报告不使用，仅备查）

- HS-TX：VCMTX 150/200/250 mV；|VOD| 140/200/270 mV（Half Swing 70/100/135）；ZOS 40/50/62.5 Ω；de-emphasis 3.5/7 dB 两档；tR/tF ≤0.3 UI（≤1G）/0.35 UI（>1G–1.5G）。
- HS-RX：VCMRX(DC) 70–330 mV；ZID 80/100/125 Ω；差分阈值 ±70 mV（≤1.5G）/±40 mV（>1.5G）。
- LP-TX：VOH 1.1/1.2/1.3 V（>1.5G 档 0.95–1.3 V）；VOL ±50 mV；TRLP/TFLP ≤25 ns。
- LP-RX：VIH ≥880/740 mV；VIL ≤550 mV（ULPS 300 mV）；eSPIKE ≤300 V·ps；TMIN-RX 20 ns。
- 互连：100 Ω 差分参考；飞行时间 ≤2 ns。
- 眼图（>1.5–4.5 Gbps）：BER 10⁻¹² 时 TEYE=0.5 UI、VDIF=40 mV。
- SSC：调制 30–33 kHz、频偏 −5000~0 PPM、df/dt ≤1250 PPM/µs。

## 附：关键验证锚点

- SoT Sync 序列 `00011101`（RX 锁定 Leader `011101`，容忍单比特错）；deskew sync 全 1 16 UI + `0101…` pattern。
- Escape 命令码：LPDT=0x87、ULPS=0x78、Reset-Trigger=0x46、HS Test Mode=0xBA。
- TWAKEUP=1 ms；TINIT≥100 µs；TLPX≥50 ns；TTA-GO=4·TLPX、TTA-GET=5·TLPX、TTA-SURE∈[1,2]·TLPX。
- Clock Lane 无常规 Escape mode，仅 ULPS。
