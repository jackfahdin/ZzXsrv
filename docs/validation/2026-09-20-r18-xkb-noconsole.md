# R18 xkbcomp 去控制台窗口 + 版本号 21.1.16.2 + Release 说明修复

日期：2026-09-20。基线 `a385698dd7`（vcxsrv.exe 选项文档提交）；分支 `codex/r18-xkb-noconsole-20260920`，本批三个提交（`0dbd012f81`、`d2aa7ccc73`、`3ba3f2256c`）已合入 master，tip `3ba3f2256c`。

状态：已验收并合入 master。R18 修复启动时控制台窗口闪烁（用户实测验收），外加版本号 bump 与 Release 说明两个收尾提交。

## R18 根因 / 修复 / 验证（`0dbd012f81`，单文件 `src/xorg-server/xkb/ddxLoad.c`）

- 根因：`RunXkbComp()` 的 WIN32 分支用 `system()` 启动 xkbcomp，`system()` 经 cmd.exe 运行；cmd.exe 是控制台子系统程序，vcxsrv（/SUBSYSTEM:WINDOWS、无控制台）派生它时 Windows 会创建可见控制台窗口，启动期间约闪两次。
- 修复：`CreateProcessA` + `CREATE_NO_WINDOW` 替换 `system()`，同步等待并返回子进程退出码（启动失败返回 -1，与 `system()` 语义一致；xkbcomp 失败保持非致命）。命令行不再需要 cmd.exe 要求的外层引号，asprintf 格式串按平台拆分；非 WIN32 分支不变。编码语义等价：`Win32TempDir()`（GetTempPathA）与 `XkbBinDirectory`（GetModuleFileNameA）均为 ANSI 窄字符串。
- 自动化取证（R18 工作区）：启动过程无 cmd/conhost 子进程；xkm 生成 2 次（两次编译路径均走到）；xwininfo 连通验证服务器正常；改名 xkbcomp 后启动仍非致命（容错语义保持）。
- 合并后回归 469 项通过、0 跳过（46.869 秒，`.local-validation/r18-integration-20260920/tests-after-merge.log`）。
- 用户验收：维护者实测反馈"没问题了"，记录为本版本实际使用正常。

## 版本号 21.1.16.1 → 21.1.16.2（`d2aa7ccc73`，chore）

命名决策：沿用上游规则 `<xserver 版本>.<打包修订号>`。xserver 基底不变（R12/R13 只 cherry-pick 了 21.1 分支子集，仍基于 21.1.16），故本轮产品修复（R17 xlaunch Unicode 命令行、R18 xkbcomp 去控制台）只递增打包修订号到 21.1.16.2。XWin.rc 四处同步；打包测试改为用独立正则从 XWin.rc 读期望值，以后 bump 不用改测试。

## Release 说明改为真实变更列表（`3ba3f2256c`，ci）

- 根因：`gh release create --generate-notes` 只产出 "Full Changelog: continuous-build...v21.1.16.1" 的比较链接——仓库没有 PR 可聚合，且基线是滚动快照 tag，对比无意义。
- 修复：release.yml 以上一个版本 tag 为基线、continuous-build.yml 以上一个快照 tag 为基线，用 `git log --no-merges` 生成 "Changes since ..." 变更列表加 compare 链接，`--notes-file` 发布。本地已用真实 tag 演练过生成逻辑。

## 回归与边界

R18 合并后及两个收尾提交后各跑了一次全套件：469 项通过、0 跳过（46.869 秒与 46.610 秒，后者 SourceCommit `3ba3f2256c`，日志 `tests-after-merge.log` / `tests-after-r19.log`，均针对 R13 候选运行目录——注意该目录不含 R17/R18 产品修复，套件中产品行为相关项由测试侧桩与 CI 构建产物承担）。

边界保留：

- 英文 locale + 中文用户名场景未覆盖：`CreateProcessA` 与被替换的 `system()` 同为 ANSI 语义，该路径既非回归也未改善，遗留 ANSI 限制继续保留。
- Release 说明新逻辑未在真实 tag 运行中验证（仅本地演练生成逻辑），下次打 tag 时验证。
- 新版二进制（含 21.1.16.2 版本戳与 R18 修复）未单独 GUI 实测；用户验收针对 R18 修复构建，收尾两个提交（版本戳、CI 说明）不改运行时行为。

## 本版本反馈与主线整合

三个提交自基线 `a385698dd7` 线性合入 master，tip `3ba3f2256c`。R18 取得维护者"没问题了"的实测验收；版本号与 Release 说明为工程收尾，无运行时行为变化。整合证据：`.local-validation/r18-integration-20260920/`（`tests-after-merge.log`、`tests-after-r19.log`）。分支与工作区保留。

已验收入口仍为 R13 的 `D:/File/Program/GitHub/zzxsrv-r13-xserver-20260917/dist/x64/Release/xlaunch.exe`（编译源码 `cda929acaafb96d533ec0beb209635ea356458c8`）——R17/R18 的产品修复不在该目录中，需要这些修复时应使用 CI 产物或重新构建。
