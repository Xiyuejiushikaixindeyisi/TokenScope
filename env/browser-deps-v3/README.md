# V3本地浏览器依赖

用途：本地Playwright/Chromium验收，非产品运行依赖，不进入交付包。来源事故与安装方式见[开发I01记录](../../docs/tasks/development-v3/batches/V3B007/ISSUES.md)。使用apt-get download取得Ubuntu amd64 libnss3/libnspr4/libasound2，仅dpkg-deb解包到本目录root，不安装或替换系统库；准确下载镜像URL当时未记录，不补造。

[原始三包摘要](manifest.json)保持；[本轮资产清单](LOCAL_ASSETS.json)记录现存文件大小/SHA/符号链接。archives、root、fonts、font-cache、机器专用fonts.conf仅本地保留，由.gitignore排除，目录未搬移以免破坏已有测试路径。字体msyh.ttc来源/分发许可未核实，不能把本机可用等同允许再分发。

使用前检查已有依赖和SHA，按项目既有浏览器驱动设置局部LD_LIBRARY_PATH/FONTCONFIG_FILE；不要覆盖宿主环境，不因本说明自动联网下载或重新运行验收。重建环境需自行确认包源、版本和字体使用权限。此整理不构成安装/测试授权。
