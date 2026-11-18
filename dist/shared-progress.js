'use strict';
/* Public progress lives in the repository. Notes never leave localStorage. */
(() => {
  const enabled = location.hostname === '0912904.github.io' && location.pathname.startsWith('/emotion-learning/');
  window.sharedProgressEnabled = enabled;
  if (!enabled) return;
  const api='https://api.github.com/repos/0912904/emotion-learning/contents/shared-progress.json';
  const headers={Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'};
  let token='', sha='', remote=null, saving=false, dirty=false, timer=null, writeState='unverified', statusText='正在读取共享进度…';
  let localSnapshot=null;
  try { localSnapshot=JSON.parse(localStorage.getItem('emotion-learning-v1')||localStorage.getItem('emotion-learning-before-shared-v1')||'null'); if(localSnapshot&&!localStorage.getItem('emotion-learning-before-shared-v1'))localStorage.setItem('emotion-learning-before-shared-v1',JSON.stringify(localSnapshot)); } catch {}
  const permissionLabel=()=>!token?'仅访问':writeState==='denied'?'写入受限':writeState==='allowed'?'可修改':'已授权，写入待验证';
  const status = text => { statusText=text;const el=document.querySelector('#sync-status'); if(el) el.textContent=text;const mode=document.querySelector('#sync-permission');if(mode)mode.textContent=permissionLabel(); };
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
  const writeError = async res => {
    let message='';try { message=String((await res.json()).message||''); } catch {}
    const rate=res.headers?.get('x-ratelimit-remaining')==='0'||/rate limit|abuse detection/i.test(message);
    if(res.status===429||rate)return 'GitHub 暂时限制了请求，请稍后重试；本机改动未上传';
    if(res.status===401)return 'GitHub 令牌已失效或过期，请更换授权；本机改动未上传';
    if(res.status===403){writeState='denied';return 'GitHub 拒绝写入（403）。请检查令牌是否选中 emotion-learning 仓库并授予 Contents 读写权限，也可能受到仓库规则限制';}
    if(res.status===409)return '云端进度已变化，本次未覆盖。请先导出本机记录，再刷新核对';
    if(res.status===422)return 'GitHub 未接受更新（422），可能是文件版本或仓库规则发生变化；请先导出本机记录再核对';
    return 'GitHub 同步失败（'+res.status+'），请稍后重试';
  };
  const redraw=()=>{if(!window.learningReady)return;if(!document.querySelector('#reader')?.open && !document.activeElement?.matches('textarea,#paper-search'))render();window.sharedControls();};
  const load=async()=>{try{let data;if(token)data=await read(token);else{const res=await fetch('https://raw.githubusercontent.com/0912904/emotion-learning/main/shared-progress.json?t='+Date.now(),{cache:'no-store'});if(!res.ok)throw Error('GitHub 读取失败（'+res.status+'）');data={sha:'',value:sanitize(await res.json())};}sha=data.sha;remote=data.value;apply(remote);if(remote.initialized&&window.learningReady)save();redraw();status(remote.initialized?'共享进度已加载 · 仅所有者可编辑':'共享进度尚未初始化 · 下方显示本机记录，所有者可选择导入');}catch(e){sha='';redraw();status('无法读取共享进度；显示本机记录。'+e.message);}};
  const upload=async()=>{
    clearTimeout(timer);if(saving||!dirty||!token||!sha)return;
    saving=true;dirty=false;let failed=false;const sent=current();status('正在同步到 GitHub…');
    try{
      const body={message:'Update shared learning progress',sha,content:btoa(unescape(encodeURIComponent(JSON.stringify(sent,null,2)+'\n'))),branch:'main'};
      const res=await fetch(api,{method:'PUT',headers:{...headers,'Content-Type':'application/json',Authorization:'Bearer '+token},body:JSON.stringify(body)});
      if(!res.ok){dirty=true;throw Error(await writeError(res));}
      const result=await res.json();if(!result.content?.sha){dirty=true;throw Error('GitHub 未返回文件版本，请刷新后核对');}
      sha=result.content.sha;remote=sent;writeState='allowed';status('共享进度已同步到 GitHub');
    }catch(e){failed=true;dirty=true;status(e.message+'；本机记录仍保留');}finally{saving=false;if(dirty&&!failed){timer=setTimeout(upload,1200);}}
  };
  window.sharedSchedule=()=>{if(!token||!sha)return;dirty=true;clearTimeout(timer);timer=setTimeout(upload,1200);status('等待同步…');};
  window.addEventListener('beforeunload',e=>{if(dirty||saving){e.preventDefault();e.returnValue='';}});
  document.addEventListener('change',e=>{if(e.target.matches('[data-week-check],[data-paper-check],[data-reading-state]'))setTimeout(()=>window.sharedSchedule(),0);},true);
  window.sharedProgressPanel=()=>`<section class="card permission-panel" aria-labelledby="sync-title"><div class="permission-head"><h2 id="sync-title">权限</h2><p>当前权限：<strong id="sync-permission">${esc(permissionLabel())}</strong></p></div><p id="sync-status" class="permission-status" role="status">${esc(statusText)}</p><p class="permission-help">同步路线和论文阅读状态；笔记仅保存在当前浏览器。</p><div class="actions"><button class="btn primary small" id="sync-now">同步进度</button><button class="btn small" id="sync-connect">${token?'更换授权':'授权修改'}</button>${token?'<button class="btn small" id="sync-import-local">导入本机进度</button><button class="btn small" id="sync-signout">退出授权</button>':''}</div></section>`;
  document.addEventListener('click',async e=>{
    const id=e.target.closest('button')?.id;
    if(id==='sync-now'){
      if(saving){status('正在同步，请稍候');return;}
      if(dirty){await upload();return;}
      if(token&&!remote?.initialized){if(confirm('首次同步会将本机路线和论文状态公开到 GitHub，个人笔记不会上传。继续吗？')){dirty=true;await upload();}return;}
      await load();return;
    }
    if(id==='sync-signout'){if(dirty||saving){status('仍有未同步的改动，请先导出备份或更换授权后重试');return;}token='';writeState='unverified';redraw();status('已退出授权，目前只能访问');return;}
    if(id==='sync-refresh'){if(dirty||saving){status('有未同步的改动，请先保留本机记录');return;}await load();}
    if(id==='sync-import-local'){
      if(!token||!localSnapshot)return status('没有找到进入本页前的本机进度');
      if(!confirm('将用本机保存的路线与论文状态替换公开的共享进度；个人笔记不会上传。继续吗？'))return;
      const v=validate(localSnapshot);state.weeks=v.weeks;state.papers=v.papers;state.inProgress=v.inProgress;redraw();window.sharedSchedule();
    }
    if(id!=='sync-connect')return;
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
      const data=await read(candidate);const wasDirty=dirty;const changed=wasDirty&&sha&&sha!==data.sha;token=candidate;writeState='unverified';if(!wasDirty){sha=data.sha;remote=data.value;apply(remote);if(remote.initialized)save();}document.querySelector('#sync-dialog').close();redraw();status(changed?'授权已更新，但云端进度已变化；请先导出本机记录并核对':wasDirty?'授权已更新，本机改动仍未同步；请点击同步进度':'身份已验证；修改进度后可同步，写入权限尚待验证');
    }catch(err){document.querySelector('#sync-error').textContent=err.message;}
  });
  document.addEventListener('click',e=>{if(e.target.id==='sync-cancel'){document.querySelector('#sync-token').value='';document.querySelector('#sync-dialog').close();}});
  window.addEventListener('load',async()=>{document.querySelector('#storage-description').textContent='共享路线与论文状态 · 笔记保存在当前浏览器';new MutationObserver(()=>window.sharedControls()).observe(document.body,{childList:true,subtree:true});window.sharedControls();await load();});
})();
