from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    stats = {}                     # пустой словарь для статистики
    upcoming = []                   # пустой список для предстоящих записей
    recent_reviews = []              # пустой список для последних отзывов
    return render_template('index.html',
                           stats=stats,
                           upcoming_appointments=upcoming,
                           recent_reviews=recent_reviews)