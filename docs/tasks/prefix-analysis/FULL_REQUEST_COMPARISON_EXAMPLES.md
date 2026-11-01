# L4/L5完整请求JSON对比样例

2026-10-31，构造样例，非现场数据、非编码测试，不填未经回放的收益。每个代码块为一条完整请求，model使用示意标识；实际证据必须保留原请求所有字段和值。差异证据区域不受优化卡片>1pp门槛限制。

## L4：旧system消息被更新

前序请求A完整JSON：

```json
{
  "model": "example-model",
  "messages": [
    {"role": "system", "content": "你是项目助手。当前时间：2026-10-31 09:00:00。请使用中文回答。"},
    {"role": "user", "content": "请列出今天需要核对的事项。"}
  ],
  "tools": [],
  "temperature": 0
}
```

后序请求B完整JSON：

```json
{
  "model": "example-model",
  "messages": [
    {"role": "system", "content": "你是项目助手。当前时间：2026-10-31 09:01:30。请使用中文回答。"},
    {"role": "user", "content": "请列出今天需要核对的事项。"},
    {"role": "assistant", "content": "请核对需求、测试结果和交付清单。"},
    {"role": "user", "content": "先展开测试结果的核对步骤。"}
  ],
  "tools": [],
  "temperature": 0
}
```

差异：/messages/0/content的时间变化；/messages/2和/3是正常追加，不判问题。没有外部可靠关联时，仅能说“这两条可比请求的已有内容不同”；有可靠父子关联才能确认历史改写。建议固定旧前缀、把更新时间放到明确新增位置。此处不构造收益，也不假定恢复旧时间业务正确。

## L5：工具结果JSON字符串表示变化

请求A完整JSON：

```json
{
  "model": "example-model",
  "messages": [
    {"role": "system", "content": "依据工具结果回答问题。"},
    {"role": "user", "content": "项目alpha的构建状态是什么？"},
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [{"id": "call_build_1", "type": "function", "function": {"name": "get_build", "arguments": "{\"project\":\"alpha\"}"}}]
    },
    {"role": "tool", "tool_call_id": "call_build_1", "content": "{\"project\":\"alpha\",\"status\":\"passed\"}"}
  ],
  "tools": [
    {"type": "function", "function": {"name": "get_build", "description": "查询项目构建状态。", "parameters": {"type": "object", "properties": {"project": {"type": "string"}}, "required": ["project"]}}}
  ],
  "temperature": 0
}
```

请求B完整JSON：

```json
{
  "model": "example-model",
  "messages": [
    {"role": "system", "content": "依据工具结果回答问题。"},
    {"role": "user", "content": "项目alpha的构建状态是什么？"},
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [{"id": "call_build_1", "type": "function", "function": {"name": "get_build", "arguments": "{\"project\":\"alpha\"}"}}]
    },
    {"role": "tool", "tool_call_id": "call_build_1", "content": "{\n  \"status\": \"passed\",\n  \"project\": \"alpha\"\n}"}
  ],
  "tools": [
    {"type": "function", "function": {"name": "get_build", "description": "查询项目构建状态。", "parameters": {"type": "object", "properties": {"project": {"type": "string"}}, "required": ["project"]}}}
  ],
  "temperature": 0
}
```

差异仅在/messages/3/content字符串内部的JSON键序和空白；两份内层结构和值相同。此例意在隔离序列化因素，不主张两个请求属于同一会话。实际编码后若IDs变化才属于输入表示差异；若模板已经规范化导致IDs一致，不报缓存影响。建议该工具结果采用稳定JSON序列化；这里不提供预期提升。
