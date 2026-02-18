from flask import Blueprint, render_template

dict_bp = Blueprint('dictionaries', __name__, url_prefix='/admin/dict')

@dict_bp.route('/brands')
def brands_list():
    return render_template('dictionaries/brands.html', brands=[])