# S0 问题与闭环

| ID | 发现/影响 | 修正及证据 | 状态 |
| --- | --- | --- | --- |
| S0-01 | 生成器SSE content字典少一个闭合大括号，首轮SyntaxError，无输出生成 | 修正语法；生成器最终exit0、67定义/75JSON样例/18操作 | closed |
| S0-02 | WSL系统jsonschema版本不提供Draft202012Validator；最初探测ImportError | 使用项目专用UV_CACHE_DIR中的jsonschema4.23.0独立工具环境；未改运行.venv/uv.lock；报告记录所有工具依赖版本 | closed |
| S0-03 | 现有规则允许非比率浮点阈值，简单integer/ratio二分会改变旧语义 | 增加value_kind=number兼容90.5；observed_value仍依指标编码；integer和ratio反例校验通过 | closed |
| S0-04 | 原轻证据单offset有两个数组，前端无法确定分页语义；多列排名需独立身份 | 固定section独立分页、position为筛选后全局位置；Schema/字典/样例/行为文档同步 | closed |
| S0-05 | 生成工具ruff初查E501/E731；增加报告时间后出现I001/UP017 | 拆字符串、lambda改def、排序导入并用UTC别名；最终ruff check/format通过 | closed |
| S0-06 | 十进制regex的$可能接受末尾换行；终态时间/错误及模型模式需分支约束 | 严格结尾、Receipt条件、Settings条件；反例拒绝通过 | closed |

S0无剩余契约交付阻断；实际前端接收确认、R1竞态、R2浏览器流式写入/≥256MiB资源、S1–S5服务实现均未验证，归父批后续门槛，不包装为本步骤已通过。
