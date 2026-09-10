# 中文 README 与目录迁移验证

> 源码分层迁移说明（2026-09-10）：本报告记录更早的脚本与文档目录整理；正文中的源码路径和“依赖源码目录保留原位”均表示当时状态。当前目录见[源码目录设计](../designs/2026-09-10-source-layout.md)和[路径映射](../history/2026-09-10-source-path-mapping.json)。

日期：2026-09-10。维护者已批准 README 中文化、项目来源说明和目录整理方案。

## 变更范围

- README 使用中文，提供项目来源、启动与构建入口、文档导航和版权说明。
- 项目来源位于 `docs/PROVENANCE.md`；原构建说明拆为 `docs/build/WINDOWS.md` 与 `docs/history/legacy-build.md`。
- 依赖来源文档、JSON 与包清单归入 `docs/dependencies/`；维护文件归入 `docs/maintenance/`；计划与设计分别位于 `docs/plans/`、`docs/designs/`。
- 原作者发行说明移到 `docs/history/upstream-releases/`，内容保留。相对文档链接更新；日期明确的历史命令保留原语境。
- 当前构建入口为 `scripts/build/buildall.ps1`。Docker 入口位于 `scripts/docker/`；旧 WSL、同步及版本辅助工具按用途位于 `scripts/legacy/`。
- `COPYING`、`makefile.before`、`makefile.after` 和依赖源码目录保留原位；`tools/` 中的内部工具保持布局。

实际导入 URL、原始上游 commit/tag 和来源证据等级没有改变。清单中的 `path` 和 `evidence` 指向当前文件位置；被迁移条目的原路径另外保留，历史固定提交的 URL 不重写成新路径。

## 路径验证

迁移前主线为 `7848dfb3a0504a43275dee7c24432c7f2a59c3b3`。临时工作区为 `D:/File/Program/GitHub/zzxsrv-layout-20260910`，本机执行材料保存在该目录的 `.local-validation/layout-20260910/`。

迁移前首次测试因调用进程未初始化 MSVC 环境，2 个原生测试类找不到 `cl.exe`；加载 VS2022 x64 开发环境后，59 项测试成功，3 项因尚无 MHMake/运行产物而跳过。此结果只作为迁移前基线，不算最终验收。

原生脚本移动后保留旧 `$PSScriptRoot` 定位时，`-Stage BuildTool` 实际报错 MSB1009，找不到 MHMake 项目。改为从脚本目录向上两级定位仓库后，相同调用已成功生成 `tools/mhmake/Release64/mhmake.exe`。环境与调用者目录恢复语义保留，测试入口同步使用新路径。

## 构建与验收

固定构建提交为 `3200891b72b73fd8c7eba693bc841741fb340b77`。新建独立检出后先验证 BuildTool，再执行完整 All 阶段；没有借用旧运行目录或旧依赖构建产物。后续报告提交只补充文档，程序源码与该固定提交一致。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build/buildall.ps1 `
    -Configuration Release -Architecture x64 -Jobs 8 `
    -EnvironmentReport .local-validation/layout-20260910/environment.json
```

构建使用 VS2022、MSVC 工具集 14.44.35207（编译器 19.44.35227）、Windows SDK 10.0.26100.0、Python 3.14.2 和 WinFlexBison 2.5.25。具体选用路径及包版本保存在 `environment.json`。OpenSSL 按原有规则使用 JOM `/J1`；整个 All 阶段的默认并行参数为 8。

| 验证项 | 结果 | 本机证据 |
| --- | --- | --- |
| x64 Release All 构建与 Portable 整理 | PASS，退出 0；生成 5,132 个文件 | `build-all.log`、`build-exit-code.txt` |
| 全部现有测试，启用本机工具及运行集成 | PASS，59 项，0 失败、0 跳过，26.078 秒 | `final-tests.log` |
| PE 架构、直接及延迟导入 | PASS，35 个 EXE/DLL | `runtime/dependencies.json` |
| 版本、认证启动、根窗口查询、进程清理 | 全部 PASS | `runtime/result.json` |
| 非根目录调用、报告路径、环境和目录恢复 | 7 项入口测试全部通过 | `script-review/windows-build-tests.log` |
| Docker 上下文、根挂载、退出码和调用者环境 | 替身命令检查通过；两入口分别模拟退出 0、37 | `script-review/docker-stub-results.json` |
| 旧 shell 脚本 | 三份 `.sh` 通过 Git Bash `-n` 语法检查 | `script-review/bash-syntax.json` |
| 文件、链接、来源与既有产物 | 原有 23,920 个受跟踪文件均有对应位置；196 条来源记录保留；210 个既有 EXE/DLL 哈希不变 | `layout-verification.json`、`before.json` |

最终测试在独立的 VS2022 x64 开发环境执行，设置 `VCXSRV_TEST_LOCAL_TOOLS=1` 与 `VCXSRV_TEST_RUNTIME=1`，运行目录为本次新构建的 `dist/x64/Release`。独立运行验证命令如下：

```powershell
$tools = Get-Content .local-validation/layout-20260910/environment.json -Raw | ConvertFrom-Json
& $tools.tools.python.path -B tools/verify_runtime.py --runtime dist/x64/Release `
    --dumpbin $tools.tools.dumpbin.path --source-commit $tools.source_commit `
    --output .local-validation/layout-20260910/runtime --display 97 --timeout 30
```

独立只读终审没有阻断项：127 个映射文件均被 Git 跟踪且文件模式保留；250 个相对 Markdown 链接存在；来源文档的固定 URL、JSON 中的修订与证据等级保持原值。此后只追加本报告和导航链接，并再次检查链接。完整迁移映射见[路径映射](../history/2026-09-10-path-mapping.json)。

历史 `versionchanges.btm` 所在的 `scripts/legacy/release/` 会命中原有 `Release` 忽略规则，已在 `.gitignore` 增加只针对该历史脚本目录的例外，确保它继续被跟踪；旧脚本的可执行位保持原值。原作者发行说明及归档脚本保留原 Git blob，不引入换行符转换造成的内容差异。

## 产物与收尾

新程序保存在 `D:/File/Program/GitHub/zzxsrv-layout-20260910/dist/x64/Release`。主仓库原有 `dist` 以及此前 GLX、XFIXES、输入候选运行目录均未覆盖。

本次临时开发分支按快进方式整合到 master，完成后解除临时 worktree 登记并删除分支；新程序和本机证据保留在上述目录中。解除登记后的目录按普通目录使用，不能再当作 Git worktree。主仓库 `.local-validation/layout-20260910/` 保存一份验证材料副本和登记恢复文件。远程同步结果以最终 Git 引用核对为准。

本轮没有更改 X Server 或依赖库的生产源码，也没有合入待验收的输入候选。Docker 与旧 WSL 只验证迁移相关的入口路径、参数或语法，不运行其历史构建环境，不把静态检查写成兼容性验收。已有运行目录继续保留，目录移动不等于升级依赖或完成新的 GUI 场景验收。
