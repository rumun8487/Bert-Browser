import os
from typing import Union
from PyQt5.QtCore import Qt, QUrl, QSize, QObject, QEvent, pyqtSignal
from PyQt5.QtGui import QIcon, QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineHistory, QWebEnginePage

class WebView(QWebEngineView):

    sig_new_tab = pyqtSignal(QWebEngineView)
    sig_new_window = pyqtSignal(QWebEngineView)

    def __init__(self , *args, **kwargs):
        super().__init__(*args, **kwargs)
        QApplication.instance().installEventFilter(self)
        
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

    def eventFilter(self, a0: 'QObject', a1: 'QEvent') -> bool:
        if a0.parent() == self:
            if a1.type() == QEvent.MouseButtonPress:
                if a1.button() == Qt.BackButton:
                    self.forward()
                elif a1.button() == Qt.BackButton:
                    self.back()
            elif a1.type() == QEvent.Wheel:
                modifier = QApplication.keyboardModifiers()
                if modifier == Qt.ControlModifier:
                    y_angle = a1.angleDelta().y()
                    factor = self.zoomFactor()
                    if y_angle > 0:
                        self.setZoomFactor(factor + 0.1)
                        return True
                    elif y_angle < 0:
                        self.setZoomFactor(factor-0.1)
                        return True
        return False

    def createWindow(self, windowType):
        if windowType == QWebEnginePage.WebBrowserTab:
            view = WebView()
            self.sig_new_tab.emit(view)
            return view
        elif windowType == QWebEnginePage.WebBrowserWindow:
            view = WebView()
            self.sig_new_window.emit(view)
            return view
        # open tab when ctrl key is pressed
        modifier = QApplication.keyboardModifiers()
        if modifier == Qt.ControlModifier:
            view = WebView()
            self.sig_new_tab.emit(view)
            return view
        return QWebEngineView.createWindow(self, windowType)

class WebPageWidget(QWidget):

    _is_loading: bool = False

    sig_page_icon = pyqtSignal(QIcon)
    sig_page_title = pyqtSignal(str)
    sig_new_tab = pyqtSignal(object)
    sig_new_window = pyqtSignal(object)
    sig_close = pyqtSignal(object)

    def __init__(self, parent=None, url: Union[str, QUrl] = 'https://bert-81c5d.web.app/', view: WebView = None):
        super().__init__(parent=parent)
        path_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.getcwd() != path_:
            os.chdir(path_)
        self._editUrl = QLineEdit()
        self._btnBackward = QPushButton()
        self._btnForward = QPushButton()
        self._btnRefresh = QPushButton()
        self._ReIcon = QIcon('./Resource/refresh.png')
        self._StopIcon = QIcon('./Resource/stop.png')
        self._btnZoomIn = QPushButton()
        self._btnZoomOut = QPushButton()
        self._webview = WebView() if view is None else view
        self.initControl()
        self.initLayout()
        self.load(url)
        

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
        self.setWebViewSignals()
        self._webview.titleChanged.connect(lambda x: self.sig_page_title.emit(x))
        self._webview.iconChanged.connect(lambda x: self.sig_page_icon.emit(x))


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
        self._btnZoomIn.setIcon(QIcon('./Resource/zoomin.png'))
        self._btnZoomIn.setFlat(True)
        self._btnZoomIn.setIconSize(QSize(20,20))
        self._btnZoomIn.setFixedSize(QSize(24,20))
        self._btnZoomOut.clicked.connect(self.onClickBtnZoomOut)
        self._btnZoomOut.setIcon(QIcon('./Resource/zoomout.png'))
        self._btnZoomOut.setFlat(True)
        self._btnZoomOut.setIconSize(QSize(20,20))
        self._btnZoomOut.setFixedSize(QSize(24,20))

    def setWebViewSignals(self):
        self._webview.loadStarted.connect(self.onWebViewLoadStarted)
        self._webview.loadProgress.connect(self.onWebViewLoadProgress)
        self._webview.loadFinished.connect(self.onWebViewLoadFinished)
        self._webview.sig_new_tab.connect(self.sig_new_tab.emit)
        self._webview.sig_new_window.connect(self.sig_new_window.emit)


    def load(self, url: Union[str, QUrl]):
        if isinstance(url, QUrl):
            self._webview.load(url)
        else:
            self._webview.load(QUrl(url))

    def onEditUrlPressed(self):
        url = self._editUrl.text()
        self.load(url)


    def onWebViewLoadStarted(self):
        self._is_loading = True
        self._btnRefresh.setEnabled(True)
        self._btnRefresh.setIcon(self._StopIcon)

    def onWebViewLoadProgress(self, progress: int):
        pass

    def onWebViewLoadFinished(self, result: bool):
        self._is_loading = False
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

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        modifier = QApplication.keyboardModifiers()
        if a0.key() == Qt.Key_N:
            if modifier == Qt.ControlModifier:
                self.sig_new_window.emit(None)
        elif a0.key() == Qt.Key_T:
            if modifier == Qt.ControlModifier:
                self.sig_new_tab.emit(None)
        elif a0.key() == Qt.Key_W:
            if modifier == Qt.ControlModifier:
                self.sig_close.emit(self)
        elif a0.key() == Qt.Key_F5:
            self._webview.reload()
        elif a0.key() == Qt.Key_F6:
            self._editUrl.setFocus()
            self._editUrl.selectAll()
        elif a0.key() == Qt.Key_Escape:
            self._webview.stop()
        elif a0.key() == Qt.Key_Backspace:
            self._webview.back()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        pass

    def url(self) -> QUrl:
        return self._webview.url()

    def view(self) -> WebView:
        return self._webview

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