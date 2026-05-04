from persistence.db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from enums.profile import Profile
from entities.permission import Permission
import pymysql
from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, id: int, name: str, email: str, password: str,
                 profile: Profile = None, permissions: list = None, is_active: bool = True):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.profile = profile
        self.permissions = permissions if permissions is not None else []
        # Convertimos explicitamente a bool por si la BD retorna 0 o 1 como entero
        self._is_active = bool(is_active)

    # Flask-Login usa esta propiedad para saber si el usuario puede iniciar sesion
    @property
    def is_active(self):
        return self._is_active

    # Flask-Login usa esta propiedad para identificar al usuario en la sesion
    def get_id(self):
        return str(self.id)

    # Verifica si un correo ya existe en la BD antes de registrar
    def check_email_exists(email: str) -> bool:
        connection = get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        sql = "SELECT email FROM user WHERE email = %s"
        cursor.execute(sql, (email,))
        row = cursor.fetchone()

        cursor.close()
        connection.close()
        return row is not None

    # Guarda un nuevo usuario en la BD con contraseña hasheada
    def save(name: str, email: str, password: str) -> bool:
        try:
            connection = get_connection()
            cursor = connection.cursor()

            hash_password = generate_password_hash(password)

            sql = "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, email, hash_password))
            connection.commit()

            cursor.close()
            connection.close()
            return True

        except Exception as ex:
            print(f"Error saving user: {ex}")
            return False


    # Verifica las credenciales de login
    # Retorna un objeto User si son correctas, None si no
    def check_login(email: str, password: str):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT id, name, email, password, profile, is_active FROM user WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user and check_password_hash(user["password"], password):
                permissions = Permission.get_permissions_by_user(user["id"]) #hablamos a user-permission desde la clase permission 
                return User(
                    user["id"],
                    user["name"],
                    user["email"],
                    "",                  # No guardamos el hash en sesion por seguridad
                    user["profile"],
                    permissions,
                    bool(user["is_active"])  # Conversión explicita a bool
                )

            return None

        except Exception as ex:
            print(f"Error login user: {ex}")
            return False


    # Obtiene un usuario por su ID
    # Flask-Login llama a este metodo en cada request para
    # restaurar la sesion activa del usuario
    def get_by_id(id: int):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT id, name, email, password, profile, is_active FROM user WHERE id = %s"
            cursor.execute(sql, (id,))
            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user:
                permissions = Permission.get_permissions_by_user(user["id"])
                return User(
                    user["id"],
                    user["name"],
                    user["email"],
                    user["password"],
                    user["profile"],
                    permissions,
                    bool(user["is_active"])  # se convierte a bool 
                )

            return None

        except Exception as ex:
            print(f"Error get_by_id: {ex}")
            return False