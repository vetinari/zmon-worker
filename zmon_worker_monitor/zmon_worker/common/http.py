from zmon_worker_monitor import __version__
import tokens


def get_user_agent():
    return 'zmon-worker/{}'.format(__version__)


def is_absolute_http_url(url):
    '''
    >>> is_absolute_http_url('')
    False

    >>> is_absolute_http_url('bla:8080/blub')
    False

    >>> is_absolute_http_url('https://www.zalando.de')
    True
    '''

    return url.startswith('http://') or url.startswith('https://')


def init_tokens(conf, config_key='oauth2.tokens', **kwargs):
    # will use OAUTH2_ACCESS_TOKEN_URL environment variable by default
    # will try to read application credentials from CREDENTIALS_DIR
    tokens.configure()

    token_configuration = conf.get(config_key)

    if token_configuration:
        for part in token_configuration.split(':'):
            token_name, scopes = tuple(part.split('=', 1))
            tokens.manage(token_name, scopes.split(','), kwargs)

    tokens.manage('uid', ['uid'], kwargs)

    tokens.start()
