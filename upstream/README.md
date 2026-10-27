# 固定来源源码

此目录保存真正需要阅读或复用的固定仓库和源码快照。Session 1 于 2026-10-23 取得首轮参考，10-26 补充 Ascend page/PR、Recipe 与 tokenizers 的必要片段，来源和逐文件身份见 [sources.lock.json](../env/sources.lock.json)，当前有效入口见 [监控 CODEMAP](../docs/tasks/monitoring/CODEMAP.md)。0.23.0、后续主干和未合并 PR 分开存放；这些是研究材料，尚非 TokenScope 运行依赖。华为完整 PrefixLens 仍未取得。其他候选见 [参考清单](../docs/research/implementations/CATALOG.md)。

引入时记录来源 URL 或本地原件、完整 commit 或文件摘要、获取时间、许可证、路径、用途和核验状态，更新 [sources.lock.json](../env/sources.lock.json)。

- PrefixLens 本机基础版与华为完整版本分开存放，不混为同一基线。
- 目录名保持稳定，通过锁文件表达具体身份；不能只记录 main、latest 或浮动 tag。
- 自有适配代码放 src，必要上游补丁放 patches，并记录应用基准。
- 外部源码不默认进入根项目 Git，也不默认全部进入交付包。离线备份与实际交付需要显式列出包含范围。
- 不依赖指向兄弟项目的软链接或共享可变工作树。

