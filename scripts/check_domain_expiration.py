import whois
import os
from datetime import datetime, timedelta
import sys

def get_domain_expiration_date(domain_name):
    try:
        w = whois.whois(domain_name)
        expiration_date = w.expiration_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        return expiration_date
    except Exception as e:
        print(f"Error checking domain expiration for {domain_name}: {e}")
        return None

def check_domain(domain_name):
    expiration_date = get_domain_expiration_date(domain_name)
    if not expiration_date:
        print(f"Error: Could not retrieve expiration date for {domain_name}")
        return False

    today = datetime.now()
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
    if not domain_names:
        print("Error: DOMAIN_NAMES environment variable not set")
        sys.exit(1)

    domains = [d.strip() for d in domain_names.split(',')]
    needs_renewal = False

    for domain in domains:
        if check_domain(domain):
            needs_renewal = True

    # Set output variable for GitHub Actions
    print(f"\n::set-output name=needs_renewal::{str(needs_renewal).lower()}")

if __name__ == "__main__":
    main()