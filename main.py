import sys
import os
from PyQt6.QtCore import QObject, pyqtSlot, QUrl, QTimer, Qt
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from translatingpart import translator

class Bridge(QObject):
    def __init__(self, webview):
        super().__init__()
        self.webview = webview
        self.file_path = ''

    @pyqtSlot()
    def chooseFile(self):
        # 弹出文件选择对话框
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            None, 
            "选择文件", 
            "", 
            "All Files (*)"
        )
        if file_path:
            # 调用JS更新界面
            self.webview.page().runJavaScript(f"updateFilePath('{file_path}')")

    @pyqtSlot()
    def startTranslate(self):
        # 模拟翻译过程（实际开发中替换为真实逻辑）
        print("开始翻译...")
        translator.main(self.file_path)
        
        # 延迟2秒模拟处理
        QTimer.singleShot(2000, lambda: 
            self.webview.page().runJavaScript("showComplete()")
        )

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