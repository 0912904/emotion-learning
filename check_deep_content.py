"""Check local deep-reading assets, section anchors and math syntax inputs."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
import re,json
ROOT=Path(__file__).parent
DIST=ROOT/'dist'
class Document(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.text=[];self.links=[];self.ids=set()
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in ['pre','code','script','style']:self.skip+=1
  if 'id' in a:self.ids.add(a['id'])
  for k in ['href','src']:
   if k in a:self.links.append(a[k])
 def handle_endtag(self,tag):
  if tag in ['pre','code','script','style']:self.skip=max(0,self.skip-1)
  if tag in ['p','div','h2','h3']:self.text.append('\n')
 def handle_data(self,data):
  if not self.skip:self.text.append(data)
bundle=[];fail=[];summary=[]
pages=list((DIST/'deep').glob('*.html'))
for path in pages:
 doc=Document();doc.feed(path.read_text(encoding='utf8'))
 text=''.join(doc.text)
 display=re.findall(r'\$\$(.*?)\$\$',text,re.S)
 rest=re.sub(r'\$\$.*?\$\$','',text,flags=re.S)
 inline=re.findall(r'(?<!\\)\$([^$\n]+?)(?<!\\)\$',rest)
 for latex in display:bundle.append({'page':path.name,'latex':latex,'display':True})
 for latex in inline:bundle.append({'page':path.name,'latex':latex,'display':False})
 for link in doc.links:
  uri=urlparse(link)
  if uri.scheme or uri.netloc or not uri.path and not uri.fragment:continue
  target=(path.parent/unquote(uri.path)).resolve() if uri.path else path
  if not target.exists():fail.append({'page':path.name,'missing':link})
  if uri.fragment and (not uri.path or target.suffix=='.html') and target.exists():
   if target==DIST/'index.html' and uri.fragment=='papers':continue  # Existing hash-router view.
   other=doc
   if target!=path:other=Document();other.feed(target.read_text(encoding='utf8'))
   if unquote(uri.fragment) not in other.ids:fail.append({'page':path.name,'missing_anchor':link})
 summary.append({'page':path.name,'display_math':len(display),'inline_math':len(inline),'links':len(doc.links)})
(ROOT/'math-check-input.json').write_text(json.dumps(bundle,ensure_ascii=False),encoding='utf8')
(ROOT/'deep-links-audit.json').write_text(json.dumps({'pages':summary,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'pages':len(pages),'formulas':len(bundle),'link_failures':len(fail)},ensure_ascii=False))
assert not fail,fail
