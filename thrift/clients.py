# coding: utf-8
import os
import thriftpy
import json
import logging

from thriftpy.rpc import make_client
from xylose.scielodocument import Article, Journal

LIMIT = 1000

logger = logging.getLogger(__name__)

articlemeta_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__))+'/articlemeta.thrift')


class ServerError(Exception):
    def __init__(self, message=None):
        self.message = message or 'thirftclient: ServerError'

    def __str__(self):
        return repr(self.message)


def articlemeta(host='127.0.0.1:11720'):

    h = host.split(':')[0]
    p = int(host.split(':')[1])

    return ArticleMeta(h, p)


class ArticleMeta(object):

    def __init__(self, address, port):
        """
        Cliente thrift para o Articlemeta.
        """
        self._address = address
        self._port = port

    @property
    def client(self):

        client = make_client(
            articlemeta_thrift.ArticleMeta,
            self._address,
            self._port
        )
        return client

    def journals(self, collection=None, issn=None):
        offset = 0
        while True:
            identifiers = self.client.get_journal_identifiers(collection=collection, issn=issn, limit=LIMIT, offset=offset)
            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:

                journal = self.client.get_journal(
                    code=identifier.code[0], collection=identifier.collection)

                jjournal = json.loads(journal)

                xjournal = Journal(jjournal)

                logger.info('Journal loaded: %s_%s' % ( identifier.collection, identifier.code))

                yield xjournal

            offset += 1000

    def document(self, code, collection=None, replace_journal_metadata=True, fmt='xylose'):

        query = {
            'code': code,
            'replace_journal_metadata': replace_journal_metadata,
            'fmt': fmt
        }

        if collection:
            query['collection'] = collection

        try:
            article = self.client.get_article(**query)
        except:
            msg = 'Error retrieving document: %s_%s' % (collection, code)
            raise ServerError(msg)

        if fmt == 'xylose':
            jarticle = json.loads(article)
            xarticle = Article(jarticle)
            logger.info('Document loaded: %s_%s' % ( collection, code))
            return xarticle
        else:
            logger.info('Document loaded: %s_%s' % ( collection, code))
            return article

    def documents(self, collection=None, issn=None, from_date=None,
        until_date=None, fmt='xylose'):
        offset = 0
        while True:
            identifiers = self.client.get_article_identifiers(
                collection=collection, issn=issn, from_date=from_date,
                until_date=until_date, limit=LIMIT, offset=offset)

            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:

                document = self.document(
                    code=identifier.code,
                    collection=identifier.collection,
                    replace_journal_metadata=True, 
                    fmt=fmt
                )

                yield document

            offset += 1000

    def documents_history(self, collection=None, issn=None, from_date=None,
        until_date=None, fmt='xylose'):
        offset = 0
        while True:
            identifiers = self.client.article_history_changes(
                collection=collection, issn=issn, from_date=from_date,
                until_date=until_date, limit=LIMIT, offset=offset)

            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:

                document = self.document(
                    code=identifier.code,
                    collection=identifier.collection,
                    replace_journal_metadata=True, 
                    fmt=fmt
                )

                if identifier.event == 'delete':
                    yield (identifier, None)

                if document.data:
                    yield (identifier, document)

            offset += 1000

    def collections(self):
        return [i for i in self.client.get_collection_identifiers()]
