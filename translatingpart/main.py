import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from pdf_parser import extract_text_images_tables
from translation_service import TranslationService
from document_generator import generate_result_pdf

class TranslationThread(QThread):
    progress_updated = pyqtSignal(int)
    translation_completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, pdf_path):
        super().__init__()
        self.pdf_path = pdf_path

    def run(self):
        try:
            # 提取PDF内容和位置信息
            text_content, image_paths, image_positions, tables, table_positions = extract_text_images_tables(self.pdf_path)
            if not text_content or all(not text.strip() for text in text_content):
                self.error_occurred.emit("提取的文本为空，请检查PDF文件是否包含文本内容")
                return

            # 初始化翻译服务
            translator = TranslationService()

            # 翻译文本内容
            translated_text = []
            total_pages = len(text_content)
            for i, text in enumerate(text_content):
                translated_text.append(translator.translate(text))
                self.progress_updated.emit(int((i + 1) / total_pages * 50))  # 更新进度条

            # 生成结果PDF
            output_path = "E:/translated_output.pdf"
            generate_result_pdf(translated_text, image_paths, image_positions, tables, table_positions, output_path)
            self.progress_updated.emit(100)
            self.translation_completed.emit(output_path)
        except Exception as e:
            self.error_occurred.emit(f"翻译失败：{str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF翻译工具")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.label = QLabel("请选择PDF文件")
        self.layout.addWidget(self.label)

        self.select_button = QPushButton("选择文件")
        self.select_button.clicked.connect(self.select_file)
        self.layout.addWidget(self.select_button)

        self.translate_button = QPushButton("开始翻译")
        self.translate_button.clicked.connect(self.start_translation)
        self.layout.addWidget(self.translate_button)

        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.pdf_path = None
        self.translation_thread = None

    def select_file(self):
        self.pdf_path, _ = QFileDialog.getOpenFileName(self, "选择PDF文件", "", "PDF Files (*.pdf)")
        if self.pdf_path:
            self.label.setText(f"已选择文件：{self.pdf_path}")

    def start_translation(self):
        if not self.pdf_path:
            self.label.setText("请先选择PDF文件")
            return

        self.translation_thread = TranslationThread(self.pdf_path)
        self.translation_thread.progress_updated.connect(self.update_progress)
        self.translation_thread.translation_completed.connect(self.translation_completed)
        self.translation_thread.error_occurred.connect(self.translation_failed)
        self.translation_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def translation_completed(self, output_path):
        self.label.setText(f"翻译完成，结果已保存到：{output_path}")

    def translation_failed(self, error_message):
        self.label.setText(error_message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())