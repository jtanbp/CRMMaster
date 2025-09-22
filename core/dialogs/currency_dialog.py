# 1. Standard Library

# 2. Third Party Library
import requests
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QLineEdit, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

# 3. Internal Library


# Thread to fetch rates
class FetchRatesThread(QThread):
    finished = Signal(dict)  # Emit rates as a dictionary

    def run(self):
        try:
            url = 'https://open.er-api.com/v6/latest/USD'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('result') != 'success':
                self.finished.emit({})
                return

            rates = data.get('rates', {})
            self.finished.emit(rates)
        except Exception:
            self.finished.emit({})


class CurrencyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Currency Rates to USD')
        self.resize(400, 600)

        layout = QVBoxLayout()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('Search currency...')
        self.search_bar.textChanged.connect(self.filter_table)
        layout.addWidget(self.search_bar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Currency', 'Rate'])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Start fetching rates
        self.thread = FetchRatesThread()
        self.thread.finished.connect(self.populate_table)
        self.thread.start()

        # Store rates for filtering
        self.rates = {}

    def populate_table(self, rates):
        self.rates = rates
        self.table.setRowCount(0)

        # Define preferred currencies order
        preferred = ['MYR', 'SGD', 'USD', 'EUR']

        # Create two lists: preferred first, then the rest sorted
        preferred_rates = [(cur, rates[cur]) for cur in preferred if cur in rates]
        other_rates = sorted((cur, rate) for cur, rate
                             in rates.items() if cur not in preferred)

        final_list = preferred_rates + other_rates

        # Populate table
        for row, (currency, rate) in enumerate(final_list):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(currency))
            self.table.setItem(row, 1, QTableWidgetItem(f'{rate:.4f}'))

    def filter_table(self, text):
        text = text.upper()
        self.table.setRowCount(0)
        for row, (currency, rate) in enumerate(sorted(self.rates.items())):
            if text in currency:
                self.table.insertRow(self.table.rowCount())
                self.table.setItem(
                    self.table.rowCount()-1, 0, QTableWidgetItem(currency))
                self.table.setItem(
                    self.table.rowCount()-1, 1, QTableWidgetItem(f'{rate:.4f}'))
