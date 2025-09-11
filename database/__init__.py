from database.clientdb.client_widget import ClientPage
from database.database_functions import get_connection
from database.partnerdb.partner_widget import PartnerPage
from database.supplierdb.supplier_widget import SupplierPage

# Explicitly define what this package exports
__all__ = [
    "ClientPage",
    "get_connection",
    "PartnerPage",
    "SupplierPage",
]
