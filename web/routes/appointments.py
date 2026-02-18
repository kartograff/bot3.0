from flask import Blueprint, render_template, jsonify

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/appointments')
def appointments_list():
    return render_template('appointments.html', appointments=[])

@appointments_bp.route('/appointments_by_date/<date>')
def appointments_by_date(date):
    return jsonify([])