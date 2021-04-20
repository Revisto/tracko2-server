import hashlib
import pymongo
from datetime import datetime
from validator_collection import is_none, is_numeric
import secrets
from setting import mongodb_URI

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
        username = username.lower()
        if Authentication().is_username_unique(username) is False:
            return {"logged_in": False}
        hashed_password = General().sha256_hash(password)
        api_key = Database().add_user(username, hashed_password)["api_key"]
        return {"logged_in": True, "api_key": api_key}

    def login(self, username, password):
        username = username.lower()
        hashed_password = General().sha256_hash(password)
        user_data = Database().get_user_data_with_username(username)
        if not is_none(user_data) and user_data["password"] == hashed_password:
            api_key = user_data["api_key"]
            return {"logged_in": True, "api_key": api_key}
        return {"logged_in": False}

    def is_username_unique(self, username):
        username = username.lower()
        user_data = Database().get_user_data_with_username(username)
        if is_none(user_data):
            return {"is_it_unique": True}
        return {"is_it_unique": False}

    def is_api_key_valid(self, api_key):
        user_data = Database().get_user_data_with_api_key(api_key)
        if is_none(user_data):
            return False
        return True

class User:
    def get_specific_shelf(self, api_key, shelf_name):
        all_shelves = Database().get_all_shelves(api_key)
        if shelf_name in all_shelves:
            return all_shelves[shelf_name]
        return {}

    def add_series_to_shelf(self, api_key, shelf_name, series_name):
        result = Database().add_series_to_shelf(api_key, shelf_name, series_name)
        if result is False:
            return {"status": False}
        return {"status": True}

    def move_series_to_shelf(self, api_key, series_name, from_shelf, to_shelf):
        all_shelves = Database().get_all_shelves(api_key)
        if from_shelf not in all_shelves or to_shelf not in all_shelves or series_name not in all_shelves[from_shelf]:
            return {"status": False}
        series_data = all_shelves[from_shelf][series_name]
        all_shelves[from_shelf].pop(series_name)
        all_shelves[to_shelf][series_name] = series_data
        Database().update_user_shelves(api_key, all_shelves)
        return {"status": True}
        
    def update_series(self, api_key, series_name, shelf_name, watched_till):
        watched_till_split = watched_till.split(":")
        all_shelves = Database().get_all_shelves(api_key)
        last_watched_till = all_shelves[shelf_name][series_name]["watched-till"]
        last_watched_till_split = last_watched_till.split(":")

        if len(watched_till_split) != 4:
            return {"status": False}
        for index in range (len(watched_till_split)):
            value = watched_till_split[index]
            if is_numeric(value) is False and value != "":
                return {"status": False}
            if value == "":
                watched_till_split[index] = last_watched_till_split[index]

        if shelf_name not in all_shelves or series_name not in all_shelves[shelf_name]:
            return {"status": False}
        
        all_shelves[shelf_name][series_name]["watched-till"] = ":".join(watched_till_split)
        Database().update_user_shelves(api_key, all_shelves)
        return {"status": True}

class Database:
    def __init__(self):
        self.database = pymongo.MongoClient(mongodb_URI)["tracko"]

    def add_user(self, username, hashed_password):
        api_key = Authentication().generate_api_key()
        self.database.users.insert_one(
            {
                "username": username,
                "password": hashed_password,
                "api_key": api_key,
                "shelves": {"want-to-watch":{}, "currently-watching":{}, "watched":{}},
            }
        )
        return {"api_key": api_key}

    def add_series_to_shelf(self, api_key, shelf_name, series_name):
        user_query = {"api_key": api_key}
        shelves = self.database.users.find_one(user_query)["shelves"]
        if shelf_name in shelves and series_name not in shelves[shelf_name]:
            shelves[shelf_name][series_name] = {"watched-till": "01:01:00:00"}
            self.database.users.update_one(user_query, {"$set":{"shelves": shelves}})
            return True
        return False

    def get_user_data_with_username(self, username):
        return self.database.users.find_one({"username": username})

    def get_user_data_with_api_key(self, api_key):
        return self.database.users.find_one({"api_key": api_key})

    def get_all_shelves(self, api_key):
        return self.database.users.find_one({"api_key": api_key})["shelves"]

    def update_user_shelves(self, api_key, shelves):
        user_query = {"api_key": api_key}
        self.database.users.update_one(user_query, {"$set":{"shelves": shelves}})
        return True
