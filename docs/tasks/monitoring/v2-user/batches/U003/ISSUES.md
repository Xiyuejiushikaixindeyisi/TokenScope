# U003问题闭环

- 精确比较使用SQLite自定义Fraction collation，避免double与>2^53误排序；NULL显式最后。closed。
- FastAPI查询模型中Literal整数需接受HTTP字符串，添加仅1000/2000/5000的显式转换，其余拒绝。closed。
- 查询参数容器类型推断与格式检查问题已修复；mypy全源49文件通过。
- 新路由使用INSTANCE_MISMATCH，旧S0 guard及错误格式不变。主app/CLI只注册新路由与处理器，原MA/V1保留。
