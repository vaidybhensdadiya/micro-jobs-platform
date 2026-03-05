from flask import request
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models import User
from flask_jwt_extended import create_access_token

auth_ns = Namespace('auth', description='Authentication related operations')

user_register_model = auth_ns.model('UserRegister', {
    'name': fields.String(required=True, description='User name'),
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'role': fields.String(required=True, description='Role: STUDENT, PROVIDER, ADMIN')
})

user_login_model = auth_ns.model('UserLogin', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@auth_ns.route('/register')
class UserRegister(Resource):
    @auth_ns.expect(user_register_model)
    def post(self):
        data = request.json
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'User already exists'}, 400
        
        user = User(
            name=data['name'],
            email=data['email'],
            role=data.get('role', 'STUDENT')
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return {'message': 'User created successfully', 'role': user.role}, 201

@auth_ns.route('/login')
class UserLogin(Resource):
    @auth_ns.expect(user_login_model)
    def post(self):
        data = request.json
        user = User.query.filter_by(email=data['email']).first()
        if user and user.check_password(data['password']):
            # Role can be encoded in token
            access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
            return {'access_token': access_token, 'role': user.role, 'name': user.name}, 200
        return {'message': 'Invalid credentials'}, 401
