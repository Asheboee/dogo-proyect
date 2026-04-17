from persistence.db import get_connection
import pymysql

class Transaction:
    def __init__(self, id: int, description: str, date, amount: float, type: int, id_account: int):
        self.id = id
        self.description = description
        self.date = date
        self.amount = amount
        self.type = type  # 1 Ingreso - 2 Egreso
        self.id_account = id_account

    @staticmethod
    def get_by_account(id_account):
        """
        Obtiene el historial de transacciones de una cuenta especificada por su id
        """
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
                    row["type"], 
                    row["id_account"]
                ))
            
            cursor.close()
            connection.close()
            return transactions
        except Exception as ex:
            print(f"Error retrieving transactions: {ex}")
            return []

    @staticmethod
    def save(description, amount, type, id_account):
        """
        Registra una nueva transaccion en la base de datos
        """
        try:
            connection = get_connection()
            cursor = connection.cursor()

            sql = "INSERT INTO transaction (description, amount, type, id_account, date) VALUES (%s, %s, %s, %s, NOW())"
            cursor.execute(sql, (description, amount, type, id_account))
            
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as ex:
            print(f"Error saving transaction: {ex}")
            return False