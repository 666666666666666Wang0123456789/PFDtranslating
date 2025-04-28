import fitz, os
from googletrans import Translator
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Frame

class generator:
    def __init__(self, PATH):
        self.c = canvas.Canvas(PATH, pagesize=A4)
        styles = getSampleStyleSheet()
        self.styleN = styles['Normal']
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(current_dir, 'SIMSUN.ttf')
        pdfmetrics.registerFont(TTFont('SimSun', font_path))
        self.styleN.fontName = 'SimSun'
        self.styleN.fontSize = 12
    
    def run(self, all_text):
        self.c.showPage()
        for x0, x1, y0, y1, text in all_text:
            para = Paragraph(text, self.styleN)
            frame = Frame(x0, x1, y0, y1, showBoundary=1)
            frame.addFromList([para, self.c])

class TranslationService:
    def __init__(self):
        self.translator = Translator()

    def translate(self, text, source_lang="auto", target_lang="zh-cn"):
        try:
            translated = self.translator.translate(text, src=source_lang, dest=target_lang)
            return translated.text
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")

def main(PATH):
    doc = fitz.open(PATH)
    print(PATH)
    base, ext = os.path.splitext(PATH)  # 分离基础路径和扩展名
    PATH = f"{base}(translated).pdf"    # 重新组合
    GT = generator(PATH)
    TS = TranslationService()
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # get the text-block in the page
        blocks = page.get_text("blocks")

        all_text = []

        for block in blocks:
            x0, x1, y0, y1, text, _, Btype = block
            if Btype: continue
            print(text)
            text = TS.translate(text)
            all_text.append([x0, x1, y0, y1, text])
        GT.run(all_text)
    print('*')
    GT.c.save()