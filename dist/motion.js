'use strict';
// Motion layer: presentational only. It never touches the learning state and every
// effect is skipped when the visitor prefers reduced motion (reduceMotion from ui.js).
let motionReveal=true;
const motionOn=()=>!reduceMotion.matches;
const countMemory=new Map();
const REVEAL_SELECTOR='.page-intro,.resume-strip,.section-head,.section-sub,.track-card,.milestone,.phase-fork,.phase-head,.week,.paper,.lab-card,.quiz-card,.note-card,.progress-banner,.reader-layout,.empty,#main>.info,#main>.actions,#main>.chips,#main>.toolbar,#main>.card';
function syncMotionClass(){document.documentElement.classList.toggle('motion',motionOn());}
syncMotionClass();
reduceMotion.addEventListener('change',syncMotionClass);

const hasIO='IntersectionObserver' in window;
function settle(el,delay){
  // Drop the reveal hooks once visible so hover transitions are not delayed by the stagger.
  setTimeout(()=>{el.removeAttribute('data-reveal');el.style.removeProperty('--d');},delay+800);
}
const revealIO=hasIO?new IntersectionObserver(entries=>{
  let k=0;
  for(const en of entries){
    if(!en.isIntersecting)continue;
    const el=en.target;revealIO.unobserve(el);
    if(el.hasAttribute('data-reveal')){const d=Math.min(k++,8)*60;el.style.setProperty('--d',d+'ms');settle(el,d);}
    el.classList.add('is-in');
  }
},{rootMargin:'0px 0px -6% 0px',threshold:.06}):null;

const fmtNum=(v,dec)=>dec?v.toFixed(dec):String(Math.round(v));
function tweenNumber(el,from,to,{dec=0,duration=500,format}={}){
  if(!el)return;
  cancelAnimationFrame(el._tween);clearTimeout(el._tweenEnd);
  const show=v=>{el._value=v;el.textContent=format?format(v):fmtNum(v,dec);};
  if(!motionOn()||from===to){show(to);return;}
  const t0=performance.now();
  const tick=now=>{const p=Math.min(1,(now-t0)/duration),e=1-Math.pow(1-p,3);show(p<1?from+(to-from)*e:to);if(p<1&&el.isConnected)el._tween=requestAnimationFrame(tick);};
  el._tween=requestAnimationFrame(tick);
  // Frames can stall (background tab, throttling); the final value must still land.
  el._tweenEnd=setTimeout(()=>{cancelAnimationFrame(el._tween);show(to);},duration+120);
}
function countStart(el){const key=el.dataset.countKey;return key&&countMemory.has(key)?countMemory.get(key):0;}
function runCount(el,entering=false){
  // Entering a page counts up from 0; in-place updates animate from the last shown value.
  const to=Number(el.dataset.count),dec=Number(el.dataset.decimals||0),key=el.dataset.countKey;
  const from=entering?0:countStart(el);if(key)countMemory.set(key,to);
  tweenNumber(el,from,to,{dec,duration:entering?1100:650});
}
const countIO=hasIO?new IntersectionObserver(entries=>{for(const en of entries){if(en.isIntersecting){countIO.unobserve(en.target);runCount(en.target,true);}}},{threshold:.3}):null;

function growFrom0(scope){
  // Bars and rings start empty, then transition to their real value. A forced style flush
  // records the empty state, so the CSS transition starts without waiting for frames.
  const items=[...scope.querySelectorAll('.progress-track>div,.bar-fill,.cl-final')].map(el=>[el,el.style.width]);
  const ring=scope.querySelector('.ring-value'),ringTarget=ring?.style.strokeDashoffset;
  if(!items.length&&!ring)return;
  items.forEach(([el])=>{el.style.transition='none';el.style.width='0';});
  if(ring){ring.style.transition='none';ring.style.strokeDashoffset='100';}
  scope.getBoundingClientRect();
  items.forEach(([el,w])=>{el.style.removeProperty('transition');el.style.width=w;});
  if(ring){ring.style.removeProperty('transition');ring.style.strokeDashoffset=ringTarget;}
}

function motionEnhance(){
  const main=document.querySelector('#main');if(!main)return;
  const mode=motionReveal;motionReveal=false;
  const reveal=!!mode&&motionOn();
  updateScrollProgress();
  if(reveal&&hasIO&&mode==='partial'){
    // Filter changes: only the changed list animates; page chrome stays still.
    main.querySelectorAll('.phase-fork,.phase-head,.week,.paper,.empty').forEach(el=>{el.setAttribute('data-reveal','');revealIO.observe(el);});
    main.querySelectorAll('.phase').forEach(growFrom0);
    return;
  }
  const counts=main.querySelectorAll('[data-count]');
  const lines=main.querySelectorAll('.milestones');
  if(!reveal||!hasIO){
    counts.forEach(el=>{if(el.dataset.countKey)runCount(el);});
    lines.forEach(el=>el.classList.add('is-in'));
    return;
  }
  const crumb=document.querySelector('#breadcrumb');
  if(crumb){crumb.classList.remove('swap');void crumb.offsetWidth;crumb.classList.add('swap');}
  main.querySelector('.hero')?.classList.add('play');
  main.querySelectorAll(REVEAL_SELECTOR).forEach(el=>{if(el.closest('.hero'))return;el.setAttribute('data-reveal','');revealIO.observe(el);});
  lines.forEach(el=>revealIO.observe(el));
  counts.forEach(el=>{el.textContent=fmtNum(0,Number(el.dataset.decimals||0));countIO.observe(el);});
  growFrom0(main);
}
function motionPulse(el){if(!el||!motionOn())return;el.classList.remove('refresh');void el.offsetWidth;el.classList.add('refresh');}

// Small celebratory burst when a stage, paper or answer is completed.
function celebrate(anchor){
  if(!anchor||!motionOn())return;
  const r=anchor.getBoundingClientRect();if(!r.width&&!r.height)return;
  const box=document.createElement('div');box.className='burst';box.setAttribute('aria-hidden','true');
  box.style.left=r.left+r.width/2+'px';box.style.top=r.top+r.height/2+'px';
  const colors=['#0f5c52','#4b4a9c','#e4a84c','#66a385'];
  for(let i=0;i<16;i++){const s=document.createElement('i'),ang=i/16*Math.PI*2+Math.random()*.4,dist=26+Math.random()*30;
    s.style.setProperty('--tx',(Math.cos(ang)*dist).toFixed(1)+'px');s.style.setProperty('--ty',(Math.sin(ang)*dist).toFixed(1)+'px');s.style.setProperty('--c',colors[i%colors.length]);box.append(s);}
  (anchor.closest('dialog[open]')||document.body).append(box);
  setTimeout(()=>box.remove(),950);
}

// Reading progress in the sticky topbar.
const motionTopbar=document.querySelector('.topbar'),scrollBar=document.createElement('div');
scrollBar.className='scroll-progress';scrollBar.setAttribute('aria-hidden','true');motionTopbar?.append(scrollBar);
let scrollQueued=false;
function updateScrollProgress(){
  scrollQueued=false;
  const max=document.documentElement.scrollHeight-innerHeight,p=max>0?Math.min(1,Math.max(0,scrollY/max)):0;
  scrollBar.style.setProperty('--p',p.toFixed(4));motionTopbar?.classList.toggle('scrolled',scrollY>8);
}
const queueScroll=()=>{if(!scrollQueued){scrollQueued=true;requestAnimationFrame(updateScrollProgress);}};
addEventListener('scroll',queueScroll,{passive:true});
addEventListener('resize',queueScroll,{passive:true});

// Pointer spotlight on cards (fine pointers only).
const finePointer=matchMedia('(hover:hover) and (pointer:fine)');
document.addEventListener('pointermove',e=>{
  if(!finePointer.matches||!motionOn())return;
  const card=e.target.closest?.('.track-card,.paper,.week,.note-card');if(!card)return;
  const r=card.getBoundingClientRect();
  card.style.setProperty('--mx',(e.clientX-r.left).toFixed(0)+'px');card.style.setProperty('--my',(e.clientY-r.top).toFixed(0)+'px');
},{passive:true});
