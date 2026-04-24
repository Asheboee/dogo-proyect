from enum import Enum

class ValuePermission(Enum):
    COSTUMER_EDIT = 1
    COSTUMER_DELETE = 2
    ACCOUNT = 3
    TRANSACTION_COMMIT = 4