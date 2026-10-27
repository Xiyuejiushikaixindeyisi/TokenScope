# B001 问题记录

更新：2026-10-27。无阻断门槛的未决问题。

| ID | 发现/影响 | 修复与验证 | 状态 |
| --- | --- | --- | --- |
| B001-01 | 首轮 ruff 33 项导入/行长问题；pytest 65 项通过、mypy 通过 | 排序/格式化并拆分长字符串，最终 ruff 与 format 通过；首次日志保留 | closed |
| B001-02 | 自查发现输入 contextmanager 会误标记调用方 OSError；固定 partial 名可能误删旧文件 | 打开错误与调用方错误隔离；唯一临时文件、exclusive link、fsync；路径/异常/重复目标测试通过 | closed |
| B001-03 | 自查：1e999 JSON 转为非有限浮点，重复使用 staging store 可混淆质量状态；配置更新响应再次读取有 revision 竞争 | 全树校验非有限数，staging 单次启动事务，响应使用本次更新值；补回归后 66 项通过 | closed |
| B001-04 | TestClient 上游提示 httpx 适配将弃用（1 条 warning） | 当前锁版本实际测试及独立 HTTP 进程均通过；保留警告，未来依赖升级时迁移；不影响生产 uvicorn | non_blocking |

未运行真正编码或缓存仿真。缺词表不是本批实现失败，归 B002；完整分析提交返回 PIPELINE_NOT_READY，不写虚假 completed 记录。
