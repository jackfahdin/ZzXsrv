# ZzXsrv 项目来源与维护

本项目在 [marchaesen/vcxsrv](https://github.com/marchaesen/vcxsrv) 的 Windows / Visual Studio 适配基础上继续开发。项目仓库为 [jackfahdin/ZzXsrv](https://github.com/jackfahdin/ZzXsrv)，SSH 地址 `git@github.com:jackfahdin/ZzXsrv.git`。

## 最初导入

- 来源提交：`d0a1eaf7ee15fcdf4f683388a88fec49078e6408`，原作者 master 的固定提交。
- 导入日期：2026-09-09。
- 本地初始提交：`e13a9d52d43c447d402932e89fcb3db9e177093b`，文件树与来源提交相同。
- [当时导入的源码](https://github.com/marchaesen/vcxsrv/tree/d0a1eaf7ee15fcdf4f683388a88fec49078e6408)。产品版本为 21.1.16.1，但此提交并不等同于该版本标签。

版权、许可证和第三方署名继续保留，许可证入口为 [COPYING](COPYING) 及各组件目录中的许可文件。

## 当前规则（2026-09-10 起）

只维护线性的 `master` 主线，不再维护 `upstream`、`released` 或原作者整合快照分支。临时开发可以隔离进行，交付时使用快进、rebase 后快进或 squash，不向 master 增加 merge commit。组件来源、固定修订和实际导入链接统一见 [依赖来源文档](docs/DEPENDENCY_SOURCES.md)，更新流程见 [维护规则](docs/UPSTREAM.md)。

本次整理保留原 master 的 23 个第一父链步骤及其各自文件树，将合并节点线性化。旧分支、标签和旧工作区登记已清理；旧源码目录、运行文件及本机日志保留为普通目录，恢复材料位于本地忽略目录。旧报告中的 SHA 是历史证据，不要求在当前主线中仍可直接定位。

整理前后的对应关系、归档和验证见 [2026-09-10 整理记录](docs/validation/2026-09-10-repository-reorganization.md)。本次未升级组件，也没有将尚待实际使用确认的输入处理候选合入；其源码补丁与原候选构建均已留存。
