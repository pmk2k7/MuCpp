import os
import re
import sys
import time
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import QSize, Qt, QThread, Signal
from PySide6.QtGui import (
    QAction,
    QColor,
    QFont,
    QIcon,
    QKeySequence,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from compiler import CompilationResult, CompilerManager, Diagnostic
from dialogs import (
    CompilerOptionsDialog,
    FindReplaceDialog,
    GotoLineDialog,
    NewProjectDialog,
)
from editor import CodeEditor
from project import Project
from icons import get_icon, get_app_icon


class CompileWorker(QThread):
    """Background thread to execute compiler without freezing the UI."""
    finished_signal = Signal(CompilationResult)

    def __init__(self, compiler_mgr: CompilerManager, sources: List[str], output_exe: str, is_cxx: bool):
        super().__init__()
        self.compiler_mgr = compiler_mgr
        self.sources = sources
        self.output_exe = output_exe
        self.is_cxx = is_cxx

    def run(self):
        res = self.compiler_mgr.compile(self.sources, self.output_exe, self.is_cxx)
        self.finished_signal.emit(res)


class MuCppMainWindow(QMainWindow):
    """Fast, modern C/C++ IDE in Python with PySide6."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MuCpp IDE")
        self.setWindowIcon(get_app_icon())
        self.resize(1100, 750)

        self.compiler_mgr = CompilerManager()
        self.current_project: Optional[Project] = None
        self.last_compiled_exe: Optional[str] = None
        self.compile_worker: Optional[CompileWorker] = None

        self.init_ui()
        self.init_menus()
        self.init_toolbar()
        self.init_statusbar()

        # Open a default initial file
        self.new_source_file()

    def init_ui(self):
        # Main Splitter: Left Sidebar vs Editor + Bottom Panel
        self.main_splitter = QSplitter(Qt.Horizontal, self)
        self.setCentralWidget(self.main_splitter)

        # 1. Left Sidebar
        self.sidebar_tabs = QTabWidget()
        self.sidebar_tabs.setTabPosition(QTabWidget.West)

        # Project tree
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabel("Project Files")
        self.project_tree.itemDoubleClicked.connect(self.on_tree_item_double_clicked)
        self.sidebar_tabs.addTab(self.project_tree, "Project")

        # Symbols / Classes tree
        self.symbols_tree = QTreeWidget()
        self.symbols_tree.setHeaderLabel("Classes & Functions")
        self.symbols_tree.itemDoubleClicked.connect(self.on_symbol_double_clicked)
        self.sidebar_tabs.addTab(self.symbols_tree, "Classes")

        self.main_splitter.addWidget(self.sidebar_tabs)

        # 2. Right Vertical Splitter (Editor Tabs + Bottom Panel)
        self.right_splitter = QSplitter(Qt.Vertical)

        # Central Editor Tabs
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setMovable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)
        self.editor_tabs.currentChanged.connect(self.on_tab_changed)
        self.right_splitter.addWidget(self.editor_tabs)

        # Bottom Panel Tabs (Compiler Log, Issues Table, Runner)
        self.bottom_tabs = QTabWidget()

        # Compile Log Tab
        self.compile_log = QPlainTextEdit()
        self.compile_log.setReadOnly(True)
        log_font = QFont("Consolas", 10)
        self.compile_log.setFont(log_font)
        self.bottom_tabs.addTab(self.compile_log, "Compile Log")

        # Compiler Issues Tab
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(5)
        self.issues_table.setHorizontalHeaderLabels(["Severity", "Line", "Col", "Message", "File"])
        self.issues_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.issues_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.issues_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.issues_table.cellDoubleClicked.connect(self.on_issue_double_clicked)
        self.bottom_tabs.addTab(self.issues_table, "Issues / Diagnostics")

        # Program Output Tab
        self.program_output = QPlainTextEdit()
        self.program_output.setReadOnly(True)
        self.program_output.setFont(log_font)
        self.bottom_tabs.addTab(self.program_output, "Program Output")

        self.right_splitter.addWidget(self.bottom_tabs)

        # Splitter sizing
        self.right_splitter.setSizes([520, 200])
        self.main_splitter.addWidget(self.right_splitter)
        self.main_splitter.setSizes([220, 880])

    def init_menus(self):
        mb = self.menuBar()

        # File Menu
        file_menu = mb.addMenu("&File")

        new_menu = file_menu.addMenu(get_icon("new_file"), "&New")
        act_new_source = new_menu.addAction(get_icon("new_file"), "&Source File")
        act_new_source.setShortcut(QKeySequence.New)
        act_new_source.triggered.connect(self.new_source_file)

        act_new_project = new_menu.addAction(get_icon("new_project"), "&Project...")
        act_new_project.setShortcut(QKeySequence("Ctrl+Shift+N"))
        act_new_project.triggered.connect(self.new_project_dialog)

        act_open = file_menu.addAction(get_icon("open_file"), "&Open...")
        act_open.setShortcut(QKeySequence.Open)
        act_open.triggered.connect(self.open_file_dialog)

        act_open_proj = file_menu.addAction(get_icon("open_file"), "Open Pro&ject...")
        act_open_proj.triggered.connect(self.open_project_dialog)

        file_menu.addSeparator()

        self.act_save = file_menu.addAction(get_icon("save"), "&Save")
        self.act_save.setShortcut(QKeySequence.Save)
        self.act_save.triggered.connect(self.save_current_file)

        act_save_as = file_menu.addAction(get_icon("save"), "Save &As...")
        act_save_as.setShortcut(QKeySequence.SaveAs)
        act_save_as.triggered.connect(self.save_as_current_file)

        act_save_all = file_menu.addAction(get_icon("save_all"), "Save A&ll")
        act_save_all.setShortcut(QKeySequence("Ctrl+Shift+S"))
        act_save_all.triggered.connect(self.save_all_files)

        file_menu.addSeparator()

        act_close = file_menu.addAction(get_icon("stop"), "&Close")
        act_close.setShortcut(QKeySequence("Ctrl+W"))
        act_close.triggered.connect(lambda: self.close_tab(self.editor_tabs.currentIndex()))

        act_close_all = file_menu.addAction("Close All")
        act_close_all.triggered.connect(self.close_all_tabs)

        file_menu.addSeparator()
        act_exit = file_menu.addAction("E&xit")
        act_exit.setShortcut(QKeySequence.Quit)
        act_exit.triggered.connect(self.close)

        # Edit Menu
        edit_menu = mb.addMenu("&Edit")
        act_undo = edit_menu.addAction(get_icon("undo"), "&Undo")
        act_undo.setShortcut(QKeySequence.Undo)
        act_undo.triggered.connect(lambda: self.current_editor().undo() if self.current_editor() else None)

        act_redo = edit_menu.addAction(get_icon("redo"), "&Redo")
        act_redo.setShortcut(QKeySequence.Redo)
        act_redo.triggered.connect(lambda: self.current_editor().redo() if self.current_editor() else None)

        edit_menu.addSeparator()
        act_cut = edit_menu.addAction(get_icon("cut"), "Cu&t")
        act_cut.setShortcut(QKeySequence.Cut)
        act_cut.triggered.connect(lambda: self.current_editor().cut() if self.current_editor() else None)

        act_copy = edit_menu.addAction(get_icon("copy"), "&Copy")
        act_copy.setShortcut(QKeySequence.Copy)
        act_copy.triggered.connect(lambda: self.current_editor().copy() if self.current_editor() else None)

        act_paste = edit_menu.addAction(get_icon("paste"), "&Paste")
        act_paste.setShortcut(QKeySequence.Paste)
        act_paste.triggered.connect(lambda: self.current_editor().paste() if self.current_editor() else None)

        edit_menu.addSeparator()
        act_select_all = edit_menu.addAction("Select &All")
        act_select_all.setShortcut(QKeySequence.SelectAll)
        act_select_all.triggered.connect(lambda: self.current_editor().selectAll() if self.current_editor() else None)

        # Search Menu
        search_menu = mb.addMenu("&Search")
        act_find = search_menu.addAction(get_icon("find"), "&Find / Replace...")
        act_find.setShortcut(QKeySequence.Find)
        act_find.triggered.connect(self.open_find_replace)

        act_goto = search_menu.addAction("&Go to Line...")
        act_goto.setShortcut(QKeySequence("Ctrl+G"))
        act_goto.triggered.connect(self.open_goto_line)

        # Execute Menu (MuCpp / C++ shortcuts)
        exec_menu = mb.addMenu("E&xecute")
        act_compile = exec_menu.addAction(get_icon("compile"), "&Compile")
        act_compile.setShortcut(QKeySequence(Qt.Key_F9))
        act_compile.triggered.connect(self.action_compile)

        act_run = exec_menu.addAction(get_icon("run"), "&Run")
        act_run.setShortcut(QKeySequence(Qt.Key_F10))
        act_run.triggered.connect(self.action_run)

        act_compile_run = exec_menu.addAction(get_icon("compile_run"), "Compile && &Run")
        act_compile_run.setShortcut(QKeySequence(Qt.Key_F11))
        act_compile_run.triggered.connect(self.action_compile_and_run)

        act_rebuild = exec_menu.addAction(get_icon("rebuild"), "Re&build All")
        act_rebuild.setShortcut(QKeySequence(Qt.Key_F12))
        act_rebuild.triggered.connect(self.action_rebuild_all)

        exec_menu.addSeparator()
        act_compiler_opts = exec_menu.addAction(get_icon("settings"), "Compiler &Options...")
        act_compiler_opts.triggered.connect(self.open_compiler_options)

        # Project Menu
        proj_menu = mb.addMenu("&Project")
        act_add_file = proj_menu.addAction(get_icon("new_file"), "&Add to Project...")
        act_add_file.triggered.connect(self.add_file_to_project)
        act_close_proj = proj_menu.addAction("&Close Project")
        act_close_proj.triggered.connect(self.close_project)

        # View Menu
        view_menu = mb.addMenu("&View")
        act_toggle_sidebar = view_menu.addAction("Toggle Project &Sidebar")
        act_toggle_sidebar.setCheckable(True)
        act_toggle_sidebar.setChecked(True)
        act_toggle_sidebar.toggled.connect(self.sidebar_tabs.setVisible)

        act_toggle_bottom = view_menu.addAction("Toggle &Bottom Panel")
        act_toggle_bottom.setCheckable(True)
        act_toggle_bottom.setChecked(True)
        act_toggle_bottom.toggled.connect(self.bottom_tabs.setVisible)

        # Help Menu
        help_menu = mb.addMenu("&Help")
        act_about = help_menu.addAction(get_icon("app_logo"), "&About MuCpp...")
        act_about.triggered.connect(self.show_about_dialog)

    def init_toolbar(self):
        tb = QToolBar("Main Toolbar", self)
        tb.setObjectName("MainToolbar")
        tb.setIconSize(QSize(22, 22))
        tb.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.main_toolbar = tb
        self.addToolBar(tb)

        # Right-click context menu on toolbar to toggle display style
        tb.setContextMenuPolicy(Qt.CustomContextMenu)
        tb.customContextMenuRequested.connect(lambda pos: self.show_toolbar_menu(tb, pos))

        # File Actions
        self.tb_new = tb.addAction(get_icon("new_file"), "New", self.new_source_file)
        self.tb_new.setToolTip("New Source File (Ctrl+N)")

        self.tb_new_proj = tb.addAction(get_icon("new_project"), "New Project", self.new_project_dialog)
        self.tb_new_proj.setToolTip("New Project... (Ctrl+Shift+N)")

        self.tb_open = tb.addAction(get_icon("open_file"), "Open", self.open_file_dialog)
        self.tb_open.setToolTip("Open Source File... (Ctrl+O)")

        self.tb_save = tb.addAction(get_icon("save"), "Save", self.save_current_file)
        self.tb_save.setToolTip("Save Current File (Ctrl+S)")

        self.tb_save_all = tb.addAction(get_icon("save_all"), "Save All", self.save_all_files)
        self.tb_save_all.setToolTip("Save All Files (Ctrl+Shift+S)")

        tb.addSeparator()

        # Edit Actions
        self.tb_undo = tb.addAction(get_icon("undo"), "Undo", lambda: self.current_editor().undo() if self.current_editor() else None)
        self.tb_undo.setToolTip("Undo (Ctrl+Z)")

        self.tb_redo = tb.addAction(get_icon("redo"), "Redo", lambda: self.current_editor().redo() if self.current_editor() else None)
        self.tb_redo.setToolTip("Redo (Ctrl+Y)")

        self.tb_cut = tb.addAction(get_icon("cut"), "Cut", lambda: self.current_editor().cut() if self.current_editor() else None)
        self.tb_cut.setToolTip("Cut Selection (Ctrl+X)")

        self.tb_copy = tb.addAction(get_icon("copy"), "Copy", lambda: self.current_editor().copy() if self.current_editor() else None)
        self.tb_copy.setToolTip("Copy Selection (Ctrl+C)")

        self.tb_paste = tb.addAction(get_icon("paste"), "Paste", lambda: self.current_editor().paste() if self.current_editor() else None)
        self.tb_paste.setToolTip("Paste Clipboard (Ctrl+V)")

        tb.addSeparator()

        # Search Action
        self.tb_find = tb.addAction(get_icon("find"), "Find", self.open_find_replace)
        self.tb_find.setToolTip("Find and Replace in File (Ctrl+F)")

        tb.addSeparator()

        # Primary Compiler / Execution Actions
        self.tb_compile = tb.addAction(get_icon("compile"), "Compile", self.action_compile)
        self.tb_compile.setToolTip("Compile (F9)")

        self.tb_run = tb.addAction(get_icon("run"), "Run", self.action_run)
        self.tb_run.setToolTip("Run Program (F10)")

        self.tb_compile_run = tb.addAction(get_icon("compile_run"), "Compile & Run", self.action_compile_and_run)
        self.tb_compile_run.setToolTip("Compile and Run (F11)")

        self.tb_rebuild = tb.addAction(get_icon("rebuild"), "Rebuild All", self.action_rebuild_all)
        self.tb_rebuild.setToolTip("Rebuild All (F12)")

        tb.addSeparator()

        # Settings & Utility
        self.tb_settings = tb.addAction(get_icon("settings"), "Compiler Options", self.open_compiler_options)
        self.tb_settings.setToolTip("Compiler & Toolchain Options...")

        self.tb_clean = tb.addAction(get_icon("clean"), "Clear Log", self.clear_logs)
        self.tb_clean.setToolTip("Clear Compilation and Output Logs")

    def show_toolbar_menu(self, tb: QToolBar, pos):
        menu = QMenu(self)
        a_icon_only = menu.addAction("Icons Only")
        a_beside = menu.addAction("Text Beside Icons")
        a_under = menu.addAction("Text Under Icons")
        a_text_only = menu.addAction("Text Only")

        act = menu.exec(tb.mapToGlobal(pos))
        if act == a_icon_only:
            tb.setToolButtonStyle(Qt.ToolButtonIconOnly)
        elif act == a_beside:
            tb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        elif act == a_under:
            tb.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        elif act == a_text_only:
            tb.setToolButtonStyle(Qt.ToolButtonTextOnly)

    def clear_logs(self):
        self.compile_log.clear()
        self.issues_table.setRowCount(0)
        self.program_output.clear()
        self.statusBar().showMessage("Logs and diagnostics cleared", 2500)

    def init_statusbar(self):
        sb = self.statusBar()
        sb.showMessage("Ready", 3000)
        self.lbl_cursor = QLabel("Line: 1, Col: 1  ")
        self.lbl_total = QLabel("Lines: 1  ")
        self.lbl_encoding = QLabel("UTF-8  ")
        sb.addPermanentWidget(self.lbl_cursor)
        sb.addPermanentWidget(self.lbl_total)
        sb.addPermanentWidget(self.lbl_encoding)

    # --- Tab & Editor Management ---

    def current_editor(self) -> Optional[CodeEditor]:
        idx = self.editor_tabs.currentIndex()
        if idx >= 0:
            return self.editor_tabs.widget(idx)
        return None

    def new_source_file(self, content: str = "", title: str = "Untitled.cpp", file_path: str = "") -> CodeEditor:
        editor = CodeEditor(file_path=file_path)
        if content:
            editor.setPlainText(content)
        else:
            default_template = """#include <iostream>

using namespace std;

int main(int argc, char** argv) {
    cout << "Hello, World from MuCpp!" << endl;
    return 0;
}
"""
            editor.setPlainText(default_template)

        idx = self.editor_tabs.addTab(editor, title)
        self.editor_tabs.setCurrentIndex(idx)
        editor.textChanged.connect(lambda: self.on_editor_modified(editor))
        editor.cursorPositionChanged.connect(self.update_status_cursor)
        self.update_symbols_tree(editor)
        self.update_window_title()
        return editor

    def update_window_title(self):
        editor = self.current_editor()
        tab_name = ""
        if editor:
            idx = self.editor_tabs.indexOf(editor)
            if idx >= 0:
                tab_name = self.editor_tabs.tabText(idx)

        if self.current_project:
            if tab_name:
                self.setWindowTitle(f"MuCpp - [{self.current_project.name} : {tab_name}]")
            else:
                self.setWindowTitle(f"MuCpp - [{self.current_project.name}]")
        else:
            if tab_name:
                self.setWindowTitle(f"MuCpp - [{tab_name}]")
            else:
                self.setWindowTitle("MuCpp IDE")

    def on_editor_modified(self, editor: CodeEditor):
        idx = self.editor_tabs.indexOf(editor)
        if idx >= 0:
            tab_text = self.editor_tabs.tabText(idx)
            if not tab_text.startswith("*"):
                self.editor_tabs.setTabText(idx, "*" + tab_text)
                self.update_window_title()

    def on_tab_changed(self, idx: int):
        self.update_status_cursor()
        editor = self.current_editor()
        if editor:
            self.update_symbols_tree(editor)
        self.update_window_title()

    def update_status_cursor(self):
        editor = self.current_editor()
        if not editor:
            self.lbl_cursor.setText("Line: 1, Col: 1  ")
            self.lbl_total.setText("Lines: 0  ")
            return
        cursor = editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        total_lines = editor.blockCount()
        self.lbl_cursor.setText(f"Line: {line}, Col: {col}  ")
        self.lbl_total.setText(f"Lines: {total_lines}  ")

    def close_tab(self, idx: int):
        if idx < 0:
            return
        editor = self.editor_tabs.widget(idx)
        tab_text = self.editor_tabs.tabText(idx)
        
        if tab_text.startswith("*"):
            reply = QMessageBox.question(
                self,
                "Save Changes?",
                f"File '{tab_text.lstrip('*')}' has been modified.\nDo you want to save changes?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self.save_current_file()
            elif reply == QMessageBox.Cancel:
                return

        self.editor_tabs.removeTab(idx)
        self.update_window_title()

    def close_all_tabs(self):
        while self.editor_tabs.count() > 0:
            self.close_tab(0)

    # --- File IO ---

    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Open C/C++ Source File",
            "",
            "C/C++ Files (*.cpp *.c *.cxx *.cc *.h *.hpp);;All Files (*.*)"
        )
        for f in files:
            self.open_file(f)

    def open_file(self, file_path: str):
        # Check if already open
        for i in range(self.editor_tabs.count()):
            ed = self.editor_tabs.widget(i)
            if os.path.abspath(ed.file_path) == os.path.abspath(file_path):
                self.editor_tabs.setCurrentIndex(i)
                return

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.new_source_file(content=content, title=os.path.basename(file_path), file_path=file_path)
        except Exception as ex:
            QMessageBox.critical(self, "Error Opening File", f"Could not open {file_path}:\n{ex}")

    def save_current_file(self) -> bool:
        editor = self.current_editor()
        if not editor:
            return False
        if not editor.file_path:
            return self.save_as_current_file()
        
        try:
            with open(editor.file_path, "w", encoding="utf-8") as f:
                f.write(editor.toPlainText())
            idx = self.editor_tabs.indexOf(editor)
            self.editor_tabs.setTabText(idx, os.path.basename(editor.file_path))
            self.statusBar().showMessage(f"Saved: {editor.file_path}", 3000)
            return True
        except Exception as ex:
            QMessageBox.critical(self, "Save Error", f"Error saving file:\n{ex}")
            return False

    def save_as_current_file(self) -> bool:
        editor = self.current_editor()
        if not editor:
            return False
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            editor.file_path or "main.cpp",
            "C++ Source (*.cpp);;C Source (*.c);;Header (*.h *.hpp);;All Files (*.*)"
        )
        if path:
            editor.file_path = path
            return self.save_current_file()
        return False

    def save_all_files(self):
        for i in range(self.editor_tabs.count()):
            self.editor_tabs.setCurrentIndex(i)
            self.save_current_file()

    # --- Project Management ---

    def new_project_dialog(self):
        dlg = NewProjectDialog(self)
        if dlg.exec():
            project_dir, name, template_name = dlg.get_project_details()
            proj = Project.create_new(project_dir, name, template_name)
            self.load_project(proj)

    def open_project_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "MuCpp Projects (*.mcpp *.dev);;All Files (*.*)"
        )
        if path:
            try:
                proj = Project.load(path)
                self.load_project(proj)
            except Exception as ex:
                QMessageBox.critical(self, "Error", f"Failed to load project:\n{ex}")

    def load_project(self, proj: Project):
        self.current_project = proj
        self.project_tree.clear()

        root_item = QTreeWidgetItem([f"Project: {proj.name}"])
        root_item.setExpanded(True)
        self.project_tree.addTopLevelItem(root_item)

        for src in proj.source_files:
            item = QTreeWidgetItem([os.path.basename(src)])
            item.setData(0, Qt.UserRole, src)
            root_item.addChild(item)
            self.open_file(src)

        self.update_window_title()
        self.statusBar().showMessage(f"Project '{proj.name}' loaded.", 4000)

    def on_tree_item_double_clicked(self, item: QTreeWidgetItem, col: int):
        path = item.data(0, Qt.UserRole)
        if path and os.path.isfile(path):
            self.open_file(path)

    def add_file_to_project(self):
        if not self.current_project:
            QMessageBox.information(self, "No Project", "No active project is open.")
            return
        files, _ = QFileDialog.getOpenFileNames(
            self, "Add Files to Project", self.current_project.project_dir, "C/C++ Files (*.cpp *.c *.h);;All Files (*.*)"
        )
        for f in files:
            if f not in self.current_project.source_files:
                self.current_project.source_files.append(f)
        self.current_project.save()
        self.load_project(self.current_project)

    def close_project(self):
        self.current_project = None
        self.project_tree.clear()
        self.update_window_title()

    # --- Symbols Parser (Regex heuristic for functions and classes) ---

    def update_symbols_tree(self, editor: CodeEditor):
        self.symbols_tree.clear()
        text = editor.toPlainText()

        # Classes / Structs
        class_pattern = re.compile(r"^\s*(class|struct)\s+([A-Za-z0-9_]+)", re.MULTILINE)
        class_item = QTreeWidgetItem(["Classes & Structs"])
        class_item.setExpanded(True)

        for m in class_pattern.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            item = QTreeWidgetItem([f"{m.group(1)} {m.group(2)} (Line {line_no})"])
            item.setData(0, Qt.UserRole, line_no)
            class_item.addChild(item)

        # Functions
        func_pattern = re.compile(r"^[A-Za-z0-9_:<>\*\&\s]+\s+([A-Za-z0-9_]+)\s*\([^;\{]*\)\s*\{", re.MULTILINE)
        func_item = QTreeWidgetItem(["Functions"])
        func_item.setExpanded(True)

        for m in func_pattern.finditer(text):
            func_name = m.group(1)
            if func_name in ("if", "for", "while", "switch", "catch"):
                continue
            line_no = text[:m.start()].count("\n") + 1
            item = QTreeWidgetItem([f"{func_name}() (Line {line_no})"])
            item.setData(0, Qt.UserRole, line_no)
            func_item.addChild(item)

        if class_item.childCount() > 0:
            self.symbols_tree.addTopLevelItem(class_item)
        if func_item.childCount() > 0:
            self.symbols_tree.addTopLevelItem(func_item)

    def on_symbol_double_clicked(self, item: QTreeWidgetItem, col: int):
        line = item.data(0, Qt.UserRole)
        if line and self.current_editor():
            self.current_editor().goto_line(int(line))

    # --- Compilation & Execution ---

    def prepare_build_targets(self) -> Tuple[List[str], str, bool]:
        """Resolves source files, output executable path, and language standard."""
        if self.current_project:
            sources = self.current_project.source_files
            output_exe = self.current_project.output_executable
            is_cxx = any(f.endswith((".cpp", ".cxx", ".cc")) for f in sources)
            return sources, output_exe, is_cxx
        else:
            editor = self.current_editor()
            if not editor:
                return [], "", True
            if not editor.file_path:
                saved = self.save_as_current_file()
                if not saved:
                    return [], "", True
            else:
                self.save_current_file()

            source = editor.file_path
            base, ext = os.path.splitext(source)
            output_exe = base + ".exe"
            is_cxx = ext.lower() in [".cpp", ".cxx", ".cc"]
            return [source], output_exe, is_cxx

    def action_compile(self):
        sources, output_exe, is_cxx = self.prepare_build_targets()
        if not sources or not output_exe:
            QMessageBox.warning(self, "No Source", "Please open or create a source file before compiling.")
            return

        if not self.compiler_mgr.is_available(is_cxx):
            comp = self.compiler_mgr.cxx_compiler if is_cxx else self.compiler_mgr.c_compiler
            QMessageBox.critical(
                self,
                "Compiler Not Found",
                f"Cannot find compiler '{comp}'.\nPlease configure compiler path under Execute -> Compiler Options."
            )
            self.open_compiler_options()
            return

        self.compile_log.clear()
        self.issues_table.setRowCount(0)
        self.bottom_tabs.setCurrentIndex(0)
        self.statusBar().showMessage("Compiling...")

        cmd_display = " ".join(self.compiler_mgr.build_command(sources, output_exe, is_cxx))
        self.compile_log.appendPlainText(f"--- Compilation Started: {time.strftime('%X')} ---")
        self.compile_log.appendPlainText(f"Command:\n{cmd_display}\n")

        self.compile_worker = CompileWorker(self.compiler_mgr, sources, output_exe, is_cxx)
        self.compile_worker.finished_signal.connect(self.on_compile_finished)
        self.compile_worker.start()

    def on_compile_finished(self, res: CompilationResult):
        self.compile_log.appendPlainText(res.stdout)
        if res.stderr:
            self.compile_log.appendPlainText(res.stderr)

        self.compile_log.appendPlainText(f"\n--- Compilation Finished in {res.duration_sec:.2f}s (Return code: {res.return_code}) ---")

        # Populate Issues Table
        self.issues_table.setRowCount(0)
        error_lines = set()
        warning_lines = set()

        for diag in res.diagnostics:
            row = self.issues_table.rowCount()
            self.issues_table.insertRow(row)

            # Severity item with color
            sev_item = QTableWidgetItem(diag.severity.capitalize())
            if "error" in diag.severity:
                sev_item.setForeground(QColor("#D9534F"))
                error_lines.add(diag.line)
            elif "warning" in diag.severity:
                sev_item.setForeground(QColor("#F0AD4E"))
                warning_lines.add(diag.line)
            else:
                sev_item.setForeground(QColor("#5BC0DE"))

            self.issues_table.setItem(row, 0, sev_item)
            self.issues_table.setItem(row, 1, QTableWidgetItem(str(diag.line)))
            self.issues_table.setItem(row, 2, QTableWidgetItem(str(diag.column)))
            self.issues_table.setItem(row, 3, QTableWidgetItem(diag.message))
            self.issues_table.setItem(row, 4, QTableWidgetItem(os.path.basename(diag.file)))

            # Store full file path & line on item
            sev_item.setData(Qt.UserRole, (diag.file, diag.line, diag.column))

        # Update line number marks on current editor
        if self.current_editor():
            self.current_editor().set_diagnostics_marks(error_lines, warning_lines)

        if res.success:
            self.last_compiled_exe = res.output_path
            self.statusBar().showMessage(f"Compilation Successful (0 errors, {len(warning_lines)} warnings) - {res.duration_sec:.2f}s", 5000)
            self.bottom_tabs.setCurrentIndex(0)
        else:
            self.statusBar().showMessage(f"Compilation Failed: {len(error_lines)} errors, {len(warning_lines)} warnings", 5000)
            self.bottom_tabs.setCurrentIndex(1)  # Jump to issues tab automatically

    def on_issue_double_clicked(self, row: int, col: int):
        item = self.issues_table.item(row, 0)
        if not item:
            return
        data = item.data(Qt.UserRole)
        if data:
            file_path, line, column = data
            if not os.path.isabs(file_path):
                if self.current_project and os.path.isfile(os.path.join(self.current_project.project_dir, file_path)):
                    file_path = os.path.join(self.current_project.project_dir, file_path)
                elif self.current_editor() and self.current_editor().file_path:
                    cand = os.path.join(os.path.dirname(self.current_editor().file_path), file_path)
                    if os.path.isfile(cand):
                        file_path = cand
            if os.path.isfile(file_path):
                self.open_file(file_path)
            if self.current_editor():
                self.current_editor().goto_line(line, column)

    def action_run(self):
        sources, output_exe, _ = self.prepare_build_targets()
        exe_to_run = self.last_compiled_exe or output_exe

        if not os.path.isfile(exe_to_run):
            QMessageBox.information(
                self,
                "Executable Not Found",
                "Executable has not been compiled yet.\nPlease Compile (F9) first."
            )
            return

        self.statusBar().showMessage(f"Running '{os.path.basename(exe_to_run)}'...")
        self.compiler_mgr.run_executable(exe_to_run)

    def action_compile_and_run(self):
        sources, output_exe, is_cxx = self.prepare_build_targets()
        if not sources or not output_exe:
            return

        def run_after_compile(res: CompilationResult):
            if res.success and res.output_path:
                self.action_run()

        self.compile_log.clear()
        self.issues_table.setRowCount(0)
        self.statusBar().showMessage("Compiling...")

        cmd_display = " ".join(self.compiler_mgr.build_command(sources, output_exe, is_cxx))
        self.compile_log.appendPlainText(f"--- Compilation Started: {time.strftime('%X')} ---")
        self.compile_log.appendPlainText(f"Command:\n{cmd_display}\n")

        self.compile_worker = CompileWorker(self.compiler_mgr, sources, output_exe, is_cxx)
        self.compile_worker.finished_signal.connect(self.on_compile_finished)
        self.compile_worker.finished_signal.connect(run_after_compile)
        self.compile_worker.start()

    def action_rebuild_all(self):
        sources, output_exe, _ = self.prepare_build_targets()
        if os.path.isfile(output_exe):
            try:
                os.remove(output_exe)
            except Exception:
                pass
        self.action_compile()

    # --- Dialogs & Tools ---

    def open_compiler_options(self):
        dlg = CompilerOptionsDialog(self.compiler_mgr, self)
        dlg.exec()

    def open_find_replace(self):
        dlg = FindReplaceDialog(self.current_editor, self)
        dlg.show()

    def open_goto_line(self):
        editor = self.current_editor()
        if not editor:
            return
        curr = editor.textCursor().blockNumber() + 1
        total = editor.blockCount()
        dlg = GotoLineDialog(curr, total, self)
        if dlg.exec():
            editor.goto_line(dlg.get_line())

    def show_about_dialog(self):
        QMessageBox.about(
            self,
            "About MuCpp",
            "<h2>MuCpp IDE</h2>"
            "<p>A modern, lightweight, fast C/C++ Integrated Development Environment.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Integrated MinGW64 GCC/G++ Compiler toolchain</li>"
            "<li>Interactive compiler diagnostics & direct source code line navigation</li>"
            "<li>Fast syntax highlighting, code indentation, line numbers & bracket matching</li>"
            "<li>One-click Compile (F9), Run (F10), Compile & Run (F11), and Rebuild All (F12)</li>"
            "<li>Console, Win32 GUI, and Library project templates</li>"
            "</ul>"
            "<p>Built for modern C and C++ developers.</p>"
        )


# Backward compatibility alias
DevCppMainWindow = MuCppMainWindow
