# TA001 内容提取与度量

2026-10-31：closed。依赖已签收的 analysis-common-1.0（摘要验收见 TA000）。

新增本线 json_values、measurements、extraction。逐请求读取完整正文；拒绝重复键、非 JSON 常量和孤立代理字符，保留大整数/指数原词法；支持普通/旧协议工具定义、工具结果容器、多文本块、arguments 一层内嵌 JSON。原位置、内嵌根与字段位置独立，T2/T4复用同一单元；父子包含关系不累计为总负担。工具名称与定义摘要绑定，重复调用ID/同名多定义不猜身份。模板参与只消费对应位置和编码身份的证据，不向内嵌字段继承精确跨度。

验证：WSL .venv `pytest tests/unit/token_content -q`：38 passed（TA000 27项，新增解析/提取11项）；`ruff check src/tokenscope/token_content tests/unit/token_content`、`mypy src/tokenscope/token_content`通过。覆盖P01–P06、C01–C04的本线解析/身份部分：多层定义、Unicode、多块、内层错误、大数值、身份歧义、70KB正文、双层定位、稳定身份及同hash不同记录不合并。公共报告发布冲突/覆盖由后续真实存储联调验证，不声称已通过。

源不完整/正文超预算拒绝继续；单元预算及取消透传公共停止信号，由插件负责报告partial/unknown，不将部分枚举写成完整。内嵌格式错误保留外层内容事实及局部错误。没有独立Tokenizer、无公共源码修改、无真实现场数据验证。

修复：严格类型检查发现局部变量跨循环复用类型冲突，已改为独立定义身份和调用名变量；复跑通过。可通过不注册本线插件回退，原数据不受影响。下一批TA002。
