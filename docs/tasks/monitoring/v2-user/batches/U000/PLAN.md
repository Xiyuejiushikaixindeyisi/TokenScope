# U000 实施方案
2026-10-30；active。用户已认可设计v1.0并授权逐批实现，不部署打包。
本批仅契约/基线，不注册运行路由。新增src/tokenscope/user_monitoring/contracts.py及scripts/validation/check_user_contract.py，产物docs/contracts/user-monitoring-v2。
共享拥有方：csv_reader.py/domain.py由本线U001修改；app.py/pipeline.py/CLI共享装配保留MA窗口，本批不编辑；statistics.py/simulation.py不改；部署配置仅交接。
基线HEAD 6042a05…；既有各线文档及.githooks修改保留。项目.venv Python3.11，既有pytest169项为U000-T04基线。
资源门槛（开发机本地，不外推现场）：CPU预算8，批256/16MiB；索引10万facts/1万组夹具RSS增量≤256MiB、索引磁盘≤输入facts大小的3倍+32MiB，查询1万组limit100冷/热各10次单次≤2s，估算1000次总计≤2s。执行前记录CPU型号、源规模/摘要，超标按问题调查，不降低门槛。
契约必须完整定义路径、错误、分页、精确数值、恢复和状态样例，Schema生成不代替跨字段验证。全部必要门槛通过才closed并进入U001。
