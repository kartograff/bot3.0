from flask import Blueprint, render_template

channels_bp = Blueprint('channels', __name__)

@channels_bp.route('/channels')
def channels_list():
    return render_template('admin/channels.html', channels=[])