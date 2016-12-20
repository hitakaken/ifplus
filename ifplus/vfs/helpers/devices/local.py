# -*- coding: utf-8 -*-
import mimetypes
import urllib
from errno import *
from flask import make_response
from ...models.exceptions import FuseOSError
from ifplus.vfs.models.actions import CONTENT_TYPE_BINARY, STORAGE_GRIDFS, STORAGE_OBJECT


class LocalStorageDevice(object):
    def __init__(self, rid, vfs=None, **kwargs):
        self.id = rid
        self.vfs = vfs

    def init_vfs(self, vfs):
        self.vfs = vfs

    def save(self, file_object, **kwargs):
        if u'dev' not in file_object.underlying:
            file_object.underlying[u'dev'] = self.id
        if file_object.is_newly:
            if file_object.content is not None:
                file_object.size = len(file_object.content) * 2
            self.vfs.mongo.db.files.insert_one(file_object.underlying)
            if file_object.content is not None:
                self.vfs.mongo.db.contents.insert_one({
                    u'_id': file_object.id,
                    u'content': file_object.content
                })
        else:
            update_document = {u'$set': {}}
            if file_object.content is not None:
                file_object.size = len(file_object.content) * 2
            for key in file_object.changes[u'inodes']:
                update_document[u'$set'][key] = file_object.underlying[key]
            if file_object.changes[u'acl']:
                update_document[u'$set'][u'acl'] = file_object.underlying[u'acl']
            if file_object.changes[u'hits'] > 0:
                update_document[u'$inc'] = {
                    [u'hits.o', u'hits.g', u'hits.u', u'hits.p'][file_object.changes[u'hits']-1]: 1
                }
            for key in file_object.changes[u'content']:
                update_document[u'$set'][u'content.' + key] = file_object.underlying[u'content'][key]
            for key in file_object.changes[u'xattrs']:
                update_document[u'$set'][u'xattrs.' + key] = file_object.underlying[u'xattrs'][key]
            self.vfs.mongo.db.files.update_one({u'_id': file_object.id}, update_document)
            if file_object.content is not None:
                self.vfs.mongo.db.contents.update_one(
                    {u'_id': file_object.id},
                    {u'$set': {u'content': file_object.content}, u'setOnInsert': {u'_id': file_object.id}},
                    upsert=True)

    def remove(self, file_object, **kwargs):
        if file_object.is_folder:
            query = {}
            for index, partname in enumerate(file_object.partnames):
                query[u'ancestors.' + str(index)] = partname
            results = self.vfs.mongo.db.files.find(query)
            for result in results:
                self.vfs.mongo.db.trashs.insert_one(result)
            self.vfs.mongo.db.files.delete_many(query)
        self.vfs.mongo.db.trashs.insert_one(file_object.underlying)
        result = self.vfs.mongo.db.files.delete_one({u'_id': file_object.id})
        if result.deleted_count > 0:
            return {}
        else:
            raise FuseOSError(EIO)

    def write_stream(self, file_object, stream, **kwargs):
        self.vfs.mongo.save_file(file_object.fid, stream)
        stored_file = self.vfs.mongo.db[u'fs.files'].find_one_or_404({u'filename': file_object.fid})
        file_object.size = stored_file[u'length']
        file_object.modified()
        file_object.storage_type = STORAGE_GRIDFS
        file_object.content_type = CONTENT_TYPE_BINARY
        self.save(file_object)

    def read_stream(self, file_object, **kwargs):
        if file_object.storage_type == STORAGE_GRIDFS:
            resp = self.vfs.mongo.send_file(file_object.fid)
        elif file_object.storage_type == STORAGE_OBJECT:
            content = self.vfs.mongo.db.contents.find_one({u'_id': file_object.id})
            if content is not None:
                text = content[u'content']
            else:
                text = content
            resp = make_response(text)
        else:
            raise FuseOSError(ENOENT)
        ext_name = file_object.ext_name
        if ext_name is not None and ext_name in mimetypes.types_map:
            resp.headers['Content-Type'] = mimetypes.types_map[ext_name]
        else:
            resp.headers['Content-Type'] = 'application/octet-stream'
        file_name = urllib.quote(file_object.name.encode('utf8'))
        resp.headers['Content-Disposition'] = 'attachment; filename=%s' % file_name
        if file_object.is_changed:
            self.save(file_object)
        return resp

    def read_text(self, file_object, **kwargs):
        text = u''
        if file_object.storage_type == STORAGE_OBJECT:
            content = self.vfs.mongo.db.contents.find_one({u'_id': file_object.id})
            if content is not None:
                text = content[u'content']
        elif file_object.storage_type == STORAGE_GRIDFS:
            storage = GridFS(self.vfs.mongo.db, u'fs')
            try:
                fileobj = storage.get_version(filename=file_object.fid, version=-1)
                text = fileobj.read()
            except NoFile:
                pass
        return text