from flask import request
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models import Application, Job
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

applications_ns = Namespace('applications', description='Application related operations')

@applications_ns.route('/<int:id>/accept')
class ApplicationAccept(Resource):
    @jwt_required()
    def put(self, id):
        """Accept an application (Provider of the job only)"""
        application = Application.query.get_or_404(id)
        job = Job.query.get_or_404(application.job_id)
        
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        if str(job.provider_id) != str(current_user_id) and claims.get('role') != 'ADMIN':
             return {'message': 'Only the provider can accept applications'}, 403
             
        if job.status != 'OPEN':
             return {'message': 'Job is not open'}, 400
             
        # Update application status
        application.status = 'ACCEPTED'
        
        # Update job status
        job.status = 'ASSIGNED'
        
        # Reject other applications
        other_applications = Application.query.filter(Application.job_id == job.id, Application.id != id).all()
        for app in other_applications:
             app.status = 'REJECTED'
             
        db.session.commit()
        return {'message': 'Application accepted successfully'}, 200
