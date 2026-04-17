from persistence.db import get_connection
import pymysql

class Account:
    def __init__(self, id, number, creation_date, id_user):
        self.id = id
        self.number = number
        self.creation_date = creation_date
        self.id_user = id_user

    @staticmethod
    def check_account(id_user):
        """Verifica si el usuario ya tiene una cuenta asociada."""
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT number FROM account WHERE id_user = %s"
            cursor.execute(sql, (id_user,))
            row = cursor.fetchone()
            cursor.close()
            connection.close()
            return row is not None
        except Exception as ex:
            print(f"Error en check_account: {ex}")
            return False

    @staticmethod
    def get_by_user_id(id_user):
        """Retorna el objeto Account del usuario, o None si no tiene cuenta."""
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT id, number, creation_date, id_user FROM account WHERE id_user = %s"
            cursor.execute(sql, (id_user,))
            row = cursor.fetchone()
            cursor.close()
            connection.close()
            if row:
                return Account(row["id"], row["number"], row["creation_date"], row["id_user"])
            return None
        except Exception as ex:
            print(f"Error en get_by_user_id: {ex}")
            return None

    @staticmethod
    def get_balance(id_account):
        """
        Calcula el saldo actual de la cuenta.
        Suma los ingresos (type=1) y resta los egresos (type=2).
        Retorna el saldo como float, o 0.0 si no hay transacciones o hay error.
        """
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = """
                SELECT 
                    COALESCE(SUM(CASE WHEN type = 1 THEN amount ELSE 0 END), 0) AS ingresos,
                    COALESCE(SUM(CASE WHEN type = 2 THEN amount ELSE 0 END), 0) AS egresos
                FROM transaction
                WHERE id_account = %s
            """
            cursor.execute(sql, (id_account,))
            row = cursor.fetchone()
            cursor.close()
            connection.close()
            if row:
                return float(row["ingresos"]) - float(row["egresos"])
            return 0.0
        except Exception as ex:
            print(f"Error en get_balance: {ex}")
            return 0.0