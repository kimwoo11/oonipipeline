import pandas as pd
import os

from oonipipeline.config import UPLOAD_PATH
from flask import request, after_this_request, send_from_directory
from flask_restful import Resource
from oonipipeline.models.models import (MetaTable, Webconn, WebTestKeys, ControlDns, ControlHttpRequest, ControlTcpConnect,
                                        WebQueries, WebAnswers, Requests, TcpConnect, MetaTableSchema, WebconnSchema,
                                        WebTestKeysSchema, ControlHttpRequestSchema, WebQueriesSchema, WebAnswersSchema,
                                        RequestsSchema, ControlTcpConnectSchema, ControlDnsSchema, TcpConnectSchema, db)


class WebConnResource(Resource):
    def get(self, table=None):
        set_id = request.args.get('set_id')
        api_download = request.args.get('api_download')

        if not table:
            if set_id:
                query = db.session.query(Webconn).filter(Webconn.set_id == set_id).all()
                result = WebconnSchema(many=True).dump(query).data
                return {'status': 'success', 'data': result}
            else:
                query = db.session.query(MetaTable).filter(MetaTable.test_name == 'web_connectivity').all()
                result = MetaTableSchema(many=True).dump(query).data
                return {'status': 'success', 'data': result}

        if not set_id:
            return {'status': 'error', 'message': 'Please provide a set_id'}, 400

        else:
            if not db.session.query(MetaTable).filter(MetaTable.set_id == set_id).first():
                return {'status': 'error', 'message': 'Please provide a valid set_id'}, 400
            else:
                if table == 'web_test_keys':
                    query = db.session.query(WebTestKeys).join(Webconn).filter(Webconn.set_id == set_id).all()
                    result = WebTestKeysSchema(many=True).dump(query).data
                    df = pd.DataFrame(result)
                    filename = 'set_' + set_id + '-web_test_keys.csv'
                    df.to_csv(os.path.join(UPLOAD_PATH, filename))

                    if api_download != 'true':
                        @after_this_request
                        def remove_csv(response):
                            os.remove(os.path.join(UPLOAD_PATH, filename))
                            return response
                        return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                    return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv'
                                                            ' file'}
                elif table == 'web_connectivity':
                    query = db.session.query(Webconn).filter(Webconn.set_id == set_id).all()
                    result = WebconnSchema(many=True).dump(query).data
                    df = pd.DataFrame(result)
                    filename = 'set_' + set_id + '-web_conn.csv'
                    df.to_csv(os.path.join(UPLOAD_PATH, filename))

                    if api_download != 'true':
                        @after_this_request
                        def remove_csv(response):
                            os.remove(os.path.join(UPLOAD_PATH, filename))
                            return response
                        return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                    return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv'
                                                            ' file'}
                elif table == 'web_queries':
                    query = db.session.query(WebQueries).join(WebTestKeys).join(Webconn).filter(Webconn.set_id == set_id).all()
                    result = WebQueriesSchema(many=True).dump(query).data
                    df = pd.DataFrame(result)
                    filename = 'set_' + set_id + '-web_queries.csv'
                    df.to_csv(os.path.join(UPLOAD_PATH, filename))

                    if api_download != 'true':
                        @after_this_request
                        def remove_csv(response):
                            os.remove(os.path.join(UPLOAD_PATH, filename))
                            return response
                        return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                    return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv'
                                                            ' file'}
                elif table == 'web_answers':
                    query = db.session.query(WebAnswers).join(WebQueries).join(WebTestKeys).join(Webconn). \
                        filter(Webconn.set_id == set_id).all()
                    result = WebAnswersSchema(many=True).dump(query).data
                    df = pd.DataFrame(result)
                    filename = 'set_' + set_id + '-web_answers.csv'
                    df.to_csv(os.path.join(UPLOAD_PATH, filename))

                    if api_download != 'true':
                        @after_this_request
                        def remove_csv(response):
                            os.remove(os.path.join(UPLOAD_PATH, filename))
                            return response
                        return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                    return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv'
                                                            ' file'}
                elif table == 'web_requests':
                    query = db.session.query(Requests).join(WebTestKeys).join(Webconn).filter(Webconn.set_id == set_id).all()
                    result = RequestsSchema(many=True).dump(query).data
                    df = pd.DataFrame(result)
                    filename = 'set_' + set_id + '-web_requests.csv'
                    df.to_csv(os.path.join(UPLOAD_PATH, filename))

                    if api_download != 'true':
                        @after_this_request
                        def remove_csv(response):
                            os.remove(os.path.join(UPLOAD_PATH, filename))
                            return response
                        return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                    return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv'
                                                            ' file'}
                elif table == 'web_control_tcp_connect':
                    query = db.session.query(ControlTcpConnect).join(WebTestKeys).join(Webconn). \
                        filter(Webconn.set_id == set_id).all()
                    result = ControlTcpConnectSchema(many=True).dump(query).data
                    df = pd.DataFrame(result)
                    filename = 'set_' + set_id + '-web_control_tcp_connect.csv'
                    df.to_csv(os.path.join(UPLOAD_PATH, filename))

                    if api_download != 'true':
                        @after_this_request
                        def remove_csv(response):
                            os.remove(os.path.join(UPLOAD_PATH, filename))
                            return response
                        return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                    return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv'
                                                            ' file'}
                elif table == 'web_control_dns':
                    query = db.session.query(ControlDns).join(WebTestKeys).join(Webconn). \
                        filter(Webconn.set_id == set_id).all()
                    result = ControlDnsSchema(many=True).dump(query).data
                    df = pd.DataFrame(result)
                    filename = 'set_' + set_id + '-web_control_dns.csv'
                    df.to_csv(os.path.join(UPLOAD_PATH, filename))

                    if api_download != 'true':
                        @after_this_request
                        def remove_csv(response):
                            os.remove(os.path.join(UPLOAD_PATH, filename))
                            return response
                        return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                    return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv'
                                                            ' file'}
                elif table == 'web_control_http_request':
                    query = db.session.query(ControlHttpRequest).join(WebTestKeys).join(Webconn). \
                        filter(Webconn.set_id == set_id).all()
                    result = ControlHttpRequestSchema(many=True).dump(query).data
                    df = pd.DataFrame(result)
                    filename = 'set_' + set_id + '-web_control_http_request.csv'
                    df.to_csv(os.path.join(UPLOAD_PATH, filename))

                    if api_download != 'true':
                        @after_this_request
                        def remove_csv(response):
                            os.remove(os.path.join(UPLOAD_PATH, filename))
                            return response
                        return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                    return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv'
                                                            ' file'}
                elif table == 'web_tcp_connect':
                    query = db.session.query(TcpConnect).join(WebTestKeys).join(Webconn). \
                        filter(Webconn.set_id == set_id).all()
                    result = TcpConnectSchema(many=True).dump(query).data
                    df = pd.DataFrame(result)
                    filename = 'set_' + set_id + '-web_tcp_connect.csv'
                    df.to_csv(os.path.join(UPLOAD_PATH, filename))

                    if api_download != 'true':
                        @after_this_request
                        def remove_csv(response):
                            os.remove(os.path.join(UPLOAD_PATH, filename))
                            return response
                        return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                    return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv'
                                                            ' file'}
                else:
                    return {'status': 'error', 'message': 'Please select a valid table corresponding to the selected '
                                                          'data set'}, 400
