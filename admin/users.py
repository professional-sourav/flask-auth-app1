from flask import Blueprint, render_template

users_bp = Blueprint('users', __name__, template_folder='templates')

@users_bp.route('/users')
@users_bp.route('/')
def users_list():
    return render_template('users.html')