# 其他核心公开修复静态核对

> 2026-09-10 进展：本文保留最初静态缺口；RENDER/RECORD 已取得本组使用确认并快进合入 master，见[验证与整合报告](2026-09-10-render-record.md)。其他条目仍按[当前计划](../maintenance/PLAN_STATUS.md)推进。

> 目录迁移说明（2026-09-10）：文档链接已更新，正文中的旧命令与文件路径仍表示当时状态；当前入口见[文档导航](../README.md)。

> 2026-09-10 历史说明：本文保留当时的方案、提交号与验证结果。旧分支、标签和工作区登记已清理，源码及运行目录保留为普通目录；旧命令不应直接照搬执行。现行规则见[维护规则](../maintenance/UPSTREAM.md)，对应关系与恢复材料见[整理记录](2026-09-10-repository-reorganization.md)。旧依赖快照清单见[历史 JSON](../history/2026-09-09-dependency-snapshot.json)；当前不再维护上游源码分支。

日期：2026-09-09。基线：master `dd555fe9f`。参考为本次取得的官方 X.Org Server 21.1.24 源码包，解压于 `.local-validation/xserver-audit-20260909/release/xorg-server-21.1.24`；来源 https://xorg.freedesktop.org/archive/individual/xserver/xorg-server-21.1.24.tar.xz ，SHA256 `1a4eb36ca65cc3b1b936566d677a9786e13c11cd5806e951ac55f3f5ce3984af`。

仅比较源码、ChangeLog 和 Windows 构建清单，未修改源码/refs，未运行程序或网络测试。结论表示具体官方修复条件缺失，不表示已证明安装二进制的实际可利用性。2026-50256、50262 编号映射沿用本次公告索引核对；release ChangeLog 在相应提交中仅列 ZDI 编号。

## 核对结果

| 事项 | 状态 | 本地证据 | 官方最终代码特征 |
|---|---|---|---|
| CVE-2025-49175，animated cursor | 需回补 | `xorg-server/render/render.c:1799-1802` 计算 ncursor 后直接分配；`xorg-server/render/animcur.c:301-325` 未检查正数就访问 cursors[0] | ProcRenderCreateAnimCursor 和公开入口 AnimCursorCreate 均增加 `if (ncursor <= 0) return BadValue`。官方 `render/render.c:1798-1799`、`render/animcur.c:307-308`。 |
| CVE-2026-50256，font alias / ZDI-CAN-30136 | 需回补 | `xorg-server/dix/closestr.h:61` 的 XLFDMAXFONTNAMELEN 为 256，但 `libXfont2/include/X11/fonts/fntfil.h:65` 的 MAXFONTNAMELEN 为 1024；`xorg-server/dix/dixfonts.c:683-692`、`:716` 拷贝 resolvedlen；`:962` 拷贝 namelen，均缺少目标上限检查 | 官方 `include/closestr.h:65` 将上限统一到 1024；`dix/dixfonts.c:673-677`、`:943-947` 在两条 alias 复制路径检查长度，超限以 BadFontName 进入清理路径。注意本地头文件在 dix/，不在官方稳定版的 include/。 |
| CVE-2026-50262，GLX ChangeDrawableAttributes / ZDI-CAN-30165 | 需回补 | `xorg-server/glx/glxcmds.c:1597-1604` 仍禁用 REQUEST_FIXED_SIZE 并使用 `< client->req_len`；`xorg-server/glx/glxcmdsswap.c:443-448` 也为反向 `<`，随后按声明数量 swap 数组 | 官方普通入口 `glx/glxcmds.c:1525`、swapped 入口 `glx/glxcmdsswap.c:443` 均恢复 REQUEST_FIXED_SIZE。不是仅把 `<` 换成 `>` 的最终实现。 |
| July `e31efd3e`，fb/mi/glamor 负字形尺寸拒绝 | 需回补（fb/mi 部分） | `xorg-server/fb/fbglyph.c:96`、`:198` 和 `xorg-server/mi/miglblt.c:144` 均只检查 `gWidth && gHeight`，负数通过 | 官方 `fb/fbglyph.c:98`、`:200`，`mi/miglblt.c:146` 均检查 `gWidth > 0 && gHeight > 0`。该提交同时改 glamor，但 fb/mi 缺口不能因 GLAMOR 关闭而排除。不要把未独立列 CVE 的本提交再当作新增 CVE 计数。 |

## 正式 release ChangeLog 提交标识

| 事项 | 稳定分支 SHA | ChangeLog 标注的 master SHA | ChangeLog 行号 |
|---|---|---|---|
| animated cursor | `ea7b770952dbcf6c769db7538b55b4f92e1f95c5` | `0885e0b26225c90534642fe911632ec0779eebee` | 3570-3619 |
| font alias | `a569eb4f36ed96a9e445ececd7e8d98c223461a0` | `bb5158f962dc935e58ef8b4b5fcb31be201a6e07` | 365-400 |
| GLX ChangeDrawableAttributes | `94341bd715d62ba8da4c1851f517018996da1af8` | `6d459e4daf715bea8abdafa8fb130be2f8a1d145` | 446-477 |
| fb/mi/glamor 负字形尺寸 | `0f1f4bcbfb1f23b800dfe386782d3a0f05b6756f` | `e31efd3e106e53bfc29d499ff0a34b0d20013f2d` | 42-62 |

上述 SHA 与修复归属取自官方 ChangeLog，控制流结论取自官方最终源码。没有从 Git 拉取相应 commit object 来证明每一行一定由该单一提交引入；例如 font alias 应以最终源码的两条长度检查一起评审，不能仅照提交标题扩容。

## 直接相邻前置和重叠

- animated cursor 必须同时覆盖协议入口和公共 AnimCursorCreate，不能只检查一个调用点。本地早已有 BadValue 和分配 API；无需整文件替换。保留本地 `X11_RESTYPE_CURSOR` 等接口命名。
- GLX 两个入口已有 `numAttribs > (UINT32_MAX >> 3)` 上限保护（本地 `glxcmds.c:1593`、`glxcmdsswap.c:439`）；它没有检查实际收到的数据长度，不能视作已修复。REQUEST_FIXED_SIZE 宏在邻接 SGIX 路径已经使用。官方 ChangeLog 指出修复撤销 2011 年旧 Mesa 长度兼容绕过，回补应移除当前 `#if 0` 分支而不是保留相互矛盾的检查。
- font alias 同函数另缺两项先前公开的分配失败修复：本地 `dixfonts.c:660-662` 仍 malloc 并可能留下 NULL resolved；`:957-959` 仍 malloc 并可能留下 NULL savedName。官方改为 XNFalloc。前者稳定 SHA `9ee6ae7292e7f6e3fd04fdc61dab5ed127cbbce3` / master `0237462d326c78868c83b6eda35a9d35725f3b33`（ChangeLog 1572-1598）；后者稳定 `e052acfa3391a4563c084556aca22ecb7459b012` / master `dd5c2595a42d3ff0c4f18d9b53d1f6c3fd934fd4`（2656-2677）。它们不是 50256 的同一缺陷，但与其回补上下文直接重叠。
- font alias 后续还有初始化/分析器修复，本地 `dixfonts.c:573` 未初始化 resolvedlen，`:869`、`:872` 未初始化 name/namelen。官方最终版设置 resolvedlen/namelen 为 0、name 为 NULL，并在使用未返回的 name 前走 BadFontName。相关稳定/master SHA 分别为 `6c6a2dfd295f836a502410ff40b5855b133c7ffd` / `e710e570b1709d100072a8ab7d05c2aefaf41a1b`、`bf25faf5c1b825f14642f81129b28e04a024356d` / `f959f1e51f369ac26b6ba5953a3b022407e85b11`、`c0839d9cbf85261cea20cda2f7d6c8a732e16eb6` / `5d011bf3da81595bef25ca89458249c1037a4f51`（ChangeLog 140-205）。这些是相邻完整性核对项，不应全都升级为独立 CVE。
- fb/mi 差异中存在 VcXsrv 开发分支的 `dixDestroyPixmap(pPixmap, 0)` 对比稳定版回调；与正字形尺寸检查无关，应保留本地接口。对于本次检查的三个 fb/mi 条件，现有 int 变量和比较运算即可表达修复，没有发现额外库/API 前置。

## Windows 构建与排除边界

1. 当前服务器构建 `xorg-server/makefile` 链接 dix（10）、fb（11）、glx（12）、hw/xwin（13）、mi（16）、render（28）；相应源清单为 `dix/makefile:21`、`fb/makefile:22`、`glx/makefile:23-24`、`mi/makefile:10`、`render/makefile:4,14`。`include/dix-config.h:54` 启用 GLXEXT，`:302` 启用 RENDER；`mi/miinitext.c:129`、`:168` 注册 RENDER / GLX。
2. fb 不只是文件存在：`hw/xwin/winscrinit.c:267` 和 `:297` 调用 fbSetupScreen / fbFinishScreenInit；`fb/fbscreen.c:122` 安装 fbCreateGC；`fb/fbgc.c:57-58` 的操作表引用 fbImageGlyphBlt / fbPolyGlyphBlt。miPolyGlyphBlt 确实编入 libmi，但在当前源码中找到的外部调用位于 GLAMOR 回退路径，未以此单独证明它最终被链接或运行。fb 两个位置已足以否定“整条 e31efd3e 不适用 Windows”的说法。
3. 字体库通过 `xorg-server/makefile:39` 链接 libXfont2，`libXfont2/makefile:21,26,55` 包含目录/字体文件与 PCF 读取源码；font alias、字形尺寸均与当前依赖有关。尚未验证任何攻击者可控字体目录或特定字形输入的运行时权限。
4. DRI2：`include/dix-config.h:404` 明确 undef DRI2；服务器 Windows 库清单无 hw/xfree86/dri2，glx Windows makefile 也未编入 glxdri2.c。因此仅限 DRI2 实现的公开问题可标为当前 Windows 构建不适用，而非源码已修复。还可见 DRI3、XF86DRI、GLX_DRI 分别在 `:51`、`:401`、`:57` 关闭。
5. GLAMOR：`include/dix-config.h:510` undef GLAMOR，Windows 服务器库清单不包含 glamor。仅位于 glamor 的 atlas/纹理等修复可从当前构建影响排除；共享 fb/mi 修复不可排除。
6. xfree86：Windows 服务器选择 hw/xwin 并无 hw/xfree86 服务器/驱动库，`include/dix-config.h:359` 关闭 XF86VIDMODE。只在 hw/xfree86 的模式设置/驱动/输入实现的修复可从本构建排除。不能按名称含 “XFree86” 统一排除：`include/dix-config.h:356` 仍启用 XF86BIGFONT，`Xext/Makefile:17` 编入 xf86bigfont.c，`mi/miinitext.c:127` 注册 XFree86-Bigfont；makefile.before 也引用 hw/xfree86/common 头文件路径。因此这是按具体编译单元的边界，不是整个名称空间绝对未用。

DRI2、GLAMOR、xfree86 的检查限于当前 Windows 构建路径，不宣称仓库在其他平台或自定义配置下安全。未执行链接器或运行时二进制检查。

## 补查：CVE-2025-49179 与 CVE-2025-49180

这两项主修复分别属于 RECORD 和 RandR，不能归入 xfree86 构建排除。

| 事项 | 源码状态 | 本地缺失特征 | 官方对应证据 |
|---|---|---|---|
| CVE-2025-49179 | 需回补 | `xorg-server/record/record.c:1294` 的 RecordSanityCheckRegisterClients 在 `:1302-1304` 直接以 `4*nClients + SIZEOF(xRecordRange)*nRanges` 计算请求长度，缺少计数与乘加溢出前置检查 | 官方 `record/record.c:1303-1307` 先拒绝 `nClients > LimitClients`，再拒绝 `nRanges > (MAXINT - 4*nClients)/SIZEOF(xRecordRange)`，均返回 BadValue。稳定 `8592cab6820f77c209c2ea9a7b94e0d4d1ac848c` / master `2bde9ca49a8fd9a1e6697d5e7ef837870d66f5d4`，ChangeLog 3444-3472。 |
| CVE-2025-49180 | 需回补；Windows 有效 provider 前置仍须单独判断 | `xorg-server/randr/rrproviderproperty.c:133` 的 RRChangeProviderProperty 在 `:173-175` 求累计 total_len，然后 `:180-181` 直接把 `total_len * size_in_bytes` 写入 int total_size 并分配 | 官方 `randr/rrproviderproperty.c:182-183` 在乘法前增加 `if (total_len > MAXINT / size_in_bytes) return BadValue`。稳定 `7c626aa63af274a347b91dd923027e715ed89023` / master `3c3a4b767b16174d3213055947ea7f4f88e10ec6`，ChangeLog 3421-3440。 |

RECORD 的 Windows 证据：`include/dix-config.h:299` 定义 XRECORD；`xorg-server/record/makefile:1` 编译 record.c；`xorg-server/makefile:23` 链接 librecord；`mi/miinitext.c:146` 注册 RECORD，运行时受 noTestExtensions 控制。普通请求派发 `record.c:2468-2470` 提供 CreateContext / RegisterClients；`:1867`、`:1894` 调用 RecordRegisterClients，后者 `:1554` 执行缺失保护的检查。swapped 包装中的额外长度验证不弥补普通请求入口的缺失。该保护使用的 MAXINT 已在本地 `include/misc.h:178` 定义；LimitClients 已有服务器配置与 64–2048 的范围控制（`os/utils.c:640-646`），无须引入新 API。

RandR 的 Windows 证据：`include/dix-config.h:296` 定义 RANDR；`randr/makefile:19` 编入 rrproviderproperty.c；`xorg-server/makefile:22` 链接 librandr；`mi/miinitext.c:131` 注册扩展；`randr/rrdispatch.c:263` 分派 ChangeProviderProperty，协议入口在 `rrproviderproperty.c:531` 调用缺失保护的函数。本地协议入口已有 format 为 8/16/32 的检查（`:509-511`）及当前请求长度检查（`:514-518`），但未保护函数内 append/prepend 累计后的 total_len，不能据此认定修复已存在。

RandR 的动态前置边界必须保留：协议入口 `rrproviderproperty.c:520` 先执行 VERIFY_RR_PROVIDER。对全仓 C 文件检索 RRProviderCreate，除函数定义 `randr/rrprovider.c:391` 外，唯一调用位于 `hw/xfree86/modes/xf86RandR12.c:1762`；XWin 的 `hw/xwin/winrandr.c:232-245` 初始化 RandR 并创建 CRTC/output，没有看到创建 provider。故主修复代码确实进入 Windows 构建，源码需回补；但不能仅凭 RANDR 启用就声称当前 XWin 有可供请求引用的 provider。此静态结果没有证明当前 Windows 启动配置能到达该内存分配点，更没有证明利用性。

`0235121c6a7a6eb247e2addb3b41ed6ef566853d`（稳定 `bb89548515a75d30399c3c9d7cae9f3706241808`，ChangeLog 3400-3417）是另一项配套 xfree86 驱动 provider 函数指针 NULL 检查，ChangeLog 明确标为 “Related to CVE-2025-49180”。它可以按当前 xfree86 驱动构建边界排除，但不能替代上述主补丁的状态判定；不要将两项 SHA 混为一项。
