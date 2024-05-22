import requests
import json
import argparse
from tqdm import tqdm
import os

# Load the fingerprints from the can-i-take-over-xyz repository
def load_fingerprints(file_path):
    print(f"Loading fingerprints from: {file_path}")
    with open(file_path, 'r') as file:
        data = json.load(file)

    fingerprints = {}
    for entry in data:
        # Check if entry is a dictionary and contains expected keys
        if isinstance(entry, dict) and 'service' in entry and 'fingerprint' in entry and 'vulnerable' in entry:
            # Only add fingerprints that are marked as vulnerable
            if entry['vulnerable']:
                service_name = entry.get('service', 'Unknown')
                takeover_string = entry.get('fingerprint', '')
                if takeover_string:
                    fingerprints[service_name] = takeover_string
        else:
            print(f"Unexpected entry format or missing keys: {entry}")

    return fingerprints

# Check for subdomain takeover based on fingerprints
def check_subdomain_takeover(subdomain, fingerprints):
    try:
        response = requests.get(f"http://{subdomain}", timeout=5)
        for service, indicator in fingerprints.items():
            if indicator in response.text:
                return f"Potential takeover detected on {subdomain} ({service})"
        return None  # No issues detected
    except requests.exceptions.RequestException:
        return None  # Error checking subdomain

def main(domain=None, file_path=None):
    # Determine the path to the fingerprints.json file in the same directory as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fingerprints_file = os.path.join(script_dir, 'fingerprints.json')

    # Load fingerprints
    fingerprints = load_fingerprints(fingerprints_file)

    # Get subdomains from file or generate example subdomains
    if file_path:
        with open(file_path, 'r') as file:
            subdomains = [line.strip() for line in file]
    else:
        subdomains = [f"test.{domain}", f"dev.{domain}", f"staging.{domain}"]

    results = []
    for subdomain in tqdm(subdomains, desc="Checking subdomains"):
        result = check_subdomain_takeover(subdomain, fingerprints)
        if result:
            results.append(result)

    for result in results:
        print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Subdomain Takeover Tool')
    parser.add_argument('-d', '--domain', type=str, help='The domain to scan')
    parser.add_argument('-f', '--file', type=str, help='File containing subdomains to scan')

    args = parser.parse_args()

    if not args.domain and not args.file:
        print("Usage: python takeover.py [-d domain | -f file]")
    else:
        main(domain=args.domain, file_path=args.file)
