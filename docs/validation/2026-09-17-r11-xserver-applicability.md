# R11 xserver 上游 21.1 分支未合入提交适用性评估

日期：2026-09-17。基线 `23a3c9609a`；分支 `codex/r11-xserver-20260917`，独立工作区 `D:/File/Program/GitHub/zzxsrv-r11-xserver-20260917`。

状态：候选待验收。本轮为**纯评估，不导入任何代码**：对 R9.8 筛出的 server-21.1-branch 104 个本地未合入提交逐 commit 判定适用性，每个判定均核对上游完整 diff、本地构建覆盖（mhmake makefile）、漏洞模式是否在本地文件中实际存在、以及与本地 fork 改动的冲突风险。无产品代码改动，不需要重建。

## 数据基础与方法

继承 R9.8 证据：上游官方仓库完整克隆 `.local-validation/r9-xserver-20260917/upstream-xserver/`（含 server-21.1-branch 全历史，分支顶端 `640a967175c8`，2026-06-26，已过 21.1.24 发布 9 个提交）、候选集台账 `branch-assessment.json`（193 个提交 = 39 已登记 + 50 固定点已含 + 104 未合入）。104 个未合入提交按子系统分 8 组并行核查：逐 commit `git show` 上游 diff，对照本地树确认漏洞模式在场与否，交叉核对 SOURCES.json 全部 39 个已登记补丁确认无覆盖重叠，并评估 cherry-pick 上下文冲突。

判定档位：A 建议合入（参与构建、漏洞模式在场、安全/崩溃类）；B 可选合入（正确性修复、低风险）；C 需功能评估（代码链入但触发路径不确定）；D 不适用（不构建/平台专用/发布与 CI/文档/已被覆盖）。

## 总体结论

104 个提交：**A 19 个、B 15 个、C 5 个、D 65 个**。安全相关的实际收益集中在 A 档 19 个，全部经本地漏洞模式逐一确认在场；D 档 65 个中约半数为 glamor（16）与 xfree86/xquartz/平台代码（18），本地 Windows 构建均不包含。

## A 档：建议合入（19 个）

| SHA（短） | 主题 | 依据摘要 |
| --- | --- | --- |
| `8d604fa1` | render: duplicate glyphs 同 glyphset UAF | render/glyph.c:270 漏洞条件在场；单行修复，上下文干净 |
| `ab2766f3` | Xi: XIChangeCursor 校验 window 非空 | xichangecursor.c:86-92 空指针解引用在场；3 行修复 |
| `8a6e5f0f` | dix/colormap: FindColorInRootCmap 越界读 | colormap.c:1305 旧循环不回绕，客户端可控越界读；上下文干净 |
| `1888711c` | glx: FeedbackBuffer/SelectBuffer 拒绝负 size | single2.c/single2swap.c 共 4 处缺负值检查；直接 cherry-pick |
| `78368d1b` | dix: ChangeWindowDeviceCursor 分配失败判空 | window.c:3502 malloc 未判空；行号漂移约 +10，无冲突 |
| `04321adc` | dix: DeviceFocusEvent 分配失败判空 | enterleave.c:786-787 calloc 未判空；无冲突 |
| `a3a37c56` | dix: FollowKeyboard 焦点键盘选择 | events.c:1724/1774 崩溃模式在场，可经协议触发；三处 hunk 上下文干净 |
| `0249e717` | dix: 反向 BUG_RETURN 检查 | enterleave.c:735：DeviceStateNotify 永不投递 + 超限时越栈写，安全相关；单行修改 |
| `757a0d03` | Xi: add_master_func 分配失败判空 | xibarriers.c:730 模式在场；无冲突 |
| `d31e4534` | Xi: ProcXListInputDevices 分配失败判空 | listdev.c:364 calloc 未判空；冲突风险低 |
| `fd6d0408` | Xi: ProcXGetDeviceDontPropagateList 分配失败判空 | getprop.c:119 xallocarray 未判空；单行插入 |
| `995fe28e` | Xi: CopySwapKbdFeedback 补 led_values | getfctl.c:82-91 未初始化值随 reply 外发；单行插入 |
| `b171669dc` | Xi: wOtherInputMasks NULL 判空（5 处） | exevents.c 5 处模式全部在场；第 4 个 hunk 因本地 `RT_NONE`→`X11_RESTYPE_NONE` 改名需手工套用 |
| `bf37ce8e` | Xi: disallow grabbing disabled devices | xigrabdev.c:84 缺 enabled 检查，grab 后段错误；无冲突 |
| `d29339ed` | Xext/xtest: ProcXTestFakeInput NULL 判空 | xtest.c:354 客户端传 slave 设备 ID 即可触发；仅行号偏移 |
| `a39d4c3a` | Xext/xres: ProcXResQueryClients NULL 判空 | xres.c:228 xallocarray 未判空；单行插入 |
| `976ef43f` | Xext/sync: malloc 失败返回已释放指针（UAF） | sync.c:1056-1059 模式逐字在场；hunk 因 `X11_RESTYPE_NONE` 改名需手工改 `return NULL;` |
| `9bad510a` | Xext/sync: init_system_idle_counter NULL 判空 | sync.c:2870-2873 模式在场；每设备初始化可达 |
| `7097560c` | Xext/sync: SysCounterGetPrivate NULL 判空 | sync.c 4 处 IdleTime handler 未防御；与 9bad510a 配套 |

合入顺序注意：sync 三个必须按 `7097560c` → `9bad510a` → `976ef43f` 的上游依赖顺序合入；`b171669dc` 第 4 个 hunk 与 `976ef43f` 各有一处因本地 `X11_RESTYPE_NONE` 改名需手工处理，其余 A 档预计均可直接 cherry-pick（本地 fork 差异均在 hunk 上下文窗口之外）。本地 fork 曾在 exevents.c:1867 自加同类 sprite 判空，说明这类崩溃路径在本项目真实出现过。

## B 档：可选合入（15 个）

| SHA（短） | 主题 | 说明 |
| --- | --- | --- |
| `c285ed7d` | glx: 重复 vendor=NULL 赋值 | 低风险正确性；危害路径基本被遮蔽 |
| `c9cd39f9` | Xi: XIPassiveUngrabDevice gesture 类型检查 | 协议校验缺口，无内存不安全路径 |
| `c0146196` | dix: ChangeGCXIDs errorValue 取值 | 仅错误信息不正确 |
| `68c186bf` | dix: ProcListProperties 内存泄漏 | 需 XACE hook 拦截才触发，本地无安全 hook 注册 |
| `236e712f` | dix: swaprep 缓冲区倍数断言 | 纯静态分析加固，不修实际缺陷 |
| `9848e11d` / `63d6cbf2` | panoramiX 两处分分配失败判空 | Xinerama + OOM 才触发 |
| `33eee35e` | os: FormatInt64 LONG_MIN | 本地函数已迁至 os/fmt.c，需手工移植而非 cherry-pick |
| `5ebf0a9d` + `bdc7eb8f` | xkb: 无级别名键型序列化/拷贝 | **必须成对合入**（bdc7eb8f 在前），单独合入会让 XkbGetNames 出错 |
| `d2f1d74f` | xkb: locked/latched indicator 同步 | 多键盘场景，Xwin 通常单键盘 |
| `123f50ac` | render: gradient 错误路径内存泄漏 | 三处缺 free，客户端可触发的小型泄漏 |
| `7cd443c6` | os: xsha1 OpenSSL 3 EVP API | 面向未来的 deprecation 清理；COPYING hunk 与本项目无关应跳过 |
| `dd924b16` / `3069f64d` | COPYING 两处许可证文本修正 | 法律文本完整性；建议文档同步而非 cherry-pick（上下文必冲突） |

## C 档：需功能评估（5 个）

| SHA（短） | 主题 | 说明 |
| --- | --- | --- |
| `4a562d37` | dix: gestures/touch NULL 判空 | Xwin 从不创建触摸设备，路径为死代码；合入零风险 |
| `ce300ed2` | randr: primaryOutput UAF | 需 GPU screen，Xwin 单屏不创建，触发路径不存在；合入无害 |
| `ef781045` / `d7279b8e` / `09eb9aa3` | miext/rootless 三个 | librootless.lib 链入 Xwin，代码与上游逐字节一致可干净应用；收益面向 multiwindow 模式的 Render/文本重绘，未验证。其中 `09eb9aa3`（Glyphs damage box max→min）是最明确的计算错误，若后续验证 multiwindow 重绘问题可优先单独评估 |

## D 档：不适用（65 个）

- **glamor 16 个**：`glamor/` 无 mhmake makefile，hw/xwin 对 glamor 零引用，全部不可达。含 CVE-2026-55999 的 `f3df3c9a`——已登记补丁 `0f1f4bcb` 登记时显式排除了 glamor 部分，fb/mi 侧防护已就位。另 5 个为 21.1 分支回退 master 提交的反向差异（被回退代码在本地基线中但不构建）：**未来若启用 glamor，不应照搬本地基线的 glx_provider 状态**——21.1 的实践证明 glamor_glx_provider + GlxVendorLibrary 路径有已确认的段错误和 NVIDIA/AMD 回归。
- **hw/xfree86 / xquartz / 平台 18 个**：xfree86 整树与 config/udev.c 不参与构建（config/makefile 仅编译 config.c），xquartz 为 macOS 专用。含 CVE-2025-49180 的 `bb895485`（xf86RandR12.c）与 DRI2 两个客户端可触发修复——Xwin 的 RandR/GLX 走独立路径，漏洞不可达，留此记录备查。
- **发布 / 构建系统 / CI / man 页 19 个**：7 个 21.1.x 版本号提交；configure.ac/Makefile.am/test/Makefile.am/SECURITY.md 本地不存在；meson.build、.gitlab-ci.yml、xorg-server.pc.in 为死文件；man 页不构建不分发（笔误在本地存在但无交付影响）。
- **Xext 不构建部分 5 个**：xselinux×2、shm、vidmode 在 Xext/makefile 中注释或无引用；xf86bigfont 仅修 gcc14 告警。
- **其他 6 个**：`7a6c6bf9`（本地 XACE 恒开且 fork 已重写该段，**不要强合**，合入反而引入冲突风险）；`032715f2`（Unix fd 继承语义，Windows socket 默认不可继承）；`447fec7d`（mingw 构建错误，MSVC 无此问题）；`ff10e6d0`（Fopen 整体在 `#if !defined(WIN32)` 内）；`c49bf5f7`（本地 master 线已重构 logVHdrMessageVerb，漏洞模式不在场）；`368ff1d5`（ROOTLESS_SAFEALPHA 宏仅 XQuartz 定义，mhmake 构建为 no-op）。

## 证据与范围

分组核查明细与逐 commit 判定依据在证据目录 `.local-validation/r11-xserver-20260917/`（git 忽略、不入库）。本轮范围为适用性评估：未导入任何提交、未修改产品代码、未触发构建。A/B 档是否启动新一轮补丁整合（建议另立 R12，需完整构建、452 项回归与维护者验收）由维护者决策。

## 下一步

候选交付维护者验收。若批准合入 A 档，建议范围：19 个 A 档（含 sync 三连的顺序约束与两处手工适配），B 档是否顺带带入（注意 xkb 成对约束与 COPYING 的文档同步方式）由维护者一并决定。
