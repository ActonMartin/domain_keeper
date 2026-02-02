import os
from datetime import datetime, timedelta
import pytz
import sys
import requests

def get_domain_expiration_date(domain_name, api_key, api_secret):
    api_url = "https://api005.dnshe.com/index.php?m=domain_hub&endpoint=dns_records&action=list"
    
    try:
        response = requests.get(
            api_url,
            headers={
                "X-API-Key": api_key,
                "X-API-Secret": api_secret
            }
        )
        
        response.raise_for_status()
        data = response.json()
        
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
            return None
    except Exception as e:
        print(f"Error checking domain expiration for {domain_name}: {e}")
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

    # Set output variable for GitHub Actions
    print(f"\n::set-output name=needs_renewal::{str(needs_renewal).lower()}")

if __name__ == "__main__":
    main()