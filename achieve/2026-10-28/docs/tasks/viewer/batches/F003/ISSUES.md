# F003 问题闭环

- 组件测试动态new URL被Vite识别为资源glob，误扫描项目外契约：测试改用Node path.resolve明确文件，未放宽应用文件访问规则。
- 浏览器请求页合法响应被拒：scope使用了snapshot identity额外publish_seq；assertScope改为只校验协议明确的五个范围字段，补跨DTO复用回归，保持实际实例/run/appid/model隔离，不修改后端Schema。
- 首轮失败保留pass2，修复后pass3通过；不以更改后端或删除断言绕过。

无阻断；正式真实服务联调属于后端统一阶段。本批人工合成业务夹具不作为计量真实性证据。
