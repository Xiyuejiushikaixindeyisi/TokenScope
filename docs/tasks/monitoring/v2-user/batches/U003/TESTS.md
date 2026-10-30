# U003实测

pytest test_user_ranking.py及旧test_interfaces.py：28 passed，2.67s，一条第三方Starlette弃用提示。XML artifacts/validation/user-monitoring/U003/tests.xml。

四指标双向排序/分页与独立Fraction穷举oracle一致；组合界限、NULL、UTF8同值、中文/%/_、大小写、>2^53、mode逐页、非法参数/身份/revision均验证。真实ASGI HTTP响应严格DTO通过；GET前后全部文件mtime不变。

10000组limit100，20次新连接查询含摘要校验，最慢0.2163s≤2s。见resources/query.json；这是应用连接冷/重复访问，未清空操作系统页缓存。索引及RSS预算复测通过。mypy49文件、ruff通过。真实socket/CLI统一测试在U005。
