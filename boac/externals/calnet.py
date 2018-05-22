"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""


import os
import ssl

from boac.lib import mockingbird
import ldap3

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

    def search_uids(self, uids):
        all_out = []
        for i in range(0, len(uids), BATCH_QUERY_MAXIMUM):
            uids_batch = uids[i:i + BATCH_QUERY_MAXIMUM]
            entries = self._search_uids(uids_batch)
            out = [_attributes_to_dict(entry) for entry in entries]
            all_out += out
        return all_out

    def _search_csids(self, csids):
        with self.connect() as conn:
            conn.search('ou=people,dc=berkeley,dc=edu', self._csids_filter(csids), attributes=ldap3.ALL_ATTRIBUTES)
            entries = conn.entries
        return entries

    def _search_uids(self, uids):
        with self.connect() as conn:
            conn.search('ou=people,dc=berkeley,dc=edu', self._uids_filter(uids), attributes=ldap3.ALL_ATTRIBUTES)
            entries = conn.entries
        return entries

    @classmethod
    def _csids_filter(cls, csids):
        clauses = ''.join(f'(berkeleyeducsid={sid})' for sid in csids)
        return f'(&(objectclass=person)(|{clauses}))'

    @classmethod
    def _uids_filter(cls, uids):
        clauses = ''.join(f'(uid={uid})' for uid in uids)
        return f'(&(objectclass=person)(|{clauses}))'


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
    cl.server.info.to_file(f'{fixture_output}/calnet_server_info.json')
    cl.server.schema.to_file(f'{fixture_output}/calnet_server_schema.json')
    conn = cl.connect()
    conn.search('ou=people,dc=berkeley,dc=edu', cl._csids_filter(sample_csids), attributes=ldap3.ALL_ATTRIBUTES)
    conn.response_to_file(f'{fixture_output}/calnet_search_entries.json', raw=True)
    conn.unbind()


def _fixture_path(pattern):
    fixtures_path = mockingbird._get_fixtures_path()
    return f'{fixtures_path}/calnet_{pattern}.json'
