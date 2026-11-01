# LH006 执行记录

2026-10-31，纯服务流程闭环。experiments.py从冻结范围选择包含发现两端的连续时间窗（同时间请求整体纳入，超过预算则sample_insufficient），两侧独立空账本；精确门槛复用analysis-common-1.0。pilot未通过不full，全范围同transformation_digest实际重放；保存pilot/full Plan，单改和组合独立计算。

真实GLM六请求测试1 passed（9.52s）：两个动态因素单独修改均未通过pilot，组合通过pilot/full，分别N=3/6，仅full可展示。0.99/1.00/1.01pp精确边界在公共契约测试中覆盖；不把合成样本视为现场性能。无样本不足时强行拼接、未调用线上模型。后台恢复/停止及HTTP属LH007–LH009继续验证，未打包部署。

最终补充真实pilot通过而full不达门槛：加入不匹配变换的大体量后继，完整6条重放后full_below_gate、不展示卡片。初始fixture短于缓存块，pilot实际H=0，调整为超过块大小的有效fixture后通过；未修改业务门槛。该项及封存2项共3 passed（7.11s）。

