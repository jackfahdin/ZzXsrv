# 中文 README 与目录迁移验证

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

完整 All 构建、运行验证及最终测试结果将在完成后追加于本节。本报告此时不代表这些步骤已经通过。

本轮没有更改 X Server 或依赖库的生产源码，也没有合入待验收的输入候选。Docker 与旧 WSL 只验证迁移相关的入口路径、参数或语法，不运行其历史构建环境，不把静态检查写成兼容性验收。已有运行目录继续保留，目录移动不等于升级依赖或完成新的 GUI 场景验收。
