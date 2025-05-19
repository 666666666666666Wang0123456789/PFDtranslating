import re
from translate import Translator

class TranslationService:
    def __init__(self):
        self.from_lang = "en"  # 修正为语言代码
        self.to_lang = "zh"
        self.translator = Translator(from_lang=self.from_lang, to_lang=self.to_lang)

    def run(self, text):
        try:
            return self.translator.translate(text)
        except Exception as e:
            print(f"翻译失败: {str(e)}")
            return text  # 返回原文本以避免错误

def process_markdown_file(input_file, output_file):
    """处理Markdown文件并生成翻译后的版本"""
    translate = TranslationService()
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    translated_content = []
    in_code_block = False
    in_math_block = False
    in_table = False
    table_lines = []

    for line in md_content.split('\n'):
        # 处理代码块
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            translated_content.append(line)
            continue
        if in_code_block:
            translated_content.append(line)
            continue

        # 处理数学公式块
        if line.strip().startswith('$$'):
            in_math_block = not in_math_block
            translated_content.append(line)
            continue
        if in_math_block:
            translated_content.append(line)
            continue

        # 处理表格（增强检测逻辑）
        if '|' in line:
            if re.match(r'^\s*\|', line) and re.search(r'\|', line[1:]):
                if not in_table:
                    # 检查是否为表头或分隔线
                    if any('---' in cell for cell in line.split('|')) or (in_table and len(table_lines) == 1):
                        in_table = True
                    else:
                        in_table = True
                table_lines.append(line)
                continue
            elif in_table:
                in_table = False
        else:
            if in_table:
                in_table = False

        if in_table:
            table_lines.append(line)
        else:
            if table_lines:
                translated_content.extend(table_lines)
                table_lines = []

        # 处理图片和链接（优化正则表达式）
        if re.match(r'^!?\[.*?\]:?\(.*?\)|^<.*?>$', line.strip()):
            translated_content.append(line)
            continue

        # 处理普通文本
        if line.strip():
            parts = re.split(r'(`[^`]+`|\$[^$]+\$)', line)
            translated_parts = []
            for part in parts:
                if part and (part.startswith('`') or part.startswith('$')):
                    translated_parts.append(part)
                elif part:
                    translated_parts.append(translate.run(part))
            translated_line = ''.join(translated_parts)
            translated_content.append(translated_line)
        else:
            translated_content.append(line)

    # 处理最后剩余的表格行
    if table_lines:
        translated_content.extend(table_lines)

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(translated_content))

if __name__ == "__main__":
    input_md = "E:/test0512.md"
    output_md = "E:/output_zh.md"
    process_markdown_file(input_md, output_md)
    print(f"翻译完成，结果已保存到 {output_md}")