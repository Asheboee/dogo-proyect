from persistence.db import get_connection
from datetime import datetime
from enums.transaction_type import TransactionType
import pymysql

class Transaction ():
    #def __init__(self, id: int, description: str, date, amount: float, type: int, id_account: int):
    def __init__(self, id: int, description: str, date: datetime, amount: float, type: TransactionType):
        self.id = id
        self.description = description
        self.date = date
        self.amount = amount
        self.type = type  # 1 Ingreso - 2 Egreso


    # Obtiene el historial de transacciones de una cuenta especificada por su id
    @staticmethod
    def get_transactions_by_account(id_account):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            # Consultamos todas las transacciones de la cuenta
            sql = "SELECT id, description, date, amount, type, id_account FROM transaction WHERE id_account = %s ORDER BY date DESC"
            cursor.execute(sql, (id_account,))
            
            rows = cursor.fetchall()
            
            transactions = []
            for row in rows:
                transactions.append(Transaction(
                    row["id"], 
                    row["description"], 
                    row["date"], 
                    row["amount"], 
                    row["type"]
                ))
            
            cursor.close()
            connection.close()
            return transactions
        except Exception as ex:
            print(f"Error retrieving transactions: {ex}")
            return []