import os
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QWidget, QLineEdit
from PyQt5.QtWidgets import QVBoxLayout,QHBoxLayout, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineHistory, QWebEngineView

class WebView(QWebEngineView):
    def __init__(self , *args, **kwargs):
        super().__init__(*args, **kwargs)

    def release(self):
        self.deleteLater()
        self.close()

    def load(self, *args):
        if isinstance(args[0], QUrl):
            qurl: QUrl = args[0]
            if qurl.isRelative():
                qurl.setScheme('http')
            return super().load(qurl)
        return super().load(*args)

class WebPageWidget(QWidget):
    _is_loading: bool = False
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._editUrl = QLineEdit()
        self._webview = WebView()
        self._btnBackward = QPushButton()
        self._btnForward = QPushButton()
        self._btnRefresh = QPushButton()
        self._ReIcon = QIcon('./Resource/refresh.png')
        self._StopIcon = QIcon('./Resource/stop.png')
        self._btnZoomIn = QPushButton()
        self._btnZoomOut = QPushButton()
        self.initControl()
        self.initLayout()
        

    def release(self):
        self._webview.release()

    def initLayout(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0,4,0,0)
        vbox.setSpacing(4)

        subwidght = QWidget()
        subwidght.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        
        hbox = QHBoxLayout(subwidght)
        #hbox = horizontal box
        
        

        hbox.setContentsMargins(4, 0, 4, 0)
        hbox.setSpacing(4)
        
        #앞 뒤 버튼
        hbox.addWidget(self._btnBackward)
        hbox.addWidget(self._btnForward)
        
        #새로고침 중지
        hbox.addWidget(self._btnRefresh)

        #URL 검색
        hbox.addWidget(self._editUrl)

        #확대, 축소
        hbox.addWidget(self._btnZoomIn)
        hbox.addWidget(self._btnZoomOut)

        vbox.addWidget(subwidght)
        vbox.addWidget(self._webview)

        



    def initControl(self):

        self._editUrl.returnPressed.connect(self.onEditUrlPressed)
        self._webview.loadStarted.connect(self.onWebViewLoadStarted)
        self._webview.loadProgress.connect(self.onWebViewLoadProgress)
        self._webview.loadFinished.connect(self.onWebViewLoadFinished)

        self._btnBackward.setEnabled(False)
        self._btnBackward.clicked.connect(lambda: self._webview.back())
        self._btnBackward.setIcon(QIcon('./Resource/previous.png'))
        self._btnBackward.setFlat(True)
        self._btnBackward.setIconSize(QSize(20, 20))
        self._btnBackward.setFixedSize(QSize(24, 20))
        self._btnForward.setEnabled(False)
        self._btnForward.clicked.connect(lambda: self._webview.forward())
        self._btnForward.setIcon(QIcon('./Resource/forward.png'))
        self._btnForward.setFlat(True)
        self._btnForward.setIconSize(QSize(20, 20))
        self._btnForward.setFixedSize(QSize(24, 20))
        self._btnRefresh.setEnabled(False)

        self._btnRefresh.setEnabled(False)
        self._btnRefresh.clicked.connect(self.onClickBtnRefresh)
        self._btnRefresh.setIcon(self._ReIcon)
        self._btnRefresh.setFlat(True)
        self._btnRefresh.setIconSize(QSize(20,20))
        self._btnRefresh.setFixedSize(QSize(24,20))

        self._btnZoomIn.clicked.connect(self.onClickBtnZoomIn)
        self._btnZoomIn.setIcon(QIcon('./Resource/plus.png'))
        self._btnZoomIn.setFlat(True)
        self._btnZoomIn.setIconSize(QSize(20,20))
        self._btnZoomIn.setFixedSize(QSize(24,20))
        self._btnZoomOut.clicked.connect(self.onClickBtnZoomOut)
        self._btnZoomOut.setIcon(QIcon('./Resource/minus.png'))
        self._btnZoomOut.setFlat(True)
        self._btnZoomOut.setIconSize(QSize(20,20))
        self._btnZoomOut.setFixedSize(QSize(24,20))

    
    def onEditUrlPressed(self):
        url = self._editUrl.text()
        self._webview.load(QUrl(url))


    def onWebViewLoadStarted(self):
        self._is_loading = True
        self._btnRefresh.setEnabled(True)
        self._btnRefresh.setIcon(self._StopIcon)

    def onWebViewLoadProgress(self, progress: int):
        pass

    def onWebViewLoadFinished(self, result: bool):
        url:QUrl = self._webview.url()
        self._editUrl.setText(url.toString())
        history: QWebEngineHistory = self._webview.history()
        self._btnBackward.setEnabled(history.canGoBack())
        self._btnForward.setEnabled(history.canGoForward())
        self._is_loading = False
        self._btnRefresh.setIcon(self._ReIcon)

    def onClickBtnRefresh(self):
        if self._is_loading:
            self._webview.stop()
        else:
            self._webview.reload()

    def onClickBtnZoomIn(self):
        factor = self._webview.zoomFactor()
        self._webview.setZoomFactor(factor + 0.1)
    
    def onClickBtnZoomOut(self):
        factor = self._webview.zoomFactor()
        self._webview.setZoomFactor(factor - 0.1)

#실행코드
if __name__ == '__main__':
    import sys
    from PyQt5.QtCore import QCoreApplication
    from PyQt5.QtWidgets import QApplication

    QApplication.setStyle('fusion')
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    wgt_ = WebPageWidget()
    wgt_.show()
    wgt_.resize(1280,720)

    app.exec_()
    wgt_.release()