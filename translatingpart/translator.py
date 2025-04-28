import fitz
import os
from googletrans import Translator
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Frame

class PDFGenerator:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.styleN = self.styles['Normal']
        self.a4_width, self.a4_height = A4
        
        # 注册中文字体
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(current_dir, 'SIMSUN.ttf')
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"字体文件未找到: {font_path}")
        pdfmetrics.registerFont(TTFont('SimSun', font_path))
        
        self.styleN.fontName = 'SimSun'
        self.styleN.fontSize = 10
        self.styleN.leading = 12
        self.styleN.wordWrap = 'CJK'  # 正确处理中文换行

    def add_translated_frame(self, x, y, width, height, text):
        """添加翻译文本到指定位置的框架"""
        frame = Frame(
            x, 
            y,
            width,
            height,
            leftPadding=0,
            bottomPadding=0,
            rightPadding=0,
            topPadding=0,
            showBoundary=0  # 调试时可开启边界
        )
        para = Paragraph(text, self.styleN)
        frame.addFromList([para], self.c)

    def save(self):
        self.c.save()

class TranslationService:
    def __init__(self):
        self.translator = Translator(service_urls=['translate.google.com'])

    def safe_translate(self, text):
        try:
            return self.translator.translate(text, dest='zh-cn').text
        except Exception as e:
            print(f"翻译失败: {str(e)}")
            return text  # 返回原文作为降级处理

def process_pdf(input_path):
    # 初始化工具
    doc = fitz.open(input_path)
    base_path = os.path.splitext(input_path)[0]
    output_path = f"{base_path}_translated.pdf"
    
    # 初始化PDF生成器
    pdf_gen = PDFGenerator(output_path)
    translator = TranslationService()
    
    # 页面处理循环
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pdf_gen.c.showPage()  # 新建页面
        
        # 获取文本块并处理
        blocks = page.get_text("blocks")
        for block in blocks:
            # PyMuPDF返回的block结构：(x0, y0, x1, y1, "text", block_no, block_type)
            if block[6] != 0:  # 跳过非文本块
                continue
            
            # 坐标转换
            x0, y0_orig, x1, y1_orig = block[:4]
            width = x1 - x0
            height = y1_orig - y0_orig
            
            # 转换为ReportLab坐标系（原点在左下角）
            y_position = pdf_gen.a4_height - y1_orig
            
            # 提取并翻译文本
            raw_text = block[4]
            translated_text = translator.safe_translate(raw_text)
            
            # 添加文本框架
            pdf_gen.add_translated_frame(
                x=x0,
                y=y_position,
                width=width,
                height=height,
                text=translated_text
            )
    
    # 保存最终PDF
    pdf_gen.save()
    print(f"文件已保存至: {output_path}")

# 使用示例
if __name__ == "__main__":
    input_pdf = "/home/left/Downloads/1611.07612v9(1).pdf" 
    process_pdf(input_pdf)