# 1. Standard Library

# 2. Third Party Library

# 3. Internal Library
from core import BasePageWidget
from database.supplierdb import SupplierFormDialog

# Define the column order matching your QTableWidget
COLUMN_ORDER = [
    'supplier_id',
    'supplier_name',
    'supplier_contact',
    'supplier_type',
    'supplier_status',
    'description',
    'contract_start',
    'contract_end'
]

HEADERS = [
    'Supplier ID',
    'Supplier Name',
    'Contact',
    'Type',
    'Status',
    'Description',
    'Contract Start',
    'Contract End'
]


class SupplierPage(BasePageWidget):
    def __init__(self, parent=None, dev_mode=False, conn=None):
        super().__init__(
            parent=parent,
            dev_mode=dev_mode,
            conn=conn,
            table_name='supplier',
            column_order=COLUMN_ORDER,
            headers=HEADERS,
            dialog_class=SupplierFormDialog,
            data_name='Supplier'
        )
