# U002 closed

绑定/稀疏投影/发布恢复及资源门槛通过，进入U003。实现见src/tokenscope/user_monitoring/{storage,service,projection}.py；精确字符串总量不使用SQLite SUM。历史升级是新增侧索引，不改封存；回退停用独立模块即可，需保留独立控制库以保存绑定身份，不能删除源。显式rebuild可恢复派生索引。

本批没有装配HTTP/CLI，U003负责；无部署打包，真实校准/前端仍待验证。
