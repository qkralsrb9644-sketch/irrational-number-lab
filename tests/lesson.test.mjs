import test from 'node:test';
import assert from 'node:assert/strict';
import { lesson, cleanState, grade, squareFromThousandths } from '../lesson-data.js';

test('45-minute lesson and independently specified answer keys',()=>{
  assert.equal(lesson.stages.reduce((n,s)=>n+s.minutes,0),45);
  assert.deepEqual(lesson.cards.map(c=>c.answer),['irrational','rational','rational','rational','rational','irrational','rational','rational']);
  assert.deepEqual(lesson.exit.map(q=>q.answer),[2,1,2]);
  assert.equal(lesson.standard,'[9수01-08]');
});
test('exact decimal arithmetic at the critical sqrt(2) boundary',()=>{
  assert.deepEqual(squareFromThousandths(1414),{length:'1.414',square:'1.999396',relation:'<'});
  assert.deepEqual(squareFromThousandths(1415),{length:'1.415',square:'2.002225',relation:'>'});
  assert.deepEqual(squareFromThousandths(1000),{length:'1.000',square:'1.000000',relation:'<'});
  assert.deepEqual(squareFromThousandths(2000),{length:'2.000',square:'4.000000',relation:'>'});
  for(let v=1000;v<=2000;v++) assert.equal(squareFromThousandths(v).relation,v<=1414?'<':'>');
});
test('invalid slider values cannot propagate NaN into the diagram',()=>{
  for(const n of [999,2001,NaN,Infinity,1414.5,'x']) assert.throws(()=>squareFromThousandths(n),RangeError);
});
test('grading distinguishes unanswered, wrong and correct, including option zero',()=>{
  const result=grade(lesson.exit,{q1:0,q2:1});
  assert.deepEqual(result,[{id:'q1',answered:true,correct:false},{id:'q2',answered:true,correct:true},{id:'q3',answered:false,correct:false}]);
});
test('stored state rejects corrupt, obsolete, duplicated and injected values',()=>{
  assert.equal(cleanState({version:99,slider:2000}).slider,1414);
  const state=cleanState({version:1,completed:['case','case','bad'],slider:'bad',cards:{a:'irrational',b:'html',unknown:'rational'},exit:{q1:0,q2:5,q3:'2'}});
  assert.deepEqual(state,{version:1,completed:['case'],slider:1414,cards:{a:'irrational'},exit:{q1:0}});
  assert.deepEqual(cleanState(null),cleanState({version:1}));
});
