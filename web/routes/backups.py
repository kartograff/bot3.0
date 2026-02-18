from flask import Blueprint, render_template

backups_bp = Blueprint('backups', __name__)

@backups_bp.route('/backups')
def backups_list():
    return render_template('admin/backups.html', backups=[])