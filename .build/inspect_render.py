from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parent/'render'
pdf=pdfium.PdfDocument(str(root/'TokenScope_design_v01.pdf'))
thumbs=[]
for i,page in enumerate(pdf):
    img=page.render(scale=1.5).to_pil()
    img.save(root/f'page-{i+1}.png')
    tp=page.get_textpage()
    text=tp.get_text_range()
    (root/f'page-{i+1}.txt').write_text(text,encoding='utf-8')
    clean=[x.strip() for x in text.splitlines() if x.strip()]
    print(i+1,len(text),repr(clean[1:4]),repr(clean[-3:]))
    th=img.copy();th.thumbnail((340,440))
    canvas=Image.new('RGB',(360,470),'#DDE2E6')
    canvas.paste(th,((360-th.width)//2,8))
    ImageDraw.Draw(canvas).text((12,450),str(i+1),fill='black')
    thumbs.append(canvas)
for start in range(0,len(thumbs),6):
    batch=thumbs[start:start+6]
    contact=Image.new('RGB',(1080,470*((len(batch)+2)//3)),'white')
    for j,im in enumerate(batch):contact.paste(im,((j%3)*360,(j//3)*470))
    contact.save(root/f'contact-{start//6+1}.png')
