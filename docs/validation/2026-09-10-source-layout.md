# 源码目录分层验证

日期：2026-09-10。结果：Windows x64 Release 完整构建、61 项测试及实际运行验证通过。

## 范围与源码

按已确认的[设计](../designs/2026-09-10-source-layout.md)和[路径映射](../history/2026-09-10-source-path-mapping.json)，将 36 个原有目录迁入 `src/`、`third_party/`、`include/`。根目录从 41 个受管理目录收敛为 `src`、`third_party`、`include`、`tools`、`scripts`、`docs`、`docker` 共 7 个；`dist/` 仍为本地生成目录。

- 起点：`5001962c3e6338eacf090f929d60b9ded58b89a9`。
- 最终完整构建的运行源码：`948c1a36c8ddb09461f2490dc58650d2e5d3c72b`。后续交付提交补齐文档、测试引用和旧维护脚本路径，不改变该构建使用的运行源码。
- 独立构建目录：`D:\File\Program\GitHub\zzxsrv-structure-20260910`，最初由 Git 创建，无旧服务器、依赖或字体构建缓存。
- 新运行目录：`D:\File\Program\GitHub\zzxsrv-structure-20260910\dist\x64\Release`。

生产 C/C++ 内容保持不变，组件名称、内部组织、许可与作者声明保留。没有升级依赖，也没有合入此前待验收的输入处理候选。

## 构建与回归修复

`MHMAKECONF` 仍为仓库根目录，两个公共 makefile 保留在根目录；组件位置集中定义于 `scripts/build/paths.mak`。PowerShell、MHMake、跨组件生成规则和四份 NSIS 清单均更新至新位置。

迁移后先复现旧测试源码路径失效，再更新引用。额外发现并修复两处实际回归：

1. Mesa 的版本生成器按固定父目录定位 `.git`，迁移后静默生成空版本标识。改为从脚本绝对目录执行 `git -C ... rev-parse HEAD`；独立工作目录中的真实生成测试先失败、后通过。
2. 初次 All 在字体管道失败：组件变量中的正斜杠使旧 Windows 命令解析器误判工具名。改用反斜杠；真实 `MHMake → bdftopcf → Python gzip` 测试先失败、后通过，并检查解压后的 PCF 文件头。

首次失败记录保留；其生成字体目录已移入本地 `failed-font-output/`，随后重新执行完整 All，重新生成全部字体。重跑前以修复后的版本生成器刷新 Mesa 构建版本头，记录于 `mesa-build-revision.log`。

最终命令：

```powershell
pwsh -NoProfile -File scripts/build/buildall.ps1 -Jobs 8 `
  -EnvironmentReport .local-validation/structure-20260910/environment-final.json
```

使用 Visual Studio 2022、MSVC 14.44、Windows SDK 10.0.26100.0、Python 3.14.2 及原有原生生成工具。最终 All 退出码为 0，完成依赖、构建工具、服务器、字体、键盘数据和便携目录整理。完整工具路径及版本保存在环境报告。

## 验证结果

| 检查 | 结果 |
| --- | --- |
| 完整自动测试 | 61 项通过，0 失败，0 跳过；启用本地 MSVC 与真实运行验证 |
| PE 依赖 | 35 个 EXE/DLL 通过检查 |
| 实际运行 | 版本查询、端口检查、认证、启动、根窗口查询和清理均 PASS；独立 display 97 |
| 便携目录 | 5,129 个唯一文件，与前次已验证便携目录的相对文件集合完全一致 |
| 压缩字体 | 4,297 个 `.pcf.gz` 全部能完整解压，并具有正确 PCF 文件头 |
| 原文件保留 | 起点的 23,925 个受管理文件均存在于对应位置，Git 文件模式一致 |
| 旧运行文件 | 245 个既有 EXE/DLL 的 SHA-256 不变 |
| 依赖来源 | 196 条记录保留；1,383 个 URL/ref/tag/commit/confidence/revision 值不变；本地位置按映射更新 |
| 来源文档 | 405 个来源 URL 及来源/修订表格列不变 |
| 导航 | 文档子任务的 291 个相对链接有效；交付报告加入后再次执行完整链接检查 |
| 独立审查 | 核心、入口、测试和两次定向修复复核均无未解决问题 |

打包工具输出的 `5132 files` 是复制清单项数，其中三个 CRT 文件被重复列入；实际目录有 5,129 个唯一文件，前次目录也为 5,129 个。本次验证按实际文件集合比较，没有将复制项数当作唯一文件数。

## 本地证据与交付

原始证据保存在构建目录的 `.local-validation/structure-20260910/`，并复制到主工作区同名忽略目录。主要记录包括：

- `environment-final.json`、`build-all-final.log`、`build-final-exit-code.txt`。
- `final-tests.log`、`runtime/result.json`、`runtime/dependencies.json`。
- `portable-files.json`、`structure-verification.json`、`docs-review.json`、`core-review.md`。
- 首次失败的 `build-all.log` 及 Mesa、字体管道的红/绿测试日志。

交付沿用线性主线：快进合入 master，普通推送，清理临时 Git 工作区登记与分支，保留构建结果。主工作区旧源码位置残留的未跟踪编译产物移入 `.local-validation/structure-20260910/old-build-artifacts/`；原有 `dist/` 和以前的候选运行目录保持原样。

本次实际构建与运行覆盖 x64 Release。其他配置的安装清单做了路径等价核对，没有执行 Win32、Debug、WSL 或安装器完整构建。
