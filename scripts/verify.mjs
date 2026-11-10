import assert from 'node:assert/strict';
import { readFile,stat } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const html=await readFile(path.join(root,'index.html'),'utf8');
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
assert.equal(new Set(ids).size,ids.length,'Duplicate HTML IDs');
const refs=[...html.matchAll(/(?:href|src)="([^"#]+)"/g)].map(m=>m[1]);
const css=await readFile(path.join(root,'styles.css'),'utf8');
refs.push(...[...css.matchAll(/url\(['"]?([^)'"\s]+)/g)].map(m=>m[1]));
for(const ref of refs.filter(r=>r.startsWith('./'))){
  const item=await stat(path.resolve(root,ref));assert(item.isFile(),`Missing ${ref}`);assert(item.size>0,`Empty ${ref}`);
}
for(const m of html.matchAll(/href="#([^"]+)"/g)) assert(ids.includes(m[1]),`Broken anchor ${m[1]}`);
for(const file of ['learning-guide.pdf','worksheet.pdf','teacher-guide.pdf','student-set.pdf']){
  const b=await readFile(path.join(root,'downloads',file));assert.equal(b.subarray(0,5).toString(),'%PDF-');
}
assert(!html.includes('학교명: 음성'),'Unexpected school branding');
assert(!html.match(/https?:\/\/[^" ]+\.(?:js|css)/),'External runtime dependency');
console.log(`PASS: ${ids.length} unique IDs; all local assets, font, PDF links and section anchors exist.`);
