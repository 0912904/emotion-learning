# 情绪研究学习室

静态交互网站；无需安装依赖。内容来自工作区的完整学习路线。

运行 `python build_content.py` 更新 `dist/content.js` 和 Markdown 下载副本。
本地预览：`python -m http.server 8765 --directory dist --bind 127.0.0.1`。
也可直接打开 `dist/index.html`，全部内容通过本地脚本载入，无 CDN 依赖。

功能：28 周学习路线、26 篇论文搜索与筛选、详情与原文链接、周／论文进度、笔记、JSON 导入导出、多标签阈值实验、持续学习指标实验、8 题自测、完整手册。

进度保存在浏览器 localStorage；不同来源与浏览器不自动同步。导入会询问是否覆盖已有状态。部署身份见 `.openai/hosting.json`。
