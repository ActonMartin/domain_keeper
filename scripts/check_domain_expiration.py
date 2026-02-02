import os
from datetime import datetime
import pytz
import sys
import requests
import time

def get_domain_expiration_date(domain_name, api_key, api_secret):
    # Use official API endpoint from documentation
    api_endpoints = [
        "https://api005.dnshe.com/index.php?m=domain_hub&endpoint=dns_records&action=list"
    ]
    
    headers = {
        "X-API-Key": api_key,
        "X-API-Secret": api_secret,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for api_url in api_endpoints:
        # Retry logic for 502/504 errors
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    api_url,
                    headers=headers,
                    timeout=30
                )
                
                # If we get a 5xx error, retry
                if 500 <= response.status_code < 600:
                    print(f"Server error {response.status_code} on attempt {attempt+1}/{max_retries}. Retrying...")
                    time.sleep(2)
                    continue
                    
                response.raise_for_status()
                
                try:
                    data = response.json()
                except ValueError:
                    print(f"Error: Invalid JSON response from {api_url}")
                    print(f"Response content: {response.text[:200]}...")
                    return None

                if data.get("success"):
                    for subdomain in data.get("subdomains", []):
                        if subdomain.get("subdomain") == domain_name:
                            expires_at = subdomain.get("expires_at")
                            if expires_at:
                                return datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
                    print(f"Error: Domain {domain_name} not found in API response")
                    return None
                else:
                    print(f"Error: API request failed - {data.get('error')}")
                    # If it's a logic error, don't verify other endpoints, but here we only have one.
                    return None

            except requests.exceptions.HTTPError as e:
                print(f"HTTP Error with endpoint {api_url}: {e}")
                if response.status_code == 404:
                     print("Make sure the API URL is correct and the server is reachable.")
                continue
            except requests.exceptions.RequestException as e:
                print(f"Connection Error with endpoint {api_url}: {e}")
                continue
    
    print(f"All API endpoints failed for domain {domain_name}")
    return None

def check_domain(domain_name, api_key, api_secret):
    expiration_date = get_domain_expiration_date(domain_name, api_key, api_secret)
    if not expiration_date:
        print(f"Error: Could not retrieve expiration date for {domain_name}")
        return False

    today = datetime.now(pytz.UTC)
    if expiration_date.tzinfo is None:
        expiration_date = expiration_date.replace(tzinfo=pytz.UTC)
    days_remaining = (expiration_date - today).days

    print(f"\nDomain: {domain_name}")
    print(f"Expiration Date: {expiration_date.strftime('%Y-%m-%d')}")
    print(f"Days Remaining: {days_remaining}")

    if days_remaining <= 30:
        print(f"Domain {domain_name} needs renewal (30 days or less remaining)")
        return True
    else:
        print(f"Domain {domain_name} does not need renewal yet")
        return False

def main():
    domain_names = os.getenv('DOMAIN_NAMES')
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    
    if not domain_names or not api_key or not api_secret:
        print("Error: Missing environment variables")
        sys.exit(1)

    domains = [d.strip() for d in domain_names.split(',')]
    needs_renewal = False

    for domain in domains:
        if check_domain(domain, api_key, api_secret):
            needs_renewal = True

    # Set output variable for GitHub Actions using the new method
    github_output = os.getenv('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"needs_renewal={str(needs_renewal).lower()}\n")
    else:
        # Fallback for local testing
        print(f"::set-output name=needs_renewal::{str(needs_renewal).lower()}")

if __name__ == "__main__":
    main()