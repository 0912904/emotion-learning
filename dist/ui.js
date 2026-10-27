'use strict';
// UI enhancements share the existing version-1 store and never replace paper content.
let fusionTimers=[],fusionDemoPlayed=false;
const reduceMotion=matchMedia('(prefers-reduced-motion:reduce)');
function markReading(id){
  state.lastVisited={type:'paper',id};
  if(!state.papers.includes(id)&&!state.inProgress.includes(id))state.inProgress.push(id);
  save();
}
function enhanceProse(scope){
  scope.querySelectorAll('pre:not(.mermaid)').forEach(pre=>{
    if(pre.querySelector('.copy-code'))return;
    const button=document.createElement('button');button.type='button';button.className='copy-code';button.textContent='复制';
    button.setAttribute('aria-label','复制此代码或模板');
    button.addEventListener('click',async()=>{
      const text=pre.querySelector('code')?.textContent||Array.from(pre.childNodes).filter(n=>n!==button).map(n=>n.textContent).join('');
      try{await navigator.clipboard.writeText(text);button.textContent='已复制';toast('模板已复制');}
      catch{button.textContent='请选中复制';toast('剪贴板不可用，请选中模板后手动复制。');}
      setTimeout(()=>{if(button.isConnected)button.textContent='复制';},1800);
    });pre.append(button);
  });
  scope.querySelectorAll('a[href^="#s"]').forEach(a=>{
    if(/^#s\d+$/.test(a.getAttribute('href')))a.href='#handbook/'+a.getAttribute('href').slice(1);
  });
  const book=scope.matches?.('.handbook-content')?scope:scope.querySelector('.handbook-content');
  if(!book)return;
  const section=book.dataset.bookSection;
  function bindCheck(container,text){
    const key=section+':'+text.trim();
    const label=document.createElement('label');label.className='check handbook-check';
    const input=document.createElement('input');input.type='checkbox';input.dataset.handbookCheck=key;input.checked=!!state.checks[key];
    label.append(input,document.createTextNode(text));container.replaceChildren(label);
  }
  book.querySelectorAll('li').forEach(li=>{if(li.textContent.trim().startsWith('□'))bindCheck(li,li.textContent.trim().slice(1).trim());});
  if(section==='s11')book.querySelectorAll('tbody tr').forEach(tr=>{
    const cell=tr.cells[0];if(!cell||cell.querySelector('input'))return;
    const label=document.createElement('label');label.className='check handbook-check';
    const input=document.createElement('input');input.type='checkbox';input.dataset.handbookCheck=section+':'+tr.cells[1].textContent.trim();input.checked=!!state.checks[input.dataset.handbookCheck];
    label.append(input,document.createTextNode(cell.textContent));cell.replaceChildren(label);
  });
  book.querySelectorAll('h4').forEach((h,i)=>{h.id=section+'-part-'+i;});
  if(book.querySelectorAll('h4').length>1){
    const toc=document.createElement('nav');toc.className='section-toc';toc.setAttribute('aria-label','本章小节');
    book.querySelectorAll('h4').forEach(h=>{
      const b=document.createElement('button');b.type='button';b.textContent=h.textContent;
      b.addEventListener('click',()=>document.getElementById(h.id).scrollIntoView({behavior:reduceMotion.matches?'instant':'smooth',block:'start'}));toc.append(b);
    });book.querySelector('h2').after(toc);
    let pending=false;
    const highlight=()=>{pending=false;if(!book.isConnected){window.removeEventListener('scroll',onScroll);return;}const headings=[...book.querySelectorAll('h4')];const active=headings.filter(h=>h.getBoundingClientRect().top<160).pop()||headings[0];[...toc.children].forEach((b,i)=>{if(headings[i]===active)b.setAttribute('aria-current','location');else b.removeAttribute('aria-current');});};
    const onScroll=()=>{if(!pending){pending=true;requestAnimationFrame(highlight);}};
    window.addEventListener('scroll',onScroll,{passive:true});highlight();
  }
}
function enhancePage(){
  fusionTimers.forEach(clearTimeout);fusionTimers=[];
  enhanceProse(document.querySelector('#main'));
  const badge=document.querySelector('[data-page="roadmap"] em');if(badge)badge.textContent=state.weeks.length?state.weeks.length+'/28':'28';
  document.querySelector('#mobile-more')?.classList.toggle('active',['lab','quiz','notes'].includes(page));
  const needsBackup=!!(state.weeks.length||state.papers.length||Object.values(state.notes).some(Boolean)||Object.values(state.checks).some(Boolean))&&(!state.lastExportAt||Date.now()-Date.parse(state.lastExportAt)>7*86400000);
  const reminder=document.querySelector('#backup-reminder');if(reminder)reminder.hidden=!needsBackup;
  const fusion=document.querySelector('#fusion');if(!fusion)return;
  const on=new Set(['t']);let touched=false;
  const outputs={t:['平静','文字：“我没事”'],ta:['可能低落','哽咽的声音与字面意思不一致'],tv:['可能担忧','紧皱的眉头与字面意思不一致'],tav:['可能压抑','音视频提供负面线索；标签仍需核验']};
  const toggle=m=>{
    on.has(m)?on.delete(m):on.add(m);fusion.dataset.on=[...on].join(' ');
    fusion.querySelector(`[data-modality="${m}"]`).setAttribute('aria-pressed',String(on.has(m)));
    const [verdict,why]=outputs[['t','a','v'].filter(x=>on.has(x)).join('')];
    fusion.querySelector('#fusion-verdict').textContent=verdict;fusion.querySelector('#fusion-why').textContent=why;
    // Restart the pulse so each change of evidence visibly updates the judgement.
    [fusion.querySelector('.fusion-core'),fusion.querySelector('#fusion-why')].forEach(el=>{el.classList.remove('bump');void el.offsetWidth;el.classList.add('bump');});
  };
  fusion.addEventListener('click',e=>{const b=e.target.closest('[data-modality]:not(:disabled)');if(b){touched=true;fusionTimers.forEach(clearTimeout);toggle(b.dataset.modality);}});
  // One optional explanatory sequence per document, cancelled by any interaction or route change.
  if(!reduceMotion.matches&&!fusionDemoPlayed){fusionDemoPlayed=true;[['a',2500],['v',4200]].forEach(([m,ms])=>fusionTimers.push(setTimeout(()=>{if(!touched&&fusion.isConnected&&!reduceMotion.matches&&!document.hidden)toggle(m);},ms)));}
}
document.addEventListener('click',e=>{
  const link=e.target.closest('a[href*="deep/"]');
  if(link){const href=link.getAttribute('href');const entry=Object.entries(deepPapers).find(([,v])=>href.endsWith('/'+v.slug+'.html'));if(entry)markReading(entry[0]);}
  if(e.target.closest('#mobile-more'))document.querySelector('#more-menu').showModal();
  if(e.target.closest('#close-more')||e.target.closest('#more-menu a'))document.querySelector('#more-menu').close();
});
document.addEventListener('change',e=>{
  const el=e.target;
  if(el.dataset.readingState){const id=el.dataset.readingState;if(el.value==='read'&&typeof celebrate==='function')celebrate(el);state.papers=state.papers.filter(x=>x!==id);state.inProgress=state.inProgress.filter(x=>x!==id);if(el.value==='read')state.papers.push(id);if(el.value==='reading')state.inProgress.push(id);save();document.querySelector('#paper-results').innerHTML=paperCards();toast(id+' 已更新为'+el.options[el.selectedIndex].text);}
  if(el.dataset.handbookCheck){if(el.checked&&typeof celebrate==='function')celebrate(el);state.checks[el.dataset.handbookCheck]=el.checked;save();toast(el.checked?'已记下这项完成记录':'已取消勾选');}
});
window.addEventListener('storage',e=>{
  if(!window.learningReady||e.key!==KEY)return;
  // Flush a focused note first so a remote update cannot erase uncommitted input.
  const focused=document.activeElement, noteId=focused?.dataset?.note, value=focused?.value;
  try{state=validate(JSON.parse(e.newValue||'null')||blank());storageOK=true;
    if(noteId){if(state.notes[noteId]!==value){state.notes[noteId]=value;toast('另一标签页已更新；当前正在编辑的文字已保留，请继续编辑后保存。');}return;}
    if(document.querySelector('#reader').open){const n=document.querySelector('#reader [data-note]');if(n)n.value=state.notes[n.dataset.note]||'';document.querySelectorAll('#reader [data-week-check]').forEach(c=>c.checked=state.weeks.includes(+c.dataset.weekCheck));document.querySelectorAll('#reader [data-paper-check]').forEach(c=>c.checked=state.papers.includes(c.dataset.paperCheck));}
    if(document.activeElement?.id==='paper-search')return;
    render();
  }catch{toast('另一标签页的数据无法读取，当前记录已保留。');}
});
reduceMotion.addEventListener('change',()=>{if(reduceMotion.matches)fusionTimers.forEach(clearTimeout);});
