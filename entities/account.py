from persistence.db import get_connection
from datetime import datetime
from entities.user import User
from entities.transaction import Transaction
import pymysql

class Account ():
    def __init__(self, id: int, number: str, creation_date: datetime, user: User, transactions: list):
        self.id = id
        self.number = number
        self.creation_date = creation_date
        self.user = user
        self.transactions = transactions


    # Metodo para obtener la cuenta de un usuario por su id_user
    def get_account_by_user(id_user: int):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT id, number, creation_date, id_user FROM account WHERE id_user = %s"
            cursor.execute(sql, (id_user,))

            rs = cursor.fetchone()

            user = User.get_by_id(rs["id_user"])
            transactions = Transaction.get_transactions_by_account(rs["id"])

            account = Account(
                rs["id"],
                rs["number"],
                rs["creation_date"],
                user,
                transactions
            )
            return account
        except Exception as ex:
            print(f"Error retrieving account: {ex}")
            return None
        


    def calculate_balance(account):
        balance = 0.0
        for transaction in account.transactions:
            if transaction.type == 1:  # Ingreso
                balance += float(transaction.amount)
            elif transaction.type == 2:  # Egreso
                balance -= float(transaction.amount)
        return balance