from pathlib import Path
import re, json, html

root = Path(__file__).parent
source = root.parent.parent / '细粒度与跨场景情绪研究_初学者完整学习路线.md'
md = source.read_text(encoding='utf-8')

def inline(s):
    s = html.escape(s)
    s = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)', lambda m: '<a href="'+m[2]+'"'+(' target="_blank" rel="noopener noreferrer"' if m[2].startswith('https://') else '')+'>'+m[1]+'</a>' if m[2].startswith(('https://','#')) else m[1]+'（见本地原文）', s)
    s = re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
    return re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)

def render(s):
    lines=s.splitlines(); out=[]; i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line or line.startswith('<a id=') or line=='---': i+=1; continue
        if line.startswith('```'):
            kind=line[3:]; block=[]; i+=1
            while i<len(lines) and not lines[i].startswith('```'): block.append(lines[i]); i+=1
            if kind=='mermaid': out.append('<div class="flow">共同基础 → ALMT 消融 → 细粒度 / 跨场景 → 受控实验与研究报告</div>')
            else: out.append('<pre><code>'+html.escape('\n'.join(block))+'</code></pre>')
        elif line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=lines[i].strip().strip('|').split('|')
                if not all(re.fullmatch(r'\s*:?-+:?\s*',c) for c in cells): rows.append(cells)
                i+=1
            out.append('<div class="table-scroll"><table><thead><tr>'+''.join('<th>'+inline(c.strip())+'</th>' for c in rows[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+inline(c.strip())+'</td>' for c in row)+'</tr>' for row in rows[1:])+'</tbody></table></div>'); continue
        elif re.match(r'^#{1,6} ',line):
            level=min(len(line.split(' ')[0])+1,6); out.append(f'<h{level}>'+inline(line.split(' ',1)[1])+f'</h{level}>')
        elif re.match(r'^(- |\d+\. )',line):
            items=[]
            while i<len(lines) and re.match(r'^(- |\d+\. )',lines[i].strip()):
                items.append('<li>'+inline(re.sub(r'^(- |\d+\. )','',lines[i].strip()).replace('[ ] ','□ '))+'</li>'); i+=1
            out.append('<ul>'+''.join(items)+'</ul>'); continue
        else: out.append('<p>'+inline(line)+'</p>')
        i+=1
    return '\n'.join(out)

sections=[]
for match in re.finditer(r'<a id="(s\d+)"></a>\s*## ([^\n]+)\n(.*?)(?=<a id="s\d+"></a>|\Z)',md,re.S):
    sections.append(dict(id=match[1],title=match[2],html=render(match[3])))
papers=[]
for match in re.finditer(r'### (P\d+)｜([^\n]+)\n(.*?)(?=\n### P|\n<a id="s7"|\Z)',md,re.S):
    n=int(match[1][1:]); body=match[3].strip()
    group='common' if n in [1,2,5,6,7,8,25,26] else 'fine' if n in [3,4,9,10,11,12,13,14,15] else 'cross'
    core=n in [1,2,6,7,8,10,11,12,13,14,16,18,19,21,22]
    problem=re.search(r'\*\*问题：\*\*\s*([^\n]+)',body)
    papers.append(dict(id=match[1],title=match[2],group=group,core=core,summary=problem[1] if problem else '',meta=body.splitlines()[0],html=render(body)))
data={'sections':sections,'papers':papers}
(root/'dist/content.js').write_text('window.COURSE='+json.dumps(data,ensure_ascii=False)+';',encoding='utf-8')
(root/'dist/learning-roadmap.md').write_text(md,encoding='utf-8')
print(json.dumps({'sections':len(sections),'papers':len(papers)},ensure_ascii=False))
