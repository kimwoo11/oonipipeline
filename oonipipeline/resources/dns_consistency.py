import pandas as pd
import os

from oonipipeline.config import UPLOAD_PATH
from flask import request, send_from_directory, after_this_request
from flask_restful import Resource
from oonipipeline.models.models import MetaTableSchema, MetaTable, DnsConsistency, DnsTestKeys, Errors, Failed, Inconsistent,\
    DnsQueries, DnsAnswers, DnsConsistencySchema, DnsTestKeysSchema, ErrorsSchema, FailedSchema, InconsistentSchema, \
    DnsQueriesSchema, DnsAnswersSchema, db


class DnsConsistencyResource(Resource):
    """
    GET: Downloads specified tables through path parameters
    """
    def get(self, table=None):
        set_id = request.args.get('set_id')
        api_download = request.args.get('api_download')

        if not table:
            if not set_id:
                # /api/dns_consistency
                # returns all dns_consistency data sets from meta_table
                query = db.session.query(MetaTable).filter_by(test_name='dns_consistency').all()
                result = MetaTableSchema(many=True).dump(query).data
                return {'status': 'success', 'data': result}
            else:
                # /api/dns_consistency?set_id={set_id}
                # returns specified data set from dns_consistency table
                query = db.session.query(DnsConsistency).filter_by(set_id=set_id).all()
                result = DnsConsistencySchema(many=True).dump(query).data
                return {'status': 'success', 'data': result}
        if not set_id:
            return {'status': 'error', 'message': 'Please provide a set_id'}, 400
        else:
            if not db.session.query(MetaTable).filter_by(set_id=set_id).all():
                return {'status': 'error', 'message': 'Please provide a valid set_id'}, 400
            if table == 'dns_consistency':
                query = db.session.query(DnsConsistency).filter_by(set_id=set_id).all()
                result = DnsConsistencySchema(many=True).dump(query).data
                df = pd.DataFrame(result)
                filename = 'set_' + set_id + '-dns_consistency.csv'
                df.to_csv(os.path.join(UPLOAD_PATH, filename))

                if api_download != 'true':
                    @after_this_request
                    def remove_csv(response):
                        os.remove(os.path.join(UPLOAD_PATH, filename))
                        return response
                    return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv '
                                                        'file'}
            elif table == 'dns_answers':
                query = db.session.query(DnsAnswers).join(DnsQueries).join(DnsTestKeys).join(DnsConsistency).\
                    filter_by(set_id=set_id).all()
                result = DnsAnswersSchema(many=True).dump(query).data
                df = pd.DataFrame(result)
                filename = 'set_' + set_id + '-dns_answers.csv'
                df.to_csv(os.path.join(UPLOAD_PATH, filename))

                if api_download != 'true':
                    @after_this_request
                    def remove_csv(response):
                        os.remove(os.path.join(UPLOAD_PATH, filename))
                        return response
                    return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv '
                                                        'file'}
            elif table == 'dns_queries':
                query = db.session.query(DnsQueries).join(DnsTestKeys).join(DnsConsistency).\
                    filter_by(set_id=set_id).all()
                result = DnsQueriesSchema(many=True).dump(query).data
                df = pd.DataFrame(result)
                filename = 'set_' + set_id + '-dns_queries.csv'
                df.to_csv(os.path.join(UPLOAD_PATH, filename))

                if api_download != 'true':
                    @after_this_request
                    def remove_csv(response):
                        os.remove(os.path.join(UPLOAD_PATH, filename))
                        return response
                    return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv '
                                                        'file'}
            elif table == 'dns_inconsistent':
                query = db.session.query(Inconsistent).join(DnsTestKeys).join(DnsConsistency).filter_by(set_id=set_id).\
                    all()
                result = InconsistentSchema(many=True).dump(query).data
                df = pd.DataFrame(result)
                filename = 'set_' + set_id + '-dns_inconsistent.csv'
                df.to_csv(os.path.join(UPLOAD_PATH, filename))

                if api_download != 'true':
                    @after_this_request
                    def remove_csv(response):
                        os.remove(os.path.join(UPLOAD_PATH, filename))
                        return response
                    return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv '
                                                        'file'}
            elif table == 'dns_failed':
                query = db.session.query(Failed).join(DnsTestKeys).join(DnsConsistency).filter_by(set_id=set_id).all()
                result = FailedSchema(many=True).dump(query).data
                df = pd.DataFrame(result)
                filename = 'set_' + set_id + '-dns_failed.csv'
                df.to_csv(os.path.join(UPLOAD_PATH, filename))

                if api_download != 'true':
                    @after_this_request
                    def remove_csv(response):
                        os.remove(os.path.join(UPLOAD_PATH, filename))
                        return response
                    return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv '
                                                        'file'}
            elif table == 'dns_errors':
                query = db.session.query(Errors).join(DnsTestKeys).join(DnsConsistency).filter_by(set_id=set_id).all()
                result = ErrorsSchema(many=True).dump(query).data
                df = pd.DataFrame(result)
                filename = 'set_' + set_id + '-dns_errors.csv'
                df.to_csv(os.path.join(UPLOAD_PATH, filename))

                if api_download != 'true':
                    @after_this_request
                    def remove_csv(response):
                        os.remove(os.path.join(UPLOAD_PATH, filename))
                        return response
                    return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv '
                                                        'file'}
            elif table == 'dns_test_keys':
                query = db.session.query(DnsTestKeys).join(DnsConsistency).filter_by(set_id=set_id).all()
                result = DnsTestKeysSchema(many=True).dump(query).data
                df = pd.DataFrame(result)
                filename = 'set_' + set_id + '-dns_test_keys.csv'
                df.to_csv(os.path.join(UPLOAD_PATH, filename))

                if api_download != 'true':
                    @after_this_request
                    def remove_csv(response):
                        os.remove(os.path.join(UPLOAD_PATH, filename))
                        return response
                    return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv '
                                                        'file'}
            else:
                return {'status': 'error', 'message': 'Please select a valid table corresponding to the selected '
                                                      'data set'}, 400
