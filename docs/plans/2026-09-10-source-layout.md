# 源码目录分层实现计划

> 在当前会话按 subagent-driven-development 协作执行；路径迁移与构建修复由主代理连续执行，文档维护和最终审查独立处理。

**目标：** 将根目录的 41 个受管理目录整理为 7 个职责明确的目录，同时保持构建与运行行为。

**架构：** 单仓库保留组件边界；产品代码放入 src，依赖按来源领域放入 third_party，公共头文件放入 include。MHMAKECONF 仍为仓库根目录。

**技术栈：** PowerShell、Python、MHMake、MSBuild、MSVC、NSIS 清单。

**规格：** [源码目录分层设计](../designs/2026-09-10-source-layout.md)。

## 任务

- [x] 1. 保存基线 HEAD、文件清单和旧运行文件哈希；在独立 worktree 运行现有测试。
- [x] 2. 写入完整路径映射，迁移目录；用现有构建测试确认旧路径失效；定义 paths.mak 并修复组件引用、工程和打包路径。
- [x] 3. 更新 README、目录索引、依赖来源清单及当前维护文档；历史文档保留历史事实并修复导航。
- [x] 4. 运行 `pwsh -File scripts/build/buildall.ps1 -Jobs 8 -EnvironmentReport .local-validation/structure-20260910/environment.json`，完成干净 x64 Release All 构建。
- [x] 5. 在 MSVC 环境启用 VCXSRV_TEST_LOCAL_TOOLS 和 VCXSRV_TEST_RUNTIME，运行 `python -B -m unittest discover -s tools/tests -v`；保存独立运行验证、依赖与文件保留检查。
- [x] 6. 审查完整改动并修复问题，写入验证报告。交付方式为快进合入 master、普通推送并清理临时 Git 分支登记，保留构建结果。

## 检查约束

目录迁移不改变组件内部名称；相对路径按原文件所在目录解析后映射，避免盲目替换上游 URL 和头文件名称。移动前检查源与目标绝对路径均在工作区内。完整验证前不宣称构建完成；不使用目录链接掩盖旧引用。

完成证据见[源码目录分层验证](../validation/2026-09-10-source-layout.md)。
