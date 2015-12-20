import os
import shutil
import time
import subprocess32 as subprocess
import traceback
from bigneuron_app import items_log
from bigneuron_app.clients.constants import *
from bigneuron_app.utils.constants import USER_JOB_LOG_EXT
from bigneuron_app.clients import s3
from bigneuron_app.jobs.constants import OUTPUT_FILE_SUFFIXES, PLUGINS
from bigneuron_app.utils.constants import JOB_ITEMS_LOG_FILE
from bigneuron_app.utils.command import Command
from bigneuron_app.utils.exceptions import MaxRuntimeException

class Vaa3dJob():
	def __init__(self, input_filename, output_filename, input_file_path, 
		output_file_path, plugin=VAA3D_DEFAULT_PLUGIN, method=VAA3D_DEFAULT_FUNC, channel=1):
		self.plugin = plugin
		self.method = method
		self.channel = channel
		self.input_filename = input_filename
		self.output_filename = output_filename
		self.input_file_path = input_file_path
		self.output_file_path = output_file_path

	def as_dict(self):
		return self.__dict__

def build_vaa3d_job(job_item):
	input_filename = job_item.filename
	output_filename = input_filename + job_item.job.output_file_suffix
	input_file_path = os.path.abspath(input_filename)
	output_file_path = os.path.abspath(output_filename)
	return Vaa3dJob(input_filename, output_filename, input_file_path, output_file_path, 
		job_item.job.plugin, job_item.job.method, job_item.job.channel)

def run_job(job):
	items_log.info("Tracing neuron... " + job['input_filename'])
	input_file_path = os.path.abspath(job['input_filename'])
	output_file_path = os.path.abspath(job['output_filename'])
	log_file_path = output_file_path + USER_JOB_LOG_EXT
	logfile = open(log_file_path, "w")
	cmd_args = [VAA3D_PATH, "-x", job['plugin'], "-f", job['method'], 
		"-i", input_file_path, "-p", str(job['channel']), "-o", output_file_path]
	items_log.info("Running Command: " + " ".join(cmd_args))
	start_time = int(time.time())
	max_runtime_sec = get_timeout(input_file_path)
	cmd = Command(cmd_args, logfile)
	try:
		status = cmd.run(max_runtime_sec)
		runtime = int(time.time()) - start_time
		if status == "OK":
			ok_msg = "\nTrace complete! Runtime = " + str(runtime) + " seconds"
			logfile.write("\n" + ok_msg)
			items_log.info(ok_msg)
		elif status == "TIMEOUT":
			max_runtime_msg = "Throwing Exception b/c Max Runtime Exceeded: " + str(max_runtime_sec) + " seconds"
			logfile.write("\n" + max_runtime_msg)
			items_log.info(max_runtime_msg)
			raise MaxRuntimeException(max_runtime_msg)
		else:
			job_failed_msg = "Throwing Exception b/c Job Item Failed: " + input_file_path
			logfile.write(job_failed_msg)
			raise Exception(job_failed_msg)
	finally:
		logfile.close()

def get_timeout(file_path):
	"""
	Returns filesize in bytes
	1000 bytes = 1 KB
	1000000 bytes = 1 MB
	APP1 = 3.5 secs / MB
	APP1 = .0000033457 secs / byte
	"""
	file_size_bytes = os.stat(file_path).st_size
	items_log.info("Filesize in MB " + str(file_size_bytes/BYTES_PER_MEGABYTE))
	estimated_runtime = SECONDS_PER_BYTE * file_size_bytes
	items_log.info("Estimated Runtime " + str(int(estimated_runtime)) + " seconds")
	timeout = max(MIN_RUNTIME, int(estimated_runtime * BUFFER_MULTIPLIER))
	items_log.info("Runtime w Buffer " + str(timeout) + " seconds")
	return timeout

def cleanup(input_file_path, output_file_path):
	os.remove(input_file_path)
	os.remove(output_file_path)
	filelist = [ f for f in os.listdir(".") if f.endswith(".swc") ]
	for f in filelist:
		os.remove(os.path.abspath(f))

def cleanup_all(list_of_filenames):
	filelist = [ f for f in os.listdir(".") if f.endswith(".swc") ]
	loglist = [ f for f in os.listdir(".") if f.endswith("log.txt") ]
	filelist.extend(loglist)
	filelist.extend(list_of_filenames)
	print "Files " + str(filelist)
	for f in filelist:
		try:
			os.remove(os.path.abspath(f))
		except Exception, e:
			items_log.info("File to remove not found " + str(e))

