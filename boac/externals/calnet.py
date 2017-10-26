import logging
import os
import ssl

from boac.lib import mockingbird
import ldap3
import ldap3.utils.log as ldap3_log

SCHEMA_DICT = {
    'berkeleyEduAffiliations': 'affiliations',
    'berkeleyEduCSID': 'csid',
    'berkeleyEduOfficialEmail': 'campus_email',
    'cn': 'sortable_name',
    'displayName': 'name',
    'mail': 'email',
    'givenName': 'first_name',
    'sn': 'last_name',
    'uid': 'uid',
}

BATCH_QUERY_MAXIMUM = 500


def client(app):
    if mockingbird._environment_supports_mocks():
        c = MockClient(app)
    else:
        c = Client(app)
    return c


def init_logging(app):
    # For more detail, specify BASIC or NETWORK.
    ldap3_log.set_library_log_detail_level(ldap3_log.ERROR)
    logger = logging.getLogger('ldap3')
    logger.setLevel(logging.DEBUG)
    for handler in app.logger.handlers:
        logging.getLogger('ldap3').addHandler(handler)


class Client:
    def __init__(self, app):
        self.app = app
        self.host = app.config['LDAP_HOST']
        self.bind = app.config['LDAP_BIND']
        self.password = app.config['LDAP_PASSWORD']
        tls = ldap3.Tls(validate=ssl.CERT_REQUIRED)
        server = ldap3.Server(self.host, port=636, use_ssl=True, get_info=ldap3.ALL, tls=tls)
        self.server = server

    def connect(self):
        conn = ldap3.Connection(self.server, user=self.bind, password=self.password, auto_bind=ldap3.AUTO_BIND_TLS_BEFORE_BIND)
        return conn

    def search_csids(self, csids):
        all_out = []
        for i in range(0, len(csids), BATCH_QUERY_MAXIMUM):
            csids_batch = csids[i:i + BATCH_QUERY_MAXIMUM]
            entries = self._search_csids(csids_batch)
            out = [_attributes_to_dict(entry) for entry in entries]
            all_out += out
        return all_out

    def _csids_filter(self, csids):
        clauses = ''.join('(berkeleyeducsid={id})'.format(id=id) for id in csids)
        return '(&(objectclass=person)(|{clauses}))'.format(clauses=clauses)

    def _search_csids(self, csids):
        with self.connect() as conn:
            conn.search('ou=people,dc=berkeley,dc=edu', self._csids_filter(csids), attributes=ldap3.ALL_ATTRIBUTES)
            entries = conn.entries
        return entries


class MockClient(Client):
    def __init__(self, app):
        self.app = app
        self.host = app.config['LDAP_HOST']
        self.bind = app.config['LDAP_BIND']
        self.password = app.config['LDAP_PASSWORD']
        server = ldap3.Server.from_definition(self.host, _fixture_path('server_info'), _fixture_path('server_schema'))
        self.server = server

    def connect(self):
        conn = ldap3.Connection(self.server, user=self.bind, password=self.password, client_strategy=ldap3.MOCK_SYNC)
        conn.strategy.entries_from_json(_fixture_path('search_entries'))
        return conn


def _attributes_to_dict(entry):
    out = dict.fromkeys(SCHEMA_DICT.values(), None)
    # ldap3's entry.entry_attributes_as_dict would work for us, except that it wraps a single value as a list.
    for attr in SCHEMA_DICT:
        if attr in entry.entry_attributes:
            out[SCHEMA_DICT[attr]] = entry[attr].value
    return out


def _create_fixtures(app, sample_csids):
    fixture_output = os.environ.get('FIXTURE_OUTPUT_PATH') or mockingbird._get_fixtures_path()
    cl = Client(app)
    cl.server.info.to_file('{fixture_output}/calnet_server_info.json'.format(fixture_output=fixture_output))
    cl.server.schema.to_file('{fixture_output}/calnet_server_schema.json'.format(fixture_output=fixture_output))
    conn = cl.connect()
    conn.search('ou=people,dc=berkeley,dc=edu', cl._csids_filter(sample_csids), attributes=ldap3.ALL_ATTRIBUTES)
    conn.response_to_file('{fixture_output}/calnet_search_entries.json'.format(fixture_output=fixture_output), raw=True)
    conn.unbind()


def _fixture_path(pattern):
    fixtures_path = mockingbird._get_fixtures_path()
    return '{}/calnet_{}.json'.format(fixtures_path, pattern)
