from flask import Flask, request, jsonify
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

if __name__ == '__main__':
    app.run()
