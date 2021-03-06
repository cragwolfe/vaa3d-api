import sys, time
import signal
import traceback
from time import gmtime, strftime
from bigneuron_app import db
from bigneuron_app import tasks_log
from bigneuron_app.jobs.models import Job
from bigneuron_app.jobs import job_manager
from bigneuron_app.jobs.constants import PROCESS_JOBS_CREATED_TASK, PROCESS_JOBS_IN_PROGRESS_TASK
from bigneuron_app.emails import email_manager
from bigneuron_app.fleet import fleet_manager
import bigneuron_app.clients.constants as client_constants


POLL_JOBS_SLEEP=60
POLL_JOBS_MAX_RUNS=10

def poll_jobs_queue():
	count = 0
	while count < POLL_JOBS_MAX_RUNS:
		try:
			tasks_log.info("Polling jobs created + in-progress queues " + str(count))
			update_jobs_created()
			update_jobs_in_progress()
		except Exception, err:
			tasks_log.error(traceback.format_exc())
		finally:
			count += 1
			time.sleep(POLL_JOBS_SLEEP)
	db.remove()

def update_jobs_in_progress():
	jobs_in_progress = job_manager.get_jobs_by_status("IN_PROGRESS")
	for job in jobs_in_progress:
		job_items = job_manager.get_job_items(job.job_id)
		complete = True
		has_error = False
		for job_item in job_items:
			if job_item['job_item_status'] in ['ERROR','TIMEOUT']:
				has_error = True
			elif job_item['job_item_status'] in ['CREATED', 'IN_PROGRESS']:
				complete = False
				break

		if complete:
			if has_error:
				job.status_id = job_manager.get_job_status_id("COMPLETE_WITH_ERRORS")
			else:
				job.status_id = job_manager.get_job_status_id("COMPLETE")
			db.commit()
			email_manager.send_job_complete_email(job)

def update_jobs_created():
	jobs_created = job_manager.get_jobs_by_status("CREATED")
	for job in jobs_created:
		tasks_log.info("Found new job")
		job.status_id = job_manager.get_job_status_id("IN_PROGRESS")
		db.commit()
		email_manager.send_job_created_email(job)

