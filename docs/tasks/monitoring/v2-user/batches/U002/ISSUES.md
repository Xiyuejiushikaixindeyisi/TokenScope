# U002 问题闭环

- I01：纯统计函数会保留全部并列箱；生产投影改为SQLite稀疏箱持久化，查询分页，不调用该内存列表函数。closed。
- I02：原草案派生键含冒号，不满足基础RunSubmission格式；使用uv2.<user_run_id>，不改变外部键。closed。
- I03：资源探针首次用相对路径as_uri失败；改绝对项目内路径，重跑通过。closed。
- I04：类型检查发现嵌套DTO字典类型不符，显式构造DTO；格式/类型检查通过。closed。
- 储存短暂故障保留accepted/indexing并由worker重试；不可用源明确failed/REANALYSIS_REQUIRED，原结果不改。重试次数和自动退避未新增产品语义。
