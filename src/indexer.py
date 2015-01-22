from elasticsearch import Elasticsearch
from hashlib import md5
import json

# By default we connect to localhost:9200
es = Elasticsearch()

# Load the JSON data from a file
def load_library():
    with open('../data/testdocs.json', 'r') as fin:
        for doc in fin:
            yield json.loads(doc.strip())

# Add a list of documents to the index
def index(documents):
    for doc in docs:
        print "Adding document: %s" % json.dumps(doc)
        es.index(index='library',
                 doc_type='books',
                 id=md5(json.dumps(doc)).hexdigest(),
                 body=doc)

if __name__ == '__main__':
    docs = list(load_library())
    index(docs)
