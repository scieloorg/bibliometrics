# coding: utf-8
import logging
import argparse

import requests
from datetime import datetime, timedelta

from thrift import clients

logger = logging.getLogger(__name__)
FROM_DATE = (datetime.now()-timedelta(60)).isoformat()[:10]


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


def main(from_date=None):

    logger.info('Carregando dados')

    articlemeta = clients.articlemeta()

    size = 10
    x = 0
    logger.info('Listando coleção')
    for collection in articlemeta.collections():
        x += 1
        print collection
        if size == x:
            break

    size = 10
    x = 0
    logger.info('Listando documentos de qualquer coleção')
    for document in articlemeta.documents():
        x += 1
        print document.collection_acronym, document.journal.title, document.original_title()
        if size == x:
            break

    size = 10
    x = 0
    logger.info('Listando documentos de coleção específica')
    for document in articlemeta.documents(collection='mex'):
        x += 1
        print document.collection_acronym, document.journal.title, document.original_title()
        if size == x:
            break

    size = 10
    x = 0
    logger.info('Listando revistas de qualquer coleção')
    for journal in articlemeta.journals():
        x += 1
        print journal.collection_acronym, journal.title
        if size == x:
            break

    size = 10
    x = 0
    logger.info('Listando revistas de coleção específica')
    for journal in articlemeta.journals(collection='mex'):
        x += 1
        print journal.collection_acronym, journal.title
        if size == x:
            break

parser = argparse.ArgumentParser(
    description="Load SciELO Network data no bibliometrics indicators"
)

parser.add_argument(
    '--from_date',
    '-f',
    default=FROM_DATE,
    help='ISO date like 2013-12-31, will fetch the processing date'
)

parser.add_argument(
    '--logging_file',
    '-o',
    help='Full path to the log file, the stdout is the default output'
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
