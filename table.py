import pymongo

from settings import connection_mongo, CA_file


class DB():
    def __init__(self, db_name, col_name):
        self.db = pymongo.MongoClient(connection_mongo, ssl=True, tlsCAFile=CA_file)[db_name]
        self.collection = self.db[col_name]

    def get_all_datas(self):
        return list(self.collection.find({}))

    def save_data(self, data):
        if isinstance(data, dict):
            return self.collection.insert_one(data).inserted_id

        else:
            if len(data):
                self.collection.insert_many(data)

    def update_item(self, id, data: dict):
        self.collection.update_one({'_id': id}, {'$set': data})

    def delete_data(self, data: dict):
        self.collection.delete_one(data)

    def clear(self):
        self.collection.drop()

#FB_table = DB('feedback_sng_db', 'feedback_sng')

#FB_table.clear()

'''
FB_list = FB_table.get_all_datas()

table_data = []

for fb in FB_list:
    a = []
    for i in fb.values():
        a.append(i)
    table_data.append(a)

'''