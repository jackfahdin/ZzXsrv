# 本地验证记录

[R9.4 Fontconfig 2.18.3](2026-09-16-r9-fontconfig.md)：R9.4 已于 2026-09-16 取得本版本使用正常的反馈并快进合入 master。Fontconfig 2.18.3 的完整构建、合入前后各 449 项回归（0 跳过）、7 项 Fontconfig 消费者检查、候选独立运行和新旧缓存共存检查通过。编译源码 `6b2f8aecfefd52bd18dee3e95e754309cab6d38e`；5152 个交付文件及摘要不变。本版本实际使用正常，未提供逐项测试明细，未确认范围保留；分支、工作区与新旧运行目录保留，未推送。

[R9.3 Pixman](2026-09-16-r9-pixman.md)：R9.3 已于 2026-09-16 取得“R9.3 正常，合入”的反馈并快进合入 master。Pixman 0.46.4 的完整构建、合入前后各 442 项回归（0 跳过）、候选独立运行和实际 Render 像素检查通过。编译源码 `d9117d088946b0e7a5fa45f19f952c7522d099d3`；5150 个交付文件及摘要不变。本版本实际使用正常，未提供逐项测试明细，未确认范围保留；分支、工作区与新旧运行目录保留，未推送。

[R9.2 libxcb](2026-09-16-r9-xcb.md)：R9.2 已于 2026-09-16 取得“R9.2 正常，合入”的反馈并快进合入 master。libxcb/xcb-proto 保持 1.17.0，补齐来源记录并修正生成器数组分配；完整构建、合入前后各 433 项回归通过（0 跳过），候选独立运行检查通过。构建源码 `17f39e75cfc44c42b8b1af8225841a643d1c510f`；5148 个交付文件及摘要不变。本版本实际使用正常，未提供逐项测试明细，未确认范围保留；分支、工作区及新旧运行目录保留，未推送。

[R9.1 libX11 1.8.13](2026-09-15-r9-libx11.md)已于 2026-09-16 取得“R9.1 正常，合入”的反馈后，已快进合入 master。libX11 1.8.13 的完整构建、合入前后各 425 项回归（0 跳过）和候选独立运行检查通过。构建源码 `f1e9330b0d62078e4a3ed5bdb0b0fecce9f2830d`；5145 个交付文件及摘要不变。本版本实际使用正常，未提供逐项测试明细，未确认范围保留；分支、工作区与运行目录保留，未推送。

[R8 键盘、图标与压缩依赖](2026-09-15-r8-dependencies.md)已于 2026-09-15 取得“R8 正常，合入”的反馈并快进合入 master：xkbcomp 1.5.0、libXpm 3.5.19、zlib 1.3.2；完整构建、合入前后各 420 项测试通过（0 跳过），5143 个运行文件不变。构建源码 `4f8ddf84a`，实际反馈边界和整合证据见报告，未推送。

[R7 OpenSSL 3.5.8 LTS](2026-09-15-openssl.md)已于 2026-09-15 取得“R7 正常，合入”的反馈并快进合入 master：官方 5767 文件原样导入，完整 x64 Release All 构建成功；合入前后各 410 项测试通过、0 跳过，5136 个运行文件不变。构建源码 `e41de0979`，独立运行及旧对象/新 DLL 兼容对照通过；实际反馈边界和整合验证见报告，未推送。

[R6 Expat 升级](2026-09-15-expat.md)已于 2026-09-15 取得“R6 正常，合入”的反馈并快进合入 master：官方 Expat 2.8.4、Windows 随机源与静态配置，保留 Mesa 的静态配置行为。完整构建经 MSVC 异常恢复后完成，合入前后各 404 项测试通过、0 跳过，独立运行检查 PASS，5134 个运行文件不变；构建源码 `73e74d4bd`。合入验证与人工反馈边界见报告，未推送。

[R5 原生 XML 依赖整合](2026-09-15-libxml2-native.md)已接入 libxml2 2.15.4 和 libiconv 1.19，保留 gzip/HTTP 配置读取，393 项自动回归通过、0 跳过。构建源码 `af0cd70e4`，2026-09-15 取得“R5 正常 ，合入吧”的反馈后快进合入 master；完整构建、合入验证、来源和人工反馈边界见报告，未 push。

[libxml2 编码与文件读取兼容性调查](2026-09-15-libxml2-compatibility.md)记录正式实施前的调查：原生 libiconv 1.19 与 libxml2 2.15.4、现有 zlib 联动验证，9 组编码及实际 XLaunch/Fontconfig 正常消费者通过。gzip 需显式解压选项，HTTP 需应用层适配；调查阶段尚未替换生产库，后续正式实施与整合见上方 R5 报告。

[libxml2 来源与重建评估](2026-09-15-libxml2-assessment.md)记录当时继承的 x64 DLL 为 2.9.1，并在隔离目录构建官方 2.15.4，验证实际 XLaunch 配置往返和 Fontconfig 缓存。无 iconv 试验版无法读取旧版支持的 GBK/GB18030，当时未直接替换；后续兼容调查及正式实施见上方报告。

[Fontconfig Windows 目录枚举修复](2026-09-14-fontconfig-directory.md)已于 2026-09-15 取得本版本“没问题，继续”的反馈并快进合入 master，合入前后各 370 项测试通过、0 跳过。实际缓存创建及重载均为 2 条记录，运行目录保持不变；人工反馈的逐项边界和构建恢复记录见报告。仅本地整合，未 push。

[R4 字体依赖升级](2026-09-14-font-dependencies.md)已取得新版本启动、gitk、中文显示和重启正常的反馈并快进合入 master，包含 libXfont2 2.0.9、FreeType 2.14.3 和公共头文件同步；合入前后各 363 项测试通过。字体／字号切换未确认，异常输入回归缺口保留，详见报告。

当前 [GLX 属性、字体消费方及 RANDR 整合报告](2026-09-14-r3-final.md)记录三项独立提交与实际使用确认；已快进合入 master，合入前后各 350 项测试通过、0 跳过。R3 历史清单 21 项均已整合。传统字体、OpenGL 和双向复制未测试；临时分支及工作区登记因自动审批阻止清理而保留。

当前 [XSYNC/PRESENT/屏保报告](2026-09-11-sync-present.md)和[认证整合报告](2026-09-11-auth-binary.md)记录两组各自的使用确认与快进整合；合入前后各 201 项测试通过、0 跳过。临时分支及工作区登记已清理，运行目录保留；双向复制未测试。

前组 [XKB 验证与整合报告](2026-09-10-xkb.md)记录 8 项修复、17 个补丁来源及验证结果。维护者已确认本组使用正常，修复已快进合入 master；合入后 158 项测试通过、0 跳过。临时分支与工作区登记已清理，运行目录保留。

前组 R3 的 [RENDER/RECORD 验证与整合报告](2026-09-10-render-record.md)记录两项修复、来源及验证结果。维护者已确认本组使用正常，修复已快进合入 master；合入后 97 项测试通过，临时分支及工作区登记已清理，运行目录保留。

更新日期：2026-09-10。[源码目录分层报告](2026-09-10-source-layout.md)记录本次完整构建、61 项测试与运行验证。[中文 README 与目录迁移报告](2026-09-10-readme-layout.md)记录前次脚本路径调整、文档导航、构建与验证范围；当前源码分层见[设计](../designs/2026-09-10-source-layout.md)与[路径映射](../history/2026-09-10-source-path-mapping.json)。此前[仓库整理报告](2026-09-10-repository-reorganization.md)记录历史线性化、旧引用归档和首次推送。[依赖来源清单](../dependencies/SOURCES.md)记录组件来源证据和未知项。

当前状态见 [计划状态](../maintenance/PLAN_STATUS.md)；逐项人工场景见 [兼容性记录](../maintenance/COMPATIBILITY.md)。[XFIXES 修复报告](2026-09-09-xfixes-request-length.md) 记录用户使用确认、主线整合及合入后的 59 项测试结果。

当前唯一长期分支为线性 master，origin 为 `git@github.com:jackfahdin/ZzXsrv.git`；不再保留 upstream、旧工作分支或旧 tags。[依赖快照与开发主线](2026-09-09-component-baseline.md)只记录当时的历史方案。旧报告中的提交号、标签名、分支名和 worktree 命令属于历史语境，不代表当前引用或目录仍可按原方式使用。

[X Server 适用性盘点](2026-09-09-xserver-applicability.md)保留此前逐项核对结果；[输入处理候选](2026-09-09-xserver-input.md)已取得本版本实际使用反馈，修复按当前目录恢复并合入主线。本次完整构建、73 项测试与运行检查见[输入整合报告](2026-09-10-xserver-input-integration.md)。历史候选的源码、运行目录和归档继续保留，不能再当作 worktree 或未完成任务重复导入。GUI-001 已关闭，不再跟进，剪贴板/OpenGL 等未验证范围继续保留。

已完成的首轮基线：[2026-09-09 Windows x64 Release](2026-09-09-baseline.md)。报告记录历史被测源码提交、当时标签、实际结果和未验证范围；标签已归档后删除，验证结论仍限于原源码和运行目录。

后续 GLX 修复、构建问题及候选程序的验证见 [2026-09-09 GLX 上下文标签修复](2026-09-09-glx-context-tags.md)。实际应用验收与自动检查分别记录。

本目录保存可提交的验证摘要。主机相关的原始记录保存在仓库根目录的
`.local-validation/`，该目录已被 Git 忽略。建议每次验证使用独立的运行编号，布局如下：

```text
.local-validation/<run-id>/
├── environment.json
├── build.log
├── tests.log
└── runtime/
    ├── result.json
    └── *.log
```

不要把完整环境变量、认证 cookie、临时 Xauthority 文件或运行二进制写入提交的摘要。
失败记录应保留在自己的运行编号下，重跑时新建目录。

## 环境报告

`scripts/build/buildall.ps1 -EnvironmentReport <path>` 在工具选择和 Visual Studio 环境初始化成功后
写入 UTF-8 JSON。`-CheckOnly` 同样生成报告，但不执行编译或源码生成。报告采用以下结构：

| 字段 | 内容 |
| --- | --- |
| `schema_version` | 当前为整数 `1` |
| `source_commit` | 执行构建脚本的源码提交，40 位 Git SHA |
| `target` | `architecture` 和 `configuration` |
| `host` | 主机名、Windows 版本和当前 PowerShell 版本 |
| `tools` | 本阶段实际选择的工具；每项包含 `path` 和 `version` |
| `python_packages` | 被选中 Python 中的 `lxml`、`mako` 和 `PyYAML` 版本 |

`tools` 可使用 `python`、`cl`、`msbuild`、`dumpbin`、`flex`、`bison`、
`perl`、`nasm`、`gperf`、`jom`、`msvc` 和 `sdk` 键。路径指向实际选中的文件；
`msvc` 与 `sdk` 的路径为已初始化环境中的目录。无法可靠取得的版本写为 `null`。
没有为当前阶段选择的工具不出现在对象中，例如 `BuildTool` 报告不包含
`perl`、`nasm`、`gperf` 或 `jom`。报告不会记录完整环境变量。

可分别检查 Windows PowerShell 5.1 与 PowerShell 7：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build\buildall.ps1 -CheckOnly -EnvironmentReport .local-validation\environment-ps51.json
pwsh -NoProfile -File .\scripts\build\buildall.ps1 -CheckOnly -EnvironmentReport .local-validation\environment-ps7.json
Get-Content .local-validation\environment-ps51.json -Raw | ConvertFrom-Json | Out-Null
Get-Content .local-validation\environment-ps7.json -Raw | ConvertFrom-Json | Out-Null
```

参数解析、工具检查、Python 包查询或 Git 提交查询失败时，命令返回非零，并且不会为
本次新路径写出一份成功报告。

## 构建和运行记录

完整基线运行把构建的全部控制台输出保存为 `build.log`，把脚本测试输出保存为
`tests.log`。运行验证器把机器可读结果写入 `runtime/result.json`，并把各子进程输出保存为
同目录下的独立日志。提交的摘要应记录原始目录、被验证的源码提交、命令、退出码、
测试数量、跳过原因及已知限制。

运行结果 JSON 的顶层字段为 `schema_version`、`source_commit`、`runtime`、
`started_at`、`duration_seconds`、`status` 和 `steps`。每个步骤包含 `name`、
`status`、`exit_code`、`log_paths` 和 `reason`。`source_commit` 由验证命令的必需参数提供，
用于关联构建来源；它本身不能证明二进制来源。

## 判定规则

- `PASS`：该步骤已执行，所有规定断言成立且命令退出码为零。
- `FAIL`：该步骤已执行但检查或命令失败；结果必须指出失败步骤和原因。
- `NOT_RUN`：前置条件不满足或更早步骤失败，当前步骤未执行；整体结果为失败。
- `SKIP`：显式可选的场景未运行并记录原因；跳过不算通过。

只有环境采集、干净构建、脚本测试、全部运行依赖检查和认证启动检查都为 `PASS`，
才能把本次运行记为 Windows x64 Release 本地基线。静态导入扫描不覆盖任意
`LoadLibrary` 路径，最小启动检查也不证明完整 OpenGL、输入法、剪贴板或多显示器兼容性。
