> V2历史材料，仅供追溯，不是当前启动/修复/打包指令。[原始字节](../../../../../originals/docs/tasks/viewer/analysis/PROMPT_LOW_HIT_READONLY_RECEIPT.md) · [当前会话登记](../../../../../../../../memory/SESSIONS.md)。下文仅迁移导航链接，历史决定和结果未更新。

# 低命中／公共后端接入确认补充 prompt FE-R-L1

接收会话：低命中率异常分析后端，01a18be2-7112-7aa2-919b-5137d1f1b1ad。
用户已明确授权前端将本补充prompt发送给两个现有后端session并等待回传。当前只确认接入缺口、整理文档/样例/摘要，不改业务源码、不启动分析服务/真实任务、不打包部署或Git收口。请核实自身ID与memory/SESSIONS.md，保留其他会话工作。无需向前端发送跨会话消息：将结果写到下面指定的本线文件，并在本聊天最终回复路径和结论，前端会等待并读取。
项目根/home/zhangxiyue/TokenScope；前端session 01a19111-344a-75c1-84e0-14db8be08f4f。UI-03及轻量缓存/历史/返回方案已获用户认可。前端仅展示问题/证据、修改建议、后端已有预期收益，不提供单项参数/授权/评估操作，不自动POST；业务修改Agent后在用户监控查看当前命中率。完成通知后GET、打开/重连对齐目录、不轮询，partial保留旧默认报告。
请先读docs/tasks/viewer/analysis/DEVELOPMENT_READINESS.md、INTERACTION_DRAFT.md最新范围；按问题读本线交接，不重读全库。discovery-1已由公共方完成，本轮前端5项摘要初核一致，不再当缺失。所有测试注明历史/本轮、构造/真实，不把说明性JSON当运行成果。接口缺失如实列出，不临时编码填补，不要求用户重复批准已有原则。

回传统一按四项组织：①字段映射与只读能力；②当前版本/文件身份；③可消费关联样例；④返回用户监控的范围身份。结尾逐项给“已明确/存在缺口/需要用户决定或提供信息”，区分开发方案前阻碍与后续联合验证。已有材料完整时引用精确路径/章节即可，避免重造整套契约。

一、字段映射：逐条L1–L5列出业务标题/描述/建议/例子/证据/已量化收益对应的GET路由、kind、JSON字段路径、关联键、可空条件及资格。区分原字段、可由前端固定业务文案解释、后端未提供，尤其title/description和影响请求数不能假装都有。明确finding→experiment/optimization/evaluation→plan→comparison及父task追溯。完整full/direct_full严格>1pp、恰1pp、pilot未full、L4/L5独立事实；收益范围/精确分数/n/j/p/h/c语义。无前端评估操作时哪些收益在初始分析自动存在，哪些需既存显式评估，不承诺都有。
二、身份：给当前common/http/discovery、低命中、路由app装配、相关资源/锁与适用测试身份；HEAD与未提交文件摘要分开。新storage已不同于旧local-2，给当前清单或引用当前已有清单；旧manifest不改。不要代签Token私有身份（Token会话另回传）。
三、样例：定位或另存文档JSON（不发起任务）覆盖ready全链路>1pp、恰1pp无优化卡、L4/L5完整双请求、partial/empty/legacy无默认、方向隔离、时间null、读取错误。至少有一套可沿真实关联字段从目录→report→finding/experiment/evaluation/plan→全文走通的构造响应；若只有测试生成器，标明缺静态响应与可复现入口。不要假造合法摘要或把示例scope当实际模型资产。
四、监控映射：确认binding.appid/model_id/common_name/source_kind、scope.source的run/快照/配置身份如何映射base与user_v2监控读取范围；缺common_name/历史源不可用的能力限制。可以核对已有监控接口，不接管监控代码。区分“原报告源监控”和“同服务当前监控”，不强行证明可比较；具体前端hash路由由前端负责。公共字段确认你负责，Token不重复设计。
回传到docs/tasks/prefix-analysis/FRONTEND_READONLY_RECEIPT.md，可另存同目录只读样例及当前identity JSON。不要改前端文档或Token文件。最后说明用户还需批准什么/提供什么，若无请明确“无需新增业务输入，剩余为工程计划/后续联调”。
