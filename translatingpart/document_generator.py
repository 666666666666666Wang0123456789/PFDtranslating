from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def generate_result_pdf(text, image_paths, image_positions, tables, table_positions, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4

    pdfmetrics.registerFont(TTFont('SimSun', "SIMSUN.TTC"))
    c.setFont('SimSun', 12)

    if isinstance(text, list):
        text = '\n'.join(text)

    text_lines = text.split('\n')

    elements = []
    for image_path, position in zip(image_paths, image_positions):
        if position and image_path:
            x, y, w, h, page = position
            elements.append(('image', image_path, x, y, w, h, page))

    for table, table_pos in zip(tables, table_positions):
        if table_pos:
            x, y, w, h, page = table_pos
            elements.append(('table', table, x, y, w, h, page))

    text_elements = []
    current_page_num = 0
    y_position = height - 100
    for line in text_lines:
        text_width = c.stringWidth(line, 'SimSun', 12)
        available_width = width - 200
        if text_width > available_width:
            words = line.split()
            current_line = ""
            for word in words:
                word_width = c.stringWidth(word + " ", 'SimSun', 12)
                if c.stringWidth(current_line + word + " ", 'SimSun', 12) <= available_width:
                    current_line += word + " "
                else:
                    text_elements.append(('text', current_line, 100, y_position, None, None, current_page_num))
                    y_position -= 20
                    current_line = word + " "
                    if y_position < 100:
                        current_page_num += 1
                        y_position = height - 100
            if current_line:
                text_elements.append(('text', current_line, 100, y_position, None, None, current_page_num))
                y_position -= 20
        else:
            text_elements.append(('text', line, 100, y_position, None, None, current_page_num))
            y_position -= 20
        if y_position < 100:
            current_page_num += 1
            y_position = height - 100

    elements.extend(text_elements)
    elements.sort(key=lambda x: (x[6], -x[3]))

    current_page = -1
    current_y = height - 100  # 初始绘制位置

    for element in elements:
        element_type, content, x, y, w, h, page = element

        # 如果页面变化，开始新页面
        if page != current_page:
            c.showPage()
            current_page = page
            current_y = height - 100  # 重置当前绘制位置

        # 如果是图片或表格，计算其高度并检查是否需要换页
        if element_type == 'image':
            with Image.open(content) as img:
                img_width, img_height = img.size
                aspect_ratio = img_height / img_width
                max_image_width = width - 200
                new_width = min(img_width, max_image_width)
                new_height = new_width * aspect_ratio

                # 检查是否需要换页
                if current_y - new_height < 100:
                    c.showPage()
                    current_page += 1
                    current_y = height - 100

                # 绘制图片
                c.drawImage(content, x, current_y - new_height, width=new_width, height=new_height)
                current_y -= new_height  # 更新当前绘制位置

        elif element_type == 'table':
            # 绘制表格边框
            c.rect(x, current_y - h, w, h)

            # 绘制表格内容
            c.setFont('SimSun', 10)
            text_object = c.beginText(x + 5, current_y - h + 15)
            text_object.setFont('SimSun', 10)
            text_object.textLine(content)
            c.drawText(text_object)

            # 更新当前绘制位置
            current_y -= h

        elif element_type == 'text':
            # 绘制文本行
            text_object = c.beginText(x, current_y)
            text_object.setFont('SimSun', 12)
            text_object.textLine(content)
            c.drawText(text_object)
            current_y -= 20  # 更新当前绘制位置

        # 检查是否需要换页
        if current_y < 100:
            c.showPage()
            current_page += 1
            current_y = height - 100

    c.save()