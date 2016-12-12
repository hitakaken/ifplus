# -*- coding: utf-8 -*-
# bitsAllSet
import os
from errno import *
from ..base.operations import Operations, FuseOSError
from ..models.file import FileObject
# from .devices import MongoDevice


class VirtualFileSystem(object):
    def __init__(self, app, devices=None, **kwargs):
        # super(VirtualFileSystem, self).__init__(**kwargs)
        self.mongo = app.mongo  # MongoDB Collection: files
        self.cache = app.cache

    def register(self, device):
        pass

    # def start(self):
    #     collection_names = self.mongo.db.collection_names()
    #     if 'files' not in collection_names:
    #         self.mongo.db.create_collection('files')
    #     indexes = self.mongo.db.files.index_information()
    #     indexes_to_create = []
    #     for file_index in FileMetaInfo.MONGO_INDEXES + FileTreeNode.MONGO_INDEXES:
    #         if file_index.document['name'] not in indexes:
    #             indexes_to_create.append(file_index)
    #     if len(indexes_to_create) > 0:
    #         self.mongo.db.files.create_indexes(indexes_to_create)

    # def device_of(self, file_path):
    #     path = file_path
    #     while path != '/':
    #         folder = os.path.dirname(path)
    #         if folder in self.devices:
    #             return self.devices[folder]
    #     return self.devices['/']
    #
    # def device_path(self, file_path, device=None):
    #     device = device if device is not None else self.device_of(file_path)
    #     return os.path.relpath(file_path, device.root)

    def resolve_file_path(self, file_path, **kwargs):
        pass

    def lookup(self, file_path):
        pass

    def mkdir(self, file_path, **kwargs):
        pass


