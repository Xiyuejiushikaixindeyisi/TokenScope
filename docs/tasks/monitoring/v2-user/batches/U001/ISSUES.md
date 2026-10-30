# U001 问题
| ID | 问题 | 修复/复测 | 状态 |
| --- | --- | --- | --- |
| U001-I01 | 机械编辑domain产生重复逗号，pytest无法导入 | 删除多余逗号、格式化；28定点测试/ruff/mypy通过 | resolved |
| U001-I02 | 既有测试假设所有新安装DeepSeek默认未决 | readiness更新为新安装ready；pending测试显式保存default，仍验证未决保护 | resolved |
| U001-I03 | 日期解析异常字段硬编码处理起点 | 新增field参数，MA可定位request_time，保留旧签名和UTC默认 | resolved |
| U001-I04 | 跨模型别名配置冲突未检查 | 同一BEGIN IMMEDIATE/CAS事务验证，失败不加revision | resolved |
| U001-I05 | 全量175通过、4失败/4错误：编码测试以新settings配旧profile.name=default，身份校验拒绝 | 保留编码器严格校验，将历史编码夹具显式绑定default，再新增现场模式等价用例；复测中 | resolved；最终205测试通过 |
| U001-I06 | 新测试使用1线程修改全进程RAYON环境，后续8线程测试触发CPU_BUDGET_CONFLICT | 改为统一测试进程8线程，保留运行资源校验；全量复测 | resolved；最终205测试通过 |
