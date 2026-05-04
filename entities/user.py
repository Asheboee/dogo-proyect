from persistence.db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from enums.profile import Profile
from entities.permission import Permission
import pymysql
from flask_login import UserMixin


class User(UserMixin):

    # ----------------------------------------------------------
    # Constructor: define los atributos de cada objeto User.
    # _is_active con guión bajo evita conflicto con la propiedad
    # is_active de Flask-Login, que sobreescribimos más abajo.
    # ----------------------------------------------------------
    def __init__(self, id: int, name: str, email: str, password: str,
                 profile: Profile = None, permissions: list = None, is_active: bool = True):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.profile = profile
        self.permissions = permissions if permissions is not None else []
        self._is_active = is_active

    # ----------------------------------------------------------
    # Propiedad requerida por Flask-Login.
    # Retorna True si el usuario puede iniciar sesión,
    # False si su cuenta está deshabilitada (is_active = 0 en BD).
    # ----------------------------------------------------------
    @property
    def is_active(self):
        return self._is_active


    # ----------------------------------------------------------
    # Verifica si un correo ya existe en la BD antes de registrar.
    # Retorna True si ya está registrado, False si está disponible.
    # ----------------------------------------------------------
    def check_email_exists(email: str) -> bool:
        connection = get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        sql = "SELECT email FROM user WHERE email = %s"
        cursor.execute(sql, (email,))
        row = cursor.fetchone()

        cursor.close()
        connection.close()
        return row is not None


    # ----------------------------------------------------------
    # Guarda un nuevo usuario en la BD.
    # Nunca guarda la contraseña en texto plano, siempre como hash.
    # Retorna True si se guardó bien, False si hubo error.
    # ----------------------------------------------------------
    def save(name: str, email: str, password: str) -> bool:
        try:
            connection = get_connection()
            cursor = connection.cursor()

            # Convertimos la contraseña a hash antes de guardar
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


    # ----------------------------------------------------------
    # Verifica las credenciales de login.
    # CORRECCIONES aplicadas:
    #   1. Se agregó 'password' a la query SQL (faltaba la coma).
    #   2. Se corrigió el orden de argumentos al construir User.
    #   3. Se agregó la carga de permisos con Permission.get_permissions_by_user.
    # Retorna un objeto User si las credenciales son correctas,
    # None si el email no existe o la contraseña no coincide.
    # ----------------------------------------------------------
    def check_login(email: str, password: str):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            # CORRECCIÓN 1: Se incluyó 'password' en la query con la coma correcta
            sql = "SELECT id, name, email, password, profile, is_active FROM user WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user and check_password_hash(user["password"], password):
                # CORRECCIÓN 2: Se carga la lista de permisos del usuario
                permissions = Permission.get_permissions_by_user(user["id"])

                # CORRECCIÓN 3: Se corrigió el orden y los argumentos del constructor
                return User(
                    user["id"],
                    user["name"],
                    user["email"],
                    "",                  # No guardamos el hash en sesión por seguridad
                    user["profile"],
                    permissions,
                    user["is_active"]
                )

            return None

        except Exception as ex:
            print(f"Error login user: {ex}")
            return False


    # ----------------------------------------------------------
    # Obtiene un usuario por su ID.
    # Flask-Login llama a este método en cada request para
    # restaurar la sesión activa del usuario.
    # CORRECCIONES aplicadas:
    #   1. Se agregó 'profile' e 'is_active' a la query SQL.
    #   2. Se cargan los permisos del usuario.
    #   3. Se pasan todos los campos al constructor de User.
    # ----------------------------------------------------------
    def get_by_id(id: int):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            # CORRECCIÓN: Se incluyeron profile e is_active en la query
            sql = "SELECT id, name, email, password, profile, is_active FROM user WHERE id = %s"
            cursor.execute(sql, (id,))
            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user:
                # CORRECCIÓN: Se cargan los permisos del usuario
                permissions = Permission.get_permissions_by_user(user["id"])

                return User(
                    user["id"],
                    user["name"],
                    user["email"],
                    user["password"],
                    user["profile"],
                    permissions,
                    user["is_active"]
                )

            return None

        except Exception as ex:
            print(f"Error get_by_id: {ex}")
            return False