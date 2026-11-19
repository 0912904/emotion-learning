"""Build the complete reading collection from audited article JSON sources."""
from pathlib import Path
import json,re,html,shutil,sys
ROOT=Path(__file__).parent
OUT=ROOT/'dist/deep'
RESEARCH=ROOT.parent.parent/'paper_analysis/remaining'
CATALOG=[('P01','attention','Transformer'),('P02','bert','BERT'),('P03','clip','CLIP'),('P04','wav2vec2','wav2vec 2.0'),('P05','mult','MulT'),('P06','almt','ALMT'),('P07','ch-sims','CH-SIMS'),('P08','mosei','CMU-MOSEI'),('P09','norm-tr','NORM-TR'),('P10','emer','EMER'),('P11','ovmer','OV-MER'),('P12','affectgpt','AffectGPT'),('P13','ecpa','ECPA'),('P14','cera','CERA'),('P15','lora','LoRA'),('P16','est','EST'),('P17','dann','DANN'),('P18','lwf','LwF'),('P19','ewc','EWC'),('P20','gpm','GPM'),('P21','emworld','EmWorld'),('P22','ferv39k','FERV39k'),('P23','pcl','PCL'),('P24','pcfrl','PCFRL'),('P25','resnet','ResNet'),('P26','simclr','SimCLR'),('P37','agent-mer','Agent-MER'),('P38','affectgpt-rl','AffectGPT-RL')]
SUPPLEMENTAL={'P37','P38'}
supplement_only='--supplement-only' in sys.argv
BASE=(OUT/'almt.html').read_text(encoding='utf8')
CSS=re.search(r'<style>(.*?)</style>',BASE,re.S).group(1)
CSS+='''.reading-note{padding:24px;background:#eff5ef;border:1px solid #ccd9ce;border-radius:12px;margin:30px 0}.reading-note textarea{width:100%;min-height:140px;font:inherit;padding:12px;border:1px solid #a5b9a9;border-radius:8px;resize:vertical}.reading-note label{display:block;margin:12px 0}.article-nav{display:flex;gap:18px;flex-wrap:wrap}.table-scroll{overflow:auto}table{min-width:440px}h2{scroll-margin-top:90px}a{overflow-wrap:anywhere}.collection-card{border:1px solid #c7d6c8;border-radius:12px;padding:20px;margin:16px 0}.collection-card h2{margin:0;font-size:22px}.collection-card p{margin:8px 0}.collection-tools{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0}.collection-tools input,.collection-tools select{padding:12px;font:inherit;max-width:100%}[hidden]{display:none!important}@media print{.reading-note,.collection-tools{display:none}}'''
HEAD='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · 情绪研究学习室</title><link rel="stylesheet" href="vendor/katex.min.css"><style>'+CSS+'</style><script defer src="vendor/katex.min.js"></script><script defer src="vendor/auto-render.min.js"></script><script defer src="vendor/mermaid.min.js"></script><script defer src="papers.js"></script><script defer src="collection.js?v=20261117-sync1"></script></head><body>'
FOOT='<footer>论文精读整理：2026-10-24 · 原文、源码核验与教学练习分别标注 · <a href="assets/licenses/index.html">代码节选来源与许可</a></footer></main></body></html>'
def top():return '<div class="topbar"><a href="../index.html#papers">← 阅读室</a><a href="index.html">全部精读</a><span id="render-status">正在排版公式与图表…</span><button id="print">打印 / 保存 PDF</button></div>'
course_js=(ROOT/'dist/content.js').read_text(encoding='utf8')
course=json.loads(course_js[course_js.index('=')+1:].strip().rstrip(';'))
original_groups={p['id']:p['group'] for p in course['papers']}
original_groups.update(dict.fromkeys(SUPPLEMENTAL,'fine'))
def group(pid):return original_groups[pid]
GROUPS={'common':'共同基础','fine':'细粒度方向','cross':'跨场景方向'}
stats={}; manifest=[]; pending=[]
if supplement_only:
 existing_manifest=json.loads((OUT/'collection-manifest.json').read_text(encoding='utf8'))
 manifest=[row for row in existing_manifest if row['id'] not in SUPPLEMENTAL]
(ROOT/'deep-content').mkdir(exist_ok=True)
for pid,slug,name in CATALOG:
 if supplement_only and pid not in SUPPLEMENTAL:continue
 source=ROOT/'deep-content'/f'{slug}.json'
 fresh=RESEARCH/f'{slug}-content.json'
 if fresh.exists():shutil.copyfile(fresh,source)
 if source.exists():
  data=json.loads(source.read_text(encoding='utf8'))
  body=data.get('body') or ''.join(f'<h2 id="{s["id"]}">{s["title"]}</h2>'+s['html'] for s in data['sections'])
  body=body.replace(r'\[','$$').replace(r'\]','$$')
  section_num=[0]
  def heading_id(match):
   section_num[0]+=1
   return '<h2 id="section-'+str(section_num[0])+'">'
  body=re.sub(r'<h2>',heading_id,body)
  body=body.replace('$$<span>','$$<span class="equation-label">')
  # Wrap tables without changing their numeric content.
  body=re.sub(r'(?<!<div class="table-scroll">)(<table\b.*?</table>)',r'<div class="table-scroll">\1</div>',body,flags=re.S)
  counts={'chinese_characters':len(re.findall('[\u4e00-\u9fff]',re.sub('<[^>]+>','',body))),'paragraphs':len(re.findall(r'<p\b',body)),'equations':body.count('$$')//2,'tables':len(re.findall(r'<table\b',body)),'mermaid':len(re.findall(r'class=["\']mermaid["\']',body))}
  if pid in SUPPLEMENTAL:
   assert counts['chinese_characters']>=1200 and counts['tables']>=1 and counts['mermaid']>=1,(slug,counts)
   lessons=[{'title':html.unescape(title),'html':section.strip()} for title,section in re.findall(r'<h2 id="[^"]+">(.*?)</h2>(.*?)(?=<h2 id=|\Z)',body,re.S)]
   # In the compact reader, omit the diagram and display math. They render in the full article.
   for lesson in lessons:
    lesson['html']=re.sub(r'<pre class="mermaid">.*?</pre>|<div class="equation">.*?</div>', '', lesson['html'],flags=re.S)
    lesson['html']=re.sub(r'(?<!\$)\$([^$\n]+)\$(?!\$)',r'<code>\1</code>',lesson['html'])
    lesson['html']=re.sub(r'href="((?:agent-mer|affectgpt-rl)\.html)"', r'href="deep/\1"', lesson['html'])
   course['papers']=[row for row in course['papers'] if row['id']!=pid]
   course['papers'].append({'id':pid,'group':'fine','core':True,'title':data['title'],'summary':data['summary'],'meta':re.sub('<[^>]*>','',data['metadata']),'html':'<p>'+data['metadata']+'</p>','lessons':lessons,'searchText':' '.join(re.sub('<[^>]*>',' ',part['html']) for part in lessons)})
  else:
   assert counts['chinese_characters']>=4000 and counts['paragraphs']>=20 and counts['equations']>=5 and counts['tables']>=2 and counts['mermaid']>=1,(slug,counts)
  toc=''.join(f'<a href="#{i}">{re.sub("<[^>]+>","",t)}</a>' for i,t in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>',body,re.S))
  idx=next(i for i,c in enumerate(CATALOG) if c[0]==pid)
  nearby=CATALOG[max(0,idx-1):idx]+CATALOG[idx+1:idx+2]
  navigation='<nav class="article-nav">'+''.join(f'<a href="{s}.html">{n} →</a>' for _,s,n in nearby)+'</nav>'
  note='<section class="reading-note" data-paper="'+pid+'"><h2>自己的解释与验收记录</h2><p>写出一条输入到输出的链路、一个关键公式的含义，以及你完成的最小检查。笔记仅保存在当前浏览器，可从主站「我的学习笔记」导出。</p><label><input type="checkbox" id="deep-read"> 已完成阅读与自己的笔记</label><label for="deep-note">阅读笔记</label><textarea id="deep-note" maxlength="20000" placeholder="问题、公式、源码位置、练习结果与尚未理解之处…"></textarea><output id="note-status" aria-live="polite"></output></section>'
  doc=HEAD.replace('{title}',html.escape(data['title']))+top()+'<main><header><div class="eyebrow">PAPER ANALYZER · '+pid+' · '+GROUPS[group(pid)]+'</div><h1>'+html.escape(data['title'])+'</h1><p class="lede">'+data.get('subtitle','')+'</p></header><div class="meta">'+data.get('metadata','')+'</div><div class="summary-box"><h3>一句话总结</h3><p>'+data['summary']+'</p></div><nav class="toc">'+toc+'</nav>'+body+note+navigation+FOOT
  (OUT/f'{slug}.html').write_text(doc,encoding='utf8')
  stats[slug]={'structure':counts,'evidence':data.get('audit',{})}
 elif not (OUT/f'{slug}.html').exists():pending.append(slug);continue
 manifest.append({'id':pid,'slug':slug,'name':name,'group':group(pid),'summary':data['summary'] if source.exists() else '已完成的完整学术精读：概念、公式、方法、源码、实验与练习。'})

assert not pending and len(manifest)==len(CATALOG),{'missing_papers':pending,'available':len(manifest)}

js=r'''document.addEventListener('DOMContentLoaded',()=>{
const area=document.querySelector('[data-paper]');
if(area){const key='emotion-learning-v1',id=area.dataset.paper,note=document.querySelector('#deep-note'),read=document.querySelector('#deep-read'),out=document.querySelector('#note-status');
const get=()=>{try{const v=JSON.parse(localStorage.getItem(key)||'null');if(!v||typeof v!=='object')throw Error('invalid state');return {...v,weeks:Array.isArray(v.weeks)?v.weeks:[],papers:Array.isArray(v.papers)?v.papers.filter(x=>typeof x==='string'):[],notes:v.notes&&typeof v.notes==='object'&&!Array.isArray(v.notes)?v.notes:{},quizBest:Number(v.quizBest)||0};}catch(e){return {weeks:[],papers:[],notes:{},quizBest:0};}};
let state=get();note.value=state.notes?.[id]||'';read.checked=(state.papers||[]).includes(id);
const save=()=>{try{let s=get();s.notes=s.notes||{};s.notes[id]=note.value.slice(0,20000);s.papers=(s.papers||[]).filter(x=>x!==id);if(read.checked)s.papers.push(id);localStorage.setItem(key,JSON.stringify(s));out.textContent='已保存在当前浏览器';}catch(e){out.textContent='保存失败，请复制笔记备份';}};note.addEventListener('input',save);read.addEventListener('change',save);}
const search=document.querySelector('#collection-search'),filter=document.querySelector('#collection-filter');if(search){const update=()=>{let n=0;document.querySelectorAll('.collection-card').forEach(c=>{const ok=c.textContent.toLowerCase().includes(search.value.toLowerCase())&&(filter.value==='all'||c.dataset.group===filter.value);c.hidden=!ok;if(ok)n++;});document.querySelector('#collection-count').textContent=`显示 ${n} 篇`};search.addEventListener('input',update);filter.addEventListener('change',update);update();}
});'''
if (ROOT/'reading-collection.js').exists():
 js=(ROOT/'reading-collection.js').read_text(encoding='utf8')
if not supplement_only:(OUT/'collection.js').write_text(js,encoding='utf8')
cards=''.join('<article class="collection-card" data-group="'+m['group']+'"><div class="eyebrow">'+m['id']+' · '+GROUPS[m['group']]+'</div><h2><a href="'+m['slug']+'.html">'+m['name']+'</a></h2><p>'+m['summary']+'</p><a href="'+m['slug']+'.html">打开完整精读 →</a></article>' for m in manifest)
start='<section class="summary-box"><h3>按当前问题选择入口</h3><p><strong>看不懂 ALMT 的张量和注意力：</strong>从 <a href="attention.html">Transformer</a>、<a href="bert.html">BERT</a>、<a href="mult.html">MulT</a> 开始。先完成一个 3×5 交叉注意力的形状与归一化检查，再读 ALMT。</p><p><strong>准备做细粒度：</strong>用 <a href="mosei.html">MOSEI</a> 理清多标签与强度；用 <a href="est.html">EST</a> 理解时间片段；再用 <a href="ecpa.html">ECPA</a>、<a href="cera.html">CERA</a> 和 <a href="ovmer.html">OV-MER</a> 比较描述、证据与开放词汇评价。先交付标签字典和五条可核查案例。</p><p><strong>准备做跨场景：</strong>可访问目标域无标签数据时读 <a href="dann.html">DANN</a>；场景按顺序到来时读 <a href="lwf.html">LwF</a>、<a href="ewc.html">EWC</a>、<a href="gpm.html">GPM</a>，再读 <a href="emworld.html">EmWorld</a>。先写清旧数据、目标数据和标签的访问范围，再选择方法。</p></section>'
index=HEAD.replace('{title}','完整论文精读目录')+top()+'<main><header><div class="eyebrow">PAPER ANALYZER · 阅读、计算、核验</div><h1>把论文读到能解释、能检查。</h1><p class="lede">'+str(len(manifest))+' 篇完整精读。先看输入、标签与输出，再沿公式和源码理解机制；每篇附可验收的小任务。</p></header>'+start+'<div class="collection-tools"><input id="collection-search" aria-label="搜索精读" placeholder="搜索论文与方法…"><select id="collection-filter" aria-label="筛选方向"><option value="all">全部方向</option><option value="common">共同基础</option><option value="fine">细粒度方向</option><option value="cross">跨场景方向</option></select><span id="collection-count"></span></div>'+cards+FOOT
(OUT/'index.html').write_text(index,encoding='utf8')
(OUT/'collection-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
for old_slug in ([] if supplement_only else ['almt','norm-tr','est']):
 path=OUT/f'{old_slug}.html'
 old=path.read_text(encoding='utf8')
 if '全部论文精读目录' not in old:
  old=old.replace('<nav class="series-links"','<p><a href="index.html">全部论文精读目录 →</a></p><nav class="series-links"',1)
  path.write_text(old,encoding='utf8')
if not supplement_only:(ROOT/'remaining-papers-audit.json').write_text(json.dumps({'papers':stats,'pending':pending},ensure_ascii=False,indent=2),encoding='utf8')
(ROOT/'dist/content.js').write_text('window.COURSE='+json.dumps(course,ensure_ascii=False)+';',encoding='utf8')
app=ROOT/'dist/app.js';s=app.read_text(encoding='utf8')
mapping={m['id']:{'slug':m['slug'],'name':m['name']} for m in manifest}
s=re.sub(r'const deepPapers=\{.*?\};','const deepPapers='+json.dumps(mapping,ensure_ascii=False,separators=(',',':'))+';',s,count=1)
s=re.sub(r'找到 \$\{list.length\} 篇 · .*?</p>',r'找到 ${list.length} 篇 · '+str(len(manifest))+' 篇完整学术精读 · <a href="deep/index.html">查看精读目录 →</a></p>',s,count=1)
s=s.replace('26 篇论文提供基础讲义；ALMT、NORM-TR、EST 已新增完整学术精读，包含公式、实验与可运行练习。可搜索正文中的术语。',str(len(manifest))+' 篇完整学术精读，逐步解释概念、公式、源码与实验，附具体练习和验收要求。可搜索基础讲义中的术语，或进入完整精读目录。')
s=re.sub(r'\d+ 篇完整学术精读，逐步解释概念、公式、源码与实验，附具体练习和验收要求。可搜索基础讲义中的术语，或进入完整精读目录。',str(len(manifest))+' 篇完整学术精读，逐步解释概念、公式、源码与实验，附具体练习和验收要求。可搜索基础讲义中的术语，或进入完整精读目录。',s)
app.write_text(s,encoding='utf8')
print(json.dumps({'built':len(stats),'available':len(manifest),'pending':pending},ensure_ascii=False))
