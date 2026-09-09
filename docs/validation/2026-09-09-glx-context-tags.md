# GLX 上下文标签修复记录

本次回补 GLX 上下文标签生命周期修复；不代表已完成 X Server 全部后续公告的核对。

## 来源与范围

- 本地起点：`59cca4a6c`，工作分支：`codex/update-xserver-security`。
- 上游提交：`2779affbdb4354e894f490e56f962527d6125043`，作者 Peter Hutterer，作者日期 2026-05-31。
- [X.Org 原始提交](https://gitlab.freedesktop.org/xorg/xserver/-/commit/2779affbdb4354e894f490e56f962527d6125043)；本次从 [XQuartz 镜像的同一 Git 提交](https://github.com/XQuartz/xorg-server/commit/2779affbdb4354e894f490e56f962527d6125043) 核对差异。
- 对应 CVE-2026-56000；上游标注引入问题的提交为 `4781f2a5a8c2`。本地已存在它所描述的“延后释放旧 tag”行为，无需再导入该引入问题的提交。
- 只应用 `glx/vndcmds.c` 的生产 hunk，路径适配为 `xorg-server/glx/vndcmds.c`，内容一致（5 行增加、3 行删除）。未整包替换 X Server、修改产品版本号或升级 OpenSSL。
- 原始文件版权与许可声明完整保留。上游测试依赖本仓库没有的 `pyxtest` 框架，因此编写本地 MSVC 测试，不导入该框架。
- 原会话取得的补丁证据：`.local-validation/glx-security/upstream.patch`，SHA-256 `EB79DF6631B0444F5931280D5490B3DC47BA1F48D48DE1FA262C4E7F4B6C35BD`；元数据为同目录 `upstream.json`。本轮未下载源码包或安装工具。

## 根因与回归证据

旧 `oldTag` 指向客户端 tag 数组；分配新 tag 时数组可能搬移，随后释放旧 tag 就会写入已释放内存。修复将旧 tag 的清理移至成功解除旧 context 之后、新 tag 分配之前。解除失败时仍保留旧状态。

测试直接编译实际 `vndcmds.c` 与 `vndservermapping.c`。仅替换分配器和外围服务器服务；未使用的链接替身被调用时立即终止。每个场景使用独立进程，通过 MSVC AddressSanitizer 检查内存访问。

| 验证 | 结果 | 证据 |
| --- | --- | --- |
| 修复前回归 | 8 项中 3 项失败：正常及交换字节序的满数组切换触发 ASAN heap-use-after-free；新 context 创建失败路径残留旧 tag | `.local-validation/glx-security/red-tests.log` |
| 修复后回归 | 8 项通过，0 跳过 | `.local-validation/glx-security/green-tests.log` |
| 其他已覆盖场景 | 无旧 context 的扩容、相同 context、解除绑定、解除失败、分配失败、非法 context/tag | `tools/tests/test_glx_context_tags.py` |
| 独立代码审查 | 未发现阻断项；生产差异与上游一致，已复核测试与已有日志 | 当前接续任务的只读审查记录 |

复跑：在 x64 Visual Studio 开发环境设置 `VCXSRV_TEST_LOCAL_TOOLS=1`，执行 `python -B -m unittest discover -s tools/tests -p test_glx_context_tags.py -v`。使用 `/fsanitize=address`；缺少编译器、头文件或链接依赖会明确失败。

测试编译准备中修正了 `damage.h` 的包含路径、重复定义的函数和独立链接所需的服务替身。上述准备错误不算问题复现；红灯证据来自测试已成功编译后的 ASAN 与状态断言失败。

## 待完成的集成验收

固定源码提交后执行本工作区的首次 x64 Release All 构建，随后执行全部脚本/运行集成测试、PE 依赖与认证连接验证，并记录新产物哈希。主目录及此前基线运行目录保持独立。

真实 Linux OpenGL 应用、键盘和窗口操作、GLX 客户端断开清理尚未验证。当前单元测试使用外围 vendor 替身，不能把普通 tag 释放等同于真实客户端断开，也不能替代完整桌面回归。实际应用场景验收前，不将这项组件维护标记为全部完成。
