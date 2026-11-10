"""Create the four A4 learning PDFs from the website's shared lesson data."""
import json, os, sys, shutil
from pathlib import Path
from html import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads(sys.stdin.read())
OUT = ROOT / 'output/pdf'
OUT.mkdir(parents=True, exist_ok=True)
(ROOT / 'downloads').mkdir(exist_ok=True)
body = Path(os.environ.get('PDF_FONT_REGULAR', 'C:/Windows/Fonts/malgun.ttf'))
bold = Path(os.environ.get('PDF_FONT_BOLD', 'C:/Windows/Fonts/malgunbd.ttf'))
if not body.exists():
    body = ROOT / 'assets/fonts/Gugi-Regular.ttf'
if not bold.exists():
    bold = body
pdfmetrics.registerFont(TTFont('Body', str(body)))
pdfmetrics.registerFont(TTFont('Bold', str(bold)))
pdfmetrics.registerFont(TTFont('Display', str(ROOT / 'assets/fonts/Gugi-Regular.ttf')))
math_font = Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/share/fonts/DejaVuSans.ttf'
if not math_font.exists():
    math_font = Path(os.environ.get('PDF_FONT_MATH', 'C:/Windows/Fonts/seguisym.ttf'))
pdfmetrics.registerFont(TTFont('Math', str(math_font)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold', italic='Body', boldItalic='Bold')
W, H = A4
M = 42
CW = W - M * 2
INK = '#30273d'
MUTED = '#696273'
PURPLE = '#6840af'
PALE = '#f1edf7'
LINE = '#d9d2e1'
LIME = '#eaf2d5'
audit = []

def rect(c, x, y, w, h, fill='#ffffff', stroke=LINE, radius=8):
    c.setFillColor(HexColor(fill)); c.setStrokeColor(HexColor(stroke)); c.setLineWidth(.65)
    c.roundRect(x, H-y-h, w, h, radius, fill=1, stroke=1)

def text(c, s, x, y, size=10, color=INK, font='Body'):
    c.setFillColor(HexColor(color))
    for ch in s:
        chosen = font if ord(ch) in pdfmetrics.getFont(font).face.charToGlyph else 'Math'
        assert ord(ch) in pdfmetrics.getFont(chosen).face.charToGlyph, f'Missing glyph: {ch}'
        c.setFont(chosen,size); c.drawString(x,H-y-size,ch)
        x += pdfmetrics.stringWidth(ch,chosen,size)

def para(c, s, x, y, w=CW, size=10, leading=16, color=INK, bold=False):
    for char in ['−','≈']:
        s = s.replace(char, '<font name="Math">'+char+'</font>')
    style = ParagraphStyle('p', fontName='Bold' if bold else 'Body', fontSize=size, leading=leading,
        textColor=HexColor(color), wordWrap='CJK', spaceAfter=0)
    p = Paragraph(s, style); _, h = p.wrap(w, 1000)
    if y+h > H-44:
        raise ValueError(f'Page overflow at {y}: {s[:60]}')
    p.drawOn(c, x, H-y-h)
    audit.append({'page': c.getPageNumber(), 'top': y, 'bottom': y+h, 'text': s[:65]})
    return y+h

def heading(c, number, title, y):
    text(c, number, M, y+3, 10, PURPLE, 'Bold')
    text(c, title, M+29, y, 15, INK, 'Bold')
    return y+30

def header(c, kind, title, subtitle, page, total):
    c.setTitle(f'무리수 탐정단 - {kind}'); c.setAuthor('무리수 탐정단 수업자료')
    text(c, 'MATH DETECTIVE LAB  /  CASE 01', M, 25, 8, PURPLE, 'Bold')
    text(c, kind, W-M-95, 25, 8, MUTED)
    text(c, title, M, 53, 24, INK, 'Display')
    text(c, subtitle, M, 94, 9, MUTED)
    c.setStrokeColor(HexColor(LINE)); c.line(M, H-119, W-M, H-119)
    c.line(M, 36, W-M, 36)
    text(c, '무리수 탐정단 · 중학교 3학년 · 2022 개정 교육과정', M, H-29, 7, MUTED)
    text(c, f'{page} / {total}', W-M-24, H-29, 7, MUTED)

def lines(c, x, y, w, count=2, gap=23):
    c.setStrokeColor(HexColor('#b9b1c4')); c.setLineWidth(.5)
    for n in range(count): c.line(x, H-y-n*gap, x+w, H-y-n*gap)

def square(c, x, y, side=125, label='√2 m'):
    rect(c, x, y, side, side, PALE, '#8a70af', 0)
    c.setStrokeColor(HexColor(PURPLE)); c.setLineWidth(2); c.setDash(5,3)
    c.line(x, H-y-side, x+side, H-y); c.setDash()
    c.setLineWidth(.7); c.line(x, H-y-side+14, x+14, H-y-side+14); c.line(x+14,H-y-side+14,x+14,H-y-side)
    text(c, '1 m', x+side/2-10, y+side+6, 10)
    text(c, '1 m', x-28, y+side/2-5, 10)
    text(c, label, x+side*.48, y+side*.38, 13, PURPLE, 'Bold')

def table(c, headers, rows, widths, y, row_h=34, font_size=9):
    xs = [M]
    for w in widths: xs.append(xs[-1]+w)
    total_h = row_h*(len(rows)+1)
    rect(c, M, y, sum(widths), total_h, '#ffffff', LINE, 0)
    c.setFillColor(HexColor(PALE)); c.rect(M,H-y-row_h,sum(widths),row_h,fill=1,stroke=0)
    c.setStrokeColor(HexColor(LINE)); c.setLineWidth(.5)
    for i, row in enumerate([headers]+rows):
        for j, val in enumerate(row):
            para(c, escape(str(val)), xs[j]+8, y+i*row_h+8, widths[j]-16, font_size, 13, bold=i==0)
        if i: c.line(M,H-y-i*row_h,M+sum(widths),H-y-i*row_h)
    for x in xs[1:-1]: c.line(x,H-y,x,H-y-total_h)
    return y+total_h

def build_learning():
    c=canvas.Canvas(str(OUT/'learning-guide.pdf'),pagesize=A4)
    header(c,'개념 학습자료','분수로는 잡히지 않는 수, √2','수사 목표: 무리수를 구분하고, 정확한 길이를 표현할 때의 유용성을 설명한다.',1,2)
    rect(c,M,136,CW,57,LIME,'#d3ddb9')
    para(c,'<b>오늘의 질문</b><br/>한 변이 1 m인 정사각형의 대각선 길이를 정확하게 나타내려면 어떤 수가 필요할까?',M+15,146,CW-30,10,16)
    heading(c,'01','모양에서 시작하는 수사',215)
    square(c,89,263,138)
    para(c,'피타고라스 정리를 적용하면<br/><b>x² = 1² + 1² = 2</b><br/><br/>길이는 양수이므로 <b>x = √2</b>.<br/>√2 m는 이 대각선의 정확한 길이다.<br/>이 수는 두 정수의 비로 나타낼 수 없다.',281,267,228,11,21)
    heading(c,'02','두 수 사이에서 단서 찾기',443)
    table(c,['작은 수의 제곱','큰 수의 제곱','찾아낸 범위'],[
        ['1.4² = 1.96','1.5² = 2.25','1.4 < √2 < 1.5'],
        ['1.41² = 1.9881','1.42² = 2.0164','1.41 < √2 < 1.42'],
        ['1.414² = 1.999396','1.415² = 2.002225','1.414 < √2 < 1.415']
    ],[CW*.32,CW*.32,CW*.36],477,38)
    rect(c,M,651,CW,80,PALE)
    para(c,'<b>탐정의 주의 사항</b><br/>√2 ≈ 1.414이지만 √2 = 1.414는 아니다. 계산기 화면의 소수 몇 자리만 보고 순환 여부를 판단할 수 없다. 이 탐구는 근삿값을 찾는 활동이며, √2가 무리수임을 증명한 것은 아니다.',M+15,664,CW-30,10,17)
    c.showPage()
    header(c,'개념 학습자료','정체 확인! 유리수와 무리수','두 정수의 비로 나타낼 수 있는지 확인하고, 기호보다 실제 값을 살펴보자.',2,2)
    rect(c,M,138,CW,65,PALE)
    para(c,'<b>무리수</b>는 두 정수 a, b의 비 a/b (b ≠ 0)로 나타낼 수 없는 수이다.<br/>소수로 나타내면 <b>순환하지 않는 무한소수</b>가 된다. 예: √2, √3, π',M+15,151,CW-30,11,20)
    heading(c,'03','두 종류의 수를 비교하기',225)
    table(c,['분류','유리수','무리수'],[
        ['분수로 표현','두 정수의 비로 나타낼 수 있다.','두 정수의 비로 나타낼 수 없다.'],
        ['소수 표현','유한소수 또는 순환소수','순환하지 않는 무한소수'],
        ['예','−3, 0, 1/2, √4','√2, √3, π']
    ],[72,(CW-72)/2,(CW-72)/2],258,46,9)
    para(c,'<b>실수</b>는 유리수와 무리수를 합친 수 전체이다. 두 종류에 동시에 속하는 수는 없다.',M,458,CW,10,17)
    heading(c,'04','흔한 오해를 점검하기',500)
    y=535
    for claim, correction in [
        ('근호가 있으면 모두 무리수다?','√4 = 2이므로 유리수이다. 실제 값을 먼저 확인한다.'),
        ('무한소수는 모두 무리수다?','0.333…은 3이 반복되는 순환소수로, 1/3과 같다.'),
        ('√2와 1.414는 같은 수다?','1.414는 유한소수인 유리수이며, √2의 근삿값이다.')]:
        text(c,claim,M,y,10,INK,'Bold');para(c,correction,M,y+20,CW,10,16,MUTED);y+=63
    rect(c,M,734,CW,42,LIME,'#d3ddb9')
    para(c,'<b>왜 필요할까?</b> √2는 길이를 정확하게 표현하고, 근삿값은 실제 측정과 비교에 편리하다.',M+12,745,CW-24,9,14)
    c.save()

def build_worksheet():
    c=canvas.Canvas(str(OUT/'worksheet.pdf'),pagesize=A4)
    header(c,'학생 활동지','무리수 탐정단 · 수사 기록','3학년 ____반  ____번  이름 ________________    모둠 ____________',1,2)
    heading(c,'01','사건 접수 | 나의 첫 추측 (5분)',138)
    square(c,84,183,106,'? m')
    para(c,'한 변이 1 m인 정사각형의 대각선 길이를 예상해 보자.<br/>① 1 m, 2 m와 비교하면?<br/>② 피타고라스 정리를 이용한 식은?<br/>③ 이 길이를 분수로 정확히 쓸 수 있을까?',235,181,275,10,22)
    text(c,'나의 추측과 이유',M,323,10,INK,'Bold');lines(c,M,363,CW,2,26)
    heading(c,'02','단서 탐구 | 제곱해서 2에 가까워지기 (12분)',420)
    para(c,'웹 탐구실에서 값을 선택하고 제곱값을 기록하자. 두 양수의 제곱과 2를 비교하여 √2가 있는 범위를 찾아보자.',M,452,CW,9,16)
    table(c,['작은 수','제곱값','큰 수','제곱값','√2가 있는 범위'],[
      ['1.4','','1.5','','____ < √2 < ____'],
      ['1.41','','1.42','','____ < √2 < ____'],
      ['1.414','','1.415','','____ < √2 < ____']
    ],[57,92,57,92,CW-298],497,42)
    para(c,'계산기에 1.414…이 보인다는 사실만으로 무리수임을 증명했다고 말할 수 있을까? 이유도 적어 보자.',M,683,CW,10,17)
    lines(c,M,737,CW,2,26)
    c.showPage()
    header(c,'학생 활동지','정체 분류 · 사건 종결','분류의 근거를 적고, 짝에게 설명한 다음 웹에서 확인해 보자.',2,2)
    heading(c,'03','개념 정리 (8분)',136)
    para(c,'무리수는 두 정수의 비로 나타낼 수 ( 있는 / 없는 ) 수이다.<br/>소수로 나타내면 ________________________________ 이다.',M,167,CW,10,21)
    heading(c,'04','분류 미션과 생활 속 적용 (15분)',224)
    rows=[]
    for card in DATA['cards']:
        label=card['value']+ (' (3 반복)' if card.get('note') else '')
        rows.append([label,'유리수 / 무리수',''])
    table(c,['수','분류에 ○ 표시','판단한 이유'],rows,[132,106,CW-238],257,27,9)
    para(c,escape(DATA['application']['prompt']),M,513,CW,9,15)
    text(c,'정확한 길이: ____________  근삿값: ____________',M,562,10)
    text(c,'두 표현의 쓰임:',M,590,9);lines(c,M+85,606,CW-85,1)
    heading(c,'05','출구 티켓 (5분)',629)
    y=661
    for i,q in enumerate(DATA['exit']):
        # Same prompt and options as the website, compactly laid out for handwriting.
        y=para(c,f"<b>{i+1}. {escape(q['prompt'])}</b>",M,y,CW,8.2,12)
        opts='   /   '.join(f'{j+1}) {o}' for j,o in enumerate(q['options']))
        y=para(c,escape(opts),M+12,y+2,CW-12,8.2,12)+6
    para(c,'한 문장 정리: 무리수는 __________이고, __________할 때 유용하다.',M,778,CW,8,12)
    c.save()

def build_teacher():
    c=canvas.Canvas(str(OUT/'teacher-guide.pdf'),pagesize=A4)
    header(c,'교사용 지도·해설','45분 수업 운영 가이드','2027학년도 이후 중학교 3학년 · 웹 탐구 + 종이 활동지',1,3)
    rect(c,M,137,CW,74,PALE)
    para(c,f"<b>{DATA['standard']}</b> {DATA['officialText']}<br/>목표: 무리수를 구분하고, 정확한 길이를 나타내는 데 필요한 이유를 자신의 말로 설명한다.",M+14,151,CW-28,10,18)
    heading(c,'01','수업 준비',233)
    para(c,'<b>준비물:</b> 교사 화면 또는 모둠별 기기, 학생용 세트 4쪽, 필기도구.<br/><b>선수학습:</b> 제곱근의 뜻, 피타고라스 정리, 유리수와 순환소수.<br/><b>활동 방식:</b> 개인 추측 → 짝·모둠 탐구 → 개인 정리. 기기가 없으면 학습자료의 표를 이용한다.',M,267,CW,10,20)
    heading(c,'02','시간별 지도 흐름',352)
    table(c,['단계','핵심 활동·교사 발문','관찰할 학습 증거'],[
      ['접수 5분','1 m 정사각형의 대각선 예상하기.\n“길이의 제곱은 얼마일까?”','1 < x < 2, x² = 2를\n말이나 식으로 설명한다.'],
      ['탐구 12분','슬라이더로 양쪽 경계를 좁히기.\n“어느 두 값 사이에 있을까?”','제곱값과 2를 비교하여\n세 가지 범위를 기록한다.'],
      ['정리 8분','유리수·무리수의 정의 비교.\n“0.333…은 왜 유리수일까?”','순환 여부와 정수의 비를\n연결하여 설명한다.'],
      ['분류 15분','8개 수 분류 8분, 이유 비교 4분,\n대각선 활용 3분.','√4, 1.414를 유리수로\n분류하고 이유를 말한다.'],
      ['출구 5분','혼자 3문항 풀이 및 한 문장 정리.\n오답에 따라 다음 수업 준비.','무리수의 정의와 유용성을\n자신의 말로 설명한다.']
    ],[64,244,CW-308],385,60,9)
    para(c,'진행 표시는 학습자가 직접 체크한다. 자동 채점은 선택형만 제공한다. 서술형은 교사가 근거를 확인하고 피드백한다. 공동 기기 사용 후에는 ‘처음부터’로 초기화한다.',M,762,CW,8.5,14,MUTED)
    c.showPage()
    header(c,'교사용 지도·해설','정답보다, 판단의 근거','공개 해설입니다. 학생용 세트와 분리하여 수업 중 필요한 시점에 활용하세요.',2,3)
    heading(c,'03','탐구 기록과 분류 미션 정답',137)
    para(c,'<b>도입:</b> 1 < x < 2, x² = 1² + 1² = 2, x = √2 (x > 0).<br/><b>탐구:</b> 1.4² = 1.96, 1.5² = 2.25 / 1.41² = 1.9881, 1.42² = 2.0164 / 1.414² = 1.999396, 1.415² = 2.002225.<br/><b>범위:</b> 1.4 < √2 < 1.5 → 1.41 < √2 < 1.42 → 1.414 < √2 < 1.415.<br/><b>개념 빈칸:</b> 없는 / 순환하지 않는 무한소수.',M,172,CW,9.5,18)
    rows=[[c['value'], '유리수' if c['answer']=='rational' else '무리수', c['why']] for c in DATA['cards']]
    table(c,['수','분류','핵심 근거'],rows,[69,56,CW-125],288,43,9)
    heading(c,'04','생활 속 적용 예시 답안',694)
    para(c,escape(DATA['application']['answer']),M,729,CW,9.5,17)
    c.showPage()
    header(c,'교사용 지도·해설','오개념을 발견하는 피드백','정답 개수와 함께, 판단의 근거와 정확한 값·근삿값의 구분을 살펴보세요.',3,3)
    heading(c,'05','출구 티켓 정답과 피드백',137)
    y=173
    for i,q in enumerate(DATA['exit']):
        y=para(c,f"<b>{i+1}. {escape(q['options'][q['answer']])}</b> - {escape(q['why'])}",M,y,CW,10,18)+13
    heading(c,'06','이렇게 되물어 보세요',323)
    y=360
    for a,b in [
      ('“근호가 있으니까 무리수예요.”','“√4를 계산하면 무엇이 되지? 정수도 분수로 쓸 수 있을까?”'),
      ('“끝이 없으니까 무리수예요.”','“0.333… = 1/3을 떠올려 볼까? 반복되는 부분이 있니?”'),
      ('“계산기에 나왔으니 증명했어요.”','“화면에 보이지 않는 뒤쪽 자리까지 확인한 걸까?”'),
      ('“√2는 1.414예요.”','“1.414를 제곱하면 정확히 2가 되니? =와 ≈ 중 무엇을 쓸까?”')]:
        y=para(c,f'<b>{a}</b><br/>{b}',M,y,CW,9.5,18)+12
    rect(c,M,591,CW,69,LIME,'#d3ddb9')
    para(c,'<b>형성평가 기준</b><br/>도달: 분류의 근거와 무리수의 유용성을 모두 설명한다.<br/>보완: 근호·무한소수의 모양만으로 분류하거나 정확한 값과 근삿값을 혼동한다. 해당 반례를 다시 비교하게 한다.',M+13,602,CW-26,9,15)
    para(c,'<b>출처와 지도 근거</b><br/>교육부 고시 제2022-33호 [별책 8] 수학과 교육과정, [9수01-08] (PDF 39쪽, MCP 원문 확인). [별책 3] 중학교 교육과정 186쪽의 해설·고려 사항은 생활 속 무리수의 유용성, 실수의 구성, 피타고라스 정리와 정사각형 대각선을 통한 직관적 도입, 계산기 활용을 제시한다. 본 자료의 발문·문항·평가 기준은 이를 바탕으로 새로 구성했다.',M,683,CW,8,13,MUTED)
    para(c,'<link href="'+DATA['sourceUrl']+'" color="#6840af">NCIC 수학과 교육과정 원문 열기</link> · <link href="https://www.law.go.kr/admRulInfoP.do?admRulSeq=2100000273516" color="#6840af">교육과정 적용 일정 확인</link>',M,758,CW,8,13)
    c.save()

build_learning();build_worksheet();build_teacher()
writer=PdfWriter()
for filename in ['learning-guide.pdf','worksheet.pdf']:
    writer.append(str(OUT/filename))
writer.add_metadata({'/Title':'무리수 탐정단 - 학생용 세트','/Author':'무리수 탐정단 수업자료'})
with open(OUT/'student-set.pdf','wb') as f: writer.write(f)
expected={'learning-guide.pdf':2,'worksheet.pdf':2,'teacher-guide.pdf':3,'student-set.pdf':4}
for name,count in expected.items():
    reader=PdfReader(OUT/name)
    assert len(reader.pages)==count,(name,len(reader.pages))
    assert all('무리수' in p.extract_text() for p in reader.pages),name
    shutil.copy2(OUT/name,ROOT/'downloads'/name)
    print(f'{name}: {count} A4 pages; {len((OUT/name).read_bytes())} bytes')
(ROOT/'tmp').mkdir(exist_ok=True)
(ROOT/'tmp/pdf-layout-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
