import fileinput
import gzip
import json
import os
import uuid

import boto3

from elasticsearch import Elasticsearch, helpers

# Parameters - should be parameterized through lambda config somehow
HOSTS = [os.environ['ES_HOST']]

INDEX = 'tweets'

# in bytes, 100MB is ES py library default
DEFAULT_MAX_CHUNK_SIZE = 100 * 1024 * 1024


s3_client = boto3.client('s3')
es = Elasticsearch(hosts=HOSTS)

def documents(index, jsonfile):
    for tweet_str in gzip.open(jsonfile):
        tweet = json.loads(tweet_str)
        doc = {'_index': index, '_type': 'document',
                '_id': tweet['id'], '_source': tweet}
        yield doc


def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
        s3_client.download_file(bucket, key, download_path)
        helpers.bulk(client=es, actions=documents(INDEX, download_path),
                     max_chunk_bytes=DEFAULT_MAX_CHUNK_SIZE)
