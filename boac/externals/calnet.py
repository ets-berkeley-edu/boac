import logging
import ssl
import ldap3
import ldap3.utils.log as ldap3_log


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

    def cs_ids_filter(self, cs_ids):
        clauses = ''.join(f'(berkeleyeducsid={id})' for id in cs_ids)
        return f'(&(objectclass=person)(|{clauses}))'

    def cs_ids_to_uids(self, cs_ids):
        map = dict.fromkeys(cs_ids)
        found = self.search_cs_ids(cs_ids)
        for entry in found:
            map[entry.berkeleyEduCSID.value] = entry.uid.value
        return map

    def search_cs_ids(self, cs_ids):
        with self.connect() as conn:
            conn.search('ou=people,dc=berkeley,dc=edu', self.cs_ids_filter(cs_ids), attributes=ldap3.ALL_ATTRIBUTES)
            entries = conn.entries
        return entries


def init_logging(app):
    # For more detail, specify BASIC or NETWORK.
    ldap3_log.set_library_log_detail_level(ldap3_log.ERROR)
    logger = logging.getLogger('ldap3')
    logger.setLevel(logging.DEBUG)
    for handler in app.logger.handlers:
        logging.getLogger('ldap3').addHandler(handler)
