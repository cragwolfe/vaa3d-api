import os
from subprocess import call
from boto.s3.connection import S3Connection
from boto.s3.key import Key

AWS_ACCESS_KEY = os.getenv('VAA3D_AWS_ACCESS_KEY', 'password')
AWS_SECRET_KEY = os.getenv('VAA3D_AWS_SECRET_KEY', 'password')

S3_INPUT_BUCKET='vaa3d-input'
S3_OUTPUT_BUCKET='vaa3d-output'

TEST_INPUT_FILENAME='input.tif'
TEST_OUTPUT_FILENAME='output.swc'
TEST_INPUT_FILE_PATH=os.path.abspath(TEST_INPUT_FILENAME)
TEST_OUTPUT_FILE_PATH=os.path.abspath(TEST_OUTPUT_FILENAME)
print TEST_INPUT_FILE_PATH
print TEST_OUTPUT_FILE_PATH

# Vaa3d Program Directory
# /Applications/vaa3d/vaa3d64.app/Contents/MacOS/vaa3d64
# /home/ec2-user/Vaa3D_CentOS_64bit_v3.100/start_vaa3d.sh
VAA3D_PATH=os.getenv('VAA3D_PATH', '/home/ec2-user/Vaa3D_CentOS_64bit_v3.100/start_vaa3d.sh')
VAA3D_PLUGIN='vn2'
FUNC_NAME='app2'

# Connect to bucket
conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)

def get_bucket(bucket_name):
	return conn.get_bucket(bucket_name, validate=False)

def download_file(filename):
	print "Downloading file..."
	k = Key(get_bucket(S3_INPUT_BUCKET))
	k.key = filename
	k.get_contents_to_filename(TEST_INPUT_FILE_PATH)
	print "Downloading complete!"

def upload_file(filename):
	print "Uploading file..."
	k = Key(get_bucket(S3_OUTPUT_BUCKET))
	k.key = filename
	k.set_contents_from_filename(TEST_OUTPUT_FILE_PATH)
	print "Upload complete!"

def run_vaa3d_job(input_filename, output_filename):
    print "Tracing neuron..."
    call([VAA3D_PATH, "-x", VAA3D_PLUGIN, "-f", FUNC_NAME, "-i", TEST_INPUT_FILE_PATH, "-o", TEST_OUTPUT_FILE_PATH])
    print "Trace complete!"

def cleanup():
        os.remove(TEST_INPUT_FILE_PATH)
	os.remove(TEST_OUTPUT_FILE_PATH)
        filelist = [ f for f in os.listdir(".") if f.endswith(".swc") ]
        for f in filelist:
                print os.path.abspath(f)
                os.remove(os.path.abspath(f))

if __name__ == '__main__':
	download_file(TEST_INPUT_FILENAME)
	run_vaa3d_job(TEST_INPUT_FILENAME, TEST_OUTPUT_FILENAME)
	upload_file(TEST_OUTPUT_FILENAME)
	cleanup()
