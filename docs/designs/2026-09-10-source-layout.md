# 源码目录分层设计

用户已确认按产品源码、第三方组件、公共头文件和工具分层。保留单仓库和线性 master，不创建上游分支或子模块。

## 目录边界

- `src/xorg-server/`：服务器及其内部 Windows、XLaunch、字体数据和安装清单，内部结构保留。
- `src/platform/libwinmain/`：Windows 入口适配。
- `third_party/xorg/`：X.Org 库、客户端程序和字体/键盘辅助工具。
- `third_party/graphics/`：Mesa、Pixman、DXTN。
- `third_party/fonts/`：FreeType、Fontconfig。
- `third_party/` 的独立组件目录：Expat、libregex、libxml2、OpenSSL、pthreads、zlib。
- `include/`：兼容头文件，以及整体迁入的 `X11/` 和 `gl/`。
- `tools/`、`scripts/`、`docs/`、`docker/` 保留职责。两个公共 makefile 保留在根目录，`MHMAKECONF` 继续表示仓库根目录。

组件名称和内部结构保留，`third_party` 不表示组件未经修改。完整迁移表见 [路径映射](../history/2026-09-10-source-path-mapping.json)。不升级依赖、不改产品功能、不移动旧运行目录，不在本轮统一中间产物目录。

## 构建与验证

共享组件位置由 `scripts/build/paths.mak` 定义。更新 MHMake 引用、跨组件相对路径、Visual Studio 工程、PowerShell 构建入口、NSIS 清单及相关测试。保留现有用户构建命令和 dist 输出位置。

从无构建缓存的独立目录执行 Windows x64 Release 全量构建；执行全部现有自动测试及认证启动、根窗口查询、依赖检查。核对迁移前后文件、模式、许可和依赖修订信息，更新当前文档路径，同时保留历史报告的原始构建事实。
