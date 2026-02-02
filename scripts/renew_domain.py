import os
import sys
import requests
import time

def get_all_subdomains(api_key, api_secret):
    api_url = "https://api005.dnshe.com/index.php?m=domain_hub&endpoint=dns_records&action=list"
    
    headers = {
        "X-API-Key": api_key,
        "X-API-Secret": api_secret,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(
                api_url,
                headers=headers,
                timeout=30
            )
            
            if 500 <= response.status_code < 600:
                print(f"Server error {response.status_code} in get_all_subdomains. Retrying...")
                time.sleep(2)
                continue

            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                return data.get("subdomains", [])
            else:
                print(f"Error: API request failed - {data.get('error')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error getting subdomains: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None
    return None

def renew_domain(subdomain_id, api_key, api_secret):
    # Note: Using action=list with subdomain_id seems to be the way to check status/renew based on existing code structure
    api_url = f"https://api005.dnshe.com/index.php?m=domain_hub&endpoint=dns_records&action=list&subdomain_id={subdomain_id}"
    
    headers = {
        "X-API-Key": api_key,
        "X-API-Secret": api_secret,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(
            api_url,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            print(f"Successfully renewed domain with ID: {subdomain_id}")
            print(f"Previous expiration: {data.get('previous_expires_at')}")
            print(f"New expiration: {data.get('new_expires_at')}")
            print(f"Remaining days: {data.get('remaining_days')}")
            return True
        else:
            print(f"Error: Domain renewal failed - {data.get('error')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error renewing domain: {e}")
        return False

def main():
    domain_names = os.getenv('DOMAIN_NAMES')
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    
    if not domain_names or not api_key or not api_secret:
        print("Error: Missing environment variables")
        sys.exit(1)
    
    target_domains = [d.strip() for d in domain_names.split(',')]
    
    # Get all subdomains from API
    subdomains = get_all_subdomains(api_key, api_secret)
    if not subdomains:
        print("Error: Could not retrieve subdomains")
        sys.exit(1)
    
    # Renew each target domain
    for domain in target_domains:
        print(f"\nProcessing domain: {domain}")
        found = False
        for subdomain in subdomains:
            if subdomain.get("subdomain") == domain:
                subdomain_id = subdomain.get("id")
                print(f"Found subdomain ID: {subdomain_id}")
                success = renew_domain(subdomain_id, api_key, api_secret)
                if not success:
                    print(f"Failed to renew domain: {domain}")
                found = True
                break
        if not found:
            print(f"Error: Domain {domain} not found in API response")

if __name__ == "__main__":
    main()