from flask import current_app
from elasticsearch import Elasticsearch as PyElasticSearch
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

class ElasticSearch(object):
    """
    A thin wrapper around pyelasticsearch.ElasticSearch()
    """
    def __init__(self, app=None, **kwargs):
        if app is not None:
            self.init_app(app, **kwargs)

    @classmethod
    def url_to_options(cls, url):
        """Translate qualified URL into Elasticsearch options"""
        parsed = urlparse(url)
        opts = {
            'host': parsed.hostname
        }
        if parsed.port:
            opts['port'] = parsed.port

        if parsed.scheme == 'https':
            opts['use_ssl'] = True
            if not parsed.port:
                opts['port'] = 443
        elif parsed.scheme == 'http' and not parsed.port:
            opts['port'] = 80

        if parsed.username and parsed.password:
            opts['http_auth'] = parsed.username + ':' + parsed.password
        return opts

    def init_app(self, app, **kwargs):
        app.config.setdefault('ELASTICSEARCH_URL', 'http://localhost:9200/')
        opts = self.url_to_options(app.config.get('ELASTICSEARCH_URL'))
        kwargs.update(opts)

        # using the app factory pattern _app_ctx_stack.top is None so what
        # do we register on? app.extensions looks a little hackish (I don't
        # know flask well enough to be sure), but that's how it's done in
        # flask-pymongo so let's use it for now.
        app.extensions['elasticsearch'] = PyElasticSearch(**kwargs)

    def __getattr__(self, item):
        if not 'elasticsearch' in current_app.extensions.keys():
            raise Exception('not initialised, did you forget to call init_app?')
        return getattr(current_app.extensions['elasticsearch'], item)
