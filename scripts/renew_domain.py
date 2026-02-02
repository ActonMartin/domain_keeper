import os
import sys
import requests
import time

def get_all_subdomains(api_key, api_secret):
    api_url = "https://api005.dnshe.com/index.php?m=domain_hub&endpoint=subdomains&action=list"
    
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
    # Use correct renewal endpoint
    api_url = f"https://api005.dnshe.com/index.php?m=domain_hub&endpoint=subdomains&action=renew&subdomain_id={subdomain_id}"
    
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
        
        print(f"Renewal response for ID {subdomain_id}: {data}")
        
        if data.get("success"):
            print(f"✅ Successfully renewed domain with ID: {subdomain_id}")
            print(f"  Message: {data.get('message')}")
            print(f"  Previous expiration: {data.get('previous_expires_at')}")
            print(f"  New expiration: {data.get('new_expires_at')}")
            print(f"  Charged amount: {data.get('charged_amount')}")
            print(f"  Remaining days: {data.get('remaining_days')}")
            return data
        else:
            print(f"❌ Domain renewal failed - {data.get('error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error renewing domain: {e}")
        return None

def send_renewal_report(renewal_results):
    # Import send_email function
    import importlib.util
    spec = importlib.util.spec_from_file_location("send_email", "scripts/send_email.py")
    send_email = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(send_email)
    
    # Prepare email content
    subject = "域名续期报告"
    body = "域名续期报告\n"
    body += "=" * 30 + "\n"
    
    for result in renewal_results:
        body += f"域名: {result['domain']}\n"
        body += f"ID: {result['id']}\n"
        body += f"状态: {'✅ 成功' if result['success'] else '❌ 失败'}\n"
        if result['success']:
            body += f"原到期时间: {result['previous_expires_at']}\n"
            body += f"新到期时间: {result['new_expires_at']}\n"
            body += f"费用: {result['charged_amount']}\n"
            body += f"剩余天数: {result['remaining_days']}\n"
        else:
            body += f"错误信息: {result['error']}\n"
        body += "-" * 30 + "\n"
    
    # Send email
    try:
        send_email.send_email(
            subject,
            body,
            os.getenv('EMAIL_TO'),
            os.getenv('SMTP_SERVER'),
            os.getenv('SMTP_PORT'),
            os.getenv('SMTP_USER'),
            os.getenv('SMTP_PASSWORD')
        )
        print("\n✅ 续期报告已发送到邮箱")
    except Exception as e:
        print(f"\n❌ 发送邮件失败: {e}")

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
    renewal_results = []
    for domain in target_domains:
        print(f"\nProcessing domain: {domain}")
        found = False
        for subdomain in subdomains:
            if subdomain.get("subdomain") == domain:
                subdomain_id = subdomain.get("id")
                print(f"Found subdomain ID: {subdomain_id}")
                result = renew_domain(subdomain_id, api_key, api_secret)
                
                if result:
                    renewal_results.append({
                        'domain': domain,
                        'id': subdomain_id,
                        'success': True,
                        'previous_expires_at': result.get('previous_expires_at'),
                        'new_expires_at': result.get('new_expires_at'),
                        'charged_amount': result.get('charged_amount'),
                        'remaining_days': result.get('remaining_days')
                    })
                else:
                    renewal_results.append({
                        'domain': domain,
                        'id': subdomain_id,
                        'success': False,
                        'error': '续期失败'
                    })
                    print(f"Failed to renew domain: {domain}")
                found = True
                break
        if not found:
            renewal_results.append({
                'domain': domain,
                'id': None,
                'success': False,
                'error': '未找到域名'
            })
            print(f"Error: Domain {domain} not found in API response")
    
    # Send renewal report
    send_renewal_report(renewal_results)

if __name__ == "__main__":
    main()