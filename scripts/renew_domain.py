import os
import sys
import requests
import time
import datetime
import smtplib
import ssl
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    # Use correct dns_records endpoint
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
        
        print(f"Renewal response for ID {subdomain_id}: {data}")
        
        if data.get("success"):
            print(f"✅ Successfully renewed domain with ID: {subdomain_id}")
            print(f"  Records found: {data.get('count')}")
            print(f"  Domain status: Active")
            # Extract expiration date from records if available
            records = data.get('records', [])
            if records:
                print(f"  First record: {records[0].get('name')} - {records[0].get('type')}")
            return data
        else:
            print(f"❌ Domain renewal failed - {data.get('error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error renewing domain: {e}")
        return None

def send_wxpusher_notification(content, wxpusher_config):
    """发送 WxPusher 微信推送通知"""
    app_token = wxpusher_config.get('WXPUSHER_APP_TOKEN')
    uids = wxpusher_config.get('WXPUSHER_UIDS')
    api_url = wxpusher_config.get('WXPUSHER_URL')
    
    # 检查配置
    if not all([app_token, uids, api_url]):
        print("\n⚠️  WxPusher 配置不完整，跳过微信推送")
        return False
    
    # 解析 UIDs（支持逗号分隔）
    uid_list = [uid.strip() for uid in uids.split(',') if uid.strip()]
    
    if not uid_list:
        print("\n⚠️  WxPusher UIDs 为空，跳过微信推送")
        return False
    
    # 构建请求数据
    payload = {
        "appToken": app_token,
        "content": content,
        "contentType": 1,  # 1 表示文本内容
        "uids": uid_list
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n📱 正在发送 WxPusher 推送...")
        print(f"   API URL: {api_url}")
        print(f"   UIDs: {', '.join(uid_list)}")
        
        response = requests.post(
            api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        # WxPusher 返回格式：{"code": 1000, "msg": "success", "data": {...}}
        if result.get('code') == 1000:
            print("✅ WxPusher 推送成功")
            return True
        else:
            print(f"❌ WxPusher 推送失败: {result.get('msg', '未知错误')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ WxPusher 推送异常: {e}")
        return False
    except Exception as e:
        print(f"❌ WxPusher 推送异常: {e}")
        return False

def send_renewal_report(renewal_results, email_config, wxpusher_config=None):
    from datetime import datetime
    
    # Calculate statistics
    total_domains = len(renewal_results)
    successful_renewals = sum(1 for r in renewal_results if r['success'])
    failed_renewals = total_domains - successful_renewals
    success_rate = (successful_renewals / total_domains * 100) if total_domains > 0 else 0
    
    # Prepare email content
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"域名续期报告 - {current_time} ({successful_renewals}/{total_domains} 成功)"
    
    # Build report header
    body = "╔" + "═" * 68 + "╗\n"
    body += "║" + "域名自动续期报告".center(66) + "║\n"
    body += "╠" + "═" * 68 + "╣\n"
    body += f"║ 报告时间: {current_time:<54}║\n"
    body += f"║ 总域名数: {total_domains:<54}║\n"
    body += f"║ 成功续期: {successful_renewals:<54}║\n"
    body += f"║ 失败续期: {failed_renewals:<54}║\n"
    body += f"║ 成功率:   {success_rate:.1f}%{' ' * 49}║\n"
    body += "╚" + "═" * 68 + "╝\n\n"
    
    # Add summary section
    if successful_renewals > 0:
        body += "✅ 成功续期的域名:\n"
        body += "─" * 70 + "\n"
        for result in renewal_results:
            if result['success']:
                body += f"  🌐 域名: {result['domain']}\n"
                body += f"     ID: {result['id']}\n"
                if result.get('previous_expires_at'):
                    body += f"     原到期时间: {result['previous_expires_at']}\n"
                if result.get('new_expires_at'):
                    body += f"     新到期时间: {result['new_expires_at']}\n"
                if result.get('remaining_days'):
                    body += f"     剩余天数: {result['remaining_days']} 天\n"
                if result.get('charged_amount'):
                    body += f"     续期费用: {result['charged_amount']}\n"
                body += "\n"
        body += "\n"
    
    # Add failed section
    if failed_renewals > 0:
        body += "❌ 失败续期的域名:\n"
        body += "─" * 70 + "\n"
        for result in renewal_results:
            if not result['success']:
                body += f"  🌐 域名: {result['domain']}\n"
                body += f"     ID: {result.get('id', 'N/A')}\n"
                body += f"     错误: {result.get('error', '未知错误')}\n"
                body += "\n"
        body += "\n"
    
    # Add detailed section
    body += "📋 详细信息:\n"
    body += "═" * 70 + "\n"
    for idx, result in enumerate(renewal_results, 1):
        status_icon = "✅" if result['success'] else "❌"
        body += f"\n{idx}. {status_icon} {result['domain']}\n"
        body += f"   状态: {'续期成功' if result['success'] else '续期失败'}\n"
        body += f"   ID: {result.get('id', 'N/A')}\n"
        
        if result['success']:
            if result.get('previous_expires_at'):
                body += f"   原到期时间: {result['previous_expires_at']}\n"
            if result.get('new_expires_at'):
                body += f"   新到期时间: {result['new_expires_at']}\n"
            if result.get('remaining_days'):
                days = result['remaining_days']
                if days > 30:
                    urgency = "🟢 充足"
                elif days > 7:
                    urgency = "🟡 即将到期"
                else:
                    urgency = "🔴 紧急"
                body += f"   剩余天数: {days} 天 {urgency}\n"
            if result.get('charged_amount'):
                body += f"   续期费用: {result['charged_amount']}\n"
        else:
            body += f"   错误信息: {result.get('error', '未知错误')}\n"
    
    # Add footer
    body += "\n" + "═" * 70 + "\n"
    body += "📌 提示:\n"
    body += "  • 绿色 🟢: 剩余天数 > 30 天，状态良好\n"
    body += "  • 黄色 🟡: 剩余天数 7-30 天，需要关注\n"
    body += "  • 红色 🔴: 剩余天数 < 7 天，需要紧急处理\n"
    body += "\n"
    body += "此报告由 Domain Keeper 自动生成并发送。\n"
    body += "如有问题，请检查 GitHub Actions 日志或联系管理员。\n"
    body += "═" * 70 + "\n"
    
    # Send email
    try:
        # Use passed email config
        email_to = email_config.get('EMAIL_TO')
        smtp_server = email_config.get('SMTP_SERVER')
        smtp_port = email_config.get('SMTP_PORT', '465')
        smtp_user = email_config.get('SMTP_USER')
        smtp_password = email_config.get('SMTP_PASSWORD')
        
        # Debug: Print environment variables
        print("\n--- Email Configuration Debug ---")
        print(f"EMAIL_TO: {email_to}")
        print(f"SMTP_SERVER: {smtp_server}")
        print(f"SMTP_PORT: {smtp_port}")
        print(f"SMTP_USER: {smtp_user}")
        print(f"SMTP_PASSWORD: {'***' if smtp_password else 'None'}")
        print("--------------------------------")
        
        # Validate required variables
        if not email_to:
            print("\n❌ 缺少 EMAIL_TO 环境变量")
        if not smtp_server:
            print("\n❌ 缺少 SMTP_SERVER 环境变量")
        if not smtp_user:
            print("\n❌ 缺少 SMTP_USER 环境变量")
        if not smtp_password:
            print("\n❌ 缺少 SMTP_PASSWORD 环境变量")
        
        if not all([email_to, smtp_server, smtp_user, smtp_password]):
            print("\n❌ 缺少邮件配置环境变量")
            return
        
        # Convert port to integer
        try:
            smtp_port = int(smtp_port)
        except ValueError:
            print(f"\n❌ 无效的 SMTP 端口: {smtp_port}")
            return
        
        # Send email using SMTP
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = email_to
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Try SSL first, then fall back to TLS
        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        except (ssl.SSLError, ConnectionRefusedError):
            # Fallback to TLS
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

        print("\n✅ 续期报告已发送到邮箱")
    except Exception as e:
        print(f"\n❌ 发送邮件失败: {e}")
    
    # Send WxPusher notification
    if wxpusher_config:
        # 为 WxPusher 准备内容（添加标题）
        wxpusher_content = f"【{subject}】\n\n{body}"
        send_wxpusher_notification(wxpusher_content, wxpusher_config)

def main():
    domain_names = os.getenv('DOMAIN_NAMES')
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    
    # Get email configuration
    email_config = {
        'EMAIL_TO': os.getenv('EMAIL_TO'),
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': os.getenv('SMTP_PORT', '465'),
        'SMTP_USER': os.getenv('SMTP_USER'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD')
    }
    
    # Get WxPusher configuration
    wxpusher_config = {
        'WXPUSHER_APP_TOKEN': os.getenv('WXPUSHER_APP_TOKEN'),
        'WXPUSHER_UIDS': os.getenv('WXPUSHER_UIDS'),
        'WXPUSHER_URL': os.getenv('WXPUSHER_URL')
    }
    
    if not domain_names or not api_key or not api_secret:
        print("Error: Missing environment variables")
        sys.exit(1)
    
    target_domains = [d.strip() for d in domain_names.split(',')]
    
    # Debug: Print target domains
    print("\n--- Target Domains ---")
    for domain in target_domains:
        print(f"  - {domain}")
    print(f"Total target domains: {len(target_domains)}")
    print("----------------------\n")
    
    # Get all subdomains from API
    subdomains = get_all_subdomains(api_key, api_secret)
    if not subdomains:
        print("Error: Could not retrieve subdomains")
        sys.exit(1)
    
    # Debug: Print all available subdomains
    print("\n--- Available Subdomains from API ---")
    for subdomain in subdomains:
        full_domain = subdomain.get('full_domain', 'N/A')
        subdomain_id = subdomain.get('id')
        status = subdomain.get('status', 'N/A')
        print(f"  - {full_domain} (ID: {subdomain_id}, Status: {status})")
    print(f"Total subdomains found: {len(subdomains)}")
    print("------------------------------------\n")
    
    # Renew each target domain
    renewal_results = []
    for domain in target_domains:
        print(f"\nProcessing domain: {domain}")
        found = False
        
        for subdomain in subdomains:
            # Use full_domain for exact matching (e.g., "jolla.ccwu.cc")
            if subdomain.get("full_domain") == domain:
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
    send_renewal_report(renewal_results, email_config, wxpusher_config)

if __name__ == "__main__":
    main()