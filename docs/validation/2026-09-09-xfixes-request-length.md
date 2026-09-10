# XFIXES 断开模式请求长度修复验证

> 2026-09-10 历史说明：本文保留当时的方案、提交号与验证结果。旧分支、标签和工作区登记已清理，源码及运行目录保留为普通目录；旧命令不应直接照搬执行。现行规则见[维护规则](../UPSTREAM.md)，对应关系与恢复材料见[整理记录](../validation/2026-09-10-repository-reorganization.md)。旧依赖快照清单见[历史 JSON](../history/2026-09-09-dependency-snapshot.json)；当前不再维护上游源码分支。

日期：2026-09-09。开发基线为已验收的 `a55ce37fd`，分支为 `codex/update-xfixes-security`。本轮只回补 CVE-2025-49177，不升级其他组件。

## 当前整合状态与历史分支检查

修复已在维护者确认使用正常后本地快进合入 master，整合提交为 `a770cb3ff34efa043face0d56c31928b73683d3a`。实际运行程序仍来自已完成干净构建的 `1e4a1cf5149df2b5da48d2571b08f2bc597a538b`；后续文档及测试空白调整不改变程序构建来源。

原会话于 2026-09-09 17:51:39（UTC+08:00）核对原作者分支，当时没有新整合快照。这个检查只说明当时的来源状态，之后不作为移动 upstream 的依据。

现行 upstream 是依赖来源集合 `9971201a65e6f8ec2d34f9c8d4fbc45479cf9578`，master 保存继承的适配和本地开发，见 [现行规则](../UPSTREAM.md)。本候选属于分支职责调整前已经完成的修复，按规则保留原提交；后续源码快照包含等价修复时再核对重复改动。本次不另行升级依赖，不推送远程。

## 来源与适用性

- [X.Org 安全索引](https://www.x.org/Development/Security/) 将 CVE-2025-49177 列为 XFIXES 6 的 SetClientDisconnectMode 数据泄漏。
- 上游修复：[`ab02fb96b1c701c3bb47617d965522c34befa6af`](https://gitlab.freedesktop.org/xorg/xserver/-/commit/ab02fb96b1c701c3bb47617d965522c34befa6af)，作者 Olivier Fourdan，2025-04-28，父提交 `03731b326a80b582e48d939fe62cb1e2b10400d9`。
- 官方 GitLab 补丁端点返回反自动化页面，实际差异通过 [同 SHA 镜像](https://github.com/LizardByte-infrastructure/xserver/commit/ab02fb96b1c701c3bb47617d965522c34befa6af) 取得；没有将 HTML 当作补丁。原文作者和许可证保留。
- 本地 XFIXES 分发包含版本 6 的 Set/Get 处理函数；普通 Set 在读取 mode 前不检查长度，换字节序 Set 仅检查最小长度。
- 回补添加普通请求的精确长度检查，并把换字节序请求的最小长度检查改为精确匹配。生产差异严格为上游的 +2/-1；整个 `xorg-server/xfixes/disconnect.c` Git blob 为 `5b2945a4a8236c4b80a3c174cfbd9089f1c3f462`，与上游修复后的文件一致。

来源、原生测试及协议脚本证据保存在开发工作区 `D:\File\Program\GitHub\vcxsrv\.worktrees\xfixes-security\.local-validation\xfixes-security`，包括 `upstream.json`、`upstream.diff`、`vcxsrv-upstream.json`、`run-tests.ps1` 和 `check-wire.py`。

## 回归验证

新增原生 C 测试直接编译实际 `disconnect.c`，使用真实协议结构、长度宏和私有字段访问函数。仅私有存储注册、回复输出及分发指针初始化由夹具提供；编译开启 MSVC AddressSanitizer。测试驱动为 `tools/tests/test_xfixes_disconnect.py`。

| 检查 | 旧代码 | 修复后 | 证据 |
| --- | --- | --- | --- |
| 普通和换字节序正常 Set/Get | 2 项通过 | 2 项通过 | `red-tests.log`、`green-tests.log` |
| 普通/换字节序短长请求拒绝，模式与缓冲区不变 | 3 项失败、1 项通过 | 4 项通过 | 同上 |
| 精确 4 字节短请求读取边界 | 普通路径触发 ASAN 越界读取；换字节序路径原已拒绝 | 2 项通过 | 同上 |
| 汇总 | 8 项执行，4 失败 | 8 项全部通过，0 跳过 | 同上 |

原生测试的 `client.req_len` 模拟传输层已解码的长度，覆盖处理函数层；实际传输与认证另行验证。独立审查核对了生产差异、真实宏、私有存储、字节序及红绿证据，没有 Critical、Important 或 Minor 问题。

## 实际协议验证

脚本使用现有程序独立启动显示号 98，临时 MIT-MAGIC-COOKIE-1 认证，最小 PATH，仅管理自身创建的服务器进程。先 QueryExtension 并协商 XFIXES 6，再验证正常 Set/Get，发送短/长 Set 并 Get，检查 `BadLength`、序号、扩展操作码以及模式未变化。

默认服务器拒绝换字节序客户端；首次 `wire-red` 因这个前置条件而没有完成四种请求，保留为初次记录。最终脚本只对临时实例设置 `+byteswappedclients`，不更改产品默认值、访问控制或用户现有实例。

| 字节序与长度 | 旧 GLX 候选结果 | 新 XFIXES 候选结果 |
| --- | --- | --- |
| 小端短请求（1 个四字节单位） | FAIL，未返回 BadLength，Get 读回非零模式 | PASS，BadLength，模式不变 |
| 小端长请求（3 个四字节单位） | FAIL，未拒绝并改变模式 | PASS，BadLength，模式不变 |
| 大端短请求 | PASS，原有最小长度检查已拒绝 | PASS，BadLength，模式不变 |
| 大端长请求 | FAIL，未拒绝并改变模式 | PASS，BadLength，模式不变 |

最终证据分别为 `wire-red-with-swapped/result.json` 和 `wire-green/result.json`，两次清理均成功。新程序与下述固定源码构建相同。

旧程序测试使用 `vcxsrv-glx-20260909-1625/dist/x64/Release` 中的可执行文件启动自有实例，没有触碰维护者正在使用的连接。短 Set 与后续 Get 连续发送，旧普通路径把后续请求字节读作 mode，明确违反当前请求的边界。此处 FAIL 是预期的漏洞回归红灯，不是之前常用 GUI 无法使用的证据。

协议脚本的独立审查通过，覆盖了认证报文、版本协商、字节序、错误包与清理。该脚本以正常 mode 为 0 验证往返，非零模式的字节序由原生测试覆盖；没有声称测试实际 reset/terminate 行为。

## 新候选构建

固定源码为 `1e4a1cf5149df2b5da48d2571b08f2bc597a538b`。干净检出目录为 `D:\File\Program\GitHub\vcxsrv-xfixes-20260909-1800`，构建证据位于其 `.local-validation/xfixes-build-20260909-175722`。

构建开始于 17:57:23（UTC+08:00），18:08:46 编译结束，18:09:23 全流程完成，结果 **PASS**。使用现有 Windows PowerShell、VS2022/MSVC 和本机工具执行 `buildall.ps1 -Stage All -Configuration Release -Architecture x64 -Jobs 8`，OpenSSL 沿用已修正的 `/J1`。

| 验证 | 实际结果 | 干净检出中的证据 |
| --- | --- | --- |
| x64 Release All 构建 | PASS，退出 0 | `environment.json`、`build.log`、`summary.json` |
| 全部脚本、ASAN 与运行集成测试 | PASS，59 项，0 失败、0 跳过，32.706 秒 | `tests.log` |
| PE 架构、直接与延迟导入 | PASS，35 个 EXE/DLL | `runtime/dependencies.json` |
| 版本、临时认证、根窗口查询、清理 | PASS，显示号 97 | `runtime/result.json` 及各子进程日志 |
| 源码状态 | PASS，构建前 Git 状态与构建后受跟踪文件差异为空 | `initial-status.txt`、`tracked-changes.txt` 及执行器断言 |
| 旧程序保护 | PASS，三个目录共 105 个 EXE/DLL 大小与哈希不变 | `old-artifacts-before.json`、`old-artifacts-after.json` |

构建执行器保存在开发工作区的 `.local-validation/xfixes-security/validate-clean-build.ps1`；该次测试显式启用了 `VCXSRV_TEST_LOCAL_TOOLS=1` 和 `VCXSRV_TEST_RUNTIME=1`，运行目录指向新候选，来源字段为完整固定源码 SHA。

新运行目录：`D:\File\Program\GitHub\vcxsrv-xfixes-20260909-1800\dist\x64\Release`。`vcxsrv.exe` 为 3,041,792 字节，SHA-256 为 `E9A4D3A94031663B906BFD255193A2A050B841D19A1799C729B420317F659CD1`，全部产物清单见 `artifacts.json`。开发分支后续只追加文档，不改变二进制来源。

本轮保留主工作目录、旧基线和已验收 GLX 候选三个运行目录，构建执行器检查共 105 个 EXE/DLL 的大小与 SHA-256。libxml2 仍为仓库携带的预编译依赖，不把 All 构建等同于所有第三方库均从源码重建。

原候选构建时尚待维护者使用确认；后续确认与接续验证记录如下。最初构建没有执行逐项 GUI 场景，不能借用 GLX 的反馈填补。

## 当前主线接续与实际使用确认

2026-09-09，维护者针对 `vcxsrv-xfixes-20260909-1800/dist/x64/Release` 明确反馈“已测试，使用正常”。记录为此 XFIXES 候选实际可用，未提供具体应用和场景明细；[兼容性记录](../COMPATIBILITY.md) 中的逐项场景仍保持未验证。

候选已合并主线 `534ce92aaad0752a0a35cff8f0d4f524b5834a3c`，接续提交为 `2fa811ae2db5f066a362743171ffbdab6a71771d`。与固定构建来源 `1e4a1cf51` 比较，程序文件完全相同，变更为维护文档与 Git 关系。独立审查通过，随后清理了一处测试文件末尾空行，不改变测试行为。

新复测在 20:28:23（UTC+08:00）完成：59 项，0 失败、0 跳过；175 个既有 EXE/DLL 的哈希不变，候选工作区干净。证据在主仓库 `.local-validation/plan-followup-20260909/candidate-20260909-202748/`。运行集成使用固定构建来源的 XFIXES 目录，未将文档接续冒称为重新编译整个服务器。为执行全部用例，在候选工作区补建了 mhmake。

此前一次执行器在 Windows PowerShell 5.1 下因标准错误流的正常测试输出触发 `NativeCommandError` 而中断，不能记作测试通过。最小例子证明：Python 仅输出诊断文本且退出 0，5.1 仍触发该异常，7.6.5 正常。改用 PowerShell 7 后全套通过；中断记录保留于 `candidate-20260909-202633/`，最小例子为同级 `stderr-probe.ps1`。该问题属于本机日志执行器，本次没有修改产品构建入口。

## 合入主线后的验收

master 从 `534ce92aa` 本地快进到 `a770cb3ff`，无冲突。合入后于 20:30:30（UTC+08:00）完成全部测试：59 项，0 失败、0 跳过，32.633 秒。测试检出为整合提交，运行集成使用上述 XFIXES 固定构建目录；生产文件与构建来源一致。175 个既有运行 EXE/DLL 的 SHA-256 不变，受跟踪工作区干净。

原始证据：主仓库 `.local-validation/plan-followup-20260909/integrated-20260909-202955/` 的 `tests.log`、`result.json`、`artifacts-before.json` 和 `artifacts-after.json`。执行器为同级 `retest.ps1`，外层使用 PowerShell 7；其中运行的是现有脚本、原生回归与真实运行集成测试，没有重建整个服务器。

本项实施计划已完成。用户反馈覆盖此次版本的实际使用可用性，具体应用场景仍按兼容性表补录。开发 worktree、固定构建目录及旧程序均保留用于追溯，标签和 upstream 依赖基线未移动，未执行远程推送。合入后的收尾提交仅更新状态文档，不将其另称为一次程序构建。
