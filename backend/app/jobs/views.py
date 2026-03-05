from flask import request
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models import Job, User, Application, Review
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

jobs_ns = Namespace('jobs', description='Job related operations')

job_model = jobs_ns.model('JobCreate', {
    'title': fields.String(required=True, description='Job title'),
    'description': fields.String(required=True, description='Job description'),
    'budget': fields.Float(required=True, description='Job budget'),
    'deadline': fields.String(required=True, description='Deadline (YYYY-MM-DD)')
})

review_response_model = jobs_ns.model('ReviewResponse', {
    'id': fields.Integer(),
    'reviewer_id': fields.Integer(),
    'reviewee_id': fields.Integer(),
    'rating': fields.Integer(),
    'feedback': fields.String()
})

job_response_model = jobs_ns.model('JobResponse', {
    'id': fields.Integer(),
    'title': fields.String(),
    'description': fields.String(),
    'provider_id': fields.Integer(),
    'budget': fields.Float(),
    'deadline': fields.String(),
    'status': fields.String(),
    'created_at': fields.DateTime(),
    'reviews': fields.List(fields.Nested(review_response_model))
})

application_model = jobs_ns.model('ApplicationCreate', {
    'cover_letter': fields.String(required=True, description='Cover letter')
})

application_response_model = jobs_ns.model('ApplicationResponse', {
    'id': fields.Integer(),
    'job_id': fields.Integer(),
    'student_id': fields.Integer(),
    'cover_letter': fields.String(),
    'status': fields.String(),
    'submission_text': fields.String()
})

job_status_model = jobs_ns.model('JobStatusUpdate', {
    'status': fields.String(required=True, description='New status: IN_PROGRESS, SUBMITTED, COMPLETED'),
    'submission_text': fields.String(description='Work submitted by the student (only used when status=SUBMITTED)')
})

@jobs_ns.route('')
class JobList(Resource):
    @jobs_ns.marshal_list_with(job_response_model)
    def get(self):
        """Get all jobs"""
        jobs = Job.query.order_by(Job.created_at.desc()).all()
        return jobs, 200

    @jwt_required()
    @jobs_ns.expect(job_model)
    def post(self):
        """Create a new job (Providers only)"""
        claims = get_jwt()
        if claims.get('role') != 'PROVIDER' and claims.get('role') != 'ADMIN':
            return {'message': 'Only providers can post jobs'}, 403
            
        current_user_id = get_jwt_identity()
        data = request.json
        
        try:
            deadline_date = datetime.strptime(data['deadline'], '%Y-%m-%d')
        except ValueError:
             try:
                 deadline_date = datetime.strptime(data['deadline'][:10], '%Y-%m-%d')
             except ValueError:
                 return {'message': 'Invalid date format, use YYYY-MM-DD'}, 400

        job = Job(
            title=data['title'],
            description=data['description'],
            budget=data['budget'],
            deadline=deadline_date,
            provider_id=current_user_id
        )
        db.session.add(job)
        db.session.commit()
        return {'message': 'Job created successfully', 'job_id': job.id}, 201

@jobs_ns.route('/<int:id>')
class JobResource(Resource):
    @jobs_ns.marshal_with(job_response_model)
    def get(self, id):
        """Get job by ID"""
        job = Job.query.get_or_404(id)
        return job, 200

    @jwt_required()
    @jobs_ns.expect(job_model)
    def put(self, id):
        """Update job (Provider of the job only)"""
        job = Job.query.get_or_404(id)
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        if str(job.provider_id) != str(current_user_id) and claims.get('role') != 'ADMIN':
             return {'message': 'Unauthorized to edit this job'}, 403
             
        data = request.json
        job.title = data.get('title', job.title)
        job.description = data.get('description', job.description)
        job.budget = data.get('budget', job.budget)
        
        if 'deadline' in data:
            try:
                job.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')
            except ValueError:
                job.deadline = datetime.strptime(data['deadline'][:10], '%Y-%m-%d')
                
        db.session.commit()
        return {'message': 'Job updated successfully'}, 200

    @jwt_required()
    def delete(self, id):
        """Delete job (Provider of the job only)"""
        job = Job.query.get_or_404(id)
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        if str(job.provider_id) != str(current_user_id) and claims.get('role') != 'ADMIN':
             return {'message': 'Unauthorized to delete this job'}, 403
             
        db.session.delete(job)
        db.session.commit()
        return {'message': 'Job deleted successfully'}, 200

@jobs_ns.route('/<int:id>/apply')
class JobApply(Resource):
    @jwt_required()
    @jobs_ns.expect(application_model)
    def post(self, id):
        """Apply for a job (Students only)"""
        job = Job.query.get_or_404(id)
        if job.status != 'OPEN':
             return {'message': 'Job is not open for applications'}, 400
             
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        if claims.get('role') != 'STUDENT' and claims.get('role') != 'ADMIN':
             return {'message': 'Only students can apply for jobs'}, 403
             
        # Check for existing application
        existing_app = Application.query.filter_by(job_id=job.id, student_id=current_user_id).first()
        if existing_app:
             return {'message': 'You have already applied for this job'}, 400
             
        data = request.json
        application = Application(
             job_id=job.id,
             student_id=current_user_id,
             cover_letter=data['cover_letter']
        )
        db.session.add(application)
        db.session.commit()
        return {'message': 'Application submitted successfully'}, 201

@jobs_ns.route('/<int:id>/applications')
class JobApplications(Resource):
    @jwt_required()
    @jobs_ns.marshal_list_with(application_response_model)
    def get(self, id):
        """Get applications for a job (Providers only)"""
        job = Job.query.get_or_404(id)
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        if str(job.provider_id) != str(current_user_id) and claims.get('role') != 'ADMIN':
             return {'message': 'Only the provider can view applications'}, 403
             
        return job.applications, 200

@jobs_ns.route('/<int:id>/status')
class JobStatus(Resource):
    @jwt_required()
    @jobs_ns.expect(job_status_model)
    def put(self, id):
        """Update job status"""
        job = Job.query.get_or_404(id)
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        data = request.json
        new_status = data['status']
        role = claims.get('role')
        
        # Check assigned student
        assigned_app = Application.query.filter_by(job_id=job.id, status='ACCEPTED').first()
        is_assigned_student = assigned_app and str(assigned_app.student_id) == str(current_user_id)
        is_provider = str(job.provider_id) == str(current_user_id)
        
        if role == 'STUDENT':
            if not is_assigned_student:
                return {'message': 'Only the assigned student can update this job status'}, 403
            
            if job.status == 'ASSIGNED' and new_status == 'IN_PROGRESS':
                job.status = 'IN_PROGRESS'
            elif job.status == 'IN_PROGRESS' and new_status == 'SUBMITTED':
                job.status = 'SUBMITTED'
                if 'submission_text' in data:
                    assigned_app.submission_text = data['submission_text']
            else:
                return {'message': f'Invalid status transition {job.status} -> {new_status} for STUDENT'}, 400
                
        elif role == 'PROVIDER':
            if not is_provider:
                return {'message': 'Only the job provider can update this job status'}, 403
                
            if job.status == 'SUBMITTED' and new_status == 'COMPLETED':
                job.status = 'COMPLETED'
            elif job.status == 'COMPLETED':
                return {'message': 'Job is already completed'}, 400
            else:
                return {'message': f'Invalid status transition {job.status} -> {new_status} for PROVIDER'}, 400
                
        else:
             return {'message': 'Admin overrides not explicitly defined here'}, 400

        db.session.commit()
        return {'message': f'Job status updated to {job.status}'}, 200

review_model = jobs_ns.model('ReviewCreate', {
    'rating': fields.Integer(required=True, description='Rating (1-5)'),
    'feedback': fields.String(description='Feedback text')
})

@jobs_ns.route('/<int:id>/review')
class JobReview(Resource):
    @jwt_required()
    @jobs_ns.expect(review_model)
    def post(self, id):
        """Leave a review for a completed job"""
        job = Job.query.get_or_404(id)
        
        if job.status != 'COMPLETED':
            return {'message': 'Reviews can only be left for COMPLETED jobs'}, 400
            
        current_user_id = str(get_jwt_identity())
        
        assigned_app = Application.query.filter_by(job_id=job.id, status='ACCEPTED').first()
        if not assigned_app:
             return {'message': 'No student was assigned to this job'}, 400
             
        student_id = str(assigned_app.student_id)
        provider_id = str(job.provider_id)
        
        if current_user_id == provider_id:
             reviewee_id = student_id
        else:
             return {'message': 'Only the provider can leave a review'}, 403
             
        existing_review = Review.query.filter_by(job_id=job.id, reviewer_id=current_user_id).first()
        if existing_review:
             return {'message': 'You have already reviewed this job'}, 400
             
        data = request.json
        review = Review(
            job_id=job.id,
            reviewer_id=current_user_id,
            reviewee_id=reviewee_id,
            rating=data['rating'],
            feedback=data.get('feedback', '')
        )
        db.session.add(review)
        db.session.commit()
        return {'message': 'Review submitted successfully'}, 201
