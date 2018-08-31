import pandas as pd
import os

from oonipipeline.config import UPLOAD_PATH
from flask import request, after_this_request, send_from_directory, url_for, redirect
from flask_restful import Resource
from oonipipeline.models.models import (MetaTable, MetaTableSchema, db)


class DownloadResource(Resource):
    def get(self, test_name=None, table=None):
        set_id = request.args.get('set_id')

        # when test_name and table are both not defined
        if not test_name:
            if not table:
                if not set_id:
                    query = db.session.query(MetaTable).all()
                    result = MetaTableSchema(many=True).dump(query).data
                    df = pd.DataFrame(result)
                    filename = 'meta_table.csv'
                    df.to_csv(os.path.join(UPLOAD_PATH, filename))

                    @after_this_request
                    def remove_csv(response):
                        os.remove(os.path.join(UPLOAD_PATH, filename))
                        return response
                    return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)
                else:
                    return {'status': 'error', 'message': 'Please provide a test name and corresponding table'}, 400
            else:
                return {'status': 'error', 'message': 'Please specify a test'}

        if test_name:
            if table:
                if not set_id:
                    return {'status': 'error', 'message': 'Please provide a set id corresponding to the specified'
                                                          ' table and test'}
                else:
                    if test_name == 'web_connectivity':
                        return redirect(url_for('api.webconnresource', _external=True) + '/' + table + '?set_id=' + set_id)
                    elif test_name == 'dns_consistency':
                        return redirect(url_for('api.dnsconsistencyresource', _external=True) + '/' + table + '?set_id=' + set_id)

            else:
                return {'status': 'error', 'message': 'Please provide a table you want to download'}, 400
