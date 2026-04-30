import boto3 # This is the official AWS SDK for Python. It allows your code to speak the "S3 language."
from botocore.exceptions import ClientError # Specific error related to S3 operations , Just for exception handing this is taken
from botocore.config import Config
import json
from collections import defaultdict
import os

# Create a "Heavy Duty" configuration
heavy_duty_config = Config(
    region_name='us-east-1',
    signature_version='v4',
    retries={
        'max_attempts': 10,  #  if http path is congested how many times it should wait until declaring failure
        'mode': 'standard'   # 'standard' handles 503s and request throttling perfectly
    },
    max_pool_connections=50  # Allow 50 simultaneous TCP pipes instead of 10. How many simultaneous Http Connection can be made to S3 is defined here
)


class S3StorageManager:
    def __init__(self, bucket_name, endpoint_url="http://localhost:9005",username="admin",aws_secret_key="password123",aws_region="us-east-1"):
        """
        :param endpoint_url: If using LocalStack, usually http://localhost:4566
                             If using MinIO, usually http://localhost:9000
        """
        # We use dummy credentials for local containers

        # This initializes the connection
        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=username,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
            config=heavy_duty_config
        )
        self.bucket_name = bucket_name
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Checks if bucket exists; if not, creates it."""
        '''
        self.s3.head_bucket(Bucket=self.bucket_name)
        
        The "Ping" (Network Layer): head_bucket is a very "cheap" (fast) HTTP HEAD request.

        What it does: it asks the S3 server: "Do you have a bucket with this specific name, and do I have permission to see it?" * Why use it: It doesn't download any data; it only checks for the existence of the "folder" structure. If it returns a 200 OK, the code moves past the try block.
        '''
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            self.s3.create_bucket(Bucket=self.bucket_name)
            print(f"Bucket '{self.bucket_name}' created.")

    def upload_data(self, key, data):
        """
        Uploads raw data (string or bytes) directly.
        Useful for saving AI-generated sentences or JSON payloads.

        key (The "Address"): This is a string that acts as the unique identifier for the object in your bucket. In a traditional file system, this is the filename (e.g., "user_101_report.json" or "logs/april_15/error.txt"). S3 uses keys to locate your data later.

        data (The "Payload"): This is the actual content you want to store. It can be a string (like an AI-generated sentence) or bytes (like an image or a compiled file).

        """
        try:
            # This is the core S3 command. It tells the Boto3 client to wrap your data into an HTTP PUT request.
            self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=data)
            return True
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return False

    def update_percentage(self, key, percentage):
        """
        Overwrites the S3 object with a single number.
        """
        try:
            # We convert the number to a string to store it as the body
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=str(percentage),
                ContentType='text/plain'
            )
            return True
        except ClientError as e:
            print(f"Error: {e}")
            return False

    def upload_local_json(self, local_file_path, s3_key):
        """
        Reads a local JSON file and uploads it to a specific S3 path.

        local_file_path: e.g., 'results.json' or 'data/clean_batch.json'
        s3_key: The destination path in S3, e.g., 'backups/today/results.json'
        """
        try:
            # Check if file exists locally before trying to upload
            if not os.path.exists(local_file_path):
                print(f"Error: Local file {local_file_path} not found.")
                return False

            # Use upload_file for better performance and reliability
            self.s3.upload_file(local_file_path, self.bucket_name, s3_key)

            print(f"Successfully uploaded {local_file_path} to s3://{self.bucket_name}/{s3_key}")
            return True

        except ClientError as e:
            print(f"S3 Upload Error: {e}")
            return False

    def get_data(self, key):
        """Retrieves data back from S3 as a string."""
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            return json.loads(response['Body'].read().decode('utf-8'))
        except ClientError as e:
            return None

    def upload_consolidated_data(self,token_data):
        '''
        Workflow - Since we will be dealing with upto 90000 k devices if we upload for each mac 90000 HTTP Connection - Overload
        Therefore will be uploading the data of tokens to S3 every 1000 devices
        token_data - Contains token to Word mapping of only 1000 devices. Goal is we need to append these words to S3 bucket already existent
        :param data:
        :return:
        '''

        for token in token_data:
            key=str(token)
            existing_words = []
            existing_data =self.get_data(key)
            if existing_data:
                pass
            else:
                existing_words = []
            # B. Merge and remove duplicates (using set for efficiency)
            updated_list = list(set(existing_words + token_data[token]))

            # C. Upload back to S3
            self.upload_data(key, json.dumps(updated_list))



# token_buffer = defaultdict(list)
#
# # Adding data to 4 keys (Simulating findings from your files)
# token_buffer["token2.jsonl"].extend(["routing", "bgp", "juniper"])
# token_buffer["token3.jsonl"].extend(["neural", "network", "weights"])
# token_buffer["token4.jsonl"].extend(["postgres", "docker", "s3"])
# token_buffer["token5.jsonl"].extend(["latency", "jitter", "packet"])

# object=S3StorageManager("shreyas")
# #object.upload_data("token10.jsonl",json.dumps(["abc","def","ghi","jkl","shreyas"]))
# new=object.get_data("token10.jsonl")
# if(new):
#     new.append("new_data")
#     object.upload_data("token10.jsonl",json.dumps(new))
#     new = object.get_data("token10.jsonl")
#     print(new)
# else:
#     object.upload_data("token10.jsonl", json.dumps(["abc", "def", "ghi", "jkl", "shreyas"]))
#     new = object.get_data("token10.jsonl")
#     print(new)
# object.upload_data("token1.jsonl",json.dumps(new))
# print(object.get_data("token1.jsonl"))

