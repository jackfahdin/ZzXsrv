# 本地验证记录

已完成的首轮基线：[2026-09-09 Windows x64 Release](2026-09-09-baseline.md)。报告记录被测源码提交、本地标签、实际结果和未验证范围。

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

`buildall.ps1 -EnvironmentReport <path>` 在工具选择和 Visual Studio 环境初始化成功后
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
powershell -NoProfile -ExecutionPolicy Bypass -File .\buildall.ps1 -CheckOnly -EnvironmentReport .local-validation\environment-ps51.json
pwsh -NoProfile -File .\buildall.ps1 -CheckOnly -EnvironmentReport .local-validation\environment-ps7.json
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
