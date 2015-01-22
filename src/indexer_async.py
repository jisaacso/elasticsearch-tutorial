import os.path
import tornado.ioloop
from tornadoes import ESConnection

from greplin import scales
from greplin.scales.meter import MeterStat

import json
from hashlib import md5

#
# This is an example of using the python asynchronous interface to elasticsearch
#

STATS = scales.collection('/index', MeterStat('docs'))

es = ESConnection('localhost', 9200)
es.httprequest_kwargs = {
    'request_timeout': 1500.00,
    'connect_timeout': 1500.00
}
# by default we connect to localhost:9200
es = Elasticsearch()

def build_library():
    with open('../data/testdocs.json', 'r') as fin:
        for doc in fin:
            yield json.loads(doc.strip())

docs = iter(build_library())

def index(response):
    try:
        STATS.docs.mark()

        if STATS.docs['count'] % 1000 == 0:
            print 'Rate: ' + str(STATS.docs['m1'])

        doc = next(docs)
        es.put('library', 'books',
            md5(json.dumps(doc)).hexdigest(), doc, callback=index)
    except StopIteration:
        print 'Everything has stopped for this doc!'
        pass

if __name__ == '__main__':
    for i in xrange(10):
        index(None)

    tornado.ioloop.IOLoop.instance().start()
