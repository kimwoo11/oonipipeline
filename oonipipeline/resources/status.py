from flask_restful import Resource
from oonipipeline.models.models import Status, db


class StatusResource(Resource):
    def get(self):
        status = db.session.query(Status.current, Status.total).\
            filter(Status.id == db.session.query(db.func.max(Status.id))).first()

        if status is not None:
            return {'current': status[0], 'total': status[1]}
        else:
            return {'current': 'empty'}

