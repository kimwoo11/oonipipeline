from flask import request
from flask_restful import Resource
from oonipipeline.models.models import MetaTable, MetaTableSchema, db


class MetaTableResource(Resource):
    def get(self):

        tables_query = MetaTable.query.all()
        tables = MetaTableSchema(many=True).dump(tables_query).data
        return {"status": "success", "data": tables}, 200

    def put(self):
        """
        Given set_id, change set_name and or comment
        """
        json_data = request.get_json(force=True)
        if not json_data:
            return {'status': 'error', 'message': 'No input data provided'}, 400

        # API Parameters
        set_id = json_data.get('set_id', None)
        set_name = json_data.get('set_name', None)
        comment = json_data.get('comment', None)

        row = MetaTable.query.filter_by(set_id=set_id).first()
        if not row:
            return {'status': 'error', 'message': 'Specified table does not exist'}, 402

        if set_name and comment:
            row.comment = comment
            row.set_name = set_name
        elif set_name:
            row.set_name = set_name
        elif comment:
            row.comment = comment
        else:
            return {'status': 'error', 'message': 'No comment or set_name provided. The meta data has not been changed'}, 400

        db.session.commit()

        new_row = MetaTable.query.filter_by(set_id=set_id).first()
        new_row = MetaTableSchema().dump(new_row).data

        return {'status': 'success', 'updated_data': new_row}

    def delete(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'status': 'error', 'message': 'No input data provided'}, 400

        # API Parameters
        set_name = json_data.get('set_name', None)
        set_id = json_data.get('set_id', None)

        if not (set_name or set_id):
            return {'status': 'error', 'message': 'Please input a set_name or set_id'}, 400

        if set_name:
            meta_set_name = MetaTable.query.filter_by(set_name=set_name)
            if not meta_set_name.first():
                return {'status': 'error', 'message': 'specified table does not exist'}, 402
            result = MetaTableSchema().dump(meta_set_name.first()).data
            meta_set_name.delete()
        elif set_id:
            meta_id = MetaTable.query.filter_by(set_id=set_id)
            if not meta_id.first():
                return {'status': 'error', 'message': 'specified table does not exist'}, 402
            result = MetaTableSchema().dump(meta_id.first()).data
            meta_id.delete()

        db.session.commit()

        return {'status': 'success', 'deleted_table': result}
