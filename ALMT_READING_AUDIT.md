# ALMT paper-analyzer 验收记录

日期：2026-10-23；用户选择：ALMT 完整示范、academic 风格。

1. 全文：ACL 正式 PDF 共12页；获取并读取正文、参考文献和附录。核对 Table 1–4 原页图像；原文 Fig.2/3/5 从已检查的原页裁取。
2. 代码：浅克隆作者 Haoyu-ha/ALMT，固定提交 da9461071f21e75eb8bf2bedff14ac23f5954605；阅读 README、models/almt.py、models/almt_layer.py、configs/sims.yaml、train.py。
3. 分析：区分论文公式、当前源码与本地实验；特别核对 token 切片、Q/K/V方向、AHL/普通注意力每头维度、PreNorm位置、指标选模与参数量口径。
4. 风格：用户已选择学术型，保留初学者符号解释与手算。
5. HTML：dist/deep/almt.html；本地 KaTeX、Mermaid、20个WOFF2字体，原图及许可证。网站 P06 阅读卡和对话框均有入口。
6. 自审：6918个中文字符、60个p段落、8组公式、3幅原文图、5张表、4段源码、3处短引。作者与独立局限分别标注。数字例子标教学构造，本地表由JSON读取生成，未重新训练。

浏览器检查：8组公式均产生KaTeX节点、无katex-error、Mermaid生成SVG；注意力滑块改变输出且结果符合softmax；方法章节和原图排版已目视检查。只声明完成本篇示范，未将其他25篇标为已按本技能重做。

来源与许可：论文为ACL CC BY 4.0，代码MIT；图表注明出处并说明裁取／重排，开源库保留许可证。
