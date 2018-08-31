from flask import Blueprint
from flask_restful import Api
from oonipipeline.resources.webconn import WebConnResource
from oonipipeline.resources.metatable import MetaTableResource
from oonipipeline.resources.dns_consistency import DnsConsistencyResource
from oonipipeline.resources.store import StoreResource
from oonipipeline.resources.headers import HeaderResource
from oonipipeline.resources.download import DownloadResource
from oonipipeline.resources.body import BodyResource
from oonipipeline.resources.status import StatusResource

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Routes
api.add_resource(WebConnResource, '/webconn', '/webconn/<string:table>')
api.add_resource(MetaTableResource, '/metatable')
api.add_resource(DnsConsistencyResource, '/dns_consistency', '/dns_consistency/<string:table>')
api.add_resource(StoreResource, '/store')
api.add_resource(HeaderResource, '/headers')
api.add_resource(BodyResource, '/body')
api.add_resource(StatusResource, '/status')
api.add_resource(DownloadResource, '/download', '/download/<string:test_name>', '/download/<string:table>',
                 '/download/<string:test_name>/<string:table>')

