from pathlib import Path
p=Path(__file__).parent/'dist/app.js'
s=p.read_text(encoding='utf-8')
start=s.index('function openWeek(')
end=s.index('function lab()',start)
s=s[:start]+'''function lessonBlocks(parts){return `<div class="lesson-stack">${parts.map((part,i)=>`<details class="lesson-part" ${i===0?'open':''}><summary><span class="lesson-number">${String(i+1).padStart(2,'0')}</span>${esc(part.title)}</summary><div class="prose lesson-text">${part.html}</div></details>`).join('')}</div>`;}
function readerTools(download){return `<div class="actions reader-tools"><button class="btn small" data-lessons="expand">展开全部章节</button><button class="btn small" data-lessons="collapse">收起全部章节</button><a class="btn small" href="${download}" download>下载详细讲义 ↓</a></div>`;}
function openWeek(n){let w=weeks[n-1];if(!w)return;let parts=COURSE.weekLessons['W'+String(n).padStart(2,'0')];openDialog(`WEEK ${String(n).padStart(2,'0')} · ${names[w.group]}`,`<div class="prose"><h2>${w.title}</h2><p class="muted">${w.sub}</p></div><div class="info">先做本周最小任务 → 保存产物 → 对照验收。前置条件缺失就先处理缺口。</div>${readerTools('week-playbook.md')}${lessonBlocks(parts)}<div class="prose"><h4>本周论文入口</h4><div class="actions">${w.papers.length?w.papers.map(id=>`<button class="btn small" data-paper="${id}">${id} · ${esc(COURSE.papers.find(p=>p.id===id).title.split(':')[0])}</button>`).join(''):'<p>围绕已选分支的关键论文与实验记录。</p>'}</div><div class="actions"><a class="btn small" href="learning_starter.py" download>下载入门练习脚本 ↓</a><label class="check"><input type="checkbox" data-week-check="${n}" ${state.weeks.includes(n)?'checked':''}>产物已完成且通过验收</label></div></div>${noteArea('week-'+n)}`);}
function openPaper(id){let p=COURSE.papers.find(p=>p.id===id);if(!p)return;if($('#reader').open)$('#reader').close();openDialog(`${p.id} · ${names[p.group]}`,`<div class="prose"><h2>${esc(p.title)}</h2></div><div class="info">精读顺序：概念 → 数据流 → 计算 → 实现 → 自测。数字例子为教学构造；示意公式与完整原方法的区别在文中说明。</div>${readerTools('paper-lessons.md')}${lessonBlocks(p.lessons)}<details class="lesson-part source-overview"><summary>原论文速览、出处与链接</summary><div class="prose lesson-text">${p.html}</div></details><label class="check"><input type="checkbox" data-paper-check="${p.id}" ${state.papers.includes(p.id)?'checked':''}>已读并完成自己的阅读笔记</label>${noteArea(p.id)}`);}
''' + s[end:]
s=s.replace('${p.summary} ${p.meta}', '${p.summary} ${p.meta} ${p.searchText||\'\'}')
s=s.replace('点击阅读卡查看问题、方法、练习与原文链接','点击精读卡，逐节理解概念、计算和实现').replace('打开阅读卡 ↗','开始逐节精读 ↗')
s=s.replace('26 篇原始论文，按用途和深度组织。每张卡从问题出发，连接技术方法、通俗解释和一个可以动手的练习。','26 篇论文均已补充概念解析、方法链路、计算示例与自测。ALMT、ECPA、CERA 和持续学习主线重点展开；可搜索正文中的术语。')
s=s.replace('按每周 10—12 小时规划。完成验收再勾选，进度可以按实际能力调整；只攻一条分支时可直接跳过另一条。','先完成共同基础，再只选一条分支。每周都有操作顺序、文件入口、必交产物和停止条件；周数是任务编号，可以按掌握情况放慢。')
s=s.replace('这里记录的是你手动确认的学习进度，不代表程序已运行实验。','已有 ALMT 实验不必重跑：先做 W01 数据核查、W07 形状追踪，再进入 W08 消融。学习勾选不代表实验已经执行。').replace('任务与验收 ↗','打开分步任务单 ↗')
s=s.replace('if(el.dataset.week)openWeek', "if(el.dataset.lessons){document.querySelectorAll('#reader .lesson-stack details').forEach(d=>d.open=el.dataset.lessons==='expand');}if(el.dataset.week)openWeek")
s=s.replace('<a class="btn" href="learning-roadmap.md" download>下载完整学习路线</a>', '<a class="btn" href="learning-roadmap.md" download>下载原学习路线</a><a class="btn" href="week-playbook.md" download>下载逐周行动手册</a><a class="btn" href="paper-lessons.md" download>下载论文精读讲义</a><a class="btn" href="learning_starter.py" download>下载入门练习脚本</a>')
p.write_text(s,encoding='utf-8')
