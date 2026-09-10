# X Server 后续公开修复适用性盘点

> 2026-09-10 更新：下表保留原盘点时的源码状态；其中 CVE-2025-49176、CVE-2025-49178 已按当前目录恢复、重新验证并合入主线，见[输入整合报告](2026-09-10-xserver-input-integration.md)。其余 19 项中，RENDER/RECORD 两项已在独立候选分支修复，尚待本组人工验收及快进整合，见[本组报告](2026-09-10-render-record.md)；另 17 项待实施。旧文中的 upstream 分支合并方案已由当前单主线来源文档规则替代。

> 目录迁移说明（2026-09-10）：文档链接已更新，正文中的旧命令与文件路径仍表示当时状态；当前入口见[文档导航](../README.md)。

> 2026-09-10 历史说明：本文保留当时的方案、提交号与验证结果。旧分支、标签和工作区登记已清理，源码及运行目录保留为普通目录；旧命令不应直接照搬执行。现行规则见[维护规则](../maintenance/UPSTREAM.md)，对应关系与恢复材料见[整理记录](2026-09-10-repository-reorganization.md)。旧依赖快照清单见[历史 JSON](../history/2026-09-09-dependency-snapshot.json)；当前不再维护上游源码分支。

日期：2026-09-09。检查基线为 master `dd555fe9febd00dc2880553a55e82a27dace284f`。本报告完成 R3 的本轮适用性核对，修复实施另行分批跟踪。

## 范围与结论

范围为 [X.Org 官方安全索引](https://www.x.org/Development/Security/) 中 2025 年 6 月至 2026 年 7 月的 X Server 公告，并补查正式源码 ChangeLog 中同组和直接相邻修复。逐函数对照 Windows 源码与构建路径，不按版本号、整文件差异或目录名称直接判定。

本表列出 **24 个不同 CVE 编号**：2 项主线已有修复，21 项缺少关键源码修复（其中 RANDR 的 Windows provider 前置另见下文），1 项仅属未编入的 GLAMOR。另列 DRI2 公告项：官方索引重复使用 50263，暂不另计一个 CVE。相邻无独立编号的补丁也单独列出，不增加 CVE 数量。

这不是全部历史漏洞或所有依赖的全面审计。旧于本轮范围的修复、具体发布二进制和任意自定义配置没有由本表完成验收。源码缺少修复与实际可利用性是不同结论。

## 来源

- 正式包：[xorg-server-21.1.24.tar.xz](https://xorg.freedesktop.org/archive/individual/xserver/xorg-server-21.1.24.tar.xz)，5,072,780 字节；SHA-256 `1a4eb36ca65cc3b1b936566d677a9786e13c11cd5806e951ac55f3f5ce3984af`。
- 正式包 ChangeLog 首提交 `65d790bd208ec380b196eb98f144abb0b32e334d`，发布日期 2026-07-08。只用作源码和提交核对，未用该包覆盖本项目，也未将产品声明为已升级 21.1.24。
- 本机材料：`.local-validation/xserver-audit-20260909/`，包括下载来源、摘要、正式解压树和逐项核对。公告邮件端点返回 403，部分 GitLab 页面获取失败，因此修复归属以正式包 ChangeLog 及最终代码交叉核对；本批输入补丁另由相同完整 SHA 的 GitHub 镜像取得逐文件内容。
- 2026-502xx 的 CVE 与 ZDI 对应来自官方公告索引，部分 ChangeLog 仅列 ZDI。DRI2 的编号歧义保留，不自行纠正。

## 逐项状态（检查基线）

| 项目 | 当前判断 | 具体依据及实施归组 |
| --- | --- | --- |
| CVE-2025-49175，动画光标 | 需回补 | `ProcRenderCreateAnimCursor` 和 `AnimCursorCreate` 均缺少正数量检查；归入 RENDER |
| CVE-2025-49176，大请求长度 | 需回补；[输入候选](2026-09-09-xserver-input.md)自动验证通过，待实际使用确认及合入 | `os/io.c` 两处转换前缺上限检查；包含 June 18 补充修复，不能只补第一条路径 |
| CVE-2025-49177，XFIXES | 已含修复并验收 | SetClientDisconnectMode 使用 `REQUEST_SIZE_MATCH`；[已有报告](2026-09-09-xfixes-request-length.md)记录 59 项测试与本候选用户反馈 |
| CVE-2025-49178，输入缓冲区共享 | 需回补；[输入候选](2026-09-09-xserver-input.md)自动验证通过，待实际使用确认及合入 | 缺少 `!oci->ignoreBytes` 条件；与大请求读取一起验证 |
| CVE-2025-49179，RECORD | 需回补 | 请求数量/范围计算缺上限检查；RECORD 编译并注册，不能当成 xfree86 专用 |
| CVE-2025-49180，RANDR provider | 源码需回补；Windows 前置受限 | `RRChangeProviderProperty` 缺乘法前上限检查；文件编译，但 xwin 未发现创建有效 provider，具体运行可达性未证实；其 xfree86 配套空指针检查单独排除 |
| CVE-2025-62229，PRESENT | 需回补 | `added = i` 未改为计数递增；另须同时核对输出 notifies 指针修复 |
| CVE-2025-62230，XKB 资源释放 | 需回补 | 释放 interest 前未释放对应资源；需要资源类型可见性前置 |
| CVE-2025-62231，XKB CompatMap | 需回补 | 分配/计数字段赋值前缺 `USHRT_MAX` 检查 |
| CVE-2026-33999，XKB CompatMap 复用 | 需回补 | 复用容量时没有扩大有效 `num_si`；与上一项不同 |
| CVE-2026-34000，XKB 几何名称 | 需回补 | KeyAlias 范围只覆盖一个名称，实际读取两个 |
| CVE-2026-34001，XSYNC fence 触发 | 需回补 | 回调删除节点后仍沿旧后继遍历 |
| CVE-2026-34002，XKB ModifierMap | 需回补 | 缺逐项请求范围检查及 client 参数 |
| CVE-2026-34003，XKB KeyTypes | 需回补 | 缺类型、map 和 preserve 区域的边界检查；配套 bounds 加固也缺失 |
| CVE-2026-50256，字体 alias | 需回补 | 名称容量与 libXfont2 不一致，两个复制路径也缺检查；归入 X Server 字体消费方，独立于 R4 库升级 |
| CVE-2026-50257，销毁 XSYNC fence | 需回补 | 与 FreeCounter/FreeAwait 共用生命周期修复，不拆成两次不完整移植 |
| CVE-2026-50258，XKB 层数 | 需回补 | 缺 `XkbMaxShiftLevel` 上界；不能由请求长度检查替代 |
| CVE-2026-50259，XKB 类型总数 | 需回补 | 缺 `nMaps` 对固定数组容量的上界 |
| CVE-2026-50260，XSYNC FreeCounter | 需回补 | 与 50257 同一官方提交；须同步更新 FreeAwait |
| CVE-2026-50261，XSYNC counter 触发 | 需回补 | 缺回调后后继存活检查；不能照搬 fence 的无条件重启遍历 |
| CVE-2026-50262，GLX drawable 属性 | 需回补 | 普通及交换字节序入口仍绕过 `REQUEST_FIXED_SIZE`；与已修的上下文标签无关 |
| CVE-2026-50263，屏保 | 需回补 | `CheckScreenPrivate` 后未重新获取可能已释放的私有指针 |
| CVE-2026-55999，GLAMOR 字体 atlas | 当前 Windows 构建不适用 | GLAMOR 关闭，未编入该实现；不表示其源码已经修复 |
| CVE-2026-56000，GLX 上下文标签 | 已含修复并验收 | [已有报告](2026-09-09-glx-context-tags.md)记录修复、51 项测试和使用反馈 |
| DRI2 do_get_buffers 公告项（索引编号重复） | 当前 Windows 构建不适用 | DRI2 关闭且未编入实现；正式包提交 `b7aa65cc3bb11b792ce2a3f511ba9b863acb11c8`、`339c279514326134b0878fc23ce6e9520440ce7f` 处理 front buffer 跟踪和附件去重 |

## 同组与相邻修复

- 输入处理：`03731b326a80b582e48d939fe62cb1e2b10400d9`、`4fc4d76b2c7aaed61ed2653f997783a3714c4fe1`、`d55c54cecb5e83eaa2d56bed5cc4461f9ba318c2`。两个长度检查必须同时具有，调用方错误语义也需验证。
- XKB：资源类型前置、更多逐项 bounds，以及 CheckKeyActions 动作总区域、Overlay/Geom/Shapes 索引、doodad 容量、vmod_ 前缀检查均需纳入该组。`_Concat` 分配失败处理是相邻普通修复，单独标记。
- PRESENT：`f70cc16c6831c9faa14c1f2a8588c6efb6ede263` 返回创建的 notifies 指针，与计数修复互不替代。
- 字体：`e31efd3e106e53bfc29d499ff0a34b0d20013f2d` 的 fb/mi 正尺寸检查缺失。Windows 实际使用 fb，因此不能随 GLAMOR 排除整条补丁。alias 同函数的分配、初始化修复也应一起评审。

完整的函数行号、官方稳定/master 提交映射、已有保护及前置关系见 [XKB 明细](2026-09-09-xserver-xkb-audit.md)、[XSYNC/PRESENT 明细](2026-09-09-xserver-sync-present-audit.md)、[核心/字体/GLX 明细](2026-09-09-xserver-core-audit.md)。明细中的行号固定于检查基线和正式包，不随后续候选变化自动更新。

## 后续实施边界

先完成输入处理候选，再分别处理 RENDER/RECORD、XKB、XSYNC/PRESENT/屏保、GLX 属性、字体消费方和 RANDR。每组固定来源、补丁前置与测试范围，再通过 upstream 到开发分支的普通合并引入。是否拆分同组，以共享状态和补丁依赖为准，不以 CVE 个数机械拆分。

本表的“需回补”不是“已完成”；候选自动测试通过也不是主线已合入。日常图形兼容性仍在 R2，字体库升级仍在 R4，其他组件 R5–R9 未被这次盘点顺带完成。
