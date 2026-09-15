# Windows 原生构建指南

使用 PowerShell 和原生 Windows 工具构建，无需 WSL 或 Cygwin。以下命令均从仓库根目录执行；构建入口为 [scripts/build/buildall.ps1](../../scripts/build/buildall.ps1)。旧环境说明已移至[历史构建文档](../history/legacy-build.md)。

## 准备工具

| 工具 | 要求 |
| --- | --- |
| Visual Studio 2022 | 安装“使用 C++ 的桌面开发”、v143 x86/x64 工具和 Windows SDK |
| CMake | 3.21 或更新版本；优先使用 VS2022 随附的 CMake，也可用 `-CMakePath` 指定 |
| Windows Python | 3.11 或更新版本，在同一个解释器中安装 lxml、Mako、PyYAML |
| Strawberry Perl | 原生 Windows Perl |
| NASM、WinFlexBison、gperf | 原生 Windows 可执行文件 |
| JOM（可选） | 用于并行构建 OpenSSL；缺失时使用 NMake |

脚本不会下载或安装工具。它通过 `vswhere` 查找 VS2022，从 `PATH` 查找生成工具，也会检查本地磁盘常见的 `Tools` / `SoftWare` 路径中的 WinFlexBison 和 Qt gperf/JOM。依赖 Cygwin/MSYS 的可执行文件会被拒绝。

**源码检出路径不能含空格**：现有 mhmake 的头文件和库路径列表仍有这一限制。工具路径和最终便携运行目录可以含空格，传参时请加引号。构建过程的环境修改是临时的。

文件筛选与字体压缩使用 Python；核心键盘数据由仓库内的 Python/Perl 生成器生成，无需 Meson。此步骤不包含 Gettext 翻译目录。

## 预检与完整构建

```powershell
.\scripts\build\buildall.ps1 -CheckOnly
.\scripts\build\buildall.ps1 -Configuration Release -Architecture x64 -Jobs 8
```

若当前执行策略限制脚本，可只对本次 PowerShell 进程指定策略：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build\buildall.ps1 -CheckOnly
```

显式工具路径优先于自动查找，指定的路径无效时会立即失败：

```powershell
.\scripts\build\buildall.ps1 -CheckOnly `
    -PythonPath D:\SoftWare\Python3\python.exe `
    -WinFlexBisonPath D:\SoftWare\win_flex_bison-2.5.25 `
    -GperfPath D:\SoftWare\Qt\5.15.2\Src\gnuwin32\bin\gperf.exe
```

还可使用 `-VisualStudioPath`（VS 安装目录）、`-PerlPath`、`-NasmPath`、`-JomPath` 和 `-CMakePath`（可执行文件路径）。示例中的本机路径需要替换成实际安装位置。

## 构建阶段

| 参数 | 执行内容 |
| --- | --- |
| `-Stage All` | 完整构建并整理便携运行目录，默认值 |
| `-Stage Dependencies` | 构建 mhmake、FreeType、OpenSSL、pthreads、zlib、libiconv 和 libxml2 |
| `-Stage BuildTool` | 只构建 mhmake，始终使用 Release |
| `-Stage Server` | 复用依赖和 mhmake，构建服务器并整理运行目录 |
| `-Stage Portable` | 只根据已有产物整理运行目录，不编译 |

默认组合是 `All`、`x64`、`Release`。参数也接受 `Debug` 和 `Win32`，但这些组合尚未验收；使用 `Server` 前应先为所选配置构建依赖。

## 运行与便携目录

```powershell
.\dist\x64\Release\xlaunch.exe
```

`xlaunch.exe` 是启动向导，也可直接启动同目录的 `vcxsrv.exe`。请完整保留目录中的运行 DLL、字体、区域设置和键盘数据。原始产物 `src\xorg-server\obj64\servrelease\vcxsrv.exe` 旁没有齐全的运行 DLL，不能独立启动。

不重新编译，只整理已有产物：

```powershell
.\scripts\build\buildall.ps1 -Stage Portable
```

整理过程读取现有 NSIS 文件清单，复制本地编译产物与匹配的 Visual Studio CRT DLL。它不安装软件、不写注册表，也不要求安装 NSIS。现有 NSIS / `packageall.sh` 安装包流程独立存在，仍需 NSIS；便携目录整理不代表安装包已经构建或验收。

## 依赖来源与构建边界

libxml2 2.15.4 与 GNU libiconv 1.19 从仓库固定源码通过 MSVC/CMake 构建，并链接同配置的 zlib。组件输出分别位于 `third_party/libxml2/build/<Architecture>/<Configuration>/` 和 `third_party/libiconv/build/<Architecture>/<Configuration>/`；XML 生成头文件位于前者的 `include/`。旧 XML 头文件、导入库及 DLL 已成套替换，不能再从历史运行目录混入。

构建入口先生成 mhmake 和 zlib，再构建 iconv/XML；CMake 只用于此依赖子构建，不替代服务器的 mhmake 工程。独立子入口 [buildxml.ps1](../../scripts/build/buildxml.ps1) 要求先准备对应配置的 zlib 导入库。便携目录包含新 DLL 及其许可证和来源说明。

XLaunch 保留本地压缩配置和 HTTP 配置读取。HTTP 传输使用 Windows WinHTTP，系统代理设置与历史 libxml2 环境变量代理不完全相同；HTTPS、代理和认证挑战未作本轮实际环境验收。来源、补丁及未知项见[依赖来源清单](../dependencies/SOURCES.md)，原 2.9.1 二进制的未知来源保留在[历史评估](../validation/2026-09-15-libxml2-assessment.md)。原生构建不等于所有第三方来源均已闭合，也不保证重复编译的二进制逐字节相同。

## 保存工具环境

预检时导出实际选中的工具及 Python 包版本：

```powershell
.\scripts\build\buildall.ps1 -CheckOnly `
    -EnvironmentReport .local-validation\environment.json
```

实际构建时使用同一参数，可记录该次构建所用环境：

```powershell
.\scripts\build\buildall.ps1 -Jobs 8 `
    -EnvironmentReport .local-validation\environment.json
```

报告包含所选路径和可获取的版本，不导出整个进程环境。请将报告与对应构建日志一同保存。

## 验证运行目录

使用 64 位 Windows Python 3.11 或更新版本：

```powershell
$environment = Get-Content .local-validation\environment.json -Raw | ConvertFrom-Json
$selectedPython = $environment.tools.python.path
$builtCommit = (git rev-parse HEAD).Trim() # 仅当产物确实由当前提交构建时使用。
& $selectedPython -B tools/verify_runtime.py --runtime dist/x64/Release `
    --dumpbin $environment.tools.dumpbin.path --source-commit $builtCommit `
    --output .local-validation/runtime-001 --display 97 --timeout 30
```

`--source-commit` 必须是实际构建这些二进制的完整提交号；验证器不能自行推断或证明产物的源码来源。若使用既有产物，请将示例变量改为实际构建提交。

每次运行使用新的输出目录，输出目录和运行目录不得互相包含。已有证据不会被覆盖。结果包含 `result.json`、`dependencies.json` 以及独立的 dumpbin、版本、认证、服务器和客户端日志。若输出路径被拒绝，无法在该路径写 JSON，原因会输出到 stderr。

验证包括：

- 检查全部 EXE/DLL 的 PE 架构、直接与延迟导入，包括 Mesa 对 `vcxsrv.exe` 的导入。依赖须在运行目录根目录或原生 `System32` 解析；API-set 名称记作 Windows 系统契约。
- 检查服务器版本，并通过带认证的 TCP 连接查询根窗口。只有根窗口尺寸为正才算通过，仅有服务器进程存活不够。
- 子进程的 `PATH` 只包含运行目录与 `System32`。临时随机 Xauthority 凭据从日志中隐去，待自有子进程退出后删除；不修改全局环境、注册表或防火墙。

显示号 97 对应 TCP 端口 6097；若已占用，请改用其他 `--display`。工具不会停止其他 X Server。`--timeout` 限制每项依赖、版本、认证命令及启动查询循环的等待时间；清理阶段另有有限的进程等待。

退出码 `0` 表示 `PASS`。缺少前提条件记为 `NOT_RUN` 并返回非零；依赖、启动、连接或清理失败记为 `FAIL` 并返回非零。

## 脚本测试与桌面集成

测试使用 Python 标准库 unittest，无需额外测试框架：

```powershell
python -B -m unittest discover -s tools/tests -v
```

默认单元测试不启动桌面程序。本机工具测试需在 **VS2022 x64 开发环境**中执行：可以从“x64 Native Tools Command Prompt for VS 2022”启动 PowerShell，再设置 `VCXSRV_TEST_LOCAL_TOOLS=1`。确认 `cl.exe` 可用；构建脚本结束时会还原环境，所以普通终端不会因为运行过构建脚本就自动获得编译器环境。

```powershell
$env:VCXSRV_TEST_LOCAL_TOOLS = '1'
python -B -m unittest discover -s tools/tests -v
```

要启用真实桌面集成，请在单独的 PowerShell 进程设置以下变量；启用后，运行目录、dumpbin 和源码提交三个参数都必须提供：

```powershell
$environment = Get-Content .local-validation\environment.json -Raw | ConvertFrom-Json
$selectedPython = $environment.tools.python.path
$builtCommit = (git rev-parse HEAD).Trim() # 改为实际构建这些产物的提交。
$env:VCXSRV_TEST_RUNTIME = '1'
$env:VCXSRV_RUNTIME_DIR = (Resolve-Path dist/x64/Release).Path
$env:VCXSRV_DUMPBIN = $environment.tools.dumpbin.path
$env:VCXSRV_SOURCE_COMMIT = $builtCommit
& $selectedPython -B -m unittest discover -s tools/tests -p test_verify_runtime.py -v
```

集成测试按顺序覆盖原运行目录、缺少 `libX11.dll` 的临时副本，以及恢复文件后路径含空格的副本，只删除自己创建的临时副本。

## 现有验证证据

2026-09-09 的干净构建基线以历史源码提交 `a4adc3dc3f2158c2308133cecee19a71cf62bcc8` 为输入，完成 Windows x64 Release `All`、43 项测试（无跳过）、35 个 PE 依赖检查和经认证的根窗口查询。环境包括 VS2022 / MSVC 14.44、SDK 10.0.26100.0、Python 3.14 和 WinFlexBison 2.5.25；Windows PowerShell 5.1 与 PowerShell 7 的预检另有记录。基线还记录了最小 PATH 下原生 WGL 初始化和 1920×1080 根窗口结果，该尺寸只是当时主机的结果。

上述为历史证据。前次脚本与文档目录整理的构建和检查记录于[目录迁移报告](../validation/2026-09-10-readme-layout.md)；当前源码分层边界见[源码目录设计](../designs/2026-09-10-source-layout.md)。旧标签和提交的现状以[仓库整理记录](../validation/2026-09-10-repository-reorganization.md)为准。GLX、XFIXES 后续验证分别见[验证索引](../validation/README.md)，当前候选与主线状态见[计划状态](../maintenance/PLAN_STATUS.md)。

静态导入检查不能覆盖所有动态 `LoadLibrary` 路径；根窗口查询不能验证完整 GUI / OpenGL、剪贴板、输入法或多显示器行为。Debug、Win32、安装包和更广泛应用兼容性尚未全面验收。证据格式及后续记录方式见[验证说明](../validation/README.md)。
