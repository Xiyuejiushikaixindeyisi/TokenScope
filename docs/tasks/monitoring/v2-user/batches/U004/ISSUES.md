# U004问题记录

- n使用精确Fraction计算，lt为ceil(budget/tau)-1，避免浮点等号和floor误用。closed。
- 不可变情景/估算均在BEGIN IMMEDIATE内检查并写入；并发同键复用同一结果，参数冲突409。closed。
- 无真实校准证据；人工情景明确user_assumption，部署/负载/思考/计时边界要求操作者确认，不把来源字段当作自动验证真实性。外部pending，不影响计算器闭环。
- 情景API未设计过期时间；按明确revision选取、不会自动选择所谓最新校准，覆盖域外返回out_of_scope。缺tau在DTO拒绝，不能默填。
