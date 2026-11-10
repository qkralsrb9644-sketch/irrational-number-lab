export const lesson = {
  title: '무리수 탐정단',
  subtitle: '√2의 정체를 밝혀라!',
  standard: '[9수01-08]',
  officialText: '무리수의 개념을 이해하고, 무리수의 유용성을 인식할 수 있다.',
  sourceUrl: 'https://ncic.re.kr/inv/org/download.do?year=2022&seq=10003559&orgType=ogi4',
  stages: [
    { id: 'case', label: '사건 접수', minutes: 5 },
    { id: 'lab', label: '단서 탐구', minutes: 12 },
    { id: 'concept', label: '개념 정리', minutes: 8 },
    { id: 'mission', label: '분류 미션', minutes: 15 },
    { id: 'exit', label: '출구 티켓', minutes: 5 }
  ],
  cards: [
    { id: 'a', value: '√2', answer: 'irrational', why: '제곱해서 2가 되는 양수는 두 정수의 비로 나타낼 수 없는 무리수입니다.' },
    { id: 'b', value: '√4', answer: 'rational', why: '√4 = 2 = 2/1입니다. 근호가 있다고 모두 무리수는 아닙니다.' },
    { id: 'c', value: '−3', answer: 'rational', why: '−3 = −3/1이므로 유리수입니다. 정수는 모두 유리수입니다.' },
    { id: 'd', value: '0.333…', note: '3이 끝없이 반복', answer: 'rational', why: '3이 반복되는 순환소수이며 1/3으로 나타낼 수 있습니다.' },
    { id: 'e', value: '1.414', answer: 'rational', why: '1.414 = 1414/1000입니다. √2의 근삿값일 뿐 √2와 같지는 않습니다.' },
    { id: 'f', value: 'π', answer: 'irrational', why: '원주율 π는 순환하지 않는 무한소수인 무리수입니다. 3.14는 π의 근삿값입니다.' },
    { id: 'g', value: '0', answer: 'rational', why: '0 = 0/1로 나타낼 수 있으므로 유리수입니다.' },
    { id: 'h', value: '√9 / 2', answer: 'rational', why: '√9 / 2 = 3/2입니다. 먼저 근호의 값을 확인하세요.' }
  ],
  exit: [
    { id: 'q1', prompt: '무리수의 소수 표현은?', options: ['유한소수', '순환소수', '순환하지 않는 무한소수'], answer: 2, why: '무리수는 순환하지 않는 무한소수로 나타납니다. 순환소수는 유리수입니다.' },
    { id: 'q2', prompt: '“근호가 있으면 모두 무리수다.” 이 말은?', options: ['맞다', '틀리다'], answer: 1, why: '√4 = 2가 반례입니다. 기호의 모양보다 실제 값을 살펴봐야 합니다.' },
    { id: 'q3', prompt: '한 변이 1 m인 정사각형의 대각선을 정확하게 나타내면?', options: ['1.4 m', '1.414 m', '√2 m'], answer: 2, why: '피타고라스 정리에 따라 대각선의 제곱은 2입니다. √2 m가 정확한 길이이고 소수로 적은 두 값은 근삿값입니다.' }
  ],
  application: {
    prompt: '한 변이 1 m인 정사각형 전시판에 모서리에서 반대쪽 모서리까지 띠를 붙이려고 한다. 띠의 정확한 길이와 소수 둘째 자리까지의 근삿값을 쓰고, 두 표현의 쓰임을 설명하자.',
    answer: '정확한 길이는 √2 m, 소수 둘째 자리까지의 근삿값은 약 1.41 m입니다. √2는 길이를 정확하게 표현하고, 1.41은 실제 측정·비교에 편리합니다. 반올림은 소수 셋째 자리에서 합니다.'
  }
};

export function squareFromThousandths(value) {
  const n = Number(value);
  if (!Number.isInteger(n) || n < 1000 || n > 2000) throw new RangeError('1000~2000 사이의 정수가 필요합니다.');
  const sq = n * n;
  return { length: (n / 1000).toFixed(3), square: (sq / 1000000).toFixed(6), relation: sq < 2000000 ? '<' : sq > 2000000 ? '>' : '=' };
}

export function grade(items, responses) {
  return items.map(item => ({ id: item.id, answered: responses[item.id] !== undefined, correct: responses[item.id] === item.answer }));
}

export function cleanState(raw) {
  const state = { version: 1, completed: [], slider: 1414, cards: {}, exit: {} };
  if (!raw || raw.version !== 1) return state;
  state.completed = [...new Set(Array.isArray(raw.completed) ? raw.completed.filter(id => lesson.stages.some(s => s.id === id)) : [])];
  if (Number.isInteger(raw.slider) && raw.slider >= 1000 && raw.slider <= 2000) state.slider = raw.slider;
  for (const c of lesson.cards) if (['rational', 'irrational'].includes(raw.cards?.[c.id])) state.cards[c.id] = raw.cards[c.id];
  for (const q of lesson.exit) if (Number.isInteger(raw.exit?.[q.id]) && raw.exit[q.id] >= 0 && raw.exit[q.id] < q.options.length) state.exit[q.id] = raw.exit[q.id];
  return state;
}
