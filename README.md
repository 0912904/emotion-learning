# 情绪研究学习室

静态交互网站；无需安装依赖。内容来自工作区的完整学习路线。

运行 `python build_content.py` 更新 `dist/content.js` 和 Markdown 下载副本。
本地预览：`python -m http.server 8767 --directory dist --bind 127.0.0.1`。
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

# 2026-10-24 完整论文精读

- `dist/deep/index.html`：26 篇完整精读目录，支持方向筛选和搜索。每篇包含概念、方法、公式、原文图表定位、实验解释、局限和具体验收任务。
- `deep-content/`：本次新增 23 篇的可重建内容快照。旧 ALMT、NORM-TR、EST 使用既有生成器和内容文件。
- `python build_remaining_deep.py`：重新生成新增精读页面、目录和主站入口；不会执行模型训练。优先读取工作区研究稿，缺少外部研究目录时使用已保存快照。
- `python collect_code_licenses.py`：从仍可用的研究仓库收集许可。已经保存的许可位于 `dist/deep/assets/licenses/`，不依赖在线 CDN。
- 检查顺序：`python check_deep_content.py`、`node check_math.cjs`、`node --check dist/app.js`、`node --check dist/deep/collection.js`。本轮浏览器检查记录在 `browser-reading-audit.json`。
- 精读页的笔记和已读状态使用原浏览器存储键，可在主站「我的学习笔记」导出。不同来源、浏览器或设备不自动同步。
- 论文数值、源码核验与教学验证分别标注。代码不可获取、仅有评估实现、原稿数值冲突等情况均在对应文章中保留，不表示已重训原论文模型。

# 2026-10-24 前端优化

- 依据用户提供的 `D:/Dolphin/claude/frontend-improvement-plan.md`，对应现有结构实施；验收和范围见 `FRONTEND_IMPROVEMENT_AUDIT.md`。
- 主站入口、基础样式为 `dist/index.html`、`dist/style.css`；增强样式和交互为 `dist/ui.css`、`dist/ui.js`，应用路由和任务内容在 `dist/app.js`。无新增外部依赖。
- 浏览器存储键仍为 `emotion-learning-v1`，保留原阶段、论文、笔记和成绩，兼容原 version-1 JSON 备份；新增在读状态、清单、续学位置、导出时间。不同标签页同步，同设备不同浏览器或跨设备仍不自动同步。
- `reading-collection.js` 是精读页公共交互源码；`build_remaining_deep.py` 将它复制到 `dist/deep/collection.js`，避免重建时覆盖本轮进度同步与防抖保存。
- 内容重建仍使用既有生成器。不要日常运行历史迁移脚本 `upgrade_ui.py`，它会覆盖现有前端函数。修改静态脚本后同步更新入口资源的查询版本，避免浏览器使用旧缓存。
- 核验：`node check_ui_state.cjs`、`node --check dist/app.js`、`node --check dist/ui.js`、`python -X utf8 check_deep_content.py`、`node check_math.cjs`。

# 2026-10-27 动态与逻辑表达优化

- 新增 `dist/motion.css`、`dist/motion.js`（加载顺序：ui → motion → app）。纯展示层，不读写学习状态；只有 JS 运行且未开启“减少动态”时才给 `<html>` 加 `motion` 类，所有动画都挂在该类下。
- 动态：首屏漂移光斑与标题分行入场、融合示意的证据流动与判断脉冲、页面切换时的逐项浮现与数字滚动、进度条/环增长、卡片悬停与光标光斑、顶栏阅读进度、抽屉滑入、完成勾选时的小型庆祝粒子。就地更新（勾选、多标签页同步、导入）不重播入场动画；筛选只动变化的列表。
- 逻辑表达：`app.js` 新增 `phases` 与 `routeStatus()`，统一“共同基础 → A/B 二选一 → 研究闭环”。首页里程碑按各阶段真实验收进度填充连线并标出当前位置，已选另一分支时标记可跳过；续学位置和路线页“下一步”遵循当前分支。路线页按阶段分组，含阶段目标、分岔/汇合提示与可点击的关联论文。实验台显示“首次学完 vs 学完 C 后”对比条与代入数值的 AA/BWT/F 算式。自测用逐题对错点表示进度。
- 存储键、状态结构、论文/阶段 ID 未变；`build_remaining_deep.py` 依赖的 `deepPapers` 与“找到 … 篇”锚点保持不变。验收见 `FRONTEND_IMPROVEMENT_AUDIT.md` 末节。离线 zip 未重新打包。

# 2026-10-28 路线修订（分批上线：第一批）

- 路线原稿新增第 12 节“路线评估与 2026-10 修订”：评估结论、P27—P36 的放置周次、8 GB 显存可行性、统计严谨性清单、两个方向的待验证选题、已核对的延伸阅读。第 4、5 节周表、第 7.2 节指标（开放集、校准）、第 8 节项目 B 对照（提示式无回放基线）和第 10.5 节完成判据同步更新。
- `week-playbook.md`：W22 改为“无回放提示基线”（GPM 降为选读），W10/11/13/15/16/17/18/19/20/23/24 各加“2026-10 新增：阅读与任务”。周数与已有进度不变。
- `dist/app.js`：自测 8→12 题；篇数与题数从数据读取；存储校验接受 P01—P36（`check_ui_state.cjs` 同步）；周任务只显示已上线的论文，P27—P36 上线后自动出现；新论文卡片带“2026-10 新增”标记。`build_content.py` 已登记 P27—P36 的方向与深度。
- 第二批（待完成）：P27—P36 的阅读卡、讲义与完整精读；到时把 10 条记录加入 `build_remaining_deep.py` 的 CATALOG，并把首页静态文字改为 36 篇。

