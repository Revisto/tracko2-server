import hashlib
import pymongo
from datetime import datetime
from validator_collection import is_none
import secrets


class General:
    def sha256_hash(self, password):
        result = hashlib.sha256(password.encode("utf-8"))
        return result.hexdigest()

    def timestamp(self):
        return datetime.now().strftime("%d-%m-%Y %H:%M:%S:%f")


class Authentication:
    def generate_api_key(self, length=50):
        generated_key = secrets.token_urlsafe(length)
        return generated_key

    def signup(self, username, password):
        if Authentication().is_username_unique(username) is False:
            return {"logged_in": False}
        hashed_password = General().sha256_hash(password)
        api_key = Database().add_user(username, hashed_password)["api_key"]
        return {"logged_in": True, "api_key": api_key}

    def login(self, username, password):
        hashed_password = General().sha256_hash(password)
        user_data = Database().get_user_data_with_username(username)
        if not is_none(user_data) and user_data["password"] == hashed_password:
            api_key = user_data["api_key"]
            return {"logged_in": True, "api_key": api_key}
        return {"logged_in": False}

    def is_username_unique(self, username):
        user_data = Database().get_user_data_with_username(username)
        if is_none(user_data):
            return {"is_it_unique": True}
        return {"is_it_unique": False}

    def is_api_key_valid(self, api_key):
        user_data = Database().get_user_data_with_api_key(api_key)
        if is_none(user_data):
            return True
        return False

class User:
    def get_specific_shelf(self, api_key, shelf_name):
        all_shelves = Database().get_all_shelves(api_key)
        if shelf_name in all_shelves:
            return all_shelves[shelf_name]
        return {}

class Database:
    def __init__(self):
        self.database = pymongo.MongoClient()["tracko"]

    def add_user(self, username, hashed_password):
        api_key = Authentication().generate_api_key()
        self.database.users.insert_one(
            {
                "username": username,
                "password": hashed_password,
                "api_key": api_key,
                "shelves": dict(),
            }
        )
        return {"api_key": api_key}

    def get_user_data_with_username(self, username):
        return self.database.users.find_one({"username": username})

    def get_user_data_with_api_key(self, api_key):
        return self.database.users.find_one({"api_key": api_key})

    def get_all_shelves(self, api_key):
        return self.database.users.find_one({"api_key": api_key})["shelves"]
