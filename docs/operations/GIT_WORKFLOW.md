# Git与本地交付版本约定

2026-10-27用户决定：个人项目，不用PR；main保存通过检查的完整源码/文档。origin为git@github.com:Xiyuejiushikaixindeyisi/TokenScope.git，仅显式push main或已决定共享的功能分支，不使用push --all / --mirror。

## 分支

- main：可运行源码、配置、测试、计划和非秘密说明。
- backup/20261027-init：本次初始化完成后的本地源码检查点，不推送。用户示例backup/20261022-init不是现存分支，不伪造历史。
- 未来analysis/ideal-hit-rate：理想命中率原因分析；analysis/token-anomaly：Token异常分析。尚未创建或开发，共用监控S0和统一计量。

源代码功能分支按个人快速方式合并，无PR：

```sh
git switch main
git merge analysis/ideal-hit-rate
git push origin main
```

若backup分支只有源码且确实需要恢复，也可按用户示例switch main→merge backup/<实际名称>→push main。**包含交付包/镜像的backup分支禁止合并到main**：即使随后删包，大文件仍进入提交历史。需要源码修复时只摘取不包含产物的提交。

## 本地交付与多轮现场验证

每轮经用户授权后，产物放artifacts/releases/<版本>/；manifest记录源码Git commit、前后端版本、依赖/编码资产SHA、代码包/镜像摘要、现场prompt和验收记录。包体忽略并留本机。

优先在本地backup/<日期>-<轮次>提交小型manifest指向本地包体，不复制巨型镜像进Git对象库。确有需要可在独立本地备份分支/工作树显式git add -f指定产物，再本地commit；该分支不设upstream、不push、不merge main。切换带产物的分支会影响工作文件，先确认本地文件位置。Git本地分支不是异机灾备，另做磁盘备份。

仓库提供.githooks/pre-push：阻止backup分支推送，并扫描待推历史的产物路径/归档扩展/大blob，防止误合并后上传。新clone需执行`git config core.hooksPath .githooks`（需要python3）。本地已启用；钩子是防误操作，不替代审阅，不携带认证信息。

.gitignore保留docs、configs普通文件、tests、src、scripts、README和计划markdown；仅忽略环境/缓存/实际数据/模型资产/产物和私有覆盖配置。原始数据不删除，必要证据清单继续维护。
