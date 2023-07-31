import subprocess
import argparse

def retrieve_certificate(url, port):
    # Step 1: Retrieve the certificate and save it to atlas.pem
    openssl_command = f"openssl s_client -connect {url}:{port} 2>&1 < /dev/null | sed -n '/-----BEGIN/,/-----END/p' > ca.pem"
    subprocess.run(openssl_command, shell=True)

def get_ocsp_uri():
    # Step 2: Get the OCSP URI from the certificate in atlas.pem
    openssl_command = "openssl x509 -noout -ocsp_uri -in ca.pem"
    result = subprocess.run(openssl_command, shell=True, capture_output=True, text=True)
    ocsp_uri = result.stdout.strip()
    print("OCSP URL: " + ocsp_uri)
    return ocsp_uri

def retrieve_chains(url, port):
    # Step 3: Retrieve all chains except for CA and write them to chain.pem
    openssl_command = f"openssl s_client -connect {url}:{port} -showcerts 2>&1 < /dev/null | sed -n '/-----BEGIN/,/-----END/p'"
    result = subprocess.run(openssl_command, shell=True, capture_output=True, text=True)

    # Find all the chains except for the first one (server's certificate)
    cert_start = result.stdout.find('-----BEGIN CERTIFICATE-----', 1)
    if cert_start != -1:
        chains = result.stdout[cert_start:].split('-----END CERTIFICATE-----')[0:-1]
        
        # Combine the individual chains (except the first) to create the chain.pem file
        with open("chain.pem", "w") as chain_file:
            for chain in chains:
                chain_file.write(chain + "-----END CERTIFICATE-----\n")    

def send_ocsp_request(ocsp_uri):
    # Step 4: Send the OCSP request and get the OCSP response
    openssl_command = f"openssl ocsp -issuer chain.pem -cert ca.pem -text -url {ocsp_uri}"
    subprocess.run(openssl_command, shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute steps to get OCSP response for a given MongoDB URL and port.")
    parser.add_argument("url", help="MongoDB URL (e.g., cluster0-shard-00-01.uyiji.mongodb.net)")
    parser.add_argument("port", help="MongoDB port (e.g., 27017)")
    args = parser.parse_args()
    
    url = args.url
    port = args.port
    retrieve_certificate(url, port)
    ocsp_uri = get_ocsp_uri()
    if ocsp_uri:
        retrieve_chains(url, port)
        send_ocsp_request(ocsp_uri)
    else:
        print("No OCSP URI found in the certificate.")
