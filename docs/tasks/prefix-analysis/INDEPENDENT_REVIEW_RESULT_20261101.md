# 低命中率后端与公共层独立复审 · 2026-11-01

**最终结论：arpc-local-4在本次低命中后端/公共层复审范围内通过；PCR-01（P1）、PCR-02（P2）均已由维护方修复并独立复验关闭。原arpc-local-3不通过记录保留。** 本报告由审查session `01a1800e-80b4-7400-a78b-a84f5b6e888d`（环境CODEX_THREAD_ID实取）形成，不是提供方自审复述。按本轮转交的明确用户授权执行，旧prompt“仅准备未启动”已被覆盖；不改业务代码、正式前端或冻结契约，不构建/打包/部署/Git发布。

## 候选与证据

原候选prefix-common-review-20261101-1 / arpc-local-3；HEAD不是候选。审查覆盖公共analysis_common、prefix_analysis、诊断API及共享装配，Token按消费依赖验证，不代签其私有策略或前端视觉验收。

[身份核对](../../../artifacts/reviews/prefix-common-independent-20261101/identity.json)：三份候选/依赖/RV1身份共418条摘要，416匹配；两条不匹配均为同一个ACCEPTANCE_UI04.md，当前追加RV1统一入口，源码/测试/契约/RV1数据未漂移。完整工作树含untracked，已按manifest读取，不用HEAD代替。

## 原候选独立发现与归口（失败时点，现已关闭）

[问题清单](INDEPENDENT_REVIEW_ISSUES_20261101.md)为复现/修复标准权威记录。

- PCR-01 / P1：工具顺序交换时L3对照绑定错误工具。独立真实GLM回放通过收益gate后，局部comparison断言失败，1 failed / 5.91s。维护方已确认并进入evidence模块修复窗口；原候选测试进程已先启动，新版本需另测，不混记。
- PCR-02 / P2：候选扫描partial仍宣称推荐members_complete=true。正常服务生成partial封存记录独立复现，1 failed / 7.75s。完整Plan收益与发现成员完整性应分别表达。

## 已完成的独立检查

- RV1原目录复制到新review/rv1-copy；在复制状态使用真实create_app/TestClient，封禁submit/process_next/encode/analyze_request。215个GET路由（含分页/错误参数）及实际JSON核对通过，实例身份一致，ready历史可读，两方向默认仍指第二ready；最新partial不覆盖。原目录84文件摘要前后不变。[结果](../../../artifacts/reviews/prefix-common-independent-20261101/rv1-readonly.json)、[实际响应](../../../artifacts/reviews/prefix-common-independent-20261101/rv1-responses.json)。不向原验收服务写入，不重启别人进程。
- 来源源码：appid及半开窗口SQL过滤、time_ns/record稳定排序、scope成员摘要与源封存校验；同一监控编码/ledger复用，无独立计量实现。
- 两阶段源码：精确Fraction严格>1pp，pilot只决定full进入；direct_full单列；N按实际raw改变统计，回放完整原scope，异常返回blocked无假after。
- L2同完整工具映射指纹、唯一function名称、固定排序；定义变化不当作纯排序。L4仅关联不足观察，L5保留完整原JSON表示。L3证据映射发现PCR-01。
- 推荐编排：先每项prepare/guard，再canonical字节复用；依据不同不合并，快照冻结且retry复用；Token tools修改显式拒绝；私密selector/generator/basis JSON从业务GET剔除。
- 状态源码：封存文件fsync/rename后事务发布；取消与发布事务串行，outbox同任务终态触发；目录默认只接受ready。成员完整性发现PCR-02。
- 局部证据：Unicode码点与escaped offsets映射、重复key显式歧义、最长公共前后缀定位、零宽删除、截断标志；不是前端重新计算。

原候选公共/低命中139 passed / 242.93s（命令wall 243.77s）；随后mypy 44源文件、ruff通过。该测试进程在维护窗口前已加载原代码；类型/静态检查在维护窗口内运行，不将这一组声称为最终版本全套。新增独立用例揭示上述两项旧回归缺口。Token消费链/监控兼容随后完成315 passed / 291.56s；该进程启动于维护窗口内，只作为兼容补充，不冒称最终候选单次全套。最终版本的受影响Token链另测见下表。

已接收[维护方修复交接](INDEPENDENT_REVIEW_FIXES_20261101.md)，最终已独立签收候选arpc-local-4。118条新身份摘要一致，最终复验进程开始时7变更文件均匹配维护身份；维护方38通过不计为独立通过。新增运行时语义改动为低命中发现覆盖与完整Plan评估分离，结构Schema保持原摘要。修复后RV1再次215路由读取一致/84原文件未变，见[新只读结果](../../../artifacts/reviews/prefix-common-independent-20261101/rv1-final-readonly.json)。

## 未覆盖与边界

构造数据使用固定真实Tokenizer/Chat Template及离线回放，不证明生产业务授权、输出质量、SLA/TTFT或费用收益。15万请求/华为现场容量未校准；256提案上限不等于大appid容量。低命中发布时Plan预算核算发生于计算后，不是前置RSS上限。现有messages不等于原生Responses，缺session/turn不推断过程。静态核对advice_examples会跳过缺location的支持、返回空例子而不捏造before/after；本轮未新增该稀缺输入的生产消费者验收。本报告不代签Token私有算法/业务策略和用户视觉。旧ARL5/ART4/RV1原始state及报告不回填。


## 修复后独立复验与最终判定

最终身份：arpc-local-4，维护方[身份清单](INDEPENDENT_REVIEW_FIX_IDENTITY_20261101.json)。审查方核对118条摘要一致；[启动身份](../../../artifacts/reviews/prefix-common-independent-20261101/final-start-identity.json)与[结束身份](../../../artifacts/reviews/prefix-common-independent-20261101/final-end-identity.json)完全一致，结束后再次与工作树匹配。修复窗口明确包含4源码+3测试，旧候选/原失败日志均不覆写。

| 独立执行 | 实际结果 | 证据 |
| --- | --- | --- |
| 最终公共/低命中单元及集成全套 | 146 passed，276.91s；包含维护方新增交换/不交换工具双侧证据、partial/ready覆盖回归 | [final-0.log](../../../artifacts/reviews/prefix-common-independent-20261101/final-0.log) |
| 审查方独立边界 | 4 passed，10.84s；PCR-01双侧同工具、PCR-02成员与评估分离、多处分离Unicode差异/零宽删除、Token不完整成员仍拒绝 | [用例](../../../artifacts/reviews/prefix-common-independent-20261101/test_independent_edges.py) · [final-1.log](../../../artifacts/reviews/prefix-common-independent-20261101/final-1.log) |
| 最终Token受影响专项 | 6 passed，53.27s；真实同scope自动推荐、三模型T3、P降C升和ART4具体方案消费 | [final-token.log](../../../artifacts/reviews/prefix-common-independent-20261101/final-token.log) |
| 最终类型/静态 | mypy 44源码文件、ruff通过 | [命令/退出码/耗时](../../../artifacts/reviews/prefix-common-independent-20261101/final-checks.json) |
| 最终旧RV1封存兼容/零计算GET | 215路由结果一致，84原文件未变化；分页不重漏、错误实例409、非法分页422、默认保持 | [只读结果](../../../artifacts/reviews/prefix-common-independent-20261101/rv1-final-readonly.json) |

以上分别计数，不与原139、兼容315、维护方38或历史ARPC/Token记录相加当作唯一用例总数。Python3.11.16、pytest9.1.1；依赖版本、锁和三个模型revision/8个实际编码资产已独立核对并固定于[环境身份](../../../artifacts/reviews/prefix-common-independent-20261101/environment.json)。保留Starlette/httpx弃用warning；transformers无PyTorch提示仅影响模型推理，本次Tokenizer离线回放不需要安装PyTorch。未安装/升级依赖。

PCR-01修复代码定位：recommendation_evidence.py:163按recipe逻辑槽位解析双方pointer，:185生成对照时校验双侧hash及Plan目标；无法映射显式COMPARISON_TARGET_UNRESOLVED。独立原复现现通过，两个原请求方向均有正确工具a对照，原Plan收益保持。

PCR-02修复代码定位：recommendation_publication.py:53传发现完整性、recommendation_projection.py:67/:168保守默认及投影，recommendations.py:250仅Token完整提案仍强制members_complete。独立partial生成保留6/6完整回放收益而成员不完整；完整ready回归为true。未删除断言或降低收益/原scope/默认发布约束，未修改公开结构Schema。

通过范围是上述固定本地候选的低命中/公共后端及消费边界；不代表Token私有算法的独立全范围复审、用户功能/视觉签字、生产策略批准或华为现场通过。当前无本范围未关闭阻断项；资源/容量、生产策略与真实数据限制保持，不因通过扩大能力。

本轮输出[结构化结果与证据摘要](INDEPENDENT_REVIEW_RESULT_20261101.json)。所有测试在新目录；原ARL5/ART4/RV1不回填，原RV1仅复制读取。没有构建镜像、交付打包、部署、远端操作或Git提交/push；HEAD保持5d824b506d9e055bcf397c3846dafc450fcf02e5。等待异常分析各线验收及后续明确统一交付安排。
