import { lesson, cleanState, squareFromThousandths, grade } from './lesson-data.js';

const key = 'irrational-number-lab-v1';
let state = cleanState(null);
let storageOK = true;
try { state = cleanState(JSON.parse(localStorage.getItem(key))); } catch { storageOK = false; }
const $ = id => document.getElementById(id);
function save() {
  try { localStorage.setItem(key, JSON.stringify(state)); } catch { storageOK = false; }
  $('storage-notice').hidden = storageOK;
}
function renderProgress() {
  $('progress').value = state.completed.length;
  $('progress-text').textContent = `수사 진행 ${state.completed.length} / 5`;
  for (const stage of lesson.stages) {
    const done = state.completed.includes(stage.id);
    document.querySelector(`[data-complete="${stage.id}"]`).setAttribute('aria-pressed', String(done));
    document.querySelector(`.journey a[href="#${stage.id}"]`).classList.toggle('done', done);
  }
  $('completion-message').hidden = state.completed.length !== 5;
}
function renderSlider() {
  const info = squareFromThousandths(state.slider);
  $('length-slider').value = state.slider;
  $('length-slider').setAttribute('aria-valuetext', `${info.length} 미터`);
  $('length-output').textContent = info.length;
  $('square-output').textContent = info.square;
  $('relation-output').textContent = `${info.relation} 2`;
  $('length-feedback').textContent = info.relation === '<' ? '아직 짧아요. 선택한 길이는 √2 m보다 작습니다.' : '조금 길어요. 선택한 길이는 √2 m보다 큽니다.';
  const delta = (state.slider / 1000) * 200 / Math.sqrt(2);
  $('guess-line').setAttribute('x2', String(105 + delta));
  $('guess-line').setAttribute('y2', String(310 - delta));
  $('guess-dot').setAttribute('cx', String(105 + delta));
  $('guess-dot').setAttribute('cy', String(310 - delta));
}
function element(tag, className, text) {
  const e = document.createElement(tag);
  if (className) e.className = className;
  if (text !== undefined) e.textContent = text;
  return e;
}
function option(name, value, text, selected) {
  const label = element('label', 'choice');
  const input = document.createElement('input');
  input.type = 'radio'; input.name = name; input.value = value; input.checked = selected;
  label.append(input, document.createTextNode(text));
  return label;
}
function renderQuestions() {
  $('number-cards').replaceChildren();
  for (const [i, c] of lesson.cards.entries()) {
    const card = element('fieldset', 'number-card');
    card.append(element('legend', '', `증거 ${String(i + 1).padStart(2, '0')}`), element('p', 'card-number', c.value), element('p', 'card-note', c.note || ''));
    const pair = element('div', 'choice-pair');
    pair.append(option(c.id, 'rational', '유리수', state.cards[c.id] === 'rational'), option(c.id, 'irrational', '무리수', state.cards[c.id] === 'irrational'));
    card.append(pair);
    const feedback = element('p', 'feedback'); feedback.id = `card-feedback-${c.id}`; feedback.hidden = true;
    card.append(feedback); $('number-cards').append(card);
  }
  $('exit-questions').replaceChildren();
  for (const [i, q] of lesson.exit.entries()) {
    const card = element('fieldset', 'exit-card');
    card.append(element('legend', '', `CHECK ${String(i + 1).padStart(2, '0')}`), element('h3', '', q.prompt));
    const opts = element('div', 'exit-options');
    q.options.forEach((text, index) => opts.append(option(q.id, String(index), text, state.exit[q.id] === index)));
    card.append(opts);
    const feedback = element('p', 'feedback'); feedback.id = `exit-feedback-${q.id}`; feedback.hidden = true;
    card.append(feedback); $('exit-questions').append(card);
  }
  $('application-question').textContent = lesson.application.prompt;
  $('application-answer').textContent = lesson.application.answer;
}
function checkAnswers(items, responses, prefix, summaryId) {
  const results = grade(items, responses);
  const unanswered = results.filter(r => !r.answered);
  if (unanswered.length) {
    $(summaryId).textContent = `아직 ${unanswered.length}문항이 남았어요. 모든 답을 선택한 뒤 확인해 보세요.`;
    document.querySelector(`input[name="${unanswered[0].id}"]`).focus();
    return;
  }
  for (const [i, result] of results.entries()) {
    const feedback = $(`${prefix}-feedback-${result.id}`);
    feedback.className = `feedback ${result.correct ? 'correct' : 'incorrect'}`;
    feedback.replaceChildren(element('strong', '', result.correct ? '✓ 맞았어요!' : '↺ 다시 살펴봐요.'), document.createTextNode(items[i].why));
    feedback.hidden = false;
  }
  const count = results.filter(r => r.correct).length;
  $(summaryId).textContent = `${items.length}문항 중 ${count}문항 정답. ${count === items.length ? '좋아요! 근거를 내 말로 설명해 보세요.' : '해설을 읽고 선택을 바꾼 뒤 다시 확인할 수 있어요.'}`;
}
document.querySelectorAll('[data-complete]').forEach(button => button.addEventListener('click', () => {
  const id = button.dataset.complete;
  state.completed = state.completed.includes(id) ? state.completed.filter(x => x !== id) : [...state.completed, id];
  renderProgress(); save();
}));
$('length-slider').addEventListener('input', event => { state.slider = Number(event.target.value); renderSlider(); save(); });
document.querySelectorAll('[data-value]').forEach(button => button.addEventListener('click', () => { state.slider = Number(button.dataset.value); renderSlider(); save(); }));
$('cards-form').addEventListener('change', event => {
  if (!lesson.cards.some(c => c.id === event.target.name)) return;
  state.cards[event.target.name] = event.target.value;
  $(`card-feedback-${event.target.name}`).hidden = true;
  $('cards-summary').textContent = '선택을 저장했어요. 모두 고른 뒤 분류 결과를 확인해 보세요.';
  save();
});
$('exit-form').addEventListener('change', event => {
  if (!lesson.exit.some(q => q.id === event.target.name)) return;
  state.exit[event.target.name] = Number(event.target.value);
  $(`exit-feedback-${event.target.name}`).hidden = true;
  $('exit-summary').textContent = '선택을 저장했어요. 모두 고른 뒤 이해를 확인해 보세요.';
  save();
});
$('cards-form').addEventListener('submit', event => { event.preventDefault(); checkAnswers(lesson.cards, state.cards, 'card', 'cards-summary'); });
$('exit-form').addEventListener('submit', event => { event.preventDefault(); checkAnswers(lesson.exit, state.exit, 'exit', 'exit-summary'); });
$('reset').addEventListener('click', () => { $('reset-confirm').hidden = false; $('reset-yes').focus(); });
$('reset-no').addEventListener('click', () => { $('reset-confirm').hidden = true; $('reset').focus(); });
$('reset-yes').addEventListener('click', () => {
  state = cleanState(null); save(); renderQuestions(); renderSlider(); renderProgress();
  document.querySelectorAll('details').forEach(d => { d.open = false; });
  $('cards-summary').textContent = '8개의 수를 모두 분류해 보세요.';
  $('exit-summary').textContent = '정답보다 중요한 건, 이유를 설명하는 것!';
  $('reset-confirm').hidden = true; $('reset').focus();
});
renderQuestions(); renderSlider(); renderProgress();
$('storage-notice').hidden = storageOK;
