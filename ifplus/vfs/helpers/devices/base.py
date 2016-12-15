# -*- coding: utf-8 -*-
import mimetypes
import urllib
from errno import *
from flask import make_response
from ...models.exceptions import FuseOSError
from ifplus.vfs.models.actions import CONTENT_TYPE_BINARY, STORAGE_GRIDFS, STORAGE_OBJECT

mimetypes.init()


class Operations(object):
    def destroy(self):
        pass

    def lookup(self, fid, name, ctx):
        pass

    def _lookup(self, fid, name, ctx):
        pass

    def getattr(self, id_, ctx):
        pass

    def readlink(self, id_, ctx):
        pass

    def opendir(self, id_,  ctx):
        pass

    def readdir(self, id_,  off):
        pass

    def getxattr(self, id_, name, ctx):
        pass

    def listxattr(self, id_, ctx):
        pass

    def setxattr(self, id_, name, value, ctx):
        pass

    def removexattr(self, id_, name, ctx):
        pass

    def lock_tree(self, id0):
        pass

    def remove_tree(self, id_p0, name0):
        pass

    def copy_tree(self, src_id, target_id):
        pass

    def unlink(self, id_p, name, ctx):
        pass

    def rmdir(self, id_p, name, ctx):
        pass

    def _remove(self, id_p, name, id_, force=False):
        pass

    def symlink(self, id_p, name, target, ctx):
        pass

    def rename(self, id_p_old, name_old, id_p_new, name_new, ctx):
        pass

    def _add_name(self, name):
        pass

    def _del_name(self, name):
        pass

    def _rename(self, id_p_old, name_old, id_p_new, name_new):
        pass

    def _replace(self, id_p_old, name_old, id_p_new, name_new, id_old,id_new):
        pass

    def link(self, id_, new_id_p, new_name, ctx):
        pass

    def setattr(self, id_, attr, fields, fh, ctx):
        pass

    def mknod(self, id_p, name, mode, rdev, ctx):
        pass

    def mkdir(self, id_p, name, mode, ctx):
        pass

    def extstat(self):
        pass

    def statfs(self, ctx):
        pass

    def open(self, id_, flags, ctx):
        pass

    def access(self, id_, mode, ctx):
        pass

    def create(self, id_p, name, mode, flags, ctx):
        pass

    def _create(self, id_p, name, mode, ctx, rdev, size):
        pass

    def read(self, fh, offset, length):
        pass

    def write(self, fh, offset, buf):
        pass

    def _readwrite(self, id_, offset, arg, buf=None, length=None):
        pass

    def fsync(self, fh, datasync):
        pass

    def forget(self, forget_list):
        pass

    def fsyncdir(self, fh, datasync):
        pass

    def releasedir(self):
        pass

    def release(self):
        pass

    def flush(self):
        pass


class RootDevice(Operations):
    def __init__(self, rid, vfs=None):
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
        text = ''
        if file_object.storage_type == STORAGE_OBJECT:
            content = self.vfs.mongo.db.contents.find_one({u'_id': file_object.id})
            if content is not None:
                text = content[u'content']
        elif file_object.storage_type == STORAGE_GRIDFS:
            resp = self.vfs.mongo.send_file(file_object.fid)
        return text
