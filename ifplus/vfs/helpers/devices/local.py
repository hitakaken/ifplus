# -*- coding: utf-8 -*-
import io
import mimetypes
import os
import urllib
from BeautifulSoup import BeautifulSoup
from errno import *
from flask import make_response, send_file
from ...models.exceptions import FuseOSError
from ifplus.vfs.models.actions import CONTENT_TYPE_BINARY, STORAGE_LOCALFS

mimetypes.init()


class LocalStorageDevice(object):
    """本地存储实现"""
    def __init__(self, rid, vfs=None,
                 local_storage_path=None, mount_point=None, use_relative=True,
                 buffer_size=16384, **kwargs):
        self.id = rid
        self.vfs = vfs
        self.local_storage_path = local_storage_path
        self.mount_point = mount_point
        self.use_relative = use_relative
        self.buffer_size = buffer_size

    def init_vfs(self, vfs):
        self.vfs = vfs

    def get_storage_path(self, file_path):
        """获取文件存储路径"""
        if self.use_relative:
            file_path = os.path.relpath(file_path, self.mount_point)
        elif file_path.startswith(u'/'):
            file_path = file_path[1:]
        return os.path.abspath(os.path.join(self.local_storage_path, file_path))

    def save(self, file_object, **kwargs):
        if u'dev' not in file_object.underlying:
            file_object.underlying[u'dev'] = self.id
        if file_object.is_newly:
            if file_object.content is not None:
                file_object.size = len(file_object.content) * 2
            try:
                storage_path = self.get_storage_path(file_object.real_path)
                if file_object.is_folder:
                    os.mkdir(storage_path, file_object.mode & 0o777)
                elif file_object.is_file:
                    if file_object.content is not None:
                        with open(storage_path, 'w') as f:
                            f.write(file_object.content)
                        f.close()
                    else:
                        if not os.path.exists(storage_path):
                            with open(storage_path, 'w') as f:
                                f.close()
            except OSError, err:
                raise FuseOSError(err.errno)
            self.vfs.mongo.db.files.insert_one(file_object.underlying)
        else:
            update_document = {u'$set': {}}
            if file_object.content is not None:
                file_object.size = len(file_object.content) * 2
                raise FuseOSError(EINVAL)
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
            try:
                storage_path = self.get_storage_path(file_object.real_path)
                if file_object.is_folder:
                    pass
                elif file_object.is_file:
                    if file_object.content is not None:
                        raise FuseOSError(EINVAL)
            except OSError, err:
                raise FuseOSError(err.errno)
            self.vfs.mongo.db.files.update_one({u'_id': file_object.id}, update_document)

    def remove(self, file_object, **kwargs):
        storage_path = self.get_storage_path(file_object.real_path)
        use_trash = u'trash' in kwargs and kwargs[u'trash']
        if file_object.is_folder:
            query = {}
            for index, partname in enumerate(file_object.partnames):
                query[u'ancestors.' + str(index)] = partname
            results = self.vfs.mongo.db.files.find(query)
            if use_trash:
                self.vfs.mongo.db.trashs.insert_many(results)
            else:
                os.rmdir(storage_path)
            self.vfs.mongo.db.files.delete_many(query)
        if use_trash:
            self.vfs.mongo.db.trashs.insert_one(file_object.underlying)
        elif os.path.exists(storage_path):
                os.remove(storage_path)
        result = self.vfs.mongo.db.files.delete_one({u'_id': file_object.id})
        if result.deleted_count > 0:
            return {}
        else:
            raise FuseOSError(EIO)

    def write_stream(self, file_object, stream, **kwargs):
        storage_path = self.get_storage_path(file_object.real_path)
        # output = io.open(storage_path, mode='wb', buffering=self.buffer_size)
        try:
            from shutil import copyfileobj
            dst = open(storage_path, 'wb')
            try:
                """copy data from file-like object fsrc to file-like object fdst"""
                while 1:
                    buf = stream.stream.read(self.buffer_size)
                    if not buf:
                        break
                    dst.write(buf)
            finally:
                dst.close()
            file_object.size = os.path.getsize(storage_path)
        except:
            raise FuseOSError(EIO)
        file_object.modified()
        file_object.storage_type = STORAGE_LOCALFS
        file_object.content_type = CONTENT_TYPE_BINARY
        self.save(file_object)

    def read_stream(self, file_object, **kwargs):
        storage_path = self.get_storage_path(file_object.real_path)
        if not os.path.exists(storage_path):
            raise FuseOSError(ENOENT)
        ext_name = file_object.ext_name
        resp = send_file(storage_path,
                         mimetype=mimetypes.types_map[ext_name]
                         if ext_name is not None and ext_name in mimetypes.types_map
                         else 'application/octet-stream',
                         attachment_filename=file_object.name.encode('utf8'))
        # file_name = urllib.quote(file_object.name.encode('utf8'))
        # resp.headers['Content-Disposition'] = 'attachment; filename=%s' % file_name
        if file_object.is_changed:
            self.save(file_object)
        return resp

    def read_text(self, file_object, **kwargs):
        text = u''
        storage_path = self.get_storage_path(file_object.real_path)
        if not os.path.exists(storage_path):
            return text
        with open(storage_path, 'rb') as f:
            input = f.read()
            f.close()
            soup = BeautifulSoup(input)
            return soup.contents[0]
        return text