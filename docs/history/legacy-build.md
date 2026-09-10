# 旧 WSL / Docker 构建说明

本文保留早期 shell、Cygwin 和 Docker 构建流程的背景，供源码追溯与后续维护参考。**这些旧工具环境未在本轮验证，以下命令不应直接作为现行构建流程执行。** 脚本含机器特定路径，使用前需要人工核对和调整；本次文档整理不自动执行、下载或安装旧环境。

当前 Windows 构建请使用 [PowerShell 原生构建指南](../build/WINDOWS.md)。

## 文件位置

| 旧入口 | 当前保留位置 |
| --- | --- |
| `buildall.sh`、`setenv.sh`、`setenv.bat`、`setenv.py` | [scripts/legacy/wsl/](../../scripts/legacy/wsl/) |
| Docker 构建与启动命令 | [scripts/docker/](../../scripts/docker/) |
| Docker 环境定义 | [docker/](../../docker/) |
| 旧上游同步脚本 | [scripts/legacy/upstream/](../../scripts/legacy/upstream/) |
| `versionchanges.btm` | [scripts/legacy/release/](../../scripts/legacy/release/) |

旧 shell 入口曾假定从 WSL 终端进入 Windows 文件夹，依赖大小写不敏感的文件系统。历史说明还包含在 Windows Docker 容器内进入 Cygwin 的路线；这两种环境不能与当前原生 PowerShell 流程混为一谈。

## 历史工具要求

- Visual Studio 2022 Community Edition。
- Strawberry Perl portable，旧路径为 `C:\perl`。
- Cygwin 包：`bison`、`flex`、`gawk`、`gperf`、`gzip`、`nasm`、`sed`、`python27`、`python38`、`python38-lxml`。
- Windows Python 3.9，含 lxml 和 Mako。
- 如需构建安装包，另需 NSIS。

这些名称和版本来自旧说明，不是当前环境的安装建议，也不表示版本已完整锁定。实际声明与来源限制见[依赖来源清单](../dependencies/SOURCES.md)。

## 历史 Docker 路线

原说明通过 Docker 构建环境再运行容器，并将源码映射到容器内 `C:\src`。当前入口名称为 `scripts\docker\dockerBuild.cmd` 和 `scripts\docker\runDocker.cmd`；旧文字中曾将前者误写为 `buildDocker.cmd`。镜像构建会下载和安装环境依赖，耗时取决于机器与网络；本轮没有运行这些入口。

旧说明在容器内记录了以下步骤，仅保留历史语义：

```text
git clone src vcx
cygwin
cd /cygdrive/c/vcx
export SHELLOPTS
set -o igncr
```

随后旧文档用 `./buildall.cmd 1 9 D` 表示 8 核机器上的 64 位 Debug 构建，但仓库保留的实际入口是 `buildall.sh`，不能假定存在同名 `.cmd` 包装。脚本移动后的调用路径、环境初始化和容器兼容性仍须单独验证。

## 旧 shell 参数

历史参数形式：

```text
buildall.sh <32/64 位标记> <并行任务数> <Debug/Release 标记> [依赖构建标记]
```

| 参数 | 历史含义 |
| --- | --- |
| 位数 | `1` 为 64 位，`0` 为 32 位 |
| 并行任务数 | 旧说明建议 CPU 数量加 1 |
| 构建类型 | `D` 为 Debug，`R` 为 Release，`A` 为两者 |
| 可选依赖标记 | `N` 表示只构建服务器，复用已有依赖 |

例如 `1 9 D` 只是旧参数示例，不代表当前可通过的验证组合。现行原生构建阶段、工具覆盖参数和运行验证均以 [Windows 构建指南](../build/WINDOWS.md)为准。
