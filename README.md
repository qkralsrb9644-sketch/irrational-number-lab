# 무리수 탐정단

2027학년도 이후 중학교 3학년의 45분 수업을 위한 정적 웹페이지입니다. 2022 개정 교육과정 `[9수01-08]`을 중심으로, 웹 탐구와 종이 활동지를 함께 사용합니다.

## 실행

Node.js 20 이상에서 별도 설치 없이 실행합니다.

```sh
npm start
npm test
npm run verify
```

미리보기: `http://127.0.0.1:4173/irrational-number-lab/`

## 수업 구성

사건 접수 5분 → 단서 탐구 12분 → 개념 정리 8분 → 분류와 활용 15분 → 출구 티켓 5분. 제곱근, 피타고라스 정리, 유리수와 순환소수를 선수학습으로 합니다.

학생 개인정보나 답안을 서버에 전송하지 않습니다. 진행 상황은 브라우저의 localStorage에만 보관하며 ‘처음부터’에서 지울 수 있습니다. 저장 공간을 사용할 수 없을 때에도 현재 화면의 활동은 작동합니다. 교사용 해설은 공개 자료입니다.

## PDF

- `downloads/learning-guide.pdf`: 개념 학습자료 2쪽
- `downloads/worksheet.pdf`: 학생 활동지 2쪽
- `downloads/teacher-guide.pdf`: 교사용 지도·해설 3쪽
- `downloads/student-set.pdf`: 학습자료 + 활동지 4쪽

웹과 PDF는 `lesson-data.js`의 동일한 문항·정답 데이터를 사용합니다. PDF를 다시 생성하려면 Python과 `reportlab`, `pypdf`가 필요합니다. `PYTHON`으로 Python 실행 파일을 지정하고 `npm run pdf`를 실행합니다. Windows에서는 맑은 고딕을 PDF에 부분 포함하며, 다른 환경은 `PDF_FONT_REGULAR`, `PDF_FONT_BOLD`에 한국어 TTF 파일을 지정할 수 있습니다. 지정하지 않으면 포함된 Gugi 글꼴을 사용합니다. `pypdfium2`, `Pillow`가 있으면 `python scripts/render-pdfs.py`로 전 페이지를 렌더링할 수 있습니다.

## 배포

GitHub 공개 저장소 `qkralsrb9644-sketch/irrational-number-lab`에서 Settings → Pages → Deploy from a branch → `main`, `/(root)`를 선택합니다. 별도 빌드나 서버가 필요하지 않습니다. `.nojekyll`을 포함하고, 에셋은 상대 경로를 사용합니다.

예정 주소: https://qkralsrb9644-sketch.github.io/irrational-number-lab/

## 출처와 글꼴

- 교육부 고시 제2022-33호 [별책 8] 수학과 교육과정, 중학교 수와 연산, `[9수01-08]`. 교육과정 MCP의 공식 원문을 확인하여 설계했습니다.
- [NCIC 원문](https://ncic.re.kr/inv/org/download.do?year=2022&seq=10003559&orgType=ogi4)
- [교육과정 적용 일정](https://www.law.go.kr/admRulInfoP.do?admRulSeq=2100000273516)
- 제목 글꼴: [Gugi](https://github.com/google/fonts/tree/main/ofl/gugi), SIL Open Font License. 라이선스는 `assets/fonts/OFL.txt`에 포함되어 있습니다. 본문은 기기의 한국어 시스템 글꼴을 사용합니다.

수업 발문·활동지·문항·도형은 본 자료를 위해 새로 구성했습니다. 근삿값 탐구를 무리수의 증명으로 설명하지 않으며, 순환소수와 완전제곱수의 제곱근을 반례로 함께 다룹니다.
