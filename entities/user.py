from persistence.db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from enums.profile import Profile
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
        self._is_active = is_active

    @property
    def is_active(self):
        return self._is_active

    @staticmethod
    def check_email_exists(email) -> bool:
        connection = get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT email FROM user WHERE email = %s"
        cursor.execute(sql, (email,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        return row is not None

    @staticmethod
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

    @staticmethod
    def check_login(email, password):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT id, name, email, password FROM user WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            if user and check_password_hash(user["password"], password):
                return User(user["id"], user["name"], user["email"], "")
            return None
        except Exception as ex:
            print(f"Error login user: {ex}")
            return None

    @staticmethod
    def get_by_id(id):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT id, name, email, password FROM user WHERE id = %s"
            cursor.execute(sql, (id,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            if user:
                return User(user["id"], user["name"], user["email"], user["password"])
            return None
        except Exception as ex:
            print(f"Error get_by_id: {ex}")
            return None