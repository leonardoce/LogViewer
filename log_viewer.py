import codecs
import sys
import os
import os.path
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.model = LogViewerModel()
        self.__create_gui()

    def __create_gui(self):
        # Basic GUI Properties
        self.resize(500, 500)
        self.statusBar().showMessage("Ready")

        # Actions
        openIcon = QIcon.fromTheme("document-open", QIcon("document-open.png"))
        exitIcon = QIcon.fromTheme("application-exit", QIcon("application-exit.png"))
        
        openAction = QAction(openIcon, "&Open", self)
        openAction.setShortcut("Ctrl-O")
        openAction.setStatusTip("Open a log file")
        openAction.triggered.connect(self.__open_file)

        exitAction = QAction(exitIcon, "&Exit", self)
        exitAction.setShortcut("Ctrl-X")
        exitAction.setStatusTip("Exit from the application")
        exitAction.triggered.connect(self.close)

        debugMessages = self.__create_toggle_for_level("debug")
        infoMessages = self.__create_toggle_for_level("info")
        errorMessages = self.__create_toggle_for_level("error")
        warningMessages = self.__create_toggle_for_level("warning")
        panicMessages = self.__create_toggle_for_level("panic")

        logFileLimitAction2MB = self.__create_action_for_file_limit(2)
        logFileLimitAction4MB = self.__create_action_for_file_limit(4)
        logFileLimitAction8MB = self.__create_action_for_file_limit(8)

        # Toolbar
        toolbar = self.addToolBar("main")
        toolbar.addAction(openAction)
        toolbar.addAction(exitAction)
        toolbar.addSeparator()
        toolbar.addAction(debugMessages)
        toolbar.addAction(infoMessages)
        toolbar.addAction(warningMessages)
        toolbar.addAction(errorMessages)
        toolbar.addAction(panicMessages)

        # MenuBar
        menubar = self.menuBar()
        
        menu_file = menubar.addMenu("&File")
        menu_file.addAction(openAction)
        menu_file.addSeparator()
        menu_file.addAction(exitAction)

        menu_levels = menubar.addMenu("&Levels")
        menu_levels.addAction(debugMessages)
        menu_levels.addAction(infoMessages)
        menu_levels.addAction(warningMessages)
        menu_levels.addAction(errorMessages)
        menu_levels.addAction(panicMessages)

        menu_settings = menubar.addMenu("&Settings")
        menu_settings.addAction(logFileLimitAction2MB)
        menu_settings.addAction(logFileLimitAction4MB)
        menu_settings.addAction(logFileLimitAction8MB)
        
        # List
        self.__list = QListWidget()
        self.setCentralWidget(self.__list)

        self.__refresh()

    def __create_toggle_for_level(self, level_name):
        result = QAction("&" + level_name.capitalize(), self)
        result.setCheckable(True)
        result.setChecked(self.model.is_level_enabled(level_name))
        result.triggered.connect(lambda evt: self.__toggle_level(level_name))
        return result

    def __create_action_for_file_limit(self, limit_mb):
        result = QAction("Log file limit &%sMB" % (str(limit_mb),), self)
        result.triggered.connect(lambda evt: self.__toggle_limit(limit_mb))
        return result
    
    def __toggle_level(self, level_name):
        self.model.toggle_level(level_name)
        self.__refresh()

    def __toggle_limit(self, limit_mb):
        self.model.bytes_limit = limit_mb * 1024 * 1024
        self.__refresh()
        
    def __open_file(self, evt):
        """
        Action that opens a log file
        """
        logFileName = str(QFileDialog.getOpenFileName(self, "Open log file"))
        if len(logFileName.strip())>0 and os.path.exists(logFileName):
            self.model.current_file = logFileName
            self.model.refresh()
            self.__refresh()

    def __refresh(self):
        """
        Refresh the GUI from the model
        """
        self.__list.clear()
        self.statusBar().showMessage(self.model.status_bar)
        self.setWindowTitle(self.model.title)

        for line in self.model.lines:
            w = QListWidgetItem(line["text"])
            w.setBackground(QBrush(QColor(line["color"])))
            self.__list.addItem(w)

    def __set_filter(self, evt):
        pass
            
class LogViewerLevel(object):
    def __init__(self, tags, enabled, color):
        self.tags = tags
        self.enabled = enabled
        self.color = color

    def matches_line(self, line):
        for t in self.tags:
            if t in line: return True

        return False

class LogViewerModel(object):
    def __init__(self):
        self.current_file = None
        self.levels = {"debug": LogViewerLevel(["DEBUG"], False, "#FFFFFF"),
                       "info": LogViewerLevel(["INFO"], False, "#FFFFFF"),
                       "warning": LogViewerLevel(["WARNING", "ATTENZIONE"], True, "#FFFED9"),
                       "error": LogViewerLevel(["ERROR"], True, "#FFB0D4"),
                       "panic": LogViewerLevel(["PANIC"], True, "#FF4096")}
        self.__bytes_limit = 2 * 1024 * 1024
        self.refresh()

    @property
    def bytes_limit(self):
        return self.__bytes_limit

    @bytes_limit.setter
    def bytes_limit(self, value):
        self.__bytes_limit = value
        self.refresh()
    
    def is_level_enabled(self, level_name):
        return self.levels[level_name].enabled

    def toggle_level(self, level_name):
        self.levels[level_name].enabled = not self.levels[level_name].enabled
        self.refresh()

    def refresh(self):
        if not self.current_file:
            self.status_bar = "Ready"
            self.title = "Log file viewer"
            self.lines = []
            return

        if not os.path.exists(self.current_file):
            self.status_bar = "File %s doesn't exist" % (self.current_file,)
            return

        self.status_bar = "Current file: %s" % (self.current_file,)
        self.title = "Log file viewer: %s" % (self.current_file,)
        with codecs.open(self.current_file, "r", "utf-8", "ignore") as f:
            self.__repos_file(f)
            self.__read_lines_from(f)

    def __repos_file(self, f):
        f.seek(0, 2)
        size = f.tell()
        if size > self.bytes_limit: pos = size - self.bytes_limit
        else: pos = 0
        f.seek(pos)

    def __color_for(self, line):
        for v in self.levels.values():
            if v.enabled and v.matches_line(line): return v.color
        return ""

    def __read_lines_from(self, f):
        self.lines = []
        for line in f:
            color = self.__color_for(line)
            if color: self.lines.append({"text": line.strip(), "color":color})

        self.lines.reverse()
        
        
def __main__():
    a = QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    sys.exit(a.exec_())

if __name__=="__main__": __main__()
