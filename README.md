# ZzXsrv

> 基于 VcXsrv 持续维护的 Windows X Server。

ZzXsrv 是运行于 Windows 的 X Server，让 X11 图形程序在 Windows 桌面显示。项目基于 VcXsrv 的 X.Org 源码与 Windows 适配，使用 Visual Studio 2022 构建，并继续维护原生构建流程、运行验证和选定的上游修复。

## 项目来源

本项目基于 [marchaesen/vcxsrv](https://github.com/marchaesen/vcxsrv) 继续开发，最初继承自固定提交 [`d0a1eaf7ee15`](https://github.com/marchaesen/vcxsrv/tree/d0a1eaf7ee15fcdf4f683388a88fec49078e6408)，保留原有 Windows 适配和第三方署名。项目仓库为 [jackfahdin/ZzXsrv](https://github.com/jackfahdin/ZzXsrv)，开发主线 `master` 保持线性历史。

来源说明与历史对应关系见[项目来源](docs/PROVENANCE.md)，各组件的固定修订、继承来源及未知项见[依赖来源清单](docs/dependencies/SOURCES.md)。

## 源码目录

| 目录 | 职责 |
| --- | --- |
| [`src/`](src/) | ZzXsrv 产品源码：X Server、Windows 入口适配、XLaunch、字体数据和安装清单 |
| [`third_party/`](third_party/) | 随仓维护的 X.Org、图形、字体及其他第三方组件；目录归类不表示组件未经修改 |
| [`include/`](include/) | 跨组件使用的兼容头文件，以及整体迁入的 `X11/` 和 `gl/` 头文件树 |
| [`tools/`](tools/) / [`scripts/`](scripts/) | 构建工具、验证器和面向维护者的脚本入口 |
| [`docs/`](docs/) | 构建、来源、维护、设计、计划、历史和验证文档 |

完整目录边界与旧路径映射见[源码目录分层设计](docs/designs/2026-09-10-source-layout.md)和[机器可读路径映射](docs/history/2026-09-10-source-path-mapping.json)。XLaunch 仍是 X Server 源码的一部分，位于 `src/xorg-server/hw/xwin/xlaunch/`；`tools/plink/` 和 `tools/mhmake/` 保留在工具目录。

## 已有能力与验证边界

- 继承 VcXsrv 的 XLaunch 启动向导、配置加载、窗口、剪贴板和键盘等产品能力。
- 提供原生 PowerShell 构建、工具预检、分阶段构建和便携运行目录整理，无需 WSL 或 Cygwin。
- 提供构建环境报告、PE 依赖检查、经认证的 X Server 启动与根窗口查询，以及独立日志。
- 已合入 GLX 上下文标签和 XFIXES 请求长度校验修复。

当前主要验证目标为 **Windows x64 Release**。Debug、Win32、安装包及完整应用场景尚未全面验证；具体进展与适用范围见[计划与功能状态](docs/maintenance/PLAN_STATUS.md)、[兼容性记录](docs/maintenance/COMPATIBILITY.md)和[验证报告](docs/validation/README.md)。

## 启动运行

构建完成后，在仓库根目录的 PowerShell 中启动向导：

```powershell
.\dist\x64\Release\xlaunch.exe
```

也可以直接运行同一目录下的 `vcxsrv.exe`。可执行文件沿用上游名称。运行目录包含所需 DLL、字体、区域设置和键盘数据，请保留整个文件夹；不要只复制一个 EXE，也不要直接启动缺少相邻运行依赖的 `src\xorg-server\obj64\servrelease\vcxsrv.exe`。

## 从源码构建

准备 Visual Studio 2022 C++ 工具、Windows SDK、Windows Python 3.11+（含 lxml、Mako、PyYAML）、Strawberry Perl、NASM、WinFlexBison 和原生 Windows gperf。源码路径不能含空格，脚本不会自动下载或安装工具。

在仓库根目录执行：

```powershell
.\scripts\build\buildall.ps1 -CheckOnly
.\scripts\build\buildall.ps1 -Jobs 8
```

默认构建 x64 Release，并生成 `dist\x64\Release`。已有编译产物时，可以单独重新整理运行目录：

```powershell
.\scripts\build\buildall.ps1 -Stage Portable
```

工具路径、构建阶段、依赖来源限制与验证方法见 [Windows 原生构建指南](docs/build/WINDOWS.md)。

## 文档导航

| 文档 | 内容 |
| --- | --- |
| [文档索引](docs/README.md) | 按用途查找全部项目文档 |
| [Windows 构建指南](docs/build/WINDOWS.md) | 环境准备、构建、便携目录与运行验证 |
| [维护路线](docs/maintenance/MAINTENANCE.md) / [当前状态](docs/maintenance/PLAN_STATUS.md) | 已完成工作、待办与验收边界 |
| [上游维护规则](docs/maintenance/UPSTREAM.md) | 线性主线、组件更新和证据要求 |
| [验证记录](docs/validation/README.md) / [兼容性记录](docs/maintenance/COMPATIBILITY.md) | 可复查的构建与使用结果 |
| [历史构建说明](docs/history/legacy-build.md) | 旧 WSL、Cygwin 与 Docker 环境，仅供追溯 |

## 版权与许可证

保留 VcXsrv、X.Org 及各第三方组件的原有版权、许可证和署名。请查阅根目录 [COPYING](COPYING) 与各组件目录中的许可文件。
