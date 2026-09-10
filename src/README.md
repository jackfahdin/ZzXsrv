# 产品源码

`src/` 保存由 ZzXsrv 产品直接维护和组装的源码。这里的目录边界描述本仓库的维护职责，不改变各项目原有许可证、组件名称或内部结构。

| 目录 | 职责 |
| --- | --- |
| `xorg-server/` | X Server 主体、Windows 后端、XLaunch、字体数据、键盘数据和安装清单。XLaunch 保持在 `xorg-server/hw/xwin/xlaunch/` |
| `platform/libwinmain/` | Windows 入口与控制台适配 |

第三方库和客户端程序位于 [`../third_party/`](../third_party/)，跨组件公共头文件位于 [`../include/`](../include/)。组件修订、实际继承链接与本地证据见[依赖来源清单](../docs/dependencies/SOURCES.md)；迁移前后的精确对应见[源码路径映射](../docs/history/2026-09-10-source-path-mapping.json)。
