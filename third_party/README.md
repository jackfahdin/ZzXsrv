# 第三方组件

`third_party/` 按来源领域归类随仓维护的依赖。归入此目录只表示维护职责，不表示源码是未经修改的纯净上游副本；许多组件包含 VcXsrv 或 ZzXsrv 的 Windows 适配。

| 目录 | 内容 |
| --- | --- |
| `xorg/` | X.Org 库、客户端程序、字体工具、键盘工具和 XCB 辅助组件 |
| `graphics/` | Mesa、Pixman 和 DXTN |
| `fonts/` | FreeType 和 Fontconfig |
| `expat/`、`libregex/`、`libxml2/`、`openssl/`、`pthreads/`、`zlib/` | 独立第三方组件 |

`tools/plink/` 和 `tools/mhmake/` 是仓库工具，继续保留在 [`../tools/`](../tools/)；公共头文件位于 [`../include/`](../include/)。不要仅凭目录名推断组件版本或上游纯净性，修订、固定 URL、导入方法和未知项以[依赖来源清单](../docs/dependencies/SOURCES.md)为准。
