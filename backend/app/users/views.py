from flask import request
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models import User, Skill, UserSkill, Application, Job
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

users_ns = Namespace('users', description='User related operations')

skill_model = users_ns.model('UserSkill', {
    'skill_name': fields.String(required=True),
    'level': fields.String()
})

user_update_model = users_ns.model('UserUpdate', {
    'name': fields.String(description='User name'),
    'skills': fields.List(fields.Nested(skill_model))
})

@users_ns.route('/me')
class UserResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        skills = []
        for us in user.skills:
            if us.skill:
                skills.append({'skill_name': us.skill.name, 'level': us.level})

        return {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'skills': skills
        }, 200

    @jwt_required()
    @users_ns.expect(user_update_model)
    def put(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
             return {'message': 'User not found'}, 404
             
        data = request.json
        
        if 'name' in data:
            user.name = data['name']
        
        if 'skills' in data:
            UserSkill.query.filter_by(user_id=user.id).delete()
            for skill_data in data['skills']:
                skill_name = skill_data.get('skill_name')
                if not skill_name:
                    continue
                level = skill_data.get('level', 'Beginner')
                skill = Skill.query.filter_by(name=skill_name).first()
                if not skill:
                    skill = Skill(name=skill_name)
                    db.session.add(skill)
                    db.session.flush()
                us = UserSkill(user_id=user.id, skill_id=skill.id, level=level)
                db.session.add(us)
                
        db.session.commit()
        return {'message': 'User updated successfully'}, 200

@users_ns.route('/me/dashboard')
class UserDashboard(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        role = claims.get('role')
        
        activity = []
        if role == 'STUDENT':
            applications = Application.query.filter_by(student_id=current_user_id).order_by(Application.id.desc()).limit(10).all()
            for app in applications:
                job = Job.query.get(app.job_id)
                activity.append({
                    'type': 'APPLICATION',
                    'job_id': job.id,
                    'job_title': job.title,
                    'job_budget': job.budget,
                    'app_status': app.status,
                    'job_status': job.status,
                    'date': app.id # Using ID as rough proxy for date if created_at isn't on Application
                })
        elif role == 'PROVIDER' or role == 'ADMIN':
            jobs = Job.query.filter_by(provider_id=current_user_id).order_by(Job.created_at.desc()).limit(10).all()
            for job in jobs:
                activity.append({
                    'type': 'JOB_POSTED',
                    'job_id': job.id,
                    'job_title': job.title,
                    'job_budget': job.budget,
                    'job_status': job.status,
                    'date': job.created_at.strftime("%Y-%m-%d")
                })
                
        return activity, 200
