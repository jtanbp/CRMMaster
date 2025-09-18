# 1. Standard Library

# 2. Third Party Library

# 3. Internal Library
from core import BasePageWidget
from database.clientdb import ClientFormDialog

# Define the column order matching your QTableWidget
COLUMN_ORDER = [
    'client_id',
    'client_name',
    'client_contact',
    'client_type',
    'status',
    'description'
]

HEADERS = [
    'Client ID',
    'Client Name',
    'Contact',
    'Type',
    'Status',
    'Description'
]


class ClientPage(BasePageWidget):
    def __init__(self, parent=None, dev_mode=False, conn=None):
        super().__init__(
            parent=parent,
            dev_mode=dev_mode,
            conn=conn,
            table_name='client',
            column_order=COLUMN_ORDER,
            headers=HEADERS,
            dialog_class=ClientFormDialog,
            data_name='Client'
        )
