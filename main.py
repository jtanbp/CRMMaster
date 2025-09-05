import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar,
    QListWidget, QDockWidget, QStackedWidget, QWidget, QLabel, QVBoxLayout
)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMessageBox
from database.database_functions import get_connection
from supplierdb.supplier_widget import SupplierPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('CRMMaster')
        self.resize(1200, 600)

        self.conn = get_connection() #This will be the main connection for any query to the SQL database

        # Toolbar
        toolbar = QToolBar('Main Toolbar')
        self.addToolBar(toolbar)

        toggle_action = QAction(QIcon(), 'Show/Hide Menu', self)
        toggle_action.triggered.connect(self.toggle_menu)
        toolbar.addAction(toggle_action)

        test_connection = QAction(QIcon(), 'Test Connection', self)
        test_connection.triggered.connect(self.connection_test_window)
        toolbar.addAction(test_connection)

        # Left Dock (Menu List)
        self.menu_list = QListWidget()
        self.dock = QDockWidget('Menu', self)
        self.dock.setWidget(self.menu_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)   # Left side

        # Central Area (Stacked Pages)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Add pages based on privileges
        # 0 = super admin/master, 1 = admin, 2 = accounting, 3 = sales, 4 = others
        self.privilege = 0 # TODO: Set this once login is set up
        self.pages = {'Home': self.create_page('🏠 Welcome to Home Page')}
        self.menu_list.addItem('Home')
        self.privileged_pages()

        for page in self.pages.values():
            self.stack.addWidget(page)

        # Connect list click → change page
        self.menu_list.currentTextChanged.connect(self.switch_page)
        self.menu_list.setCurrentRow(0)  # Show Home by default

    def create_page(self, text, main_window=None):
        widget = QWidget()
        layout = QVBoxLayout()
        if text == '📦Supplier':
            layout.addWidget(SupplierPage(parent=main_window, conn=self.conn))
        else:
            layout.addWidget(QLabel(text))
        widget.setLayout(layout)
        return widget

    def privileged_pages(self):
        if self.privilege <= 3:
            self.pages['Supplier'] = self.create_page('📦Supplier', self)
            self.pages['Client'] = self.create_page('Client', self)
            self.pages['Product'] = self.create_page('Product', self)
            self.menu_list.addItems(['Supplier', 'Client', 'Product'])
        if self.privilege <= 2:
            self.pages['Partner'] = self.create_page('Partner', self)
            self.pages['Supplier Invoice'] = self.create_page('Supplier Invoice', self)
            self.pages['Client Invoice'] = self.create_page('Client Invoice', self)
            self.menu_list.addItems(['Partner', 'Supplier Invoice', 'Client Invoice'])
        if self.privilege <= 1:
            self.pages['Reports'] = self.create_page('Reports', self)
            self.menu_list.addItem('Reports')
        if self.privilege == 0:
            self.pages['Logs'] = self.create_page('Logs', self)
            self.menu_list.addItem('Logs')

        self.pages['Settings'] = self.create_page('⚙️ Settings Page')
        self.pages['About'] = self.create_page('ℹ️ About Page')
        self.menu_list.addItems(['Settings', 'About'])

    def switch_page(self, name):
        self.stack.setCurrentWidget(self.pages[name])

    def toggle_menu(self):
        self.dock.setVisible(not self.dock.isVisible())

    def closeEvent(self, event):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        event.accept()

    def connection_test_window(self):
        if self.conn:
            try:
                cur = self.conn.cursor()
                cur.execute('SELECT version();')
                version = cur.fetchone()
                QMessageBox.information(
                    self,
                    'Database Connection',
                    f"✅ Connected to PostgreSQL:\n{version[0]}"
                )
                cur.close()
                self.conn.close()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    'Database Error',
                    f"⚠️ Query failed:\n{e}"
                )
        else:
            QMessageBox.critical(
                self,
                'Database Connection',
                '❌ Failed to connect to PostgreSQL!'
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
