# 组件更新必要性与实施顺序评估

> 2026-09-10 历史说明：本文保留当时的方案、提交号与验证结果。旧分支、标签和工作区登记已清理，源码及运行目录保留为普通目录；旧命令不应直接照搬执行。现行规则见[维护规则](../UPSTREAM.md)，对应关系与恢复材料见[整理记录](../validation/2026-09-10-repository-reorganization.md)。旧依赖快照清单见[历史 JSON](../history/2026-09-09-dependency-snapshot.json)；当前不再维护上游源码分支。

> 历史评估：本文保持首次检查时的证据和判断，不能直接当作当前待办。GLX 与 XFIXES 后均已完成整合；实时状态见 [计划状态](../PLAN_STATUS.md)。旧目标版本在实施前重新核实。

日期：2026-09-09。检查源码：`0d102004da57fd82ed6e4e6f81b12ebd6324f8ba`。

本轮完成公开公告、版本文件、Windows 构建路径和部分关键函数的只读核对，没有升级组件、下载源码包、安装工具、执行 Git 远程同步或重新编译。用户已测试的运行目录保持原样。本文是更新候选评估，不是完整漏洞审计或修复验收；目标版本是本日查询结果，实施前仍须复核。

## 建议顺序

先核对并回补 X Server 的相关安全修复，再分批处理字体和 XML 解析库；OpenSSL 按支持期限安排 LTS 迁移；Mesa 整体升级暂缓。优先级依据实际使用路径、修复证据和改动成本，不等同于漏洞严重等级。

| 顺序 | 本地组件版本 | 官方候选或修复基准 | 本项目的处理建议 |
| --- | --- | --- | --- |
| 1 | X Server：21.1.99.1 开发快照；产品标识 21.1.16.1 | [X.Org 公告及 21.1.24 修复基准](https://www.x.org/Development/Security/) | 先核对 GLX，再覆盖后续 XKB、XSYNC、XFIXES、请求长度等修复；按补丁回补，不直接用稳定版覆盖整个开发快照 |
| 2 | libXfont2：2.0.6；FreeType：2.13.3 | [libXfont2 2.0.8 安全公告](https://www.x.org/Development/Security/)；[FreeType 2.14.3](https://freetype.org/) | 字体解析代码实际编入消费者，核对差异后分别更新或回补，并一起验证字体链路 |
| 3 | libxml2：头文件 2.9.1，DLL 报告 20901；Expat：2.6.2 | [libxml2 2.15.4 发布材料](https://download.gnome.org/sources/libxml2/2.15/)；[Expat 2.8.4](https://libexpat.github.io/) | libxml2 先落实源码构建来源及兼容性；Expat 可独立更新并重建 Mesa 消费者 |
| 4 | OpenSSL：3.4.1 | [3.5.8 LTS；3.4 分支当前补丁版 3.4.7](https://openssl-library.org/source/) | 计划迁移 3.5 LTS；若接口适配阻碍短期更新，评估 3.4.7 过渡 |
| 5 | xkbcomp：1.4.7；libXpm：3.5.17；zlib：1.3 | [xkbcomp 1.5.0、libXpm 3.5.19 的修复](https://www.x.org/Development/Security/)；[zlib 1.3.2](https://zlib.net/) | 分组件核对键盘解析、图标读取和压缩数据路径，不能因顺序靠后跳过已证实适用的安全修复 |
| 暂缓整体替换 | Mesa：25.1.0-devel | [26.2.2 发布说明](https://docs.mesa3d.org/relnotes/26.2.2.html) | 先处理独立依赖及相关小补丁；有实际图形问题或明确收益后再整包升级 |

## X Server：已经找到代码层面的对应关系

本地 [meson.build](../../xorg-server/meson.build) 标识为 21.1.99.1，不能只凭产品的 21.1.16.1 判断其等于官方稳定版 21.1.16。

对 CVE-2026-56000，已核对以下路径：

- [vndcmds.c](../../xorg-server/glx/vndcmds.c) 的 `CommonMakeCurrent` 先取得 `oldTag`，再调用 `CommonMakeNewCurrent`，最后调用 `GlxFreeContextTag(oldTag)`。
- `CommonLoseCurrent` 本身只转发 vendor 回调，没有在这里释放标签槽。`CommonMakeNewCurrent` 会调用 `GlxAllocContextTag`。
- [vndservermapping.c](../../xorg-server/glx/vndservermapping.c) 中，标签直接指向数组元素；数组空间不足时使用 `realloc`，之后释放旧标签的代码仍通过旧指针写字段，没有重新查找标签。
- [GLX makefile](../../xorg-server/glx/makefile) 包含上述两个源文件；[dix-config.h](../../include/dix-config.h) 启用 GLXEXT。

结论：本地代码存在公告描述的“扩容可能移动数组，旧元素指针随后被写入”的路径，列为首个回补候选。尚未对本机成品复现内存错误，也未完成 vendor 回调和所有失败分支的动态验证，不能声称已确认当前运行程序可被利用。

公告明确区分了稳定版 21.1.16 与开发分支，不能忽略这个适用条件。修复提交为 `2779affbdb4354e894f490e56f962527d6125043`，来源为 [X.Org 维护者公告的邮件归档副本](https://www.mail-archive.com/xorg-devel@lists.x.org/msg58557.html)。本次 [官方提交页面](https://gitlab.freedesktop.org/xorg/xserver/-/commit/2779affbdb4354e894f490e56f962527d6125043) 访问受限，尚未取得并审查补丁差异，不把公告说明当成可直接应用的补丁。

其他候选尚需逐项对照：本地启用了 XKB、XSYNC、PRESENT、XFIXES；[XFIXES disconnect.c](../../xorg-server/xfixes/disconnect.c) 的普通请求处理函数未见对应长度匹配检查，需核对 CVE-2025-49177；[os/io.c](../../xorg-server/os/io.c) 的大请求长度运算需核对 CVE-2025-49176 及其补充修复。还需覆盖 2025 年 6 月、10 月及 2026 年 4 月、6 月、7 月的相关公告，不能只处理最后一批。依据：[X.Org 安全索引](https://www.x.org/Development/Security/)。

glamor 专属问题不能直接套用：当前检查的 Windows 服务器构建入口未包含 glamor 目标。扩展宏启用只证明值得继续检查，不证明每条公告的触发条件都成立。

## 字体与 XML 依赖：确有消费者，逐项确认适用性

[libXfont2 makefile](../../libXfont2/makefile) 编入 `bitscale.c`、`pcfread.c`、`bdfutils.c`，与后续字体解析修复涉及的模块有交集；FreeType 由原生构建入口编译，并被 libXfont2、Fontconfig 等使用。应先对照修复，再验证 PCF/BDF、TrueType/OpenType、中文显示及字体缓存。本轮只确认构建路径，不认定后续所有字体漏洞都适用；例如 [FreeType 配置](../../freetype/include/freetype/config/ftoption.h) 未启用 PNG 支持。

libxml2 使用情况：

- [XLaunch config.cc](../../xorg-server/hw/xwin/xlaunch/config.cc) 通过 `xmlReadFile(filename, NULL, 0)` 读取配置。
- [Fontconfig 配置](../../fontconfig/config.h) 启用 `ENABLE_LIBXML2`；xclock 也链接这条依赖链。
- 对已有完整运行目录中的 `libxml2-2.dll` 调用 `__xmlParserVersion`，返回 `20901`，与 [头文件版本](../../libxml2/include/libxml/xmlversion.h) 的 2.9.1 一致。DLL SHA-256 为 `3c68a190dc6d550334ff9d0a506e9526105b008364dad0915562413ceec092cb`，与仓库 `libxml2/bin64` 中的 DLL 相同。

这确认了 DLL 自报版本，仍不能证明其精确源码、编译选项及补丁。仓库携带头文件、导入库和 DLL，更新前要补齐可重建来源，不能只换一个新版 DLL。

2.15 系列移除了旧的 Windows 构建系统，改用 CMake，并改变内置网络访问、压缩输入等行为。因此 2.15.4 是兼容性试验候选，尚不是已批准可替换版本。试验应覆盖头文件、导入库、DLL 及全部消费者的重建，并验证 XLaunch 配置保存/加载、中文路径、错误 XML、Fontconfig 配置与缓存。它适合作为以后单组件 CMake 试验，不要求现在迁移全仓库。依据：[libxml2 2.15.0 变更说明](https://download.gnome.org/sources/libxml2/2.15/libxml2-2.15.0.news)。

Expat 的实际消费者是 Mesa：[Mesa makefile](../../mesalib/src/makefile) 链接 `libexpat.lib`，[xmlconfig.c](../../mesalib/src/util/xmlconfig.c) 使用 `XML_ParserCreate` 和 `XML_ParseBuffer` 解析配置。它可以单独更新，不要求同时替换整个 Mesa。需核对 [Expat 2.8.4 变更记录](https://github.com/libexpat/libexpat/blob/R_2_8_4/expat/Changes) 中各问题的配置条件；不能因 Windows 平台就认定启用了 Expat 的 16 位字符接口。

## OpenSSL、Mesa 与其他组件的取舍

OpenSSL 3.4 分支支持到 2026-10-22；3.5 LTS 支持到 2030-04-08。因此应排入近期维护窗口，优先评估 3.5.8，而不是只长期停留在 3.4 的补丁版。依据：[官方版本与支持周期](https://openssl-library.org/source/)。

本地 [xsha1.c](../../xorg-server/os/xsha1.c) 明确使用 OpenSSL SHA-1 API。[makefile.before](../../makefile.before) 列出 `libssl.lib`、`libcrypto.lib`，但本轮在服务器与 xkbcomp 源码检查中没有找到建立 TLS 会话的典型调用。不能据此把所有 TLS/CMS 漏洞都认定为当前功能风险，也不能把普通 X11 TCP 连接描述成 OpenSSL 加密连接。后续核对实际链接符号与 API 兼容性；`tools/plink` 的 PuTTY 加密代码需另行维护。

Mesa 当前构建启用 `GALLIUM_SOFTPIPE`，还保留 Windows 自定义 makefile 和服务器整合代码。升级至 26.2.2 的改动面较大，本轮未发现足以支持立即整包替换的已复现图形故障；其上游发布不能直接视为我们这套 Windows 整合代码已验证。先处理 Expat 等独立依赖，再按真实 GLX/OpenGL 场景选择相关修复。

zlib 使用仓库自己的 [makefile](../../zlib/makefile)，不是直接依赖上游 Visual Studio 工程；上游构建系统变化不意味着我们必须迁移整个项目到 CMake。当前目标未编入 `contrib/minizip`，不能把该子目录的安全修复自动视为当前程序受影响。更新仍需检查导出、压缩/解压、异常数据和字体消费者。

xkbcomp 与 libXpm 已纳入后续候选：前者关系到键盘规则编译，后者由 xcalc、xclock 等工具使用。libX11、libxcb、Pixman、Fontconfig 自身以及 PuTTY 等其余组件尚未完成同等深度的更新审查，不能标记为“无需更新”或“没有漏洞”。

## 下一项实施任务与验收门槛

首项任务建议为 `codex/update-xserver-security`，从届时干净的 `master` 建立独立工作区，限于 X Server 相关安全补丁，不混入 Mesa、构建系统迁移或产品版本改名。

1. 固定来源 SHA，取得官方修复差异；新增源码或补丁下载须按当前不自动下载的约定说明来源与范围。记录补丁作者、许可证、前置提交及本地适配，先确认补丁是否已经以其他形式存在。
2. 建立逐项矩阵：公告/提交、源码是否匹配、当前构建是否包含、触发前提、处理结论和证据；无关项写清排除理由，待核对项保留待定。
3. 为选中的 GLX 等修复建立针对根因的回归验证，先证明旧代码失败；同时覆盖正常上下文切换、无旧上下文、分配失败和客户端退出清理。单靠搜索代码或最小根窗口查询不能验收内存安全修复。
4. 完成干净 x64 Release All 构建、现有测试全部执行、PE 导入检查、认证连接与清理验证；增加实际 GLX/OpenGL 应用、键盘和窗口操作。需要的真实应用环境不具备时记为 `NOT_RUN`，不宣称整项完成。
5. 独立审查通过后本地提交中文标题与详细正文，记录新源码/产物、结果及回退点。新运行目录独立保存，旧基线标签与用户已验证目录继续保留。

后续字体、XML、OpenSSL 分批执行相同原则，并添加各自的解析与兼容性场景。具体实施计划应在选定补丁与来源后细化，本文没有替代补丁审查或实际验收。

## 本轮证据与边界

| 检查 | 结果 | 限制 |
| --- | --- | --- |
| 版本与构建入口核对 | PASS：上述候选都有本地版本或调用/链接依据 | 不是所有编译宏和最终链接符号的完整审计 |
| GLX 指针生命周期检查 | PASS：找到与公告对应的源码路径 | 二进制问题复现、补丁差异审查均未执行 |
| libxml2 DLL 版本探测与哈希 | PASS：20901，且与仓库 x64 DLL 哈希一致 | 自报版本不等于完整构建来源 |
| 官方公告与发布说明 | 已查询并在对应段落引用 | 部分 X.Org 邮件站点及官方补丁页访问受限；GLX 使用维护者邮件的归档副本 |
| 文档与证据一致性 | PASS：32 个相对链接存在；仅 3 个预期 Markdown 改动；DLL 版本与哈希复核一致 | 不替代未来补丁实施的测试 |
| 独立审查 | PASS：未发现阻断项；复核了 GLX 路径、XML 消费者及 OpenSSL 使用范围 | 审查对象是评估结论，不是尚未实施的补丁 |
| 编译、漏洞回归及功能复测 | NOT_RUN | 本轮仅评估，未修改程序 |

本机探测脚本及结果存放于主工作区忽略目录 `.local-validation/component-assessment-20260909/`。探测只加载已有 DLL 并查询版本，不解析用户文档。首次直接从仓库 DLL 子目录加载时因缺少同目录的传递依赖而失败；随后从完整基线运行目录加载成功，这不是用户运行目录缺文件的证据。

此前用户功能反馈及原作者分支核对见 [用户验证与上游检查](2026-09-09-user-validation-and-upstream-check.md)；实际编译来源与运行目录见 [基线报告](2026-09-09-baseline.md)。原作者分支没有新提交，与组件上游已有更新是两件独立的事。
