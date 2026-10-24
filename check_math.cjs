const fs=require('fs');
const path=require('path');
const katex=require('./dist/deep/vendor/katex.min.js');
const input=JSON.parse(fs.readFileSync(path.join(__dirname,'math-check-input.json'),'utf8'));
const failures=[];
for(const item of input){try{katex.renderToString(item.latex,{throwOnError:true,displayMode:item.display,strict:'ignore'});}catch(error){failures.push({page:item.page,latex:item.latex,error:error.message});}}
fs.writeFileSync(path.join(__dirname,'math-check-results.json'),JSON.stringify({version:katex.version,checked:input.length,failures},null,2));
console.log(JSON.stringify({checked:input.length,failures}));
if(failures.length)process.exitCode=1;
