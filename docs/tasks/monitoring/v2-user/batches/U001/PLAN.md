# U001 active
依U000 closed及已批准v1.0执行。修改csv_reader日期/显式UTC与错误字段、domain新安装别名和思考默认、storage设置CAS内别名冲突检查。旧配置不覆盖；测试显式保留旧default未决路径并增加新安装ready断言。运行U001定点及全部既有回归，mypy/ruff；恢复运行配置不在范围。迁移沿用既有GET/PUT设置CAS，只提交差异，不改旧default语义。内网参数交接审查打包，不启动Compose。
