# coding: utf-8
import logging
from datetime import datetime, timedelta
import argparse

import requests

from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from xylose.scielodocument import Article, Journal

import choices

ARTICLEMETA = "http://articlemeta.scielo.org/api/v1"
ISO_3166_COUNTRY_AS_KEY = {value: key for key, value in choices.ISO_3166.items()}

FROM = datetime.now() - timedelta(days=30)
FROM.isoformat()[:10]

ES = Elasticsearch()


def _config_logging(logging_level='INFO', logging_file=None):

    allowed_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    logging_config = {
        'level': allowed_levels.get(logging_level, 'INFO'),
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    }

    if logging_file:
        logging_config['filename'] = logging_file

    logging.basicConfig(**logging_config)


def do_request(url, params):

    response = requests.get(url, params=params).json()

    return response



def fmt_document(document):
    return document


def pages(first, last):

    try:
        pages = int(last)-int(first)
    except:
        pages = 0

    if pages >= 0:
        return pages
    else:
        return 0

def fmt_citation(document, collection='BR'):

    i = 0
    for citation in document.citations or []:
        _id = [document.journal.collection_acronym, document.publisher_id, citation.index_number]
        data = {}

        data['_id'] = _id
        data['citing_issn'] = document.journal.scielo_issn
        data['citing_id'] = document.publisher_id
        data['citing_full_title'] = document.journal.title
        data['citing_year'] = document.publication_date[0:4]
        data['citing_source'] = [document.journal.title, document.journal.abbreviated_title]
        if citation.date:
            data['citation_year'] = citation.date[0:4]
        data['citation_source'] = citation.source
        data['citation_type'] = citation.publication_type
        data['citation_id'] = '_'.join([document.publisher_id, citation.index_number])
        data['collection'] = document.collection_acronym

        yield data


def documents(endpoint, fmt=None, from_date=FROM):

    allowed_endpoints = ['journal', 'article', 'citation']

    if not endpoint in allowed_endpoints:
        raise TypeError('Invalid endpoint, expected one of: %s' % str(allowed_endpoints))

    params = {'offset': 0, 'from': from_date}

    if endpoint == 'article':
        xylose_model = Article
    elif endpoint == 'journal':
        xylose_model = Journal

    while True:
        identifiers = do_request(
            '{0}/{1}/identifiers'.format(ARTICLEMETA, endpoint),
            params
        )

        logging.debug('offset %s' % str(params['offset']))

        logging.debug('len identifiers %s' % str(len(identifiers['objects'])))

        if len(identifiers['objects']) == 0:
            raise StopIteration

        for identifier in identifiers['objects']:
            dparams = {
                'collection': identifier['collection']
            }

            if endpoint == 'article':
                dparams['code'] = identifier['code']
            elif endpoint == 'journal':
                dparams['issn'] = identifier['code'][0]

            document = do_request(
                '{0}/{1}'.format(ARTICLEMETA, endpoint), dparams
            )

            if isinstance(document, dict):
                doc_ret = document
            elif isinstance(document, list):
                doc_ret = document[0]


            for item in fmt(xylose_model(doc_ret)):
                yield item

        params['offset'] += 1000


def main(from_date=FROM):

    journal_settings_mappings = {      
        "mappings": {
            "citation": {
                "properties": {
                    "citing_id": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "citing_issn": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "citing_source": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "citing_year": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "citation_source": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "citation_year": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "collection": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "citation_type": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "citing_full_title": {
                        "type": "string",
                        "index" : "not_analyzed"                    
                    }
                }
            }
        }
    }

    try:
        ES.indices.create(index='bibliometrics', body=journal_settings_mappings)
    except:
        logging.debug('Index already available')

    for document in documents('article', fmt_citation, from_date=from_date):
        logging.debug('loading document into index bibliometrics')
        ES.index(
            index='bibliometrics',
            doc_type='citation',
            body=document
        )

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Load SciELO Network data no analytics production"
    )

    parser.add_argument(
        '--from_date',
        '-f',
        default=FROM,
        help='ISO date like 2013-12-31'
    )

    parser.add_argument(
        '--logging_file',
        '-o',
        default='/tmp/dumpdata.log',
        help='Full path to the log file'
    )

    parser.add_argument(
        '--logging_level',
        '-l',
        default='DEBUG',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logggin level'
    )

    args = parser.parse_args()

    _config_logging(args.logging_level, args.logging_file)

    main(from_date=args.from_date)
