from dotenv import load_dotenv
from os import getenv

load_dotenv(dotenv_path="../.env")

production = getenv("PRODUCTION")

""" MONGODB setting """

if production == "true":
    mongodb_URI = f"mongodb://{getenv('MONGO_INITDB_ROOT_USERNAME')}:{getenv('MONGO_INITDB_ROOT_PASSWORD')}@mongodb_container:27017/"
elif production == "false":
    mongodb_URI = "mongodb://localhost:27017/"

print ("-----------------------------------drfwef-r-------------------\nfgvertergter-ergt retgertg")
print(mongodb_URI)
