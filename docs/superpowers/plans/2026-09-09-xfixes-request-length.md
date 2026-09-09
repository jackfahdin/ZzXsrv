# XFIXES 请求长度校验实施计划

> **面向 AI 代理的工作者：** 使用 executing-plans 在当前任务内顺序执行，按下列检查点验证。

**目标：** 回补 CVE-2025-49177，拒绝长度不匹配的 SetClientDisconnectMode 请求，保持正常请求行为。

**架构：** 保留 VcXsrv 的 Windows 整合，仅采用上游 `ab02fb96b1c701c3bb47617d965522c34befa6af` 的两处长度检查。原生测试直接编译实际 `disconnect.c`，使用真实协议结构及请求检查宏；服务端外围回复和私有存储初始化由测试提供。

**技术栈：** C11、MSVC AddressSanitizer、Python unittest、现有 PowerShell 原生构建。

**规格：** [组件更新评估](../../validation/2026-09-09-component-update-assessment.md)、[上游规则](../../UPSTREAM.md)。

## 全局约束

- 从已验收的 `a55ce37fd` 建立 `codex/update-xfixes-security`；主工作目录、GLX 及旧基线程序均保留。
- 原作者 master 与已导入快照 SHA 相同则不移动 upstream；组件修复只进入维护分支。
- 不下载依赖或安装工具、不推送远程；上游小补丁只用于来源核对。
- 先观察旧代码失败，再实施修复。新候选独立构建，保留源提交、日志和产物哈希。

## 任务 1：来源与行为回归

文件：新增 `tools/tests/native/xfixes_disconnect.c`、`tools/tests/test_xfixes_disconnect.py`。

- [x] 核对原作者 SHA、上游补丁及本地普通/换字节序处理函数。基线代码与上一轮 51 项通过的 master 相同。
- [ ] 测试正常长度、过短、过长请求，分别覆盖普通和换字节序；非法请求应返回 `BadLength`，不改变原模式；正常请求 Set 后 Get 应保留值和回复字节序。
- [ ] 使用 `python -B -m unittest discover -s tools/tests -p test_xfixes_disconnect.py -v` 记录旧代码失败。额外用精确分配的短请求触发 ASAN，验证实际读取边界。

## 任务 2：最小回补

文件：`xorg-server/xfixes/disconnect.c`。

- [ ] 普通处理函数的 REQUEST 后添加 `REQUEST_SIZE_MATCH(xXFixesSetClientDisconnectModeReq);`。
- [ ] 换字节序处理函数将 `REQUEST_AT_LEAST_SIZE` 改成 `REQUEST_SIZE_MATCH`，在读取或交换 mode 前拒绝非法长度。
- [ ] 重跑定向测试并与保存的上游差异核对，独立审查后本地中文提交，正文保留 Olivier Fourdan 及完整来源 SHA。

## 任务 3：候选验收与记录

文件：新增 `docs/validation/2026-09-09-xfixes-request-length.md`，更新 `docs/validation/README.md`、`docs/UPSTREAM.md` 的进展链接。

- [ ] 在固定提交的新检出完成 x64 Release All 构建，启用本机工具及真实运行集成测试，检查认证、依赖和清理。
- [ ] 验证普通/换字节序客户端的实际 XFIXES 协议请求；记录未覆盖的 GUI 场景，不能借用上一候选的用户反馈。
- [ ] 核对全部旧运行目录哈希，记录新程序目录供维护者测试。用户确认新候选可用后再整合 master，upstream 保持原作者快照语义。
