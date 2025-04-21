from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token

from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
with app.app_context():
    db.create_all()

jwt = JWTManager(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and user.check_password(data['password']):
        token = create_access_token(identity=user.id)
        return jsonify({'message': 'Login successful', 'token': token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/create-user', methods=['POST', 'GET'])
def create_user():
    # Set up logging configuration if not already done at application level
    import logging
    # Configure logging to output to console and/or file
    if not app.logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

    if request.method == 'POST':
        try:
            # Log the form data properly
            app.logger.info("Form data received: %s", request.form)

            # Validate required fields
            required_fields = ['username', 'email', 'name', 'age', 'password']
            for field in required_fields:
                if field not in request.form or not request.form[field]:
                    app.logger.error(f"Missing required field: {field}")
                    # flash(f"Error: {field} is required", "error")
                    return render_template('user/create_user.html')

            # Create user object
            user = User(
                username=request.form['username'],
                email=request.form['email'],
                name=request.form['name'],
                age=int(request.form['age'])  # Convert age to integer
            )
            user.set_password(request.form['password'])

            # Save user to a database
            db.session.add(user)
            db.session.commit()

            app.logger.info(f"User created successfully: {user.username} (ID: {user.id})")
            # flash("User created successfully!", "success")
            return redirect(url_for('user', user_id=user.id))

        except Exception as e:
            db.session.rollback()  # Rollback transaction in case of error
            app.logger.error(f"Error creating user: {str(e)}")
            # flash(f"Error creating user: {str(e)}", "error")
            return render_template('user/create_user.html')
    else:
        return render_template('user/create_user.html')

@app.route('/users')
def users():
    sort_order = request.args.get('sort', 'asc')
    db_users = User.get_all_users(order_by=sort_order)

    return render_template('user/users.html', users=db_users, current_sort=sort_order)

@app.route('/user/<int:user_id>')
def user(user_id: int):
    db_user = User.query.filter_by(id=user_id).first()

    return render_template('user/user.html', user=db_user)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id: int):

    db_user = User.query.filter_by(id=user_id).first()

    if request.method == 'POST':
        form_user = request.form
        db_user.username = form_user['username']
        db_user.name = form_user['name']
        db_user.age = int(form_user['age'])
        db_user.email = form_user['email']
        db.session.commit()
        return redirect(url_for('user', user_id=user_id))
    else:
        return render_template('user/edit_user.html', user=db_user)

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id: int):
    try :
        db_user = User.query.filter_by(id=user_id).first()
        db.session.delete(db_user)
        db.session.commit()
        return redirect(url_for('users'))
    except Exception as e:
        return f"Error deleting user: {str(e)}"


if __name__ == '__main__':
    app.run()
