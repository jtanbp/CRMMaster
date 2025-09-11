from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QPalette, QTextCursor
from PySide6.QtWidgets import QApplication, QPushButton


def update_refresh_btn(refresh_btn: QPushButton, success: bool):
    if success:
        refresh_btn.setText('✅ Refreshed')
        refresh_btn.setStyleSheet('color: green;')
    else:
        refresh_btn.setText('❌ Failed')
        refresh_btn.setStyleSheet('color: red;')

    # Resets refresh button after 2 seconds
    QTimer.singleShot(2000, lambda: reset_refresh_btn(refresh_btn))


def reset_refresh_btn(refresh_btn: QPushButton):
    refresh_btn.setText('🔄 Refresh')
    refresh_btn.setStyleSheet('')


def update_counter(widget, max_chars: int):
    """
    Update the character counter for a widget with `input_desc` and `counter_label`.

    Args:
        widget: Object containing `input_desc` (QTextEdit) and `counter_label` (QLabel)
        max_chars: Maximum allowed characters
    """
    current_text = widget.input_desc.toPlainText()
    current_length = len(current_text)
    remaining = max_chars - current_length

    # Trim text if over limit
    if remaining < 0:
        widget.input_desc.setPlainText(current_text[:max_chars])
        cursor = widget.input_desc.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        widget.input_desc.setTextCursor(cursor)
        remaining = 0

    # Update counter label
    widget.counter_label.setText(f"{remaining} characters remaining")

    # Reset palette from the system default
    palette = widget.counter_label.palette()
    default_color = QApplication.palette().color(QPalette.ColorRole.WindowText)

    # Set red if limit reached, else default system color
    palette.setColor(
        QPalette.ColorRole.WindowText,
        QColor("red") if remaining == 0 else default_color
    )
    widget.counter_label.setPalette(palette)
