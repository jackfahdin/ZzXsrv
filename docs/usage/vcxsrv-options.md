# vcxsrv.exe 命令行参数参考

本文整理 `vcxsrv.exe` 的全部命令行参数，以本仓库源码为准：

- XWin 专属参数：`src/xorg-server/hw/xwin/InitOutput.c` 中 `winUseMsg()` 的帮助输出（`ErrorF` 块），默认值结合 `winglobals.c`、`winprocarg.c` 中的实际初始化。
- Xorg 通用参数：`src/xorg-server/os/utils.c` 中 `UseMsg()` 的帮助输出，以及 `os/xdmcp.c`（XDMCP）、`os/serverlock.c`（锁）、`xkb/xkbInit.c`（AccessX）的补充帮助。

版本基准：xserver 21.1.16.1（tag `v21.1.16.1`），master 提交 `1acde235e8`。参数行为如有出入，以本机 `vcxsrv.exe -help` 的实际输出为准（帮助文本会写入日志文件并弹出提示框说明日志位置）。

说明约定：

- `-[no]xxx` 表示该参数有成对形式 `-xxx` / `-noxxx`。
- 「默认值」一栏只写源码中可以确定的值；源码未显式给出或依赖运行时环境的标「—」。
- 带 ★ 的参数在典型用法一节有组合示例。

## 1. 窗口模式

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| ★ `-multiwindow` | 以 multiwindow 模式运行：每个顶层 X 窗口显示为独立的 Windows 窗口，并启用内置窗口管理器。不能与 `-rootless` 或 `-fullscreen` 同时使用。 | 关（默认单窗口 windowed 模式） |
| `-rootless` | 使用透明的 root window，配合外部窗口管理器（如 openbox）使用。不能与 `-multiwindow` 或 `-fullscreen` 同时使用。 | 关 |
| ★ `-fullscreen` | 以全屏模式运行服务器。 | 关 |
| `-screen scr_num [width height [x y] \| [[WxH[+X+Y]][@m]]]` | 启用编号为 scr_num 的屏幕，可选指定宽度、高度和初始位置；还可以用 `@m` 指定服务器启动所在的显示器编号，此后所有坐标都相对于该显示器。示例：`-screen 0 800x600+100+100@2`（第 2 台显示器，偏移 100,100，大小 800x600）；`-screen 0 1024x768@3`；`-screen 0 @1`（第 1 台显示器全分辨率，即默认行为）。 | `-screen 0 @1`（主显示器全分辨率） |
| `-[no]multimonitors` / `-[no]multiplemonitors` | 存在多台显示器时使用整个虚拟屏幕。 | 关；但 `-multiwindow` 会自动置开（除非显式用 `-nomultimonitors` 覆盖），`-fullscreen` / `-rootless` / `-nodecoration` 则置关 |
| `-resize=none\|scrollbars\|randr` | 窗口模式下（不）允许调整窗口大小：`scrollbars` 在需要时给窗口加滚动条；`randr` 通过 RANDR 扩展调整 X 屏幕大小。 | `randr`（全屏模式下为不允许调整） |
| `-nodecoration` | 不绘制窗口边框、标题栏等装饰。仅窗口模式有效，指定 `-fullscreen` 时被忽略。 | 关 |
| `-[no]hostintitle` | multiwindow 模式下在窗口标题中附加远程主机名。 | 开 |
| `-icon icon_specifier` | 设置窗口模式下屏幕窗口的图标。 | — |
| `-[no]trayicon` | 不创建通知区域（托盘）图标。默认为每个屏幕创建一个图标。可以先用 `-notrayicon` 全局禁用，再对特定屏幕用 `-trayicon` 单独启用。 | 开（每屏幕一个图标） |

## 2. 剪贴板集成

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| ★ `-[no]clipboard` | 启用（禁用）剪贴板集成。 | 开 |
| `-[no]primary` / `-noprimary` | 剪贴板集成启用时，是否把 X11 的 PRIMARY 选择映射到 Windows 剪贴板。CLIPBOARD 选择只要 `-clipboard` 启用就始终映射。 | 开（映射） |
| `-clipupdates num_boxes` | 当更新区域中的矩形数量达到 num_boxes 或以上时，用裁剪区域把 shadow 更新位块传送限制在更新区域内。在当前 Windows 版本上效果减弱，因为系统已把 GDI 操作批量分组，效果类似。 | — |

## 3. 显示与渲染

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `-depth bits_per_pixel` | 在全屏模式下配合 DirectDraw 引擎指定可选的位深。 | — |
| `-refresh rate_in_Hz` | 在全屏模式下配合 DirectDraw 引擎指定可选的刷新率。 | — |
| `-engine engine_type_id` | 覆盖服务器自动选择的引擎类型：`1` = Shadow GDI；`4` = Shadow DirectDraw4 Non-Locking。 | 自动选择 |
| ★ `-[no]wgl` | 启用 GLX 扩展，使用 Windows 原生 WGL 接口获得硬件加速 OpenGL。 | 开 |
| `-swrastwgl` | 启用 GLX 扩展，使用基于 swrast 接口的 Windows 原生 WGL 接口获得加速 OpenGL。 | 关 |
| `-swcursor` | 禁用 Windows 光标，改用 X11 软件光标。 | 关 |
| `-lesspointer` | 当 Windows 鼠标指针位于任何 vcxsrv 窗口之上时隐藏它，避免 Windows 光标叠加在 X 光标上产生"幽灵光标"。 | 关 |
| `-[no]compositealpha` | 带逐像素 alpha 的 X 窗口会被合成进 Windows 桌面。 | 开 |
| `-[no]compositewm` | 启用（禁用）Composite 扩展，用于 multiwindow 模式：借助 Composite 扩展的重定向为每个顶层 X 窗口维护位图，使被遮挡的窗口内容在任务栏和任务切换器预览中显示正确。 | 开 |

## 4. 输入与键盘

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `-[no]emulate3buttons [timeout]` | 模拟三键鼠标，可选指定超时（毫秒）。系统只有两键鼠标时会自动启用（超时 50 毫秒）。 | 自动（两键鼠标时开，超时 50 ms） |
| `-[no]keyhook` | 拦截特殊的 Windows 按键，如 Alt-Tab 或菜单键。 | 关 |
| `-ignoreinput` | 忽略键盘和鼠标输入。 | 关 |
| `-[no]unixkill` | Ctrl-Alt-Backspace 退出 X 服务器。该组合键默认禁用。 | 关 |
| `-[no]winkill` | Alt+F4 退出 X 服务器。 | 开 |
| `-xkblayout XKBLayout` | 设置 XKB 布局。默认使用与当前 Windows 布局匹配的布局，找不到匹配时用 `us`。示例：`-xkblayout de`。 | 匹配 Windows 布局，否则 `us` |
| `-xkbmodel XKBModel` | 设置 XKB 型号。 | `pc105` |
| `-xkbrules XKBRules` | 设置 XKB 规则。 | `xorg` |
| `-xkbvariant XKBVariant` | 设置 XKB 变体。示例：`-xkbvariant nodeadkeys`。 | 不设置 |
| `-xkboptions XKBOptions` | 设置 XKB 选项。 | 不设置 |

## 5. 诊断与日志

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `-logfile filename` | 把日志消息写入指定文件。 | `XWin.log` |
| `-logverbose verbosity` | 设置日志详细级别（目前只有少数消息遵循该设置）：`0` 只打印致命错误；`1` 额外打印配置信息；`2` 额外打印运行时信息；`3` 打印调试和跟踪信息。 | `2` |
| `-silent-dup-error` | 不显示"同一显示号已有实例在运行"的致命错误弹出框。 | 关（弹框） |

## 6. Xorg 通用：网络与安全

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| ★ `:display-number` | 以指定显示号运行服务器（如 `:0`、`:1`）。运行多个实例时必须使用互不相同的显示号。 | `0` |
| ★ `-listen protocol` / `-nolisten protocol` | 监听（不监听）指定协议，常用值为 `tcp`。例如 `-nolisten tcp` 关闭 TCP 端口 6000+N 的监听，只保留本地连接。 | 编译期默认 |
| ★ `-auth file` | 指定授权文件（Xauthority），用于基于 cookie 的客户端认证。 | — |
| `-ac` | 禁用访问控制限制（任何主机都能连接，**有安全风险**，见下文）。 | 访问控制启用 |
| `-audit int` | 设置审计跟踪级别。 | — |
| `-pn` / `-nopn` | 接受（拒绝）"无法监听所有端口"的失败继续运行。 | — |
| `-nolock` | 禁用服务器锁机制。 | — |
| `-displayfd fd` | 服务器就绪后把显示号写入指定文件描述符（供启动器探测）。 | — |
| ★ `-query host-name` | 通过 XDMCP 连接指定主机。 | — |
| `-broadcast` | 广播探测 XDMCP 主机。 | — |
| `-indirect host-name` | 通过指定主机进行间接 XDMCP 查询。 | — |
| `-port port-num` | XDMCP 发送消息使用的 UDP 端口号。 | — |
| `-from local-address` | 指定 XDMCP 连接使用的本地地址。 | — |
| `-once` | 一个会话结束后即终止服务器（XDMCP）。 | 关 |
| `-class display-class` | 指定 XDMCP manage 请求中发送的显示类。 | — |
| `-displayID display-id` | XDMCP 请求的制造商显示 ID。 | — |

## 7. Xorg 通用：其他

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `-help` | 打印本帮助信息（写入日志文件）。 | — |
| `-fp string` | 默认字体路径。 | 编译期内置字体路径 |
| `-dpi [auto\|int]` | 屏幕分辨率：`auto` 使用原生 DPI，或指定数值（点/英寸）。 | `auto` |
| `-br` | root window 使用黑色背景。 | — |
| `-wr` | root window 使用白色背景。 | — |
| `-retro` | 启动时使用经典网格（stipple）背景。 | — |
| `-background [none]` | 创建无背景的 root window。 | — |
| `+bs` / `-bs` | 启用（禁用）任意 backing store 支持。 | — |
| `-render [default\|mono\|gray\|color]` | 设置 render 颜色分配策略。 | `default` |
| `+xinerama` / `-xinerama` | 启用（禁用）XINERAMA 扩展。 | 启用 |
| `+iglx` / `-iglx` | 允许（禁止）创建间接 GLX 上下文。 | 允许 |
| `+extension name` / `-extension name` | 启用（禁用）指定扩展。 | — |
| `-terminate [delay]` | 服务器 reset 时终止，可选延迟秒数。 | 关 |
| `-noreset` / `-reset` | 最后一个客户端退出后不（/要）执行服务器 reset。 | `reset` |
| `-maxclients n` | 设置最大客户端数（2 的幂）。 | — |
| `-r` / `+r` | 关闭（开启）键盘自动重复。 | 开启 |
| `-a #` | 默认指针加速度（倍率）。 | — |
| `-t #` | 默认指针阈值（像素/t）。 | — |
| `-f #` | 响铃基准音量（0–100）。 | — |
| `-cc int` | 默认颜色 visual 类。 | — |
| `-deferglyphs [none\|all\|16]` | 延迟加载字形：不延迟 / 全部延迟 / 16 位字形延迟。 | — |
| `-tst` | 禁用测试类扩展。 | — |
| `-I` | 忽略其后所有剩余参数。 | — |
| `-dumbSched` | 禁用智能调度和线程化输入，恢复旧行为。 | — |
| `-schedInterval int` | 设置调度间隔（毫秒）。 | — |
| `-nocursor` | 禁用光标。 | — |
| `-dpms` | 禁用 VESA DPMS 显示器节能控制（需编译启用 DPMSExtension）。 | — |
| `-fakescreenfps #` | 虚拟屏幕默认帧率（1–600）。 | — |
| `[+-]accessx [...]` | 启用/禁用 AccessX 按键序列（可带 timeout 等参数）。 | — |

以下通用参数仅对 Unix/Linux 有意义，在 Windows 版 vcxsrv 中不适用或未编译进帮助输出，故不展开：`-vtN`、`-keeptty`、`-ld` / `-lf` / `-ls`（资源限制）、`-core`（core dump）、`-seat`（systemd seat）、`-vmid` / `-vsockport`（Hyper-V VSock）、`-ardelay` / `-arinterval`（MSVC 构建中不输出）。

另有一组 XWin 参数仅在启用对应编译宏时才出现在帮助中：`XWIN_XF86CONFIG` 下的 `-config` / `-configdir` / `-keyboard`（xorg.conf 风格配置文件），以及 `XWIN_EMULATEPSEUDO` 下的 `-emulatepseudo`（在 TrueColor 深度下创建 8 位 PseudoColor visual，颜色不正确且可能崩溃）。

## 典型用法组合

### 桌面集成（最常用）

```
vcxsrv.exe :0 -multiwindow -clipboard
```

- `-multiwindow`：每个 X 应用窗口成为独立的 Windows 窗口，由内置窗口管理器管理，可直接进任务栏、Alt-Tab 切换。
- `-clipboard`：Windows 剪贴板与 X 的 CLIPBOARD / PRIMARY 选择双向同步。若不希望鼠标选中（PRIMARY）就覆盖 Windows 剪贴板，加 `-noprimary`。
- 硬件 OpenGL 默认开启（`-wgl`）；`-multiwindow` 模式下默认使用多显示器的整个虚拟屏幕，可用 `-nomultimonitors` 或 `-screen 0 @1` 限定到单台显示器。

### 全屏独占

```
vcxsrv.exe :0 -fullscreen
```

- 整个屏幕被 X 桌面独占，需要远程侧启动窗口管理器/桌面环境。
- 全屏模式下 `-resize` 自动变为不允许调整；`-nodecoration` 被忽略。
- 需要 DirectDraw 引擎调整位深/刷新率时可用 `-depth` / `-refresh`。

### 无头纯转发（配合 SSH X11 forwarding）

```
vcxsrv.exe :0 -nolisten tcp -clipboard -multiwindow
```

- 本地终端 SSH 客户端通过 `ssh -X`/`-Y` 转发 X11 流量时，显示连接走 SSH 通道到本机回环（通常 `DISPLAY=localhost:10.0`），服务器**不需要**监听 TCP。
- `-nolisten tcp` 关闭 6000 端口的对外监听，是本场景最重要的安全参数。
- 不需要 X 桌面集成时可去掉 `-multiwindow`，仅以窗口模式显示 root window。

### 嵌入第三方 SSH 客户端（类似 MobaXterm 的用法）

MobaXterm 等工具内置 X 服务器并自动携带显示号与认证信息。若用外部 SSH 客户端调用 vcxsrv，推荐组合：

```
vcxsrv.exe :0 -multiwindow -clipboard -nolisten tcp -auth C:\path\to\Xauthority
```

安全注意点：

- **务必 `-nolisten tcp`**：TCP 监听一旦打开，局域网内任何主机都能尝试连接；X11 协议本身无加密。
- **用 `-auth` 指定 Xauthority 文件**做 cookie 认证，未持有效 cookie 的客户端会被拒绝。`ssh -X` 转发会自动处理 cookie，本地直连场景才需要手动管理该文件。
- **`-ac` 会完全关闭访问控制**，任何能连到端口的客户端都能操作你的 X 会话（截屏、注入按键）。仅在隔离测试环境临时使用，不要与 `-listen tcp` 一起用于日常环境。

## 交叉参考

- `src/xorg-server/hw/xwin/man/XWin.man`：上游 Cygwin XWin 的 man 页（本仓库保留），描述了三种窗口模式和屏幕参数，可与本文交叉阅读；个别表述与当前 MSVC 构建的 `-help` 输出不完全一致时，以源码 `winUseMsg()` 为准。
- 帮助文本输出后写入日志文件（默认 `XWin.log`），并弹出对话框告知日志路径。
