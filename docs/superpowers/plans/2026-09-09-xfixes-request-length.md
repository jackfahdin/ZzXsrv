# XFIXES 请求长度校验实施计划

> 2026-09-10 历史说明：本文保留当时的方案、提交号与验证结果。旧分支、标签和工作区登记已清理，源码及运行目录保留为普通目录；旧命令不应直接照搬执行。现行规则见[维护规则](../../UPSTREAM.md)，对应关系与恢复材料见[整理记录](../../validation/2026-09-10-repository-reorganization.md)。旧依赖快照清单见[历史 JSON](../../history/2026-09-09-dependency-snapshot.json)；当前不再维护上游源码分支。

状态：已完成并合入 master，整合源码 `a770cb3ff34efa043face0d56c31928b73683d3a`；实际程序构建来源仍为 `1e4a1cf5149df2b5da48d2571b08f2bc597a538b`。维护者已确认使用正常，合入后 59 项测试通过且无跳过。

> **面向 AI 代理的工作者：** 使用 executing-plans 在当前任务内顺序执行，按下列检查点验证。

**目标：** 回补 CVE-2025-49177，拒绝长度不匹配的 SetClientDisconnectMode 请求，保持正常请求行为。

**架构：** 保留 VcXsrv 的 Windows 整合，仅采用上游 `ab02fb96b1c701c3bb47617d965522c34befa6af` 的两处长度检查。原生测试直接编译实际 `disconnect.c`，使用真实协议结构及请求检查宏；服务端外围回复和私有存储初始化由测试提供。

**技术栈：** C11、MSVC AddressSanitizer、Python unittest、现有 PowerShell 原生构建。

**规格：** [组件更新评估](../../validation/2026-09-09-component-update-assessment.md)、[上游规则](../../UPSTREAM.md)。

## 全局约束

- 从已验收的 `a55ce37fd` 建立 `codex/update-xfixes-security`；主工作目录、GLX 及旧基线程序均保留。
- 现行 upstream 保存依赖源码集合，master 保存整合开发。本候选早于依赖基线整理产生，按现行规则保留已有修复提交；不把整合源码反向覆盖 upstream。
- 不下载依赖或安装工具、不推送远程；上游小补丁只用于来源核对。
- 先观察旧代码失败，再实施修复。新候选独立构建，保留源提交、日志和产物哈希。

## 任务 1：来源与行为回归

文件：新增 `tools/tests/native/xfixes_disconnect.c`、`tools/tests/test_xfixes_disconnect.py`。

- [x] 核对原作者 SHA、上游补丁及本地普通/换字节序处理函数。基线代码与上一轮 51 项通过的 master 相同。
- [x] 测试正常长度、过短、过长请求，分别覆盖普通和换字节序；非法请求应返回 `BadLength`，不改变原模式；正常请求 Set 后 Get 应保留值和回复字节序。
- [x] 使用 `python -B -m unittest discover -s tools/tests -p test_xfixes_disconnect.py -v` 记录旧代码失败。额外用精确分配的短请求触发 ASAN，验证实际读取边界。

## 任务 2：最小回补

文件：`xorg-server/xfixes/disconnect.c`。

- [x] 普通处理函数的 REQUEST 后添加 `REQUEST_SIZE_MATCH(xXFixesSetClientDisconnectModeReq);`。
- [x] 换字节序处理函数将 `REQUEST_AT_LEAST_SIZE` 改成 `REQUEST_SIZE_MATCH`，在读取或交换 mode 前拒绝非法长度。
- [x] 重跑定向测试并与保存的上游差异核对，独立审查后本地中文提交，正文保留 Olivier Fourdan 及完整来源 SHA。

## 任务 3：候选验收与记录

文件：新增 `docs/validation/2026-09-09-xfixes-request-length.md`，更新 `docs/validation/README.md`、`docs/UPSTREAM.md` 的进展链接。

- [x] 在固定提交的新检出完成 x64 Release All 构建，启用本机工具及真实运行集成测试，检查认证、依赖和清理。
- [x] 验证普通/换字节序客户端的实际 XFIXES 协议请求；记录未覆盖的 GUI 场景，不能借用上一候选的用户反馈。
- [x] 核对全部旧运行目录哈希，记录新程序目录供维护者测试。
- [x] 整理候选文档并修正旧 upstream 定义，将计划和证据纳入主线状态入口。
- [x] 接续当前 master 的依赖基线关系和维护文档，复跑全部必要自动测试：59 项通过，0 跳过。
- [x] 取得维护者对此 XFIXES 候选的实际使用确认：“已测试，使用正常”；具体应用与场景明细未提供。
- [x] 合入 master 后复核源码、测试和运行目录，并更新状态：59 项通过，175 个运行文件哈希不变；upstream 仍保存依赖来源集合。
