import sys, time
import signal
from time import gmtime, strftime
from bigneuron_app import db
from bigneuron_app.jobs.models import Job
from bigneuron_app.jobs import job_manager
from bigneuron_app.clients import sqs, dynamo
from bigneuron_app.jobs.constants import PROCESS_JOBS_CREATED_TASK, PROCESS_JOBS_IN_PROGRESS_TASK
from bigneuron_app.emails import email_manager
import bigneuron_app.clients.constants as client_constants
from bigneuron_app.utils import logger


def poll_jobs_created_queue():
	log = logger.get_logger("JobsCreatedTask")
	while True:
		try:
			log.info("Polling jobs_created queue")
			update_jobs_created()
		except Exception, err:
			log.error("ERROR while reading and processing job_created \n" + err)
		finally:
			time.sleep(10)

def poll_jobs_in_progress_queue():
	log = logger.get_logger("JobsInProgressTask")
	while True:
		try:
			log.info("Polling jobs_in_progress queue")
			update_jobs_in_progress()
		except Exception, err:
			log.error("ERROR while reading and processing job_in_progress \n" + err)
		finally:
			time.sleep(10)

def update_jobs_in_progress():
	jobs_in_progress = job_manager.get_jobs_by_status("IN_PROGRESS")
	for job in jobs_in_progress:
		job_items = job_manager.get_job_items(job.job_id)
		complete = True
		has_error = False
		for job_item in job_items:
			if job_item['job_item_status'] == 'ERROR':
				has_error = True
			elif job_item['job_item_status'] in ['IN_PROGRESS', 'CREATED']:
				complete = False

		if complete:
			if has_error:
				job.status_id = job_manager.get_job_status_id("COMPLETE_WITH_ERRORS")
			else:
				job.status_id = job_manager.get_job_status_id("COMPLETE")
			db.session.commit()
			email_manager.send_job_complete_email(job)

def update_jobs_created():
	jobs_created = job_manager.get_jobs_by_status("CREATED")
	for job in jobs_created:
		job.status_id = job_manager.get_job_status_id("IN_PROGRESS")
		db.session.commit()
		email_manager.send_job_created_email(job)

def signal_handler(signal, frame):
	print "Exiting..."
	sys.exit(0)



# Unit Tests #
