from flask import Blueprint, render_template, request

web_pages_bp = Blueprint('web_pages', __name__)


@web_pages_bp.route('/')
def home():
    return render_template('home.html')


@web_pages_bp.route('/tables')
def tables():
    return render_template('tables.html')


@web_pages_bp.route('/select_and_store', methods=['GET', 'POST'])
def select_and_store():
    progress = request.data
    return render_template('select_and_store.html', progress=progress)


@web_pages_bp.route('/webconn')
def webconn():
    return render_template('webconn.html')


@web_pages_bp.route('/dns_consistency')
def dns_consistency():
    return render_template('dns_consistency.html')


@web_pages_bp.route('/api')
def api_doc():
    return render_template('api.html')


@web_pages_bp.route('/select_and_store/success')
def success():
    return render_template('success.html')


@web_pages_bp.route('/download')
def download():
    return render_template('download.html')


@web_pages_bp.route('/headers')
def headers():
    return render_template('headers.html')


@web_pages_bp.route('/headers/success')
@web_pages_bp.route('/headers/success/<filename>')
def headers_success(filename=None):
    return render_template('headers_success.html', filename=filename)


@web_pages_bp.route('/body')
def body():
    return render_template('body.html')


@web_pages_bp.route('/body/success')
@web_pages_bp.route('/body/success/<filename>')
def body_success(filename=None):
    return render_template('body_success.html', filename=filename)

