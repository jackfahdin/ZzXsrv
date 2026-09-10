# 文档索引

初次使用请先阅读[项目首页](../README.md)和 [Windows 原生构建指南](build/WINDOWS.md)。当前维护状态以[计划与功能状态](maintenance/PLAN_STATUS.md)为准，历史报告中的提交、分支、路径和测试数字保留当时语境。

## 构建与使用

| 入口 | 内容 |
| --- | --- |
| [Windows 原生构建](build/WINDOWS.md) | 工具要求、PowerShell 参数、便携目录和运行验证 |
| [应用兼容性](maintenance/COMPATIBILITY.md) | 实际使用环境、场景与验证缺口 |
| [验证记录索引](validation/README.md) | 固定源码、工具环境、构建与运行证据 |

## 来源与维护

| 入口 | 内容 |
| --- | --- |
| [项目来源](PROVENANCE.md) | 原作者固定提交、初始导入与历史整理 |
| [依赖来源](dependencies/SOURCES.md) | 组件来源、修订证据和未确定事项 |
| [机器可读来源清单](dependencies/SOURCES.json) | 来源记录的结构化字段 |
| [继承包清单](dependencies/packages.txt) | 原有组件包记录，需结合来源文档解读 |
| [维护路线](maintenance/MAINTENANCE.md) | 维护目标、阶段与验收原则 |
| [计划与功能状态](maintenance/PLAN_STATUS.md) | 已完成事项、未合入候选和剩余工作 |
| [上游维护规则](maintenance/UPSTREAM.md) | 组件导入、线性主线与证据要求 |
| [设计文档](designs/) / [实施计划](plans/) | 各项工作的设计和执行记录 |

## 历史材料

- [旧 WSL / Docker 构建说明](history/legacy-build.md)：旧工具环境未重新验证，命令仅供追溯。
- [原作者发行说明](history/upstream-releases/)：继承的版本变化记录。
- [历史归档文档](history/)：旧来源快照和其他归档材料。
- [2026-09-10 仓库整理记录](validation/2026-09-10-repository-reorganization.md)：历史映射、归档与验证边界。

旧报告记录的构建产物、旧提交号和原路径不自动代表当前 `master`。复跑验证应使用实际构建的源码提交，并创建新的证据目录。版权与许可证见根目录 [COPYING](../COPYING) 和各组件许可文件。
