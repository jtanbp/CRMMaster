# 1. Standard Library

# 2. Third Party Library

# 3. Internal Library
from core import BasePageWidget
from database.partnerdb import PartnerFormDialog

# Define the column order matching your QTableWidget
COLUMN_ORDER = [
    'partner_id',
    'partner_name',
    'partner_contact',
    'description'
]

HEADERS = [
    'Partner ID',
    'Partner Name',
    'Contact',
    'Description'
]


class PartnerPage(BasePageWidget):
    def __init__(self, parent=None, dev_mode=False, conn=None):
        super().__init__(
            parent=parent,
            dev_mode=dev_mode,
            conn=conn,
            table_name='partner',
            column_order=COLUMN_ORDER,
            headers=HEADERS,
            dialog_class=PartnerFormDialog,
            data_name='Partner'
        )
