# elasticsearch-tutorial
A brief tutorial of building an Elasticsearch index and adding a few documents


# Getting Started
[Download Elasticsearch](http://www.elasticsearch.org/overview/elkdownloads/) and extract to a local directory. To start elasticsearch run

```
>> ./bin/elasticsearch
```

this launches a local Elasticsearch cluster at http://localhost:9200. To ensure the cluster is running, visit the url and make sure a json payload similar to the one below is shown.

```
{
status: 200,
name: "Elektro",
version: {
number: "1.1.1",
build_hash: "a85a04be3d601c105e86de475fa1fe1808968ce8",
build_timestamp: "2014-05-02T00:59:51Z",
build_snapshot: false,
lucene_version: "4.7"
},
tagline: "You Know, for Search"
}
```

Now, a bit of terminology before moving forward.

* **A field** is a single unit of data. This could be a string, date, float, etc.
* **A document** is a single json payload made made of one or more fields. For our context, this represents one HTML page plus extracted features.
* **An index** is a collection of documents, indexed together for searching. 
* **A query** is a user input text string. The goal is to find a set of documents contained within an index similar to the query.
* **A schema** is a definition for how Elasticsearch should interperate individual fields within a document. Schemas define the fields, their types, search engine parameters, and much, much more.

# Building an index

To build an index, let's first define the type of data we expect to encounter. Let's say we expect to index some books. An example document could be:


```
{
"author": "Joe",
"title": "The best book",
"content": "This book contains the most interesting content in the world. You have no idea..."
}
```

Given this data, we could anticipate building an idex with the following schema:

```
{
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        "similarity.default.type": "BM25",
	"index": {
	    "analysis": {
		"analyzer": {
		    "full_name_analyzer": {
			"type": "custom",
			"tokenizer": "full_name_tokenizer",
			"filter": ["lowercase"]
		    }
		},
		"tokenizer": {
		    "full_name_tokenizer": {
			"type": "whitespace"
		    }
		}
	    }
	}
	    
    },
    "mappings": {
        "books": {
            "properties": {
		"author": {"type": "string", "index": "not_analyzed"},
		"title": {"type": "string", "index": "not_analyzed"},
		"content": {"type": "string", "analyzer": "full_name_analyzer"}
            }
        }
    }
}

```

There's a lot going on here, so let's focus on the key points. The mappings describe a new type of document (books). Books contain three properties: author, title and content. All three are of type string. Two are not analyzed and one uses a custom analyzer. The analyzer tells lucene how a given field should be tokenized and indexed. In this case, full_name_analyzer tokenizes using the custom full_name_tokenizer. This custom tokenizer is of type "witespace", i.e., tokenize on whitespace. The custom analyzer also defines filters such as lowercasing tokens, unicode normalization and much more.

To construct an index, library, all we need to do is save the above schema as a json and run the following code (from within src directory):

```
>> curl -XPUT http://localhost:9200/library -d '@schema.json'
```

If run correctly, you should receive a response {"acknowledged": true}

Visit http://localhost:9200/library/_mapping to see if your schema was interpreted correctly. Congrats! You've built your first ES index :)

# Indexing a document

Now, let's index the beautiful document described above. To put into ES, run the command

```
curl -XPUT http://localhost:9200/library/book/0 -d '{
"author": "Joe",
"title": "The best book",
"content": "This book contains the most interesting content in the world. You have no idea..."
}'

```
notice the url takes on the form http://{host}:{port}/{index}/{type}/{id}. The id here is a unique identifier for this document. It's common to use either an integer counter or the hash of the document. Note, if you call PUT on the same {id} it will overwrite the previous document!

To ensure your document has been indexed, take a look at

```
http://localhost:9200/_search

and

http://localhost:9200/_count
```

You should see your document (_search) and a count of 1 (_count).

# Indexing multiple documents
I've placed a few documents into data/testdocs.json. To index these documents into Elasticsearch, try running src/indexer.py. Do this by running

```
>> python indexer.py
```

Note: you need to install the modules defined in requirements.txt. Now, take a look at

```
http://localhost:9200/_search
```

And you should see everything indexed!

# Searching

The full scope of ES's search features is beyond the scope of this tutorial. Let's take a look at two common operations: filtering and match queries.

Filters are a fast way to reduce the search space for a specific document. It is common to filter results in conjunction with questions. For example, let's run a query looking for a specific author

```
curl -XGET http://localhost:9200/library/_search -d '
{
 "query": {
  "filtered": {
   "query": {
    "match_all": { }
   },
   "filter": {
    "term": {"author": "Joe"}
   }
  }
 }
}
'
```

There are two components to this call: the query and the filter. The query is a match_all - meaning no score is calculated (all documents are scored equally). The filter removes all documents whose author is not Joe. Note, such term filters can only be run on fields which have "not_analyzed" as the analyzer. For the query above, the following should be returned

```
{
    "_shards": {   
        "failed": 0,
	"successful": 1,
	"total": 1
	},
	"hits": {
	    "hits": [
	        {
		    "_id": "0",
		    "_index": "library",
		    "_score": 1.0,
		    "_source": {
		        "author": "Joe",
			"content": "This book contains everything",
			"title": "The best book"
		    },
		    "_type": "book"
		}
	    ],
	    "max_score": 1.0,
	    "total": 1
	},
	"timed_out": false,
	"took": 1
}  
```

Now let's take a look at queries without filters. Again, the full extent of queries possible within ES, their scalability and their API calls are beyond the context of this tutorial. Let's focus on one, simple query: a match. Let's run:

```
curl -XGET http://localhost:9200/library/_search -d '
{
 "query": {
  "match": {
   "content": "book"
  }
 }
}    
```

This query looks to match the word "book" with documents whose content field contain the token "book". This results in several documents:

```
{
    "_shards": {
        "failed": 0,
        "successful": 1,
        "total": 1
    },
    "hits": {
        "hits": [
            {
                "_id": "ff485e87c94b9f8e03a4909184fe6366",
                "_index": "library",
                "_score": 0.31387395,
                "_source": {
                    "author": "Greg",
                    "content": "This book contains all of the science previously known and forever yet undiscovered",
                    "title": "The most scientific book"
                },
                "_type": "books"
            },
            {
                "_id": "fbeca2deba30f7a4cd89aedb6626aed3",
                "_index": "library",
                "_score": 0.31387395,
                "_source": {
                    "author": "Joe",
                    "content": "This book contains the most interesting content in the world. You have no idea...",
                    "title": "The best book"
                },
                "_type": "books"
            },
            {
                "_id": "5c76aa607d00b2de8fd7917d7b09dd56",
                "_index": "library",
                "_score": 0.31387395,
                "_source": {
                    "author": "AG",
                    "content": "AG felt the best content for his book would be, simply AG",
                    "title": "AG-test-123"
                },
                "_type": "books"
            }
        ],
        "max_score": 0.31387395,
        "total": 3
    },
    "timed_out": false,
    "took": 2
}

```

For an example of querying an elasticsearch index using python, take a look at src/query.py. To run

```
>> python query.py
```