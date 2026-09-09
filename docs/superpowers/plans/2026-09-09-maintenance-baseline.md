# 本地维护基线实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 executing-plans 推进任务；独立子任务使用 subagent-driven-development。步骤使用复选框跟踪。2026-09-09 开始执行，未勾选项尚未验收完成。

**目标：** 建立 Windows x64 Release 的干净构建与自动运行验证基线，并保留可复查的本地证据。

**架构：** 复用现有 PowerShell 构建入口与 Python 标准库测试。增加可选环境报告和独立运行验证工具；在新建本地 worktree 中运行完整构建，最后把结果摘要和被验证提交关联。

**技术栈：** PowerShell 5.1/7、VS2022/MSVC v143、Python 3.11+、unittest、Git 本地 worktree。

**规格：** [第一阶段验收规格](../specs/2026-09-09-maintenance-baseline-design.md)。执行者同时阅读 [维护路线](../../MAINTENANCE.md)。

## 全局约束

- 只在本地保存代码、提交和验证记录；不执行 push 或远程发布。
- Windows x64 Release；PowerShell 5.1/7；VS2022/MSVC v143；Python 3.11 或更新版本。
- 不依赖 WSL/Cygwin，不自动下载或安装工具，不自动更新第三方组件。
- 源码路径无空格；工具路径和运行目录路径允许含空格。
- 保留当前工作目录和运行目录；干净构建从已提交源码建立独立本地 worktree。
- 运行验证不关闭访问控制，不修改全局环境、注册表或防火墙，不终止其他 VcXsrv 实例。

## 文件职责

| 文件 | 操作 | 职责 |
| --- | --- | --- |
| `buildall.ps1` | 修改 | 在工具初始化完成后按参数导出环境报告 |
| `tools/tests/test_windows_build.py` | 修改 | 验证报告的来源、字段、无构建副作用和环境恢复 |
| `tools/verify_runtime.py` | 创建 | PE 依赖检查、启动、认证连接、超时、清理、结果 JSON |
| `tools/tests/test_verify_runtime.py` | 创建 | 依赖解析、错误位数、失败/超时清理和真实运行集成用例 |
| `.gitignore` | 修改 | 忽略根目录 `.local-validation/` 原始证据 |
| `docs/validation/README.md` | 创建 | 证据字段、复现命令、通过与失败的判定规则 |
| `docs/validation/2026-09-09-baseline.md` | 执行结束时创建 | 首轮实际结果；日期按实际执行日调整 |
| `HOW_TO_BUILD.txt` | 修改 | 报告/验证工具用法和已完成的支持范围 |

不预先创建虚假的通过报告或基线标签。实现工作使用本地 `codex/maintenance-baseline` 分支；如果已有用户工作，先按 using-git-worktrees 技能隔离。

## 任务 1：构建入口导出实际环境（B1、B5）

**文件：** `buildall.ps1`、`tools/tests/test_windows_build.py`、`.gitignore`、`docs/validation/README.md`。

- [x] 在 `WindowsBuildTests` 增加真实 CheckOnly 用例，报告输出路径使用含空格的临时目录；断言所选 Python 与包版本来自指定解释器。

```python
def test_check_only_reports_selected_python(self):
    import json
    import sys
    with tempfile.TemporaryDirectory(prefix="vcxsrv report ") as directory:
        report = Path(directory) / "environment.json"
        result = self.run_check("-PythonPath", sys.executable,
                                "-EnvironmentReport", str(report))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(report.read_text(encoding="utf-8-sig"))
        self.assertEqual(Path(data["tools"]["python"]["path"]), Path(sys.executable))
        self.assertEqual(data["target"], {"architecture": "x64", "configuration": "Release"})
        self.assertTrue({"lxml", "mako", "PyYAML"} <= data["python_packages"].keys())
```

- [x] 用下列命令确认当前缺少参数导致该用例失败；新用例遵循现有 `VCXSRV_TEST_LOCAL_TOOLS` 本机测试开关。

```powershell
$env:VCXSRV_TEST_LOCAL_TOOLS = '1'
python -B -m unittest discover -s tools/tests -p test_windows_build.py -v
```

- [x] 新增可选字符串参数 `EnvironmentReport`。在 CheckOnly 返回之前收集规格定义的字段，通过选中的 Python 查询 `importlib.metadata.version()`，通过已初始化的 MSVC 环境记录 SDK/MSVC。`ConvertTo-Json -Depth 6` 导出 UTF-8；先完成采集再写文件。版本不可用填 null，命令失败不伪造成功。

- [x] 将已有环境恢复/目录恢复用例扩展到提供报告路径的调用；失败路径使用不存在的显式 Python 路径，断言未输出一份成功报告。保留不触发编译的时间戳检查。

- [x] 写明报告字段和原始日志位置，在 `.gitignore` 增加 `/.local-validation/`。复跑本文件测试，并分别在 Windows PowerShell 5.1 和 PowerShell 7 下执行 CheckOnly 报告命令，检查 JSON 能解析。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\buildall.ps1 -CheckOnly -EnvironmentReport .local-validation\environment-ps51.json
pwsh -NoProfile -File .\buildall.ps1 -CheckOnly -EnvironmentReport .local-validation\environment-ps7.json
```

- [x] 检查 diff 后提交，中文标题为“记录实际构建环境（任务 1）”，中文正文说明选中工具、报告字段和验证结果。只暂存本任务文件。

## 任务 2：运行目录自动验收（B2、B3、B5）

**文件：** `tools/verify_runtime.py`、`tools/tests/test_verify_runtime.py`、`HOW_TO_BUILD.txt`、`docs/validation/README.md`。

- [ ] 编写依赖解析的失败测试。实现接口约定为 `parse_dependencies(text) -> list[str]`，去重、忽略 dumpbin 的统计段，兼容 CRLF；包括直接和延迟导入段。

```python
def test_parse_dependency_sections(self):
    text = "  Image has the following dependencies:\r\n    libX11.dll\r\n    KERNEL32.dll\r\n  Image has the following delay load dependencies:\r\n    OPENGL32.dll\r\n  Summary\r\n    1000 .data\r\n"
    self.assertEqual(parse_dependencies(text),
                     ["libX11.dll", "KERNEL32.dll", "OPENGL32.dll"])
```

- [ ] 增加行为用例：目录缺少 vcxsrv/xauth/xwininfo 时不启动任何进程；dumpbin 非零退出不能当成“没有依赖”；32 位 PE 混入 x64 目录失败；无法解析的导入失败并指出引用者；报告不含认证 cookie。用 `python -B -m unittest discover -s tools/tests -p test_verify_runtime.py -v` 记录失败结果。

- [ ] 实现 CLI 和检查逻辑。PE 架构直接读取 DOS/PE 标头的 Machine 字段并验证标头长度；dumpbin 通过参数数组调用，不拼 shell 命令。遍历运行目录全部 EXE/DLL，搜索顺序为运行目录和正确位数系统目录；API-set 记录为系统契约。Windows 64 位 Python 是本工具的执行条件，不满足则明确报错。

- [ ] 实现 `run_smoke(runtime, output, display, timeout)`。复用本机已验证过的调用方式：`vcxsrv -version`、`xauth -f ... add 127.0.0.1:97 . cookie`、带 `-auth` 的服务器、`xwininfo -display 127.0.0.1:97 -root`。显示号使用参数而非硬编码。通过单调时钟截止时间轮询，单次命令也有超时；输出根窗口正尺寸才算成功。

- [ ] 子进程使用最小 PATH 和规格定义的环境清理；启动窗口隐藏，服务器与客户端输出写入独立文件，避免 PIPE 填满。捕获加载器错误、端口占用、提前退出、超时，均写入 JSON 并返回非零。`finally` 只结束本次仍在运行的子进程，等待退出后清理临时认证文件。

- [ ] 增加可控失败测试：模拟客户端失败及超时，验证服务器清理发生；模拟预先存在的占用端口，验证未结束外部进程；调用命令参数含空格仍正常。测试这些行为，不断言无关内部调用次数。

- [ ] 在真实运行目录上执行以下命令。实际 dumpbin 路径从任务 1 报告取出；工具键名统一为 `dumpbin`。

```powershell
$environment = Get-Content .local-validation\environment-ps51.json -Raw | ConvertFrom-Json
$testedCommit = (git rev-parse HEAD).Trim()
python -B tools/verify_runtime.py --runtime dist/x64/Release --dumpbin $environment.tools.dumpbin.path --source-commit $testedCommit --output .local-validation/runtime --display 97 --timeout 30
```

- [ ] 新建临时运行副本，删除该副本中的 `libX11.dll`，确认验证失败并指出缺失导入。仅操作测试自己创建的临时目录，主运行目录保持完整。再在名称含空格的运行副本上验证成功。真实集成用例受 `VCXSRV_TEST_RUNTIME=1` 控制，并要求环境变量 `VCXSRV_RUNTIME_DIR`、`VCXSRV_DUMPBIN`、`VCXSRV_SOURCE_COMMIT`；默认不启动桌面程序。开关已启用却缺少参数时必须失败，不能跳过。

```powershell
$env:VCXSRV_TEST_RUNTIME = '1'
$env:VCXSRV_RUNTIME_DIR = (Resolve-Path dist/x64/Release).Path
$env:VCXSRV_DUMPBIN = $environment.tools.dumpbin.path
$env:VCXSRV_SOURCE_COMMIT = $testedCommit
python -B -m unittest discover -s tools/tests -p test_verify_runtime.py -v
```

此段在单独 PowerShell 进程执行；临时运行副本的测试按顺序启动服务器，不能争用同一个显示号。

- [ ] 执行完整现有脚本测试；所有已启用的必要用例通过后更新用法、证据格式并提交，中文标题为“验证运行依赖与服务器启动（任务 2）”，中文正文说明行为与测试结果。

结果 JSON 的必需字段：`schema_version`、`source_commit`、`runtime`、`started_at`、`duration_seconds`、`status`、`steps`；每个 step 含 `name`、`status`、`exit_code`、`log_paths`、`reason`。`source_commit` 取必需参数 `--source-commit`；不要把验证器自身所在的另一个 checkout 误认为运行产物来源。

## 任务 3：干净构建并建立本地基线（B4、B6）

**文件：** 实际结果报告、`HOW_TO_BUILD.txt` 的验证范围；不创建新的编译框架。

- [ ] 确认前两个任务已提交，使用以下命令新建从当前提交派生的本地 detached worktree。路径由现有项目父目录和时间戳生成；目标必须尚不存在。检查磁盘空间并记录，不因为空间不足清理用户目录。

```powershell
$repoRoot = (git rev-parse --show-toplevel).Trim()
$testedCommit = (git rev-parse HEAD).Trim()
$runId = Get-Date -Format 'yyyyMMdd-HHmmss'
$cleanRoot = Join-Path (Split-Path $repoRoot -Parent) "vcxsrv-baseline-$runId"
$evidenceRoot = Join-Path $repoRoot ".local-validation\$runId"
if (Test-Path -LiteralPath $cleanRoot) { throw 'Clean checkout target already exists' }
New-Item -ItemType Directory -Path $evidenceRoot -ErrorAction Stop | Out-Null
git worktree add --detach $cleanRoot $testedCommit
if ($LASTEXITCODE -ne 0) { throw 'Cannot create clean checkout' }
git -C $cleanRoot status --porcelain --untracked-files=all
```

- [ ] 确认状态为空；记录 worktree 提交与 `$testedCommit` 相同。列出 Git 跟踪的预编译 DLL/LIB，说明哪些会按既有构建流程使用，尤其是 libxml2。不要用“目录干净”推导“全部依赖从源码构建”。

- [ ] 从新目录运行完整 All 阶段，记录环境和完整输出。命令失败立即保留日志并定位；不要继续生成通过标签。

```powershell
Push-Location -LiteralPath $cleanRoot
try {
    powershell -NoProfile -ExecutionPolicy Bypass -File .\buildall.ps1 -Configuration Release -Architecture x64 -Jobs 8 -EnvironmentReport (Join-Path $evidenceRoot 'environment.json') *> (Join-Path $evidenceRoot 'build.log')
    if ($LASTEXITCODE -ne 0) { throw 'Clean build failed; inspect build.log' }
    $environment = Get-Content (Join-Path $evidenceRoot 'environment.json') -Raw | ConvertFrom-Json
    $selectedPython = $environment.tools.python.path
    $env:VCXSRV_TEST_LOCAL_TOOLS = '1'
    & $selectedPython -B -m unittest discover -s tools/tests -v *> (Join-Path $evidenceRoot 'tests.log')
    if ($LASTEXITCODE -ne 0) { throw 'Script tests failed; inspect tests.log' }
    & $selectedPython -B tools/verify_runtime.py --runtime dist/x64/Release --dumpbin $environment.tools.dumpbin.path --source-commit $testedCommit --output (Join-Path $evidenceRoot 'runtime') --display 97 --timeout 30
    if ($LASTEXITCODE -ne 0) { throw 'Runtime verification failed' }
} finally {
    Pop-Location
}
```

此段在单独 PowerShell 进程中执行，避免测试开关残留在维护者终端。检查 tests.log 中跳过项目的原因；BuildTool 已成功构建后，mhmake 集成用例必须实际运行。

- [ ] 保存 EXE/DLL 相对路径、大小和 SHA-256 清单用于识别本次产物；不要求与前一次编译逐字节相同。检查新 worktree 的受跟踪源码没有意外变化，保留日志、运行目录和 worktree 供复查。

- [ ] 创建实际结果摘要，写入源码提交、主机/工具版本、预编译依赖说明、各步骤退出码、测试数量及跳过原因、启动结果、原始证据位置、已知限制。B1–B6 各项逐一对照；只填写真实执行结果。

- [ ] 检查文档链接和 `git diff --check`，提交结果摘要。在被验证的源码提交上创建注释标签，名称规则为 `local-baseline-YYYYMMDD-短提交号`。标签说明指出结果摘要的位置。标签只引用 `$testedCommit`，不错误地声称随后文档提交也重新编译过。

```powershell
$baselineTag = 'local-baseline-' + (Get-Date -Format 'yyyyMMdd') + '-' + $testedCommit.Substring(0, 8)
git tag -a $baselineTag $testedCommit -m '已验证本地 Windows x64 Release 构建和启动，证据见 docs/validation'
git show --no-patch --format=fuller $baselineTag
```

## 自检与完成报告

- [ ] B1 对应任务 1；B2/B3 对应任务 2；B4 对应任务 3；B5 贯穿任务 1/2/3；B6 对应任务 3 最后两步。
- [ ] 参数、JSON 字段和示例命令一致；工具路径均能从实际环境报告取得。
- [ ] 明确区分已执行证据、未验证场景和后续阶段；失败/跳过不算通过。
- [ ] 汇报本地提交、标签、证据位置和剩余限制；不执行远程操作。
