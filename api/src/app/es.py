from elasticsearch import Elasticsearch
from elasticsearch import helpers
from typing import List, Union
import json
from datetime import datetime


class Source:
    _id: str
    author: str
    description: str
    main: str
    post_at: datetime
    votes: int
    views: int

    def __init__(self,  author, description, main, _id=None, post_at=None, votes=0, views=0):
        self._id = _id
        self.author = author
        self.description = description
        self.main = main
        self.post_at = post_at
        self.votes = votes
        self.views = views

    @staticmethod
    def from_response(response):
        try:
            src = response['_source']
            _id = response['_id']
            return Source(src['author'], src['description'], src['main'], _id, src['post_at'], src['votes'], src['views'])
        except KeyError:
            return None

    @staticmethod
    def from_hits(response):
        if response['hits']['total']['value'] > 0:
            hits = response['hits']['hits']
            return response['hits']['total']['value'], list(map(Source.from_response, hits))
        else:
            return 0, None

    @staticmethod
    def SerializeEncoder():
        class Serializer(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, Source):  # NotSettedParameterは'NotSettedParameter'としてエンコード
                    return str(o)
                # 他の型はdefaultのエンコード方式を使用
                return super(MyJSONEncoder, self).default(o)
        return Serializer

    def register(self, controller):
        if self.post_at is None:
            self.post_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        controller.insert({
            "author": self.author,
            "description": self.description,
            "main": self.main,
            "post_at": self.post_at,
            "votes": self.votes,
            "views": self.views,
        })

    def __str__(self):
        return json.dumps({
            "id": self._id,
            "author": self.author,
            "description": self.description,
            "main": self.main,
            "post_at": self.post_at,
            "votes": self.votes,
            "views": self.views,
        }, ensure_ascii=False)


class SourceController:
    def __init__(self, index_name='code_index', hosts=["es01:9200"], **kwargs):
        self.es = Elasticsearch(hosts=hosts, **kwargs)
        self.index_name = index_name
        self.settings = {
            "settings": {
                "analysis": {
                    "tokenizer": {
                        "kuromoji_search": {
                            "type": "kuromoji_tokenizer",
                            "mode": "search"
                        }
                    },
                    "analyzer": {
                        "kuromoji_analyzer": {
                            "type": "custom",
                            "tokenizer": "kuromoji_search"
                        },
                        "whitespace_analyzer": {
                            "tokenizer": "whitespace"
                        }
                    }
                }
            }
        }
        self.mappings = {
            "properties": {
                "author":  {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "description": {
                    "type": "text",
                    "analyzer": "kuromoji_analyzer"
                },
                "main": {
                    "type": "text",
                    "analyzer": "whitespace_analyzer"
                },
                "post_at": {
                    "type": "date",
                    "format": "yyyy-MM-dd HH:mm:ss"
                },
                "votes": {
                    "type": "long"
                },
                "views": {
                    "type": "long"
                }
            }
        }
        self.es.indices.create(index_name, ignore=400, body=self.settings)
        self.es.indices.put_mapping(
            index=index_name, body=self.mappings)

    def insert(self, data):
        self.es.index(self.index_name, data, doc_type='_doc')

    def load(self, json_path):
        with open(json_path) as f:
            helpers.bulk(self.es, json.load(f))

    def fetch_by_id(self, _id):
        return Source.from_response(self.es.get(self.index_name, id=_id))

    def fetch_by_query(self, query):
        return Source.from_hits(self.es.search(body=query, index=self.index_name))

    def update_by_id(self, _id, new_data) -> bool:
        if 'id' in new_data:
            del new_data['id']
        if 'pid' in new_data:
            del new_data['pid']
        return self.es.update(self.index_name, _id, body={"doc": new_data})

    def delete_by_id(self, _id) -> bool:
        return self.es.delete(self.index_name, _id)

    def fetch_all(self, sort={"key": "post_at", "order": "desc"}, offset=0, limit=10):
        return self.fetch_by_query({
            "query": {
                "match_all": {}
            },
            "from": offset,
            "size": limit,
            "sort": {
                sort['key']: {
                    "order": sort['order']
                }
            }
        })

    def full_text_search(self, field, keyword, sort={"key": "_score", "order": "desc"}, offset=0, limit=10):
        return self.fetch_by_query({
            "query": {
                "match": {
                    field: keyword
                }
            },
            "from": offset,
            "size": limit,
            "sort": {
                sort['key']: {
                    "order": sort['order']
                }
            }
        })

    def regex_search(self, field, pattern, sort={"key": "_score", "order": "desc"}, offset=0, limit=10):
        return self.fetch_by_query({
            "query": {
                "regex": {
                    field: pattern
                }
            },
            "from": offset,
            "size": limit,
            "sort": {
                sort['key']: {
                    "order": sort['order']
                }
            }
        })
