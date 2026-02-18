from flask import Blueprint, render_template

services_bp = Blueprint('services', __name__)

@services_bp.route('/services')
def services_list():
    return render_template('services.html', services=[])