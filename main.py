import sys
import os
from PyQt6.QtCore import QObject, pyqtSlot, QUrl, QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PDF_TO_MD import pdf_to_md
from translatemd import process_markdown_file

class TranslateWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            md_path = pdf_to_md(self.file_path)
            process_markdown_file(md_path)
        except Exception as e:
            print(str(e))
        self.finished.emit()

class Bridge(QObject):
    def __init__(self, webview):
        super().__init__()
        self.webview = webview
        self.file_path = ''

    @pyqtSlot()
    def chooseFile(self):
        # 弹出文件选择对话框
        file_dialog = QFileDialog()
        self.file_path, _ = file_dialog.getOpenFileName(
            None, 
            "选择文件", 
            "", 
            "All Files (*)"
        )
        if self.file_path:
            # 调用JS更新界面
            self.webview.page().runJavaScript(f"updateFilePath('{self.file_path}')")

    @pyqtSlot()
    def startTranslate(self):
        print('&&')
        self.thread = QThread()
        self.worker = TranslateWorker(self.file_path)
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.thread.deleteLater)
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.translateFinished)

        self.thread.start()

    def translateFinished(self):
        self.webview.page().runJavaScript("showComplete()")

    @pyqtSlot()
    def Exit(self):
        exit()

class MainWindow(QWebEngineView):
    def __init__(self):
        super().__init__()
        
        # 配置WebChannel
        self.channel = QWebChannel()
        self.bridge = Bridge(self)
        self.channel.registerObject('bridge', self.bridge)
        self.page().setWebChannel(self.channel)
        
        # 加载本地HTML
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(current_dir, "index.html")
        self.load(QUrl.fromLocalFile(html_path))
        
        # 窗口设置
        self.setWindowTitle("HTML翻译工具")
        self.setMinimumSize(1280, 720)
        self.setMaximumSize(1280, 720)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())