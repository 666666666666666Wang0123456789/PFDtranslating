import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os

def extract_text_images_tables(pdf_path, output_image_dir='extracted_images'):
    """
    提取PDF中的文本、图像和表格，并记录它们的位置信息
    :param pdf_path: PDF文件路径
    :param output_image_dir: 提取的图片保存目录
    :return: 文本内容列表、图片文件路径列表、图片位置信息列表、表格内容列表、表格位置信息列表
    """
    doc = fitz.open(pdf_path)
    text_content = []
    image_paths = []
    image_positions = []
    table_content = []
    table_positions = []

    # 创建图片保存目录
    if not os.path.exists(output_image_dir):
        os.makedirs(output_image_dir)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        text_content.append(text)

        # 如果文本为空，尝试使用OCR提取
        if not text.strip():
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img, lang='chi_sim')
            text_content[-1] = text

        # 提取图片
        image_list = page.get_images(full=True)
        for image_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # 保存图片到指定目录
            image_path = os.path.join(output_image_dir, f"page_{page_num + 1}_img_{image_index + 1}.png")
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            image_paths.append(image_path)

            # 获取图片位置信息并转换为以左上角为原点的坐标系
            rect = page.get_image_rects(img)
            if rect:
                x, y, w, h = rect[0]
                y = page.rect.height - y - h  # 转换y坐标为左上角原点
                image_positions.append((x, y, w, h, page_num))
            else:
                image_positions.append(None)

        # 提取表格（简化示例，实际提取表格需要更复杂的逻辑）
        blocks = page.get_text("blocks")
        for block in blocks:
            block_text = block[4]
            # 根据实际需求优化表格识别逻辑
            if "表格" in block_text or "Table" in block_text or "表" in block_text:
                table_content.append(block_text)
                table_positions.append((block[0], block[1], block[2], block[3], page_num))

    return text_content, image_paths, image_positions, table_content, table_positions