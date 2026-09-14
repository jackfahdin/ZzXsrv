# libxml2 来源与重建评估

状态：评估完成，生产依赖尚未替换。已确认现有 x64 DLL 运行版本为 2.9.1；官方 2.15.4 可用 MSVC/CMake 构建，实际 XLaunch 和 Fontconfig 的 UTF-8 正常场景可用，但无 iconv 的试验配置不能等价替换旧库。主线生产代码和已验收运行目录保持不变。

## 现有材料与来源边界

基线 `31ffa193008634c7a0371867a678ee0884e1de19`。`third_party/libxml2` 只有头文件、32/64 位 DLL、导出表和 MSVC 导入库，没有完整 libxml2 实现源码或原构建记录。`createimplib.txt` 说明了从 DLL 导出表生成 MSVC 导入库的步骤，并不是从源码编译 DLL 的方法。

头文件声明 2.9.1。本次在独立 Python 进程加载 x64 DLL，调用其 `__xmlParserVersion`，得到 `20901`。DLL SHA-256 为 `3c68a190dc6d550334ff9d0a506e9526105b008364dad0915562413ceec092cb`。没有 Windows 版本资源。32 位 DLL 未执行，不把 x64 结果延伸到它。

实际继承链接仍为来源清单中固定的 VcXsrv 提交；本地 Git 历史只显示初始导入和目录迁移。原始二进制发布者、构建参数、补丁集和精确源码提交仍未知。确认运行版本不等于这些来源信息已经闭合。

当前 x64 运行目录的导入表显示：

| 文件 | 相关直接依赖 |
| --- | --- |
| xlaunch.exe、xclock.exe | libxml2-2.dll |
| libxml2-2.dll | libiconv-2.dll、zlib1.dll，以及 Windows 系统 DLL |
| vcxsrv.exe | zlib1.dll；本次未发现对 libxml2 的直接导入 |
| libgcc_s_sjlj-1.dll | libwinpthread-1.dll |

Fontconfig 源码启用 libxml2 SAX/push 解析路径，是 xclock 等消费者的间接依赖。不能只核对 XLaunch。随包 GCC/pthread DLL 的去留还需完整打包依赖分析，本轮未删除任何库。

## 隔离重建试验

来源：[GNOME 官方 2.15 目录](https://download.gnome.org/sources/libxml2/2.15/)，2026-09-15 查到最新条目 2.15.4。实际下载 [源码包](https://download.gnome.org/sources/libxml2/2.15/libxml2-2.15.4.tar.xz) 与同目录校验文件，计算 SHA-256 与发布值一致：

`98087fd181d9070724f3fbc65c7377db03038eb92bd882374daff44940138821`

源包 NEWS 将该版标为 2026-09-01，下载目录条目时间为 2026-09-04；二者分别是包内发行标记和目录时间，不混写。归档、源码、生成程序和试验脚本均位于忽略目录 `.local-validation/libxml2-assessment-20260915/`，属于一次性评估材料，没有导入 `third_party`。

使用 VS2022 x64 MSVC 19.44.35227、VS 自带 CMake 3.31.6-msvc6，未使用 PATH 中的 CMake 4.4.0-rc2。CMake 生成器为 Visual Studio 17 2022、平台 x64，Release 动态库。显式关闭 ICONV、ZLIB、TESTS 和 PYTHON；其余采用该版本默认项，包括 SAX1、PUSH、TREE、OUTPUT 和线程支持。此配置用于测出最小构建的兼容性差异，不是正式产品配置。

配置与构建均退出 0，生成 `libxml2.dll` 和 `libxml2.lib`；运行版本为 `21504`。DLL 命名与旧 `libxml2-2.dll` 不同，正式接入必须同步头文件、链接和打包规则，不能仅重命名 DLL 后覆盖旧目录。

## 正常场景验证

在独立进程加载对应库，对自建正常 XML 的中文属性读取及 UTF-8 保存进行核对；所有配置均由试验生成，不读取用户配置或凭据。

| 场景 | 旧 x64 2.9.1 | 新 2.15.4，无 iconv |
| --- | --- | --- |
| UTF-8 中文与转义属性读取、保存 | 通过 | 通过 |
| UTF-16 中文读取、保存为 UTF-8 | 通过 | 通过 |
| GBK 中文读取、保存为 UTF-8 | 通过 | 不支持，解析返回失败 |
| GB18030 中文读取、保存为 UTF-8 | 通过 | 不支持，解析返回失败 |

另外重新编译仓库实际 `xlaunch/config.cc`，以真实 CConfig 执行中文、转义属性、窗口模式、显示号与剪贴板布尔值的保存/加载往返，结果通过。试验驱动最初误包含 CMake 的同名 config.h；改为明确包含 XLaunch 实际头文件后通过。原失败保存在 `xlaunch-header-collision.log`，不把驱动错误归为生产缺陷。

Fontconfig 使用上一已验收工作区的真实 `libfontconfig.lib` 和 FreeType 2.14.3，重新链接新 `libxml2.lib`，执行现有正常字体消费者：创建磁盘缓存、另一个进程重载、列举两种字体与 CFF 字体匹配均通过，两阶段输出都是 `cache-patterns=2 list-patterns=2 unique-files=2`。本次没有将 Fontconfig 全部源文件按新头文件重编，因此不宣称完整源码兼容验证完成。

本轮未运行整包构建、370 项完整 suite、上游测试套件或人工 GUI 测试；原运行版本的这些结果不移植给本试验。

## 迁移结论与后续条件

推荐继续采用官方固定源码加 MSVC/CMake 的重建路线，但不采用本次无 iconv 的精简配置：实测会失去 GBK/GB18030 支持。正式实施必须先确定可追溯的字符编码库来源和构建方式，再与 libxml2 联动导入；保留旧未知来源 iconv DLL 只能算过渡，不能宣称依赖来源全部闭合。

还需处理新版明确的行为变化：[2.15 官方发行说明](https://discourse.gnome.org/t/libxml2-2-15-0-released/31397)记录内置 HTTP 客户端移除，以及读取压缩 XML 需要 XML_PARSE_UNZIP。XLaunch 目前调用 `xmlReadFile(filename, NULL, 0)`；单纯开启 ZLIB 并不足以宣称旧的自动解压行为得到保留。HTTP/压缩配置在用户实际使用中是否需要仍无证据，应在迁移方案中明确本地配置范围及兼容处理，不默默缩减能力。

后续正式候选的完成条件：

1. 固定 libxml2 和编码依赖的源码、校验值、许可证及构建选项；确认 zlib 与 XML 文件读取行为。
2. 从新头文件重编 Fontconfig、XLaunch、xclock，接入现有原生构建和 Portable 打包，审查 DLL 依赖闭包。
3. 将上述正常配置往返与编码用例纳入持久回归，再执行完整构建、全部自动回归和独立运行检查。
4. 在独立目录交付候选并取得实际使用反馈后整合；本次评估不替代该验收。

## 证据

本地 `.local-validation/libxml2-assessment-20260915/`：`source.json`、`legacy-imports.txt`、`legacy-exports.txt`、`legacy-probe.json`、`no-iconv-probe.json`、`runtime-dependencies.json`、`configure-no-iconv.log`、`build-no-iconv.log`、`consumer-results.json` 及消费者逐项日志。试验代码为一次性探路材料，不是生产实现或已交付候选。
