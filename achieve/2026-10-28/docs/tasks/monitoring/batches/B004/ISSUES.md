# B004 问题记录

- B004-01：Pydantic不能把strict直接加在int|float联合外层；启动schema生成失败。修为各分支严格类型并保持有限浮点，首轮失败日志保留，待复测。
- B004-02：复审发现封存后控制库写失败不能立刻标failed，否则无法恢复；已保留running供下一worker校验manifest后原子提交。注入OSError测试覆盖。
- B004-03：明确无效/未完成结果不能由目录存在推导可读，所有GET先查询completed索引。只读查询前后产物mtime检查覆盖。
- 生产阈值空、DeepSeek缺省pending；测试规则和显式模式不是生产配置。
