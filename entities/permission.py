from enums.value_permission import ValuePermission
from persistence.db import get_connection
import pymysql


class Permission:
    # Constructor: cada permiso tiene un ID y un valor
    # que corresponde a un elemento del enum ValuePermission
    def __init__(self, id: int, value: ValuePermission):
        self.id = id
        self.value = value

    def get_permissions_by_user(id_user: int) -> list:
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT id, value FROM permission WHERE id_user = %s"
            cursor.execute(sql, (id_user,))
            rows = cursor.fetchall()

            cursor.close()
            connection.close()

            # Construimos la lista de objetos Permission
            permissions = []
            for row in rows:
                permissions.append(Permission(
                    row["id"],
                    row["value"]
                ))

            return permissions

        except Exception as ex:
            print(f"Error consultando permisos: {ex}")
            return []