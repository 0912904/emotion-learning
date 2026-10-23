"""Render additional paper-analyzer articles, preserving the ALMT visual system."""
from pathlib import Path
import html, json, re, shutil

ROOT=Path(__file__).parent
OUT=ROOT/'dist/deep'
almt=(OUT/'almt.html').read_text(encoding='utf-8')
css=re.search(r'<style>(.*?)</style>',almt,re.S).group(1)
js=r'''document.addEventListener('DOMContentLoaded',()=>{
const status=document.querySelector('#render-status');
try{renderMathInElement(document.querySelector('main'),{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],throwOnError:true});
status.textContent='公式已排版 · 可离线阅读';
mermaid.initialize({startOnLoad:false,theme:'neutral',securityLevel:'strict'});
mermaid.run({querySelector:'.mermaid'}).catch(()=>{status.textContent='流程图未排版，仍可阅读源结构';});
}catch(e){status.textContent='公式排版失败，请检查本地资源';status.classList.add('error');}
const alpha=document.querySelector('#grl-alpha');
if(alpha){const update=()=>{const a=Number(alpha.value);document.querySelector('#grl-output').textContent=`λ=${a.toFixed(2)} | 前向 z=2 | 判别器方向保持正常 | 提取器端梯度=${(-4*a).toFixed(2)}`;};alpha.addEventListener('input',update);update();}
const perm=document.querySelector('#snippet-permutation');
if(perm){const update=()=>{const a=perm.value.split(',').map(Number);document.querySelector('#snippet-output').textContent=`输入顺序：[${a.join(', ')}]；教学排列类别=${perm.selectedIndex}（预先固定的4种排列之一）。模型需要对整条排列做一次分类。原EST使用7个片段、10种固定排列，并非这里的4类。`;};perm.addEventListener('change',update);update();}
document.querySelector('#print').addEventListener('click',()=>window.print());
});'''
(OUT/'papers.js').write_text(js,encoding='utf-8')
stats={}
for slug,name in [('norm-tr','norm'),('est','est')]:
 source=ROOT/f'{name}-content.json'
 if not source.exists():
  print('waiting for',source.name);continue
 data=json.loads(source.read_text(encoding='utf-8'))
 body=data.get('body') or ''.join(f'<h2 id="{s["id"]}">{s["title"]}</h2>'+s['html'] for s in data['sections'])
 if data.get('references'):
  refs=data['references']
  if isinstance(refs,list): refs='<ol>'+''.join('<li><a href="'+html.escape(r['url'],quote=True)+'">'+html.escape(r['title'])+'</a></li>' for r in refs)+'</ol>'
  body+='<h2 id="sources">来源与核查</h2>'+refs
 if slug=='est':
  demo='<div class="demo"><h3>交互：打乱片段后，SSOP的标签是什么？</h3><p>用三个片段和四种固定排列做小型教学示意，原顺序为1、2、3。选择输入排列，查看整条排列对应的类别标签；不是逐位置预测原编号。真实EST为七个片段、十种固定排列。这里仅演示监督标签生成，不训练网络。</p><label for="snippet-permutation">片段输入顺序</label><select id="snippet-permutation"><option value="3,1,2">3 → 1 → 2</option><option value="2,3,1">2 → 3 → 1</option><option value="3,2,1">3 → 2 → 1</option><option value="1,2,3">1 → 2 → 3</option></select><output id="snippet-output" aria-live="polite"></output></div>'
  body=body.replace('<h2',demo+'<h2',1)
  body+='<p><a href="est_sampling_probe.py" download>下载 EST 片段采样与排列学习脚本（只用Python标准库）</a></p>'
 body=body.replace('$$<span>', '$$<span class="equation-label">')
 toc=''.join(f'<a href="#{i}">{re.sub("<[^>]+>","",t)}</a>' for i,t in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>',body,re.S))
 title=data['title']
 doc='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+' · 情绪研究学习室</title><link rel="stylesheet" href="vendor/katex.min.css"><style>'+css+'select{padding:12px;border:1px solid #b6cdbd;font:inherit;max-width:100%;background:white}.series-links{display:flex;gap:20px;flex-wrap:wrap}</style><script defer src="vendor/katex.min.js"></script><script defer src="vendor/auto-render.min.js"></script><script defer src="vendor/mermaid.min.js"></script><script defer src="papers.js"></script></head><body><div class="topbar"><a href="../index.html#papers">← 返回论文阅读室</a><span id="render-status">正在排版公式与图表…</span><button id="print">打印 / 保存 PDF</button></div><main><header><div class="eyebrow">PAPER ANALYZER · '+name.upper()+' · 学术型精读</div><h1>'+html.escape(title)+'</h1><p class="lede">'+data.get('subtitle','')+'</p></header><div class="meta">'+data.get('metadata','')+'</div><div class="summary-box"><h3>一句话总结</h3><p>'+data['summary']+'</p></div><nav class="series-links" aria-label="精读系列"><a href="almt.html">ALMT</a><a href="norm-tr.html">NORM-TR</a><a href="est.html">EST</a></nav><nav class="toc" aria-label="文章目录">'+toc+'</nav>'+body+'<footer>学术型精读 · 原论文、公开代码、教学算例分别注明 · 2026-10-23</footer></main></body></html>'
 text=re.sub('<[^>]*>','',body)
 st={'chinese_characters':len(re.findall('[\u4e00-\u9fff]',text)),'paragraphs':body.count('<p>'),'equations':body.count('class="equation"'),'tables':body.count('<table>'),'code_excerpts':body.count('class="code-source"'),'diagram':body.count('class="mermaid"')}
 assert st['chinese_characters']>=4000 and st['paragraphs']>=20 and st['equations']>=5 and st['tables']>=2,st
 assert st['diagram']>=1
 (OUT/f'{slug}.html').write_text(doc,encoding='utf-8')
 stats[slug]={'structure':st,'evidence':data.get('audit',{})}

(OUT/'assets').mkdir(exist_ok=True)
license_source=ROOT.parent.parent/'paper_analysis/norm-tr/related-code/LICENSE'
if license_source.exists(): shutil.copyfile(license_source,OUT/'assets/LNLN-CODE-LICENSE.txt')
est_script=ROOT.parent.parent/'paper_analysis/est/est_sampling_probe.py'
if est_script.exists(): shutil.copyfile(est_script,OUT/'est_sampling_probe.py')
(ROOT/'more-papers-audit.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(stats,ensure_ascii=False))
