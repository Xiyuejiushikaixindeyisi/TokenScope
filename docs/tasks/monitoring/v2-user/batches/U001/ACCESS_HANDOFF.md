# 内网参数交接（未部署）
服务继续统一端口18000。审查打包会话后续配置应将现有宿主发布地址参数化，例如 ${TOKENSCOPE_BIND_HOST:-127.0.0.1}:${TOKENSCOPE_PORT:-18000}:8000；内网部署经授权设置TOKENSCOPE_BIND_HOST为指定内网IP或0.0.0.0。不能使用0.0.0.1。
容器healthz仍访问127.0.0.1:8000，不对外部绑定地址发健康检查。浏览器使用服务器IP/域名，不使用0.0.0.0或客户端localhost。
当前deploy/monitoring/compose.yaml和env/docker/compose.monitoring.yaml未修改；本批源码修复不改变V1现网。后续网络验收检查指定网卡、实际端口占用、允许访问网段、静态资源/API/SSE/下载。访问成功及安全范围必须现场验证，本地参数说明不当现场通过。
