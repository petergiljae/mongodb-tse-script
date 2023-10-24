import os
import subprocess
import sys

if len(sys.argv) != 2:
    print("Usage: python script.py <role_name>")
    sys.exit(1)

# Retrieve the role name from the command-line argument
role_name = sys.argv[1]


# Use curl to fetch security credentials
credential_url = f"http://169.254.169.254/latest/meta-data/iam/security-credentials/{role_name}"

try:
    # Run the curl command
    process = subprocess.Popen(["curl", credential_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        credential_data = stdout.decode("utf-8").splitlines()

        # Extract AccessKeyId, SecretAccessKey, and Token from the response
        access_key_id = None
        secret_access_key = None
        token = None

        for line in credential_data:
            key, _, value = line.partition("=")
            if key == "AccessKeyId":
                access_key_id = value
            elif key == "SecretAccessKey":
                secret_access_key = value
            elif key == "Token":
                token = value

        if access_key_id and secret_access_key and token:
            # Set environment variables
            os.environ["AWS_ACCESS_KEY_ID"] = access_key_id
            os.environ["AWS_SECRET_ACCESS_KEY"] = secret_access_key
            os.environ["AWS_SESSION_TOKEN"] = token

            print("AWS credentials set as environment variables.")
        else:
            print("Failed to parse AWS credentials.")
    else:
        print("Failed to fetch AWS credentials for the specified role.")
except Exception as e:
    print("Error:", str(e))
