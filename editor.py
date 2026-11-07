import re
from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextFormat,
)
from PySide6.QtWidgets import (
    QPlainTextEdit,
    QTextEdit,
    QWidget,
)

class CppHighlighter(QSyntaxHighlighter):
    """Rich C/C++ Syntax Highlighter modeled after classic Dev-C++."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Color palette
        KEYWORD_COLOR = QColor("#0000FF")      # Classic Blue
        TYPE_COLOR = QColor("#008080")         # Teal
        PREPROC_COLOR = QColor("#008000")      # Green
        STRING_COLOR = QColor("#A31515")       # Dark Red / Crimson
        NUMBER_COLOR = QColor("#098658")       # Dark Emerald
        COMMENT_COLOR = QColor("#008000")      # Italic Green
        OPERATOR_COLOR = QColor("#000000")

        # 1. Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(KEYWORD_COLOR)
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            r"\bauto\b", r"\bbreak\b", r"\bcase\b", r"\bcatch\b", r"\bclass\b",
            r"\bconst\b", r"\bconstexpr\b", r"\bcontinue\b", r"\bdefault\b",
            r"\bdelete\b", r"\bdo\b", r"\belse\b", r"\benum\b", r"\bexplicit\b",
            r"\bexport\b", r"\bextern\b", r"\bfalse\b", r"\bfor\b", r"\bfriend\b",
            r"\bgoto\b", r"\bif\b", r"\binline\b", r"\bmutable\b", r"\bnamespace\b",
            r"\bnew\b", r"\bnoexcept\b", r"\bnullptr\b", r"\boperator\b",
            r"\bprivate\b", r"\bprotected\b", r"\bpublic\b", r"\bregister\b",
            r"\breinterpret_cast\b", r"\breturn\b", r"\bsizeof\b", r"\bstatic\b",
            r"\bstatic_assert\b", r"\bstatic_cast\b", r"\bstruct\b", r"\bswitch\b",
            r"\btemplate\b", r"\bthis\b", r"\bthread_local\b", r"\bthrow\b",
            r"\btrue\b", r"\btry\b", r"\btypedef\b", r"\btypeid\b", r"\btypename\b",
            r"\bunion\b", r"\busing\b", r"\bvirtual\b", r"\bvolatile\b", r"\bwhile\b"
        ]
        for pattern in keywords:
            self.highlighting_rules.append((re.compile(pattern), keyword_format))

        # 2. Types
        type_format = QTextCharFormat()
        type_format.setForeground(TYPE_COLOR)
        type_format.setFontWeight(QFont.Bold)
        types = [
            r"\bbool\b", r"\bchar\b", r"\bchar16_t\b", r"\bchar32_t\b", r"\bwchar_t\b",
            r"\bshort\b", r"\bint\b", r"\blong\b", r"\bsigned\b", r"\bunsigned\b",
            r"\bfloat\b", r"\bdouble\b", r"\bvoid\b", r"\bsize_t\b", r"\bint8_t\b",
            r"\bint16_t\b", r"\bint32_t\b", r"\bint64_t\b", r"\buint8_t\b",
            r"\buint16_t\b", r"\buint32_t\b", r"\buint64_t\b", r"\bstring\b",
            r"\bvector\b", r"\bmap\b", r"\bset\b", r"\bpair\b", r"\btuple\b",
            r"\bstd\b"
        ]
        for pattern in types:
            self.highlighting_rules.append((re.compile(pattern), type_format))

        # 3. Preprocessor directives
        preproc_format = QTextCharFormat()
        preproc_format.setForeground(PREPROC_COLOR)
        preproc_format.setFontWeight(QFont.Bold)
        preproc_pattern = re.compile(r"^\s*#\s*(?:include|define|undef|ifdef|ifndef|if|else|elif|endif|pragma|error|line).*")
        self.highlighting_rules.append((preproc_pattern, preproc_format))

        # 4. Numbers
        num_format = QTextCharFormat()
        num_format.setForeground(NUMBER_COLOR)
        num_pattern = re.compile(r"\b(?:0x[0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?[fFlLuU]*)\b")
        self.highlighting_rules.append((num_pattern, num_format))

        # 5. Strings & Char Literals
        string_format = QTextCharFormat()
        string_format.setForeground(STRING_COLOR)
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(?:\\.[^'\\]*)*'"), string_format))

        # 6. Single line comments
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(COMMENT_COLOR)
        self.comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r"//[^\n]*"), self.comment_format))

        # 7. Multi-line comments delimiters
        self.comment_start = re.compile(r"/\*")
        self.comment_end = re.compile(r"\*/")

    def highlightBlock(self, text: str):
        # Apply standard single-line rules
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, fmt)

        # Multi-line comment state handling
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            match = self.comment_start.search(text)
            start_index = match.start() if match else -1
        
        while start_index >= 0:
            end_match = self.comment_end.search(text, start_index + 2)
            if not end_match:
                self.setCurrentBlockState(1)
                comment_len = len(text) - start_index
            else:
                comment_len = end_match.end() - start_index

            self.setFormat(start_index, comment_len, self.comment_format)
            
            if not end_match:
                break
            
            match = self.comment_start.search(text, end_match.end())
            start_index = match.start() if match else -1


class LineNumberArea(QWidget):
    """The left gutter displaying line numbers, identical to Dev-C++ editor."""

    def __init__(self, editor: 'CodeEditor'):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Feature-rich C/C++ Code Editor with line numbers, indentation, and Dev-C++ shortcuts."""

    def __init__(self, file_path: str = "", parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.line_number_area = LineNumberArea(self)
        self.error_lines = set()
        self.warning_lines = set()

        # Editor Font
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)

        # Highlighter
        self.highlighter = CppHighlighter(self.document())

        # Signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_width(self) -> int:
        digits = 1
        max_blocks = max(1, self.blockCount())
        while max_blocks >= 10:
            max_blocks //= 10
            digits += 1
        space = 14 + self.fontMetrics().horizontalAdvance('9') * max(digits, 3)
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        # Classic Dev-C++ light gray gutter background
        painter.fillRect(event.rect(), QColor("#F0F0F0"))
        
        # Right border line
        painter.setPen(QColor("#D0D0D0"))
        painter.drawLine(event.rect().topRight(), event.rect().bottomRight())

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        current_line = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_idx = block_number + 1
                
                # Check if this line has errors or warnings
                if line_idx in self.error_lines:
                    painter.fillRect(0, top, self.line_number_area.width() - 2, self.fontMetrics().height(), QColor("#FFD2D2"))
                    painter.setPen(QColor("#CC0000"))
                elif line_idx in self.warning_lines:
                    painter.fillRect(0, top, self.line_number_area.width() - 2, self.fontMetrics().height(), QColor("#FFF3CD"))
                    painter.setPen(QColor("#856404"))
                elif block_number == current_line:
                    painter.setPen(QColor("#000000"))
                else:
                    painter.setPen(QColor("#808080"))

                line_str = str(line_idx)
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 6,
                    self.fontMetrics().height(),
                    Qt.AlignRight | Qt.AlignVCenter,
                    line_str
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#E8F2FE")  # Soft blue highlight for active line
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def set_diagnostics_marks(self, errors: set, warnings: set):
        self.error_lines = errors
        self.warning_lines = warnings
        self.line_number_area.update()

    def goto_line(self, line_number: int, column: int = 1):
        doc = self.document()
        if line_number < 1:
            line_number = 1
        if line_number > doc.blockCount():
            line_number = doc.blockCount()

        block = doc.findBlockByLineNumber(line_number - 1)
        cursor = QTextCursor(block)
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, max(0, column - 1))
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        self.setFocus()

    def keyPressEvent(self, event):
        # Auto indentation
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            cursor = self.textCursor()
            line_text = cursor.block().text()
            # Calculate current indentation
            indent_match = re.match(r"^(\s*)", line_text)
            current_indent = indent_match.group(1) if indent_match else ""
            
            # If line ends with opening brace, increase indentation by 4 spaces
            stripped = line_text.rstrip()
            extra = "    " if stripped.endswith("{") else ""

            super().keyPressEvent(event)
            self.insertPlainText(current_indent + extra)
            return

        # Tab key replaces with 4 spaces
        if event.key() == Qt.Key_Tab:
            self.insertPlainText("    ")
            return

        super().keyPressEvent(event)
