# NORM-TR 与 EST 完整精读核查（2026-10-23）

沿用用户选择的 paper-analyzer 学术型风格；本批完成 P09 NORM-TR 与 P16 EST。

- NORM-TR：作者公开期刊 PDF 共21页，全文与参考文献已读，出版商元数据核实；arXiv 摘要及HTML用于版本核查。正文 Eq.1—10，Table1/2/5/6/8/13及Figure1/2/3/4/5/11均在讲义中讨论。
- 未定位到可确认的 NORM-TR 官方源码；不声称不存在代码。已查标题、作者主页、GitHub及NRGF关键词。浅克隆同作者LNLN为相关参考，固定SHA 80a052c62b7b3b7a6cb6956846e9d9c121f56eda；读取README、核心模型、数据处理和配置。引用的两段代码仅为通用GRL，明确不冒充NORM-TR实现。
- EST：作者19页PDF全文已读，官方README、核心模型、Transformer、数据采样、主循环与配置已读；固定SHA f85a0cdcf974630648d2a60188d086ad85a0347a。图表编号依据作者稿。
- 区分论文原式、教学展开、原文实验、建议实验；未进行完整模型训练。
- EST明确报告余弦截断、局部旁路detach、set采样顺序、位置编码重排、测试列表选模等源码细节。SSOP为固定排列的整体分类；网页小型交互也按整体排列分类演示。
- NORM-TR保留D2标签描述、Table10数据集名、MOSEI样本数等待核实项；不自行补写确定实现。
- 原始图以编号、讲解和全文链接引导阅读；流程图为讲义重绘。只节选必要数据表，不再分发原PDF。

## 验证证据

- 结构统计见 more-papers-audit.json：NORM-TR约5600中文字符、11组公式、5张表；EST约7100中文字符、10组公式、4张表。
- 本机浏览器：NORM-TR 11组、EST 10组公式渲染，KaTeX错误0，每页Mermaid SVG 1个。
- GRL滑杆到λ=1显示提取器端梯度−4；EST选择排列3,2,1显示教学类别2。
- node --check dist/app.js、dist/deep/papers.js、dist/deep/almt.js通过。
- 两页所有本地链接与资源存在。阅读室显示三条完整精读入口，搜索NORM-TR可到正确页面。
- norm_learning_checks.py 已在现有ALMT环境执行：两类连续窗遮罩、未遮蔽值保持、GRL系数0/.5/1及判别器梯度、教学AUILC=.55均通过。
- est_sampling_probe.py 已验证全部30个合法起点、不同种子、固定测试采样、WAR/UAR算例；只验证教学机制。
- 离线zip完整性检查通过。

## 重建

发布资源已包含在 dist/。可运行 `python -X utf8 build_more_deep.py` 从 norm-content.json、est-content.json 重新生成两篇；沿用 dist/deep/almt.html 中的现有样式和本地渲染库。外部研究目录存在时可刷新许可证和练习文件，否则保留已跟踪资源。build_norm_deep.py 是NORM内容的写作源脚本，重新执行该脚本需要研究目录中的相关源码克隆；通常编辑JSON后重建即可。
