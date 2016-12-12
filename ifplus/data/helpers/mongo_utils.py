# -*- coding: utf-8 -*-
def init_collection(db, collection_name):
    collection_names = db.collection_names()
    if collection_name not in collection_names:
        db.create_collection(collection_name)
    return db[collection_name]

def init_indexes(db, collection_name, mongo_indexes):
    collection = init_collection(db, collection_name)
    indexes = collection.index_information
    indexes_to_create = []
    for mongo_index in mongo_indexes:
        if mongo_index.document[u'name'] not in indexes:
            indexes_to_create.append(mongo_index)
    if len(indexes_to_create) > 0:
        collection.create_indexes(indexes_to_create)
