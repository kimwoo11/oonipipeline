from marshmallow import fields
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from oonipipeline.config import SQLALCHEMY_BINDS, SQLALCHEMY_DATABASE_URI


db = SQLAlchemy()
ma = Marshmallow()

# MetaDB Engine and Session (Connection not required)
metadb_engine = db.create_engine(SQLALCHEMY_BINDS['metadb'])
meta = db.MetaData(metadb_engine, reflect=True)
metadb_session = db.scoped_session(db.sessionmaker(bind=metadb_engine))

# Pipeline Engine and Session
pipeline_engine = db.create_engine(SQLALCHEMY_DATABASE_URI)


'''------- Status -------'''


class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    current = db.Column(db.Integer)
    total = db.Column(db.Integer)
    report_file = db.String(db.String)


'''------ META TABLE ------'''


class MetaTable(db.Model):
    __tablename__ = 'meta_table'
    set_id = db.Column(db.Integer, primary_key=True)
    set_name = db.Column(db.String(150), unique=True, nullable=False)
    test_name = db.Column(db.String(25))
    comment = db.Column(db.String(150))
    creation_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    webconn = db.relationship("Webconn", backref="meta_table")
    dns = db.relationship("DnsConsistency", backref="meta_table")


'''------ WEB CONNECTIVITY ------'''


class Webconn(db.Model):
    __tablename__ = "web_connectivity"
    __table_args__ = {'extend_existing': True}  # for when error occurs
    id = db.Column(db.Integer, primary_key=True)

    # This method of implementing CASCADE is more efficient than making SQLAlchemy do the work
    set_id = db.Column(db.Integer, db.ForeignKey('meta_table.set_id', ondelete='CASCADE'))
    meta = db.relationship('MetaTable', backref=db.backref('web_connectivity_d', passive_deletes=True))

    # Other way (making SQLAlchemy do the work):
    #   children = relationship('Child', cascade='all   ,delete', backref='parent') OR
    #   parent = relationship('Parent', backref=backref('children', cascade='all,delete'))

    tested_url = db.Column(db.String(1000))
    country = db.Column(db.String(5))
    asn = db.Column(db.String(10))
    test_date = db.Column(db.TIMESTAMP)
    test_version = db.Column(db.String)
    download_link = db.Column(db.String)
    test_key = db.relationship("WebTestKeys", backref=db.backref("web_connectivity", uselist=False))


class WebTestKeys(db.Model):
    __tablename__ = "web_test_keys"
    __table_args__ = {'extend_existing': True}
    webconn_id = db.Column(db.Integer, db.ForeignKey('web_connectivity.id', ondelete='CASCADE'), primary_key=True)
    webconn = db.relationship('Webconn', backref=db.backref('web_test_keys_d', passive_deletes=True))
    accessible = db.Column(db.Boolean)
    blocking = db.Column(db.String(125))
    body_length_match = db.Column(db.Boolean)
    client_resolver = db.Column(db.String(150))
    control_failure = db.Column(db.String(150))
    dns_consistency = db.Column(db.String(125))
    headers_match = db.Column(db.Boolean)
    http_experiment_failure = db.Column(db.String)
    status_code_match = db.Column(db.Boolean)
    title_match = db.Column(db.Boolean)
    dns = db.relationship("ControlDns", backref=db.backref("web_test_keys", uselist=False))
    http_request = db.relationship("ControlHttpRequest", backref=db.backref("web_test_keys", uselist=False))
    control_tcp_connect = db.relationship("ControlTcpConnect", backref="web_test_keys")
    web_queries = db.relationship("WebQueries", backref="web_test_keys")
    requests = db.relationship("Requests", backref=db.backref("web_test_keys", uselist=False))
    tcp_connect = db.relationship("TcpConnect", backref="web_test_keys")


class ControlDns(db.Model):
    __tablename__ = "web_control_dns"
    __table_args__ = {'extend_existing': True}
    test_key_id = db.Column(db.Integer, db.ForeignKey('web_test_keys.webconn_id', ondelete='CASCADE'), primary_key=True)
    test_key = db.relationship('WebTestKeys', backref=db.backref('web_control_dns_d', passive_deletes=True))
    address = db.Column(db.String)
    failure = db.Column(db.String(150))


class ControlHttpRequest(db.Model):
    __tablename__ = "web_control_http_request"
    __table_args__ = {'extend_existing': True}
    test_key_id = db.Column(db.Integer, db.ForeignKey('web_test_keys.webconn_id', ondelete='CASCADE'),
                            primary_key=True)
    test_key = db.relationship('WebTestKeys', backref=db.backref('web_control_http_request_d', passive_deletes=True))
    body_length = db.Column(db.Integer)
    failure = db.Column(db.String(150))
    headers = db.Column(db.JSON)
    status_code = db.Column(db.Integer)
    title = db.Column(db.String)


class ControlTcpConnect(db.Model):
    __tablename__ = "web_control_tcp_connect"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    test_key_id = db.Column(db.Integer, db.ForeignKey('web_test_keys.webconn_id', ondelete='CASCADE'))
    test_key = db.relationship('WebTestKeys', backref=db.backref('web_control_tcp_connect_d', passive_deletes=True))
    address = db.Column(db.String(150))
    result = db.Column(db.JSON)


class WebQueries(db.Model):
    __tablename__ = "web_queries"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    test_key_id = db.Column(db.Integer, db.ForeignKey('web_test_keys.webconn_id', ondelete='CASCADE'))
    test_key = db.relationship('WebTestKeys', backref=db.backref('web_queries_d', passive_deletes=True))
    failure = db.Column(db.String(150))
    hostname = db.Column(db.String)
    query_type = db.Column(db.String)
    resolver_hostname = db.Column(db.String)
    resolver_port = db.Column(db.String)
    answers = db.relationship("WebAnswers", backref="web_queries")


class WebAnswers(db.Model):
    __tablename__ = "web_answers"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('web_queries.id', ondelete='CASCADE'))
    query = db.relationship('WebQueries', backref=db.backref('web_answers_d', passive_deletes=True))
    answer_type = db.Column(db.String)
    ipv4 = db.Column(db.String)
    ttl = db.Column(db.String)


class Requests(db.Model):
    __tablename__ = "web_requests"
    __table_args__ = {'extend_existing': True}
    test_key_id = db.Column(db.Integer, db.ForeignKey('web_test_keys.webconn_id', ondelete='CASCADE'),
                            primary_key=True)
    test_key = db.relationship('WebTestKeys', backref=db.backref('web_requests_d', passive_deletes=True))
    failure = db.Column(db.String(250))
    request_headers = db.Column(db.JSON)
    request_method = db.Column(db.String(5))
    request_url = db.Column(db.String)
    response_code = db.Column(db.BIGINT)
    response_headers = db.Column(db.JSON)
    response_body = db.Column(db.String)


class TcpConnect(db.Model):
    __tablename__ = "web_tcp_connect"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    test_key_id = db.Column(db.Integer, db.ForeignKey('web_test_keys.webconn_id', ondelete='CASCADE'))
    test_key = db.relationship('WebTestKeys', backref=db.backref('tcp_connect_d', passive_deletes=True))
    ip = db.Column(db.String(150))
    port = db.Column(db.Integer)
    blocked = db.Column(db.String(150))
    failure = db.Column(db.String(150))
    success = db.Column(db.String(150))


'''------ DNS CONSISTENCY ------'''


class DnsConsistency(db.Model):
    __tablename__ = "dns_consistency"
    __table_args__ = {'extend_existing': True}  # for when error occurs
    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.Integer, db.ForeignKey('meta_table.set_id', ondelete='CASCADE'))
    meta = db.relationship('MetaTable', backref=db.backref('dns_consistency', passive_deletes=True))
    input = db.Column(db.String)
    country = db.Column(db.String)
    asn = db.Column(db.String)
    test_date = db.Column(db.TIMESTAMP)
    test_name = db.Column(db.String)
    test_version = db.Column(db.String)
    download_link = db.Column(db.String)
    query_answers = db.relationship("DnsTestKeys", backref=db.backref("dns_consistency", uselist=False))


class DnsTestKeys(db.Model):
    __tablename__ = "dns_test_keys"
    __table_args__ = {'extend_existing': True}
    dns_id = db.Column(db.Integer, db.ForeignKey('dns_consistency.id', ondelete='CASCADE'), primary_key=True)
    dns_cons = db.relationship('DnsConsistency', backref=db.backref("dns_test_keys", passive_deletes=True))
    success_rate = db.Column(db.String(10))
    inconsistent_rate = db.Column(db.String(10))
    errors = db.relationship("Errors", backref="dns_test_keys")
    failed = db.relationship("Failed", backref="dns_test_keys")
    inconsistent = db.relationship("Inconsistent", backref="dns_test_keys")
    queries = db.relationship("DnsQueries", backref="dns_test_keys")


class Errors(db.Model):
    __tablename__ = "dns_errors"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    test_key_id = db.Column(db.Integer, db.ForeignKey('dns_test_keys.dns_id', ondelete='CASCADE'))
    test_keys = db.relationship('DnsTestKeys', backref=db.backref('dns_errors_d', passive_deletes=True))
    resolver_ip = db.Column(db.String(50))
    error_string = db.Column(db.String(50))


class Failed(db.Model):
    __tablename__ = "dns_failed"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    test_key_id = db.Column(db.Integer, db.ForeignKey('dns_test_keys.dns_id', ondelete='CASCADE'))
    test_keys = db.relationship('DnsTestKeys', backref=db.backref('dns_failed_d', passive_deletes=True))
    address = db.Column(db.String(50))


class Inconsistent(db.Model):
    __tablename__ = "dns_inconsistent"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    test_key_id = db.Column(db.Integer, db.ForeignKey('dns_test_keys.dns_id', ondelete='CASCADE'))
    test_keys = db.relationship('DnsTestKeys', backref=db.backref('dns_inconsistent_d', passive_deletes=True))
    address = db.Column(db.String)


class DnsQueries(db.Model):
    __tablename__ = "dns_queries"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    test_key_id = db.Column(db.Integer, db.ForeignKey('dns_test_keys.dns_id', ondelete='CASCADE'))
    test_keys = db.relationship('DnsTestKeys', backref=db.backref('dns_queries_d', passive_deletes=True))
    failure = db.Column(db.String)
    hostname = db.Column(db.String)
    query_type = db.Column(db.String)
    resolver_hostname = db.Column(db.String)
    resolver_port = db.Column(db.String)
    answers = db.relationship("DnsAnswers", backref="dns_queries")


class DnsAnswers(db.Model):
    __tablename__ = "dns_answers"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('dns_queries.id', ondelete='CASCADE'))
    query = db.relationship('DnsQueries', backref=db.backref('dns_answers_d', passive_deletes=True))
    answer_type = db.Column(db.String)
    ipv4 = db.Column(db.String)
    ttl = db.Column(db.String)


'''------ Table Schema(s) ------'''


class MetaTableSchema(ma.Schema):
    set_id = fields.Integer()
    set_name = fields.String()
    test_name = fields.String()
    comment = fields.String()
    creation_date = fields.DateTime()

    class Meta:
        ordered = True


class WebconnSchema(ma.Schema):
    id = fields.Integer()
    set_id = fields.Integer()
    tested_url = fields.String(150)
    country = fields.String(5)
    asn = fields.String(10)
    test_date = fields.DateTime()
    test_version = fields.String()
    download_link = fields.String()
    set_creation_date = fields.DateTime()

    class Meta:
        ordered = True


class WebTestKeysSchema(ma.Schema):
    webconn_id = fields.Integer()
    accessible = fields.Boolean()
    blocking = fields.String()
    body_length_match = fields.Boolean()
    client_resolver = fields.String()
    control_failure = fields.String()
    dns_consistency = fields.String()
    headers_match = fields.Boolean()
    http_experiment_failure = fields.String()
    status_code_match = fields.Boolean()
    title_match = fields.Boolean()

    class Meta:
        ordered = True


class WebQueriesSchema(ma.Schema):
    id = fields.Integer()
    test_key_id = fields.Integer()
    failure = fields.String(150)
    hostname = fields.String()
    query_type = fields.String()
    resolver_hostname = fields.String()
    resolver_port = fields.String()

    class Meta:
        ordered = True


class ControlHttpRequestSchema(ma.Schema):
    test_key_id = fields.Integer()
    body_length = fields.Integer()
    failure = fields.String()
    headers = fields.Dict()
    status_code = fields.Integer()
    title = fields.String()

    class Meta:
        ordered = True


class WebAnswersSchema(ma.Schema):
    id = fields.Integer()
    query_id = fields.Integer()
    answer_type = fields.String()
    ipv4 = fields.String()
    ttl = fields.String()

    class Meta:
        ordered = True


class RequestsSchema(ma.Schema):
    test_key_id = fields.Integer()
    failure = fields.String(250)
    request_headers = fields.Dict()
    request_method = fields.String(5)
    request_url = fields.String()
    response_code = fields.Integer()
    response_headers = fields.Dict()
    response_body = fields.String()

    class Meta:
        ordered = True


class ControlTcpConnectSchema(ma.Schema):
    id = fields.Integer()
    test_key_id = fields.Integer()
    address = fields.String(150)
    result = fields.Dict()

    class Meta:
        ordered = True


class ControlDnsSchema(ma.Schema):
    test_key_id = fields.Integer()
    address = fields.String()
    failure = fields.String(150)

    class Meta:
        ordered = True


class TcpConnectSchema(ma.Schema):
    id = fields.Integer()
    test_key_id = fields.Integer()
    ip = fields.String(150)
    port = fields.Integer()
    blocked = fields.String(150)
    failure = fields.String(150)
    success = fields.String(150)

    class Meta:
        ordered = True


class DnsConsistencySchema(ma.Schema):
    id = fields.Integer()
    set_id = fields.Integer()
    input = fields.String()
    country = fields.String()
    test_date = fields.DateTime()
    test_name = fields.String()
    test_version = fields.String()
    download_link = fields.String()

    class Meta:
        ordered = True


class DnsTestKeysSchema(ma.Schema):
    dns_id = fields.Integer()
    success_rate = fields.String()
    inconsistent_rate = fields.String()

    class Meta:
        ordered = True


class ErrorsSchema(ma.Schema):
    id = fields.Integer()
    test_key_id = fields.Integer()
    resolver_ip = fields.String()
    error_string = fields.String()

    class Meta:
        ordered = True


class FailedSchema(ma.Schema):
    id = fields.Integer()
    test_key_id = fields.Integer()
    address = fields.String()

    class Meta:
        ordered = True


class InconsistentSchema(ma.Schema):
    id = fields.Integer()
    test_key_id = fields.Integer()
    address = fields.String()

    class Meta:
        ordered = True


class DnsQueriesSchema(ma.Schema):
    id = fields.Integer()
    test_key_id = fields.Integer()
    failure = fields.String()
    hostname = fields.String()
    query_type = fields.String()
    resolver_hostname = fields.String()
    resolver_port = fields.String()

    class Meta:
        ordered = True


class DnsAnswersSchema(ma.Schema):
    id = fields.Integer()
    query_id = fields.Integer()
    answer_type = fields.String()
    ipv4 = fields.String()
    ttl = fields.String()

    class Meta:
        ordered = True


'''------ API Schema ------'''


class StorePostSchema(ma.Schema):
    set_name = fields.String(required=True)
    country = fields.String(2)
    asn = fields.String(25)
    url = fields.String()
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    comment = fields.String()
    test_name = fields.String(required=True)


'''---- Extra Schemas ----'''


class HeadersSchema(ma.Schema):
    field_name = fields.String(required=True)
    target_data = fields.String(required=True)
    country = fields.String(2)
    asn = fields.String()
    url = fields.String()
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    test_name = fields.String()


class BodySchema(ma.Schema):
    set_name = fields.String(required=True)
    target_body = fields.String(required=True)
    country = fields.String(2)
    asn = fields.String()
    url = fields.String()
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    test_name = fields.String()
