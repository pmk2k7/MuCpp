import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from project import TEMPLATES
from compiler import CompilerManager
from icons import get_app_icon

class NewProjectDialog(QDialog):
    """Dialog to create a new C/C++ project from templates (MuCpp style)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setWindowIcon(get_app_icon())
        self.resize(520, 380)

        layout = QVBoxLayout(self)

        # Template Selection
        layout.addWidget(QLabel("<b>Select Project Template:</b>"))
        self.template_list = QListWidget()
        for t_name in TEMPLATES.keys():
            item = QListWidgetItem(t_name)
            self.template_list.addItem(item)
        self.template_list.setCurrentRow(0)
        layout.addWidget(self.template_list)

        # Form fields
        form = QFormLayout()
        self.name_edit = QLineEdit("Project1")
        form.addRow("Project Name:", self.name_edit)

        dir_layout = QHBoxLayout()
        default_dir = os.path.join(os.path.expanduser("~"), "Documents", "MuCppProjects")
        self.dir_edit = QLineEdit(default_dir)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(self.browse_btn)
        form.addRow("Directory:", dir_layout)

        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Create Project")
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.accept_creation)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def browse_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder", self.dir_edit.text())
        if folder:
            self.dir_edit.setText(folder)

    def accept_creation(self):
        name = self.name_edit.text().strip()
        folder = self.dir_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please specify a project name.")
            return
        if not folder:
            QMessageBox.warning(self, "Invalid Directory", "Please specify a project directory.")
            return
        self.accept()

    def get_project_details(self):
        template = self.template_list.currentItem().text()
        name = self.name_edit.text().strip()
        base_dir = self.dir_edit.text().strip()
        project_dir = os.path.join(base_dir, name)
        return project_dir, name, template


class CompilerOptionsDialog(QDialog):
    """Compiler and Build Environment configuration dialog."""

    def __init__(self, compiler_mgr: CompilerManager, parent=None):
        super().__init__(parent)
        self.compiler_mgr = compiler_mgr
        self.setWindowTitle("Compiler & Toolchain Options")
        self.setWindowIcon(get_app_icon())
        self.resize(580, 420)

        layout = QVBoxLayout(self)

        # Toolchain paths
        toolchain_group = QGroupBox("Toolchain Binaries")
        t_form = QFormLayout(toolchain_group)

        cxx_layout = QHBoxLayout()
        self.cxx_edit = QLineEdit(self.compiler_mgr.cxx_compiler)
        cxx_browse = QPushButton("Browse...")
        cxx_browse.clicked.connect(lambda: self.browse_binary(self.cxx_edit, "Select G++ Executable"))
        cxx_layout.addWidget(self.cxx_edit)
        cxx_layout.addWidget(cxx_browse)
        t_form.addRow("G++ (C++):", cxx_layout)

        c_layout = QHBoxLayout()
        self.c_edit = QLineEdit(self.compiler_mgr.c_compiler)
        c_browse = QPushButton("Browse...")
        c_browse.clicked.connect(lambda: self.browse_binary(self.c_edit, "Select GCC Executable"))
        c_layout.addWidget(self.c_edit)
        c_layout.addWidget(c_browse)
        t_form.addRow("GCC (C):", c_layout)
        layout.addWidget(toolchain_group)

        # Language Standards and Optimization
        flags_group = QGroupBox("Compiler Flags")
        f_form = QFormLayout(flags_group)

        self.std_combo = QComboBox()
        standards = ["-std=c++11", "-std=c++14", "-std=c++17", "-std=c++20", "-std=c++23", ""]
        self.std_combo.addItems(standards)
        idx = standards.index(self.compiler_mgr.standard) if self.compiler_mgr.standard in standards else 0
        self.std_combo.setCurrentIndex(idx)
        f_form.addRow("C++ Standard:", self.std_combo)

        self.opt_combo = QComboBox()
        opts = ["-O0", "-O1", "-O2", "-O3", "-Os"]
        self.opt_combo.addItems(opts)
        idx = opts.index(self.compiler_mgr.optimization) if self.compiler_mgr.optimization in opts else 2
        self.opt_combo.setCurrentIndex(idx)
        f_form.addRow("Optimization:", self.opt_combo)

        self.wall_cb = QCheckBox("Enable all common warnings (-Wall)")
        self.wall_cb.setChecked("-Wall" in self.compiler_mgr.warnings)
        f_form.addRow("", self.wall_cb)

        self.wextra_cb = QCheckBox("Enable extra warnings (-Wextra)")
        self.wextra_cb.setChecked("-Wextra" in self.compiler_mgr.warnings)
        f_form.addRow("", self.wextra_cb)

        self.custom_edit = QLineEdit(" ".join(self.compiler_mgr.custom_flags))
        f_form.addRow("Additional Flags:", self.custom_edit)

        layout.addWidget(flags_group)

        # Execution behavior
        exec_group = QGroupBox("Execution Behavior")
        e_layout = QVBoxLayout(exec_group)
        self.ext_console_cb = QCheckBox("Launch executables in external Windows console with auto-pause (MuCpp standard)")
        self.ext_console_cb.setChecked(self.compiler_mgr.run_in_external_console)
        e_layout.addWidget(self.ext_console_cb)
        layout.addWidget(exec_group)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_binary(self, line_edit: QLineEdit, title: str):
        path, _ = QFileDialog.getOpenFileName(self, title, line_edit.text(), "Executables (*.exe);;All Files (*.*)")
        if path:
            line_edit.setText(path)

    def save_settings(self):
        self.compiler_mgr.cxx_compiler = self.cxx_edit.text().strip()
        self.compiler_mgr.c_compiler = self.c_edit.text().strip()
        self.compiler_mgr.standard = self.std_combo.currentText().strip()
        self.compiler_mgr.optimization = self.opt_combo.currentText().strip()

        warnings = []
        if self.wall_cb.isChecked():
            warnings.append("-Wall")
        if self.wextra_cb.isChecked():
            warnings.append("-Wextra")
        self.compiler_mgr.warnings = warnings

        custom = self.custom_edit.text().strip().split()
        self.compiler_mgr.custom_flags = [c for c in custom if c]
        self.compiler_mgr.run_in_external_console = self.ext_console_cb.isChecked()
        self.accept()


class FindReplaceDialog(QDialog):
    """Find and Replace Dialog."""

    def __init__(self, editor_getter, parent=None):
        super().__init__(parent)
        self.editor_getter = editor_getter
        self.setWindowTitle("Find / Replace")
        self.setWindowIcon(get_app_icon())
        self.resize(380, 200)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.find_edit = QLineEdit()
        form.addRow("Find:", self.find_edit)

        self.replace_edit = QLineEdit()
        form.addRow("Replace with:", self.replace_edit)

        self.match_case_cb = QCheckBox("Match Case")
        form.addRow("", self.match_case_cb)

        self.whole_words_cb = QCheckBox("Whole Words Only")
        form.addRow("", self.whole_words_cb)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.find_btn = QPushButton("Find Next")
        self.find_btn.clicked.connect(self.find_next)
        self.replace_btn = QPushButton("Replace")
        self.replace_btn.clicked.connect(self.replace_current)
        self.replace_all_btn = QPushButton("Replace All")
        self.replace_all_btn.clicked.connect(self.replace_all)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.find_btn)
        btn_layout.addWidget(self.replace_btn)
        btn_layout.addWidget(self.replace_all_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

    def find_next(self) -> bool:
        editor = self.editor_getter()
        if not editor:
            return False
        text = self.find_edit.text()
        if not text:
            return False

        flags = 0
        from PySide6.QtGui import QTextDocument
        if self.match_case_cb.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        if self.whole_words_cb.isChecked():
            flags |= QTextDocument.FindWholeWords

        found = editor.find(text, QTextDocument.FindFlag(flags))
        if not found:
            # Wrap around
            cursor = editor.textCursor()
            cursor.movePosition(cursor.Start)
            editor.setTextCursor(cursor)
            found = editor.find(text, QTextDocument.FindFlag(flags))
            if not found:
                QMessageBox.information(self, "Find", f"Cannot find '{text}'.")
        return found

    def replace_current(self):
        editor = self.editor_getter()
        if not editor:
            return
        cursor = editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_edit.text())
        self.find_next()

    def replace_all(self):
        editor = self.editor_getter()
        if not editor:
            return
        count = 0
        cursor = editor.textCursor()
        cursor.movePosition(cursor.Start)
        editor.setTextCursor(cursor)
        
        while self.find_next():
            c = editor.textCursor()
            c.insertText(self.replace_edit.text())
            count += 1
            
        QMessageBox.information(self, "Replace All", f"Replaced {count} occurrences.")


class GotoLineDialog(QDialog):
    """Goto Line Dialog (Ctrl+G)."""

    def __init__(self, current_line: int, max_lines: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Go to Line")
        self.setWindowIcon(get_app_icon())
        self.resize(250, 120)

        layout = QVBoxLayout(self)
        self.spin = QSpinBox()
        self.spin.setRange(1, max(1, max_lines))
        self.spin.setValue(current_line)
        layout.addWidget(QLabel(f"Enter line number (1 - {max_lines}):"))
        layout.addWidget(self.spin)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Go")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_line(self) -> int:
        return self.spin.value()
