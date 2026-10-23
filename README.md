# 情绪研究学习室

静态交互网站；无需安装依赖。内容来自工作区的完整学习路线。

运行 `python build_content.py` 更新 `dist/content.js` 和 Markdown 下载副本。
本地预览：`python -m http.server 8765 --directory dist --bind 127.0.0.1`。
也可直接打开 `dist/index.html`，全部内容通过本地脚本载入，无 CDN 依赖。

功能：28 周学习路线、26 篇论文搜索与筛选、详情与原文链接、周／论文进度、笔记、JSON 导入导出、多标签阈值实验、持续学习指标实验、8 题自测、完整手册。

进度保存在浏览器 localStorage；不同来源与浏览器不自动同步。导入会询问是否覆盖已有状态。部署身份见 `.openai/hosting.json`。
# 2026-10-23 内容深化版

- `paper-lessons.md`：26 篇论文的概念、方法链路、教学计算与自测，原文出处在生成下载版中补齐。
- `week-playbook.md`：28 个阶段的分步任务、验收产物、前置条件与暂缓事项。
- `dist/learning_starter.py`：现有可信 CH-SIMS 文件检查，以及合成数据数学／训练重载／持续学习指标练习。
- 修改内容后运行 `python build_content.py`；静态入口为 `dist/index.html`。`upgrade_ui.py` 是本次升级迁移记录，无需日常运行。
- 本次验证：26/28 内容完整性断言、JS 语法检查、浏览器任务单与精读展开、入门脚本全部子命令。合成 MLP 训练 MSE 从 5.04949 降至 0.00008606，独立进程重载最大预测差为 0。这是教学验证，不是论文实验。
- 原浏览器存储键及论文／阶段 ID 保持一致；已有进度与笔记继续使用。

