# B004 开发方案

1. SQLite精确排序与Python整数聚合；J/P/C的1K/2K/5K直方图、开放尾桶/并列众数/nearest-rank，空集保持null。
2. 每appid/model规则CAS版本表；按指标生成口径签名，缓存改动只影响H/C，不使J/P规则失效。无规则/失配/不可用不发信号；同源同规则稳定event_id。
3. 衔接快照→输入→编码→DES→统计→结果封存→控制库completed+outbox原子事务。单worker文件锁和重启恢复；错误保留未完成证据，不暴露部分成功。
4. CLI/API共服务：提交、后台worker、模型readiness、只读metrics/histograms/排名区间分页/signals、规则读写、内部explain。运行领取时冻结设置及规则；profile在运行中冻结，DeepSeek默认仍要求显式选择。
5. 边界统计、签名适用性、规则幂等、发布失败/恢复、配置快照及真实三模型小样本集成；全套静态/回归后再B005。回退B003快照与数据库备份，不清除已完成结果。
