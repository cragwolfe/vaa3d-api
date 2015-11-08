from bigneuron_app import db

class Job(db.Model):
	__tablename__ = 'jobs'
	job_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	job_status_id = db.Column(db.Integer, db.ForeignKey('job_status_types.id'), nullable=False)
	created = db.Column(db.DateTime, default=db.func.now())
	last_updated = db.Column(db.DateTime, onupdate=db.func.now())
	job_item = db.relationship('JobItem', backref=db.backref('jobs'))

	def __init__(self, user_id, job_status_id):
		self.user_id = user_id
		self.job_status_id = job_status_id

	def __repr__(self):
		return '<Job %r>' % self.job_id

class JobStatus(db.Model):
	__tablename__ = 'job_status_types'
	id = db.Column(db.Integer, primary_key=True)
	status_name = db.Column(db.String(32), nullable=False)
	description = db.Column(db.String(128))

	__table_args__ = (
        db.UniqueConstraint("id", "status_name"),
    )

	def __init__(self, status_name):
		self.status_name = status_name

	def __repr__(self):
		return '<JobStatus %r>' % self.status_name