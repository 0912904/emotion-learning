// Migration checks protect existing browser notes and version-1 backup imports.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const app=fs.readFileSync('dist/app.js','utf8'),ctx=vm.createContext({});
vm.runInContext(app.slice(app.indexOf('const blank='),app.indexOf('let state='))+';globalThis.check=validate;',ctx);
const old={weeks:[1,1,28,29,-1],papers:['P06','P06','P99'],notes:{journal:'保留我的笔记',P06:'原有论文记录',evil:'忽略此字段'},quizBest:5};
const migrated=JSON.parse(JSON.stringify(ctx.check(old)));
assert.deepEqual(migrated.weeks,[1,28]);assert.deepEqual(migrated.papers,['P06']);assert.equal(migrated.notes.journal,old.notes.journal);assert.equal(migrated.notes.P06,old.notes.P06);assert.deepEqual(migrated.inProgress,[]);assert.deepEqual(migrated.checks,{});
const extended=ctx.check({...old,inProgress:['P06','P07','P07','evil'],checks:{'s11:读第一条样本':true,bad:'yes'},lastVisited:{type:'paper',id:'P07'},lastExportAt:'2026-10-24T12:00:00Z'});
assert.deepEqual([...extended.inProgress],['P07']);assert.equal(extended.checks['s11:读第一条样本'],true);assert.equal(extended.lastVisited.id,'P07');assert.equal(extended.quizBest,5);
assert.throws(()=>ctx.check(null));assert.equal(ctx.check({notes:{journal:'a'.repeat(21000)},quizBest:100}).notes.journal.length,20000);assert.equal(ctx.check({quizBest:100}).quizBest,8);
console.log('PASS: legacy progress and notes preserved; extended states round-trip; invalid IDs and oversize notes bounded.');
