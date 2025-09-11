from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QPushButton


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
