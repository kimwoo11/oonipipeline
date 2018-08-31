import requests
import pandas as pd
import os

from oonipipeline.config import UPLOAD_PATH
from flask import request, url_for, after_this_request, send_from_directory
from flask_restful import Resource
from oonipipeline.models.models import BodySchema, Requests, Webconn, WebconnSchema, WebTestKeys, MetaTable, db


class BodyResource(Resource):
    # NOTE: The purpose of this endpoint was to be used only through client side to download csv in the web browser
    def get(self):
        filename = request.args.get('filename')

        if filename is None:
            return {'status': 'error', 'message': 'Please provide a filename'}

        @after_this_request
        def remove_csv(response):
            os.remove(os.path.join(UPLOAD_PATH, filename))
            return response

        return send_from_directory(UPLOAD_PATH, filename, mimetype="text/csv", as_attachment=True)

    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'status': 'error', 'message': 'No input data provided'}, 400

        # check for errors in user input
        data, errors = BodySchema().load(json_data)
        if errors:
            return {'status': 'error', 'message': errors}, 422

        # === Parameters === #
        set_name = json_data.get('set_name', None)  # required
        target_body = json_data.get('target_body', None)
        country = json_data.get('country', None)
        asn = json_data.get('asn', None)  # Not Required
        url = json_data.get('url', None)  # Not Required
        start = json_data.get('start_date', None)  # Required
        end = json_data.get('end_date', None)  # Required
        test_name = "web_connectivity"

        post_data = {'set_name': set_name}

        # We do the following so that null is not appended into the dictionary. If an input is not
        # provided, it should not be included in the post request to /store
        if country:
            post_data['country'] = country
        if asn:
            post_data['asn'] = asn
        if url:
            post_data['url'] = url
        if start:
            post_data['start_date'] = start
        if end:
            post_data['end_date'] = end
        if test_name:
            post_data['test_name'] = test_name

        r = requests.post(url_for("api.storeresource",  _external=True), json=post_data)

        # for when post request experiences an unexpected error:
        try:
            if r.status_code == 500:
                return {'status': 'error', 'message': 'There has been an internal error. Please try again.'}, 400
            response = r.json()
            if response['status'] == 'error':
                return response, 400
        except KeyError:
            requests.delete(url_for("api.metatableresource", _external=True), json={'set_name': set_name})
            return {'status': 'error', 'message': 'There has been an internal error. Please try again.'}, 400

        set_id = db.session.query(Webconn.set_id).join(MetaTable).filter(MetaTable.set_name == set_name).first()[0]

        # remove line breaks to be more consistent with limitations in the 'like' query

        target_body = target_body.replace('\n', '').replace('\r', '')
        data_set = db.session.query(Webconn).join(WebTestKeys).join(Requests).\
            filter(Requests.response_body.like("%" + target_body + "%")).\
            filter(Webconn.set_id == set_id).all()  # to not include querying from existing data

        if not data_set:
            requests.delete(url_for("api.metatableresource", _external=True), json={'set_id': set_id})
            return {'status': 'success', 'message': 'No data found that fits provided specifications'}, 400

        result = WebconnSchema(many=True).dump(data_set).data

        requests.delete(url_for("api.metatableresource", _external=True), json={'set_id': set_id})

        df = pd.DataFrame(result)
        filename = set_name + ".csv"
        df.to_csv(os.path.join(UPLOAD_PATH, filename))
        return {'status': 'success', 'message': 'Please check your home directory to see the downloaded csv file'}
