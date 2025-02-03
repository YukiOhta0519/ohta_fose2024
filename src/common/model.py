import pymongo


uri = "mongodb://{}:{}@{}:{}/?authSource=admin".format(
    "root",
    "password",
    "localhost",
    "27018",
)
client = pymongo.MongoClient(uri)

class DB_Controller:
    def __init__(self):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client["mscc"]

    def insert_datas(self, datas: list, collection_name: str):
        collection = self.db[collection_name]
        collection.insert_many(datas)

    def get_clone_set_list(self, meta: tuple, lang: str):
        index, _identifier = meta
        collection = self.db["sets"]
        return collection.find({"$and": [{"index": index}, {"lang": lang}]})
    
    def get_product_clone_set_list(self, meta: tuple, lang: str):
        index, _identifier = meta
        collection = self.db["product_sets"]
        return collection.find({"$and": [{"index": index}, {"lang": lang}]})
    
    def get_test_clone_set_list(self, meta: tuple, lang: str):
        index, _identifier = meta
        collection = self.db["test_sets"]
        return collection.find({"$and": [{"index": index}, {"lang": lang}]})
    
    def get_file_path_dict(self, meta: tuple, lang: str) -> dict:
        index, _identifier = meta
        collection = self.db["files"]
        result = {}
        for file in collection.find({"$and": [{"index": index}, {"lang": lang}]}):
            result[file["id"]] = file["path"]
        print("ファイル数: ", len(result))
        return result
    
    def get_file_list(self, meta: tuple, lang: str, collection_name: str) -> list:
        index, _identifier = meta
        collection = self.db[collection_name]
        return collection.find({"$and": [{"index": index}, {"lang": lang}]})
