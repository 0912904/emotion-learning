"""Preserve available licenses for the short, attributed source excerpts."""
from pathlib import Path
import html,json,subprocess,shutil
ROOT=Path(__file__).parent
RESEARCH=ROOT.parent.parent/'paper_analysis/remaining'
OUT=ROOT/'dist/deep/assets/licenses'
OUT.mkdir(parents=True,exist_ok=True)
entries=[]
repos=[]
for path in (RESEARCH/'foundations').glob('*/code'):
 repos.append((path.parent.name,path))
for path in (RESEARCH/'crossdomain').glob('*-code'):
 repos.append((path.name.removesuffix('-code'),path))
repos.extend([('mmsa',RESEARCH/'datasets/MMSA'),('pcl',RESEARCH/'finegrain/PCL'),('pcfrl',RESEARCH/'finegrain/PCFRL'),('affectgpt',RESEARCH/'finegrain/AffectGPT'),('ecpa',RESEARCH/'finegrain/ECPA')])
for name,repo in repos:
 if not repo.exists():continue
 try:
  sha=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
  remote=subprocess.check_output(['git','-C',str(repo),'remote','get-url','origin'],text=True).strip()
 except subprocess.CalledProcessError:continue
 candidates=[p for p in repo.iterdir() if p.is_file() and (p.name.lower().startswith('license') or p.name.lower().startswith('notice'))]
 if name=='affectgpt':
  for sub in ['AffectGPT','OV-MER']:
   candidates.extend(p for p in (repo/sub).glob('LICENSE*') if p.is_file())
 files=[]
 for p in candidates:
  filename=name+'-'+str(p.relative_to(repo)).replace('\\','-').replace('/','-')+'.txt'
  shutil.copyfile(p,OUT/filename);files.append(filename)
 headers=RESEARCH/'foundations/licenses'/name/'SOURCE_HEADERS.txt'
 if headers.is_file():
  filename=name+'-SOURCE_HEADERS.txt';shutil.copyfile(headers,OUT/filename);files.append(filename)
 entries.append({'name':name,'repository':remote,'commit':sha,'license_files':files})
(OUT/'manifest.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf8')
body=''.join('<li><strong>'+html.escape(e['name'])+'</strong> · <a href="'+html.escape(e['repository'],quote=True)+'">仓库</a> · '+e['commit']+'<br>'+(' · '.join('<a href="'+f+'">'+f+'</a>' for f in e['license_files']) or '本次未在已核查位置发现明确许可文件；仅作带来源的短节选分析，未分发完整实现。')+'</li>' for e in entries)
(OUT/'index.html').write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>代码节选来源与许可</title><style>body{max-width:900px;margin:40px auto;padding:20px;line-height:1.8;font-family:system-ui;overflow-wrap:anywhere}li{margin:20px 0}</style></head><body><a href="../../index.html">← 全部精读</a><h1>代码节选来源与许可</h1><p>讲义中代码按固定提交、文件和行号作短节选。下列许可文件保留原始内容；教学改写与原代码分别标注。数据和模型权重的使用条件需另行按各项目说明核验。</p><ul>'+body+'</ul></body></html>',encoding='utf8')
print(json.dumps({'repositories':len(entries),'license_files':sum(len(e['license_files']) for e in entries)}))
