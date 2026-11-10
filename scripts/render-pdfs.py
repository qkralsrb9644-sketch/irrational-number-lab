from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image, ImageOps, ImageDraw
root = Path(__file__).resolve().parents[1]
thumbs=[]
for name in ['learning-guide','worksheet','teacher-guide']:
    pdf=pdfium.PdfDocument(str(root/'downloads'/f'{name}.pdf'))
    for i,page in enumerate(pdf):
        im=page.render(scale=1.5).to_pil().convert('RGB')
        im.save(root/'tmp'/f'{name}-{i+1}.png')
        thumb=ImageOps.contain(im,(450,637))
        cell=Image.new('RGB',(470,675),'#e7e3eb')
        cell.paste(thumb,((470-thumb.width)//2,25))
        ImageDraw.Draw(cell).text((12,8),f'{name} / {i+1}',fill='black')
        thumbs.append(cell)
sheet=Image.new('RGB',(470*4,675*2),'#e7e3eb')
for i,im in enumerate(thumbs): sheet.paste(im,((i%4)*470,(i//4)*675))
sheet.save(root/'tmp/pdf-contact-sheet.png')
print('Rendered 7 unique pages and contact sheet.')
