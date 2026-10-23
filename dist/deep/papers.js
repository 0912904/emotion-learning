document.addEventListener('DOMContentLoaded',()=>{
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
});