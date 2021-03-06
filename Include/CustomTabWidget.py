from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTabBar, QTabWidget, QPushButton, QWidget
from PyQt5.QtWidgets import QMenu
from Common import makeQAction


class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def tabSizeHint(self, index: int) -> QSize:
        size = super().tabSizeHint(index)
        add_btn_width = 36
        parent_width = self.parent().width()
        if index == self.count() - 1:
            width = add_btn_width
        else:
            width_max = 240
            if (self.count() - 1) * width_max < parent_width:
                width = width_max
            else:
                width = int((parent_width - add_btn_width) / (self.count() - 1))
        return QSize(width, size.height())


class CustomTabWidget(QTabWidget):
    sig_add_tab = pyqtSignal()
    sig_new_window = pyqtSignal(int)
    sig_close = pyqtSignal(int)
    sig_close_others = pyqtSignal(int)
    sig_close_right = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._tabbar = CustomTabBar(self)
        self.setTabBar(self._tabbar)
        self.setMovable(True)

        btn = QPushButton()
        btn.setIcon(QIcon('./Resource/add.png'))
        btn.setFlat(True)
        btn.setFixedSize(16, 16)
        btn.setIconSize(QSize(14, 14))
        btn.clicked.connect(lambda: self.sig_add_tab.emit())

        self._defaultWidget = QWidget()
        self.addTab(self._defaultWidget, '')
        self.tabBar().setTabButton(0, QTabBar.LeftSide, btn)
        self.setTabEnabled(0, False)
        self.tabBar().tabMoved.connect(self.onTabMoved)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        stylesheet = "QTabBar::tab {text-align: left;}"
        self.setStyleSheet(stylesheet)

    def onTabMoved(self):

        index = self.indexOf(self._defaultWidget)
        self.tabBar().moveTab(index, self.count() - 1)

    def showContextMenu(self, point: QPoint):
        if point.isNull():
            return
        index = self.tabBar().tabAt(point)
        menu = QMenu(self)
        menuAddtab = makeQAction(parent=self, text='Add New Tab',
                                 triggered=self.sig_add_tab.emit)
        menu.addAction(menuAddtab)
        menuNewWnd = makeQAction(parent=self, text='Move to New Window',
                                 triggered=lambda: self.sig_new_window.emit(index),
                                 enabled=index >= 0)
        menu.addAction(menuNewWnd)
        menu.addSeparator()
        menuCloseTab = makeQAction(parent=self, text='Close',
                                   triggered=lambda: self.sig_close.emit(index),
                                   enabled=index >= 0)
        menu.addAction(menuCloseTab)
        menuCloseOthers = makeQAction(parent=self, text='Close Others',
                                      triggered=lambda: self.sig_close_others.emit(index),
                                      enabled=index >= 0 and self.count() > 2)
        menu.addAction(menuCloseOthers)
        menuCloseRight = makeQAction(parent=self, text='Close Right-side',
                                     triggered=lambda: self.sig_close_right.emit(index),
                                     enabled=0 <= index < self.count() - 2)
        menu.addAction(menuCloseRight)
        menu.exec(self.tabBar().mapToGlobal(point))