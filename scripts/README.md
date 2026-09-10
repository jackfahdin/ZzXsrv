# 脚本入口

从仓库根目录调用这些入口。构建内部使用的生成器、打包器和验证器保留在 `tools/`，对应测试位于 `tools/tests/`。源码分层后的共享组件位置由 `scripts/build/paths.mak` 统一提供给 MHMake；脚本入口仍以仓库根目录作为 `MHMAKECONF`，调用方式不变。

| 目录 | 用途 | 使用状态 |
| --- | --- | --- |
| `build/` | 原生 Windows PowerShell 构建 | 当前维护入口，见[构建说明](../docs/build/WINDOWS.md) |
| `docker/` | 构建 Docker 镜像、挂载仓库启动容器 | 继承的容器方案；本轮仅修正路径，未验证 Docker 构建 |
| `legacy/wsl/` | 旧 shell 构建及环境转换 | 历史入口，有机器相关路径，见[旧构建说明](../docs/history/legacy-build.md) |
| `legacy/upstream/` | 原作者同步、文件比较及旧分支辅助工具 | 停用的维护流程，不再用于更新主线 |
| `legacy/release/` | 旧产品版本修改辅助工具 | 历史材料，不是当前产品发布流程 |

```powershell
.\scripts\build\buildall.ps1 -CheckOnly
.\scripts\build\buildall.ps1 -Configuration Release -Architecture x64 -Jobs 8
```

`scripts/legacy/upstream/` 中的名称指历史工具用途，不代表存在上游源码分支。`sync.bat` 依赖原作者的外部目录布局和 `released` 目录，不能在本仓库直接照搬执行。`synchronise.py` 是原目录复制工具；`filesthatshouldbethesame.py` 记录旧文件对应表；`fastforwardotherbranch.sh` 是旧分支辅助入口。它们保留用于追溯，当前依赖维护以[维护规则](../docs/maintenance/UPSTREAM.md)为准。

两份 Docker 入口以脚本位置定位仓库，无论调用者位于哪个目录，构建上下文均为仓库的 `docker/`，容器挂载源均为仓库根目录。历史工具和容器仍需要各自原有环境；路径整理不表示这些环境已完成验收。
