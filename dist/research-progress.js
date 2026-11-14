'use strict';
// A dated, evidence-based project snapshot; independent of the visitor's own checklist.
function researchProgress(){return `<section class="research-progress" aria-labelledby="research-progress-title">
<div class="research-progress-head"><div><p class="research-progress-date">研究进度快照 · 截至 2026-11-14</p><h2 id="research-progress-title">当前：共同基础已有实验成果，正在进入细粒度方向</h2><p>阶段对应依据已有实验和记录整理；它不自动代表每周学习验收已完成。你的勾选和笔记仍由你自己管理。</p></div><a class="btn small" href="#roadmap">查看逐周路线 →</a></div>
<div class="research-progress-grid">
<article><span class="progress-label">已有实验 · W01–W08 相关</span><h3>ALMT 复现与模态对照</h3><p>CH-SIMS 完成完整模型、文本、文本＋视觉、文本＋音频的三种子对照；平均 MAE 分别为 0.4221、0.4186、0.4310、0.4307。结果不支持简单地说增加模态就一定更好。</p><p>MOSEI 完成单种子简化训练、测试与预测分析：测试 MAE 0.5365。它不是完整的论文复现。</p><a href="deep/almt.html">回顾 ALMT 精读 →</a></article>
<article><span class="progress-label">探索中 · W09–W11 部分相关</span><h3>CLIP 视频特征与情感倾向</h3><p>CH-SIMS v2.0 开发实验按视频划分训练 / 验证：256 / 128 段。验证 MAE：文本 0.5627、冻结 CLIP 帧特征 0.5952、文本＋CLIP 0.5445。</p><p>这是小规模开发集筛选，不是独立最终测试。文本与视觉标注正负相反仅 18 段，不能证明融合对冲突可靠；旧试验与这轮开发划分可能共享源视频。</p><a href="deep/clip.html">回顾 CLIP 精读 →</a></article>
<article><span class="progress-label">下一步 · 按顺序完成</span><h3>先核对标签，再建立可比基线</h3><ol><li>固定视频级训练、验证、独立测试划分，检查视频 ID 不重叠；增加视频覆盖。</li><li>对照文本、冻结 CLIP 帧特征与简单拼接；先记录整体 MAE 与各组样本数。</li><li>接入 MOSEI 原始六类情绪标签后，核对样本 ID、视频和划分；现有 ALMT 缓存已确认的是情感回归标签。</li><li>有可靠基线后再试轻量门控；人工模态标签不能作为实际推理输入。</li></ol></article>
<article><span class="progress-label">尚待完成</span><h3>细粒度标签、描述与跨场景</h3><p>MOSEI 六情绪标签与视频尚待对齐；CLIP 的 MOSEI 视频实验未完成。MAFW 数据、表情分类与描述生成尚待准备。跨场景持续学习实验尚未完成。</p><p>MOSEI 的校准和加权小实验未同时稳定改善整体与强情感误差；不要把探索性结果当作已验证的改进。</p><a href="#handbook/s4">查看细粒度路线 →</a></article>
</div><p class="research-progress-note">依据：引用的“制定论文复现计划”任务、CH-SIMS 三种子消融、MOSEI 单种子分析及 CLIP 开发实验摘要；不包含个人笔记或逐样本数据。</p></section>`;}
