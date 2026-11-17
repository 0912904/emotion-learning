'use strict';
/* Public progress lives in the repository. Notes never leave localStorage. */
(() => {
  const enabled = location.hostname === '0912904.github.io' && location.pathname.startsWith('/emotion-learning/');
  window.sharedProgressEnabled = enabled;
  if (!enabled) return;
  const api='https://api.github.com/repos/0912904/emotion-learning/contents/shared-progress.json';
  const headers={Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'};
  let token='', sha='', remote=null, saving=false, dirty=false, timer=null, statusText='正在读取共享进度…';
  let localSnapshot=null;
  try { localSnapshot=JSON.parse(localStorage.getItem('emotion-learning-before-shared-v1')||localStorage.getItem('emotion-learning-v1')||'null'); if(localSnapshot&&!localStorage.getItem('emotion-learning-before-shared-v1'))localStorage.setItem('emotion-learning-before-shared-v1',JSON.stringify(localSnapshot)); } catch {}
  const status = text => { statusText=text;const el=document.querySelector('#sync-status'); if(el) el.textContent=text; };
  const sanitize = v => {
    if(!v || v.version!==1 || typeof v.initialized!=='boolean' || !Array.isArray(v.weeks) || !Array.isArray(v.papers) || !Array.isArray(v.inProgress)) throw Error('共享进度格式不正确');
    const clean=validate({...blank(),weeks:v.weeks,papers:v.papers,inProgress:v.inProgress});
    return {version:1,initialized:v.initialized,weeks:clean.weeks,papers:clean.papers,inProgress:clean.inProgress};
  };
  const current = () => sanitize({version:1,initialized:true,weeks:state.weeks,papers:state.papers,inProgress:state.inProgress});
  const apply = value => { if(!value?.initialized)return; state.weeks=[...value.weeks];state.papers=[...value.papers];state.inProgress=[...value.inProgress]; };
  window.sharedInitialized=()=>!!remote?.initialized;
  window.sharedAfterImport=()=>{if(remote?.initialized&&!dirty&&!saving)apply(remote);};
  window.sharedControls=()=>{
    document.querySelectorAll('[data-week-check],[data-paper-check],[data-reading-state]').forEach(el=>{el.disabled=!token||!sha;el.title=el.disabled?'共享进度仅由网站所有者修改':'';});
  };
  const read = async (auth='') => {
    const res=await fetch(api+'?ref=main',{headers:auth?{...headers,Authorization:'Bearer '+auth}:headers,cache:'no-store'});
    if(!res.ok) throw Error('GitHub 读取失败（'+res.status+'）');
    const data=await res.json();
    if(data.encoding!=='base64'||typeof data.content!=='string'||!data.sha)throw Error('GitHub 返回的数据不完整');
    return {sha:data.sha,value:sanitize(JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(data.content.replace(/\s/g,'')),c=>c.charCodeAt(0)))))};
  };
  const redraw=()=>{if(!window.learningReady)return;if(!document.querySelector('#reader')?.open && !document.activeElement?.matches('textarea,#paper-search'))render();window.sharedControls();};
  const load=async()=>{try{let data;if(token)data=await read(token);else{const res=await fetch('https://raw.githubusercontent.com/0912904/emotion-learning/main/shared-progress.json?t='+Date.now(),{cache:'no-store'});if(!res.ok)throw Error('GitHub 读取失败（'+res.status+'）');data={sha:'',value:sanitize(await res.json())};}sha=data.sha;remote=data.value;apply(remote);if(remote.initialized&&window.learningReady)save();redraw();status(remote.initialized?'共享进度已加载 · 仅所有者可编辑':'共享进度尚未初始化 · 下方显示本机记录，所有者可选择导入');}catch(e){sha='';redraw();status('无法读取共享进度；显示本机记录。'+e.message);}};
  const upload=async()=>{
    clearTimeout(timer);if(saving||!dirty||!token||!sha)return;
    saving=true;dirty=false;let failed=false;const sent=current();status('正在同步到 GitHub…');
    try{
      const body={message:'Update shared learning progress',sha,content:btoa(unescape(encodeURIComponent(JSON.stringify(sent,null,2)+'\n'))),branch:'main'};
      const res=await fetch(api,{method:'PUT',headers:{...headers,'Content-Type':'application/json',Authorization:'Bearer '+token},body:JSON.stringify(body)});
      if(res.status===409||res.status===422){dirty=true;throw Error('云端进度已变化，本次未覆盖。请复制当前记录后刷新并重试');}
      if(!res.ok){dirty=true;throw Error('同步失败（'+res.status+'）');}
      const result=await res.json();if(!result.content?.sha){dirty=true;throw Error('GitHub 未返回文件版本，请刷新后核对');}
      sha=result.content.sha;remote=sent;status('共享进度已同步到 GitHub');
    }catch(e){failed=true;dirty=true;status(e.message+'；本机记录仍保留');}finally{saving=false;if(dirty&&!failed){timer=setTimeout(upload,1200);}}
  };
  window.sharedSchedule=()=>{if(!token||!sha)return;dirty=true;clearTimeout(timer);timer=setTimeout(upload,1200);status('等待同步…');};
  window.addEventListener('beforeunload',e=>{if(dirty||saving){e.preventDefault();e.returnValue='';}});
  document.addEventListener('change',e=>{if(e.target.matches('[data-week-check],[data-paper-check],[data-reading-state]'))setTimeout(()=>window.sharedSchedule(),0);},true);
  window.sharedProgressPanel=()=>`<section class="card" aria-labelledby="sync-title"><h2 id="sync-title">共享学习进度</h2><p id="sync-status" role="status">${esc(statusText)}</p><p>路线和论文状态对所有访客可见，只有站点所有者可修改。个人笔记保存在当前浏览器。</p><div class="actions"><button class="btn small" id="sync-connect">${token?'退出进度编辑':'所有者编辑进度'}</button>${token?'<button class="btn small" id="sync-import-local">用本机记录初始化或替换共享进度</button><button class="btn small" id="sync-retry">重试同步</button>':''}<button class="btn small" id="sync-refresh">刷新共享进度</button></div></section>`;
  document.addEventListener('click',async e=>{
    const id=e.target.closest('button')?.id;
    if(id==='sync-retry'){if(dirty)await upload();else status('没有待同步的改动');}
    if(id==='sync-refresh'){if(dirty||saving){status('有未同步的改动，请先保留本机记录');return;}await load();}
    if(id==='sync-import-local'){
      if(!token||!localSnapshot)return status('没有找到进入本页前的本机进度');
      if(!confirm('将用本机保存的路线与论文状态替换公开的共享进度；个人笔记不会上传。继续吗？'))return;
      const v=validate(localSnapshot);state.weeks=v.weeks;state.papers=v.papers;state.inProgress=v.inProgress;redraw();window.sharedSchedule();
    }
    if(id!=='sync-connect')return;
    if(token){if(dirty||saving){status('有未同步的改动，请先保留本机记录');return;}token='';redraw();status('已退出编辑模式');return;}
    const dialog=document.querySelector('#sync-dialog');dialog.showModal();
  });
  document.addEventListener('submit',async e=>{
    if(e.target.id!=='sync-form')return;e.preventDefault();
    const input=document.querySelector('#sync-token'),candidate=input.value.trim();input.value='';
    if(!candidate)return status('请输入 GitHub 令牌');
    try{
      const auth={...headers,Authorization:'Bearer '+candidate};
      const [u,r]=await Promise.all([fetch('https://api.github.com/user',{headers:auth,cache:'no-store'}),fetch('https://api.github.com/repos/0912904/emotion-learning',{headers:auth,cache:'no-store'})]);
      if(!u.ok||!r.ok)throw Error('GitHub 未接受此令牌');
      const user=await u.json(),repo=await r.json();
      if(user.login?.toLowerCase()!=='0912904'||!repo.permissions?.push)throw Error('需要仓库所有者及仓库写入权限');
      const data=await read(candidate);sha=data.sha;remote=data.value;apply(remote);if(remote.initialized)save();token=candidate;document.querySelector('#sync-dialog').close();redraw();status('已进入编辑模式；修改后自动同步');
    }catch(err){document.querySelector('#sync-error').textContent=err.message;}
  });
  document.addEventListener('click',e=>{if(e.target.id==='sync-cancel'){document.querySelector('#sync-token').value='';document.querySelector('#sync-dialog').close();}});
  window.addEventListener('load',async()=>{document.querySelector('#storage-description').textContent='共享路线与论文状态 · 笔记保存在当前浏览器';new MutationObserver(()=>window.sharedControls()).observe(document.body,{childList:true,subtree:true});window.sharedControls();await load();});
})();
