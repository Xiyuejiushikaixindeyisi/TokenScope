# 环境与版本

本目录保存环境描述与来源身份，实际 Python 环境已位于项目 .venv；当前运行方式与锁版本见根README及LOCAL_DEVELOPMENT.md。

- sources.lock.json：已引入的外部源码身份，保存当前已取得研究快照的身份，非运行依赖安装清单。
- profiles：本机与现场环境的事实、要求与差异；监控已有 [V100 profile](profiles/huawei-v100-2026-10-26.json)，其他目标独立核实。
- locks：按依赖工具规则保存的锁文件；工具要求位于仓库根目录的锁文件保留其规范位置，并在此索引。

环境记录覆盖需要的操作系统、CPU 架构、Python/Rust、驱动、CUDA、Docker Engine、Compose 和依赖版本。区分已观察值、要求值和未核实项，不猜测版本。

MemScope 只提供组织方式参考。用户要求先在本地环境完成实现和测试，取得打包同意后再构建镜像。已建立本地环境及待审批Docker/Compose准备文件，但没有构建镜像或交付包。

锁文件只有在实际引入来源或安装确定环境时更新；候选参考清单放 docs/research，不能用占位版本伪装锁定。

