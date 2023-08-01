import subprocess
import sys

def get_mongodb_srv_records(url):
    try:
        # Run the dig command and capture its output
        dig_command = f"dig SRV _mongodb._tcp.{url} +short"
        dig_process = subprocess.run(dig_command, shell=True, capture_output=True, text=True)

        if dig_process.returncode != 0:
            print(f"Error occurred while executing the dig command: {dig_process.stderr}")
            return []

        dig_output = dig_process.stdout.strip().split('\n')

        if not dig_output:
            print(f"No SRV records found for '{url}'.")
            return []

        # Process the output to extract the required fields
        records = []
        for line in dig_output:
            priority, weight, port, hostname = line.split()
            records.append(f"{port} {hostname.rstrip('.')}")

        return records

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing dig command: {e}")
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    records = get_mongodb_srv_records(url)
    for record in records:
        print(record)
