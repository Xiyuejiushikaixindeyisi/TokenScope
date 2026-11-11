# AR-L4 实际接入发现的局部证据缺口

接收ARPC006后前端已开始获批返工；下列是已批准UI-04需求的接入修复，不增加探测范围，不由前端补后端。请在现有Schema内修复并验证；若必须改接口，先说明差异。

实际AR-L3样例：task efb6cd64-c3f7-4d42-9bbe-ef38b1dc0da3，scope:08e98b28e62399fd961c449d5e567804f345092aac72c840324135dd4513e9cc；L1 rec:7f705f2612010811a2d609b207b851b277d6caefe9b9943e342db913ef222d8d 的 examples，before/after都是messages/0/content从头截取1024码点的stable重复文本，source.text_range=null，comparison=null。实际变更只有时间戳。

1. L1优先按实际已定位动态范围给出紧凑before/after及邻近上下文，不能把整个消息的前1024字符当作重点。若有可靠对应Finding A/B，用comparison提供问题原文对照；不混同A/B与修改前后。前端不搜索第一次出现的字符串伪造定位。
2. L4同类大消息差异也应聚焦差异附近，<=3例及全体成员计数保持。L5既有change_summary仍写“查看两条完整请求”，改为相关工具返回片段；保持JSON空格/大整数词法，原始文本模式明确，不要求前端重序列化全文。
3. Token advice_only缺basis的当前例子为空（例如完整ready ae3c5d14-467d-4d9d-b0cb-7eadd76b17b5 的 recipe_id=advice）。仍应从已核实support_refs保留原问题局部证据，不造after/N/量化。若当前代码已有能力请给可读取实例；否则由公共证据归口修复，Token私有定位需要其提供时请协调。

回传新增实际GET证据、源码/Schema/样例摘要变化、针对性验证；不必改变既有测试原始证据。给出新持久状态目录或明确更新后的读取对象；旧冻结样例保留。前端继续接口/布局开发，但不把上述缺口包装为完成，不修改后端源码、不打包部署。
