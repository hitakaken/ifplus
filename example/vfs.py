# -*- coding: utf-8 -*-
import datetime
import time
import calendar
from bson import ObjectId

import pymongo
now = datetime.datetime.utcnow()
print time.mktime(now.timetuple())
print int(calendar.timegm(now.timetuple()) * 1000 + now.microsecond / 1000)

files = [
    {
        "name": "新能源汽车",
        "acl": [{"sid": "r:7b49ef92-b9cb-4388-b5a7-a261b79ac5fa", "mask": -2088599552}, ],
        "uid": "u:7bd71624-a961-47a8-bea0-d601625b9941",
        "gid": "r:7b49ef92-b9cb-4388-b5a7-a261b79ac5fa",
        "xattrs": {
            "system": {"source": "mssql://dongge:dongge@192.168.0.2:57993/dbname=sh&table= Modules&ModuleID=470"},
            "dc": {}},
        "uuid": "97523ACC-FD8E-4809-BF7C-E475795E758B",
        "parent": "278E0D1E-0099-4505-BDB3-1CB296FDBD4A",
        "ancestors": ["上海行业情报服务网", "情报产品", "简报", "《第一情报·新能源汽车》"],
        "mode": -2147466772,
        "create": "2010-08-31T11:25:52.000Z",
        "atime": "2016-11-01T11:25:52.000Z",
        "ctime": "2010-08-31T11:25:52.000Z",
        "mtime": "2010-08-31T11:25:52.000Z",
        "dev": None,
        "nlink": 1,
        "size": 0
    },
    {
        "name": "上海行业情报服务网",
        "acl": [{"sid": "r:7b49ef92-b9cb-4388-b5a7-a261b79ac5fa", "mask": -2088599552}],
        "uid": "u:7bd71624-a961-47a8-bea0-d601625b9941",
        "gid": "r:7b49ef92-b9cb-4388-b5a7-a261b79ac5fa",
        "xattrs": {"system": {"source": "mssql://dongge:dongge@192.168.0.2:57993/dbname=sh&table=Portals&PortalID=0"},
                   "dc": {"description": "上海行业情报服务网", "subject": "科技查新,专利检索,专利地图", "language": "zh-CN"}},
        "uuid": "E92CC368-53AD-45AF-9899-BA790D276A38",
        "parent": None,
        "ancestors": [],
        "mode": 0x80000000 | 0o040750,
        "create": "2010-08-31T11:25:52.000Z",
        "atime": "2016-11-01T11:25:52.000Z",
        "ctime": "2010-08-31T11:25:52.000Z",
        "mtime": "2010-08-31T11:25:52.000Z",
        "dev": None,
        "nlink": 1,
        "size": 0
    },
    {
        "name": "2010年08期",
        "acl": [{"sid": "r:7b49ef92-b9cb-4388-b5a7-a261b79ac5fa", "mask": -2088599552}],
        "uid": "u:ce414832-e0f3-4a78-82f6-d1daa221d147",
        "gid": "r:7b49ef92-b9cb-4388-b5a7-a261b79ac5fa",
        "xattrs": {"system":
                       {"source": "mssql://dongge:dongge@192.168.0.2:57993/dbname?table= C_info&InfoID=5294"},
                   "hits": {"p": 87},
                   "dc": {"description": "", "subject": ["新能源汽车"],
                          "source": "上海科学技术情报研究所"},
                   "bibo": {"shortTitle": "最新资讯",
                            "authorList": ["祝毓", "庄盛", "路炜"]},
                   "user": {"ggfs": "摘编"}},
        "uuid": "136EC70D-05FC-4731-A2E8-3A80239DF201",
        "parent": "97523ACC-FD8E-4809-BF7C-E475795E758B",
        "ancestors": ["上海行业情报服务网", "情报产品", "简报", "《第一情报·新能源汽车》", "新能源汽车"],
        "mode": -2147466772,
        "creator": "u:ce414832-e0f3-4a78-82f6-d1daa221d147",
        "create": "2010-08-31T11:25:52.000Z",
        "atime": "2016-11-01T11:25:52.000Z",
        "ctime": "2010-08-31T11:25:52.000Z",
        "mtime": "2010-08-31T11:25:52.000Z",
        "dev": None,
        "nlink": 1,
        "size": 0
    },
    {
        "name": "《第一情报·新能源汽车》",
        "acl": [{"sid": "r:7b49ef92-b9cb-4388-b5a7-a261b79ac5fa", "mask": -2088599552}],
        "uid": "u:7bd71624-a961-47a8-bea0-d601625b9941",
        "gid": "r:7b49ef92-b9cb-4388-b5a7-a261b79ac5fa",
        "xattrs": {"system": {"source": "mssql://dongge:dongge@192.168.0.2:57993/dbname=sh&table=Tabs&TabID=125"},
                   "dc": {
                       "description": "低碳、新能源、哥本哈根无疑是2009 年度的热门话题。作为节能减排的重要领域之一，新能源汽车也当之无愧地成为“耀眼的明星”。尽管对于新能源汽车的发展，业内存在不同的声音，但可以肯定的是，传统汽车的升级换代和技术革新已经势不可挡。<br>　　低碳、新能源、哥本哈根无疑是2009 年度的热门话题。作为节能减排的重要领域之一，新能源汽车也当之无愧地成为“耀眼的明星”。尽管对于新能源汽车的发展，业内存在不同的声音，但可以肯定的是，传统汽车的升级换代和技术革新已经势不可挡。　　《第一情报·新能源汽车》的创刊，旨在提供国内外新能源汽车领域的最新发展动态和政策导向，切实发挥预警、竞合、战略的“第一情报”功能。简报为月刊形式，每月末发布。",
                       "subject": ["新能源", "汽车", "混合动力", "生物燃料", "燃料电池"]
                   }
                   },
        "uuid": "278E0D1E-0099-4505-BDB3-1CB296FDBD4A",
        "parent": "57EF5EA0-3CC1-4154-950A-DE14A1664CA6",
        "ancestors": ["上海行业情报服务网", "情报产品", "简报"],
        "mode": -2147466772,
        "create": "2010-08-31T11:25:52.000Z",
        "atime": "2016-11-01T11:25:52.000Z",
        "ctime": "2010-08-31T11:25:52.000Z",
        "mtime": "2010-08-31T11:25:52.000Z",
        "dev": None,
        "nlink": 1,
        "size": 0
    },
    {
        "name": "情报产品",
        "acl": [{"sid": "r:7b49ef92-b9cb-4388-b5a7-a261b79ac5fa", "mask": -2088599552}],
        "uid": "u:7bd71624-a961-47a8-bea0-d601625b9941",
        "gid": "r:7b49ef92-b9cb-4388-b5a7-a261b79ac5fa",
        "xattrs": {"system": {"source": "mssql://dongge:dongge@192.168.0.2:57993/dbname=sh&table=Tabs&TabID=64"},
                   "dc": {"description": "", "subject": ""}},
        "uuid": "2E06A99B-5017-400B-95C3-2A433AEB11AA",
        "parent": "E92CC368-53AD-45AF-9899-BA790D276A38",
        "ancestors": ["上海行业情报服务网"],
        "mode": -2147466772,
        "create": "2010-08-31T11:25:52.000Z",
        "atime": "2016-11-01T11:25:52.000Z",
        "ctime": "2010-08-31T11:25:52.000Z",
        "mtime": "2010-08-31T11:25:52.000Z",
        "dev": None,
        "nlink": 1,
        "size": 0
    },
    {
        "name": "简报",
        "acl": [{"sid": "r:7b49ef92-b9cb-4388-b5a7-a261b79ac5fa", "mask": -2088599552}],
        "uid": "u:7bd71624-a961-47a8-bea0-d601625b9941",
        "gid": "r:7b49ef92-b9cb-4388-b5a7-a261b79ac5fa",
        "xattrs": {"system": {"source": "mssql://dongge:dongge@192.168.0.2:57993/dbname=sh&table=Tabs&TabID=111"},
                   "dc": {"description": "", "subject": ""}},
        "uuid": "57EF5EA0-3CC1-4154-950A-DE14A1664CA6",
        "parent": "2E06A99B-5017-400B-95C3-2A433AEB11AA",
        "ancestors": ["上海行业情报服务网", "情报产品"],
        "mode": -2147466772,
        "create": "2010-08-31T11:25:52.000Z",
        "atime": "2016-11-01T11:25:52.000Z",
        "ctime": "2010-08-31T11:25:52.000Z",
        "mtime": "2010-08-31T11:25:52.000Z",
        "dev": None,
        "nlink": 1,
        "size": 0
    }
]

ids = {}

global_id = ObjectId("58532cfb33d581e6b16f5412")
global_ancestors = ['data', 'www.hyqb.sh.cn']

for file_obj in files:
    ids[file_obj['uuid']] = ObjectId()

for file_obj in files:
    file_obj['_id'] = ids[file_obj['uuid']]
    if file_obj['parent'] is not None:
        file_obj['parent'] = ids[file_obj['parent']]
    del file_obj['uuid']
    file_obj['ancestors'] = global_ancestors + file_obj['ancestors']


client = pymongo.MongoClient('10.1.80.180',27017)
db = client.istis

#  db.files.insert_many(files)
documents = db.files.find({'ancestors.0':'data', 'ancestors.1':'www.hyqb.sh.cn'})

for document in documents:
    # update_document = {}
    # update_document[u'atime'] = datetime.datetime.strptime(document[u'atime'], '%Y-%m-%dT%H:%M:%S.%fZ')
    # update_document[u'ctime'] = datetime.datetime.strptime(document[u'ctime'], '%Y-%m-%dT%H:%M:%S.%fZ')
    # update_document[u'mtime'] = datetime.datetime.strptime(document[u'mtime'], '%Y-%m-%dT%H:%M:%S.%fZ')
    # update_document[u'create'] = datetime.datetime.strptime(document[u'create'], '%Y-%m-%dT%H:%M:%S.%fZ')
    # update_document[u'uid'] = u'u:30db792e-3f41-4773-ae0d-f3916111f73d'
    # update_document[u'gid'] = u'r:a3ff2bae-4a11-49b0-8319-cee2ce0dc578'
    # update_document[u'acl.0.sid'] = u'r:a3ff2bae-4a11-49b0-8319-cee2ce0dc578'
    # db.files.update_one({u'_id': document['_id']}, {u'$set': update_document})
    if document[u'parent'] is None:
        db.files.update_one({u'_id': document[u'_id']}, {u'$set': {u'parent': global_id}})