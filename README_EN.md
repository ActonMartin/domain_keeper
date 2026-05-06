# Domain Keeper - DNSHE Domain Auto-Renewal Tool

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-blue?logo=github-actions)](https://github.com/features/actions)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[中文文档](README_CN.md) | English

A GitHub Actions-based DNSHE domain auto-renewal tool with email and WeChat push notifications.

## ✨ Features

- 🔄 **Auto-Renewal** - Daily automatic domain check and renewal
- 📧 **Email Notification** - Detailed renewal reports sent to email
- 📱 **WeChat Push** - Support WxPusher WeChat notifications
- 📊 **Detailed Reports** - Statistics, expiration times, urgency indicators
- 🔒 **Secure Storage** - GitHub Secrets for sensitive information
- 🎯 **Smart Matching** - Automatic domain matching and ID retrieval
- 📈 **Expiration Tracking** - Display domain expiration time and remaining days
- 🚀 **Easy Deployment** - One-click configuration, automatic execution

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Features Detail](#features-detail)
- [Project Structure](#project-structure)
- [FAQ](#faq)
- [Contributing](#contributing)
- [Sponsor](#sponsor)
- [License](#license)

## 🚀 Quick Start

### Prerequisites

- GitHub account
- DNSHE domain service provider account
- SMTP email service (optional)
- WxPusher account (optional, for WeChat push)

### Deployment Steps

1. **Fork this repository**
   ```bash
   Click the Fork button in the top right corner
   ```

2. **Configure GitHub Secrets**

   Go to your forked repository → Settings → Secrets and variables → Actions → New repository secret

   Add the following Secrets:

   | Secret Name | Description | Example |
   |------------|------|------|
   | `DOMAIN_NAMES` | Domain list to renew (comma-separated) | `example1.com,example2.com` |
   | `API_KEY` | DNSHE API Key | `cfsd_xxxxxxxxxx` |
   | `API_SECRET` | DNSHE API Secret | `yyyyyyyyyyyy` |
   | `EMAIL_TO` | Email to receive reports | `your@email.com` |
   | `SMTP_SERVER` | SMTP server address | `smtp.gmail.com` |
   | `SMTP_PORT` | SMTP port | `465` |
   | `SMTP_USER` | Sender email | `your@email.com` |
   | `SMTP_PASSWORD` | Email app password | `your-app-password` |
   | `WXPUSHER_APP_TOKEN` | WxPusher app token (optional) | `AT_xxxxx` |
   | `WXPUSHER_UIDS` | WxPusher user UIDs (optional) | `UID_xxxxx` |
   | `WXPUSHER_URL` | WxPusher API URL (optional) | `http://wxpusher.zjiecode.com/api/send/message` |

3. **Enable GitHub Actions**

   Go to Actions tab, click "I understand my workflows, go ahead and enable them"

4. **Manual trigger test**

   Actions → Domain Auto Renewal → Run workflow → Run workflow

### Get DNSHE API Credentials

1. Login to [DNSHE Domain Management](https://www.dnshe.com)
2. Go to API management page
3. Create new API Key and Secret
4. Copy and save to GitHub Secrets

## ⚙️ Configuration

### Required Configuration

```yaml
# Domain list
DOMAIN_NAMES=example1.com,example2.com,example3.com

# DNSHE API credentials
API_KEY=cfsd_xxxxxxxxxx
API_SECRET=yyyyyyyyyyyy
```

### Email Notification Configuration

```yaml
# Email receiving configuration
EMAIL_TO=your@email.com

# SMTP sending configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your@email.com
SMTP_PASSWORD=your-app-password
```

**Common SMTP Configurations:**

| Email Service | SMTP Server | Port |
|---------|------------|------|
| Gmail | smtp.gmail.com | 465 |
| Outlook | smtp-mail.outlook.com | 587 |
| QQ Mail | smtp.qq.com | 465 |
| 163 Mail | smtp.163.com | 465 |

### WeChat Push Configuration (Optional)

```yaml
# WxPusher configuration
WXPUSHER_APP_TOKEN=AT_xxxxx
WXPUSHER_UIDS=UID_xxxxx
WXPUSHER_URL=http://wxpusher.zjiecode.com/api/send/message
```

**Get WxPusher Credentials:**

1. Follow WxPusher WeChat official account
2. Create an app to get APP_TOKEN
3. Get user UID

## 📊 Features Detail

### Auto-Renewal Process

```
Scheduled/Manual Trigger → Get all subdomains → Match target domains
→ Get expiration time → Call renewal API → Generate report
→ Send email → Send WeChat push
```

### Renewal Report Example

```
╔════════════════════════════════════════════════════════════════════╗
║                    Domain Auto-Renewal Report                        ║
╠════════════════════════════════════════════════════════════════════╣
║ Report Time: 2026-05-06 10:30:00                                     ║
║ Total Domains: 6                                                     ║
║ Successful: 4                                                        ║
║ Failed: 2                                                            ║
║ Success Rate: 66.7%                                                  ║
╚════════════════════════════════════════════════════════════════════╝

✅ Successfully renewed domains:
──────────────────────────────────────────────────────────────────────
  🌐 Domain: example1.com
     ID: 12345
     Previous expiration: 2026-05-10
     New expiration: 2027-05-10
     Remaining days: 365 days
     Renewal fee: $0.00

❌ Failed to renew domains:
──────────────────────────────────────────────────────────────────────
  🌐 Domain: example2.com
     ID: N/A
     Error: Domain not found

📌 Tips:
  • Green 🟢: Remaining days > 30, status good
  • Yellow 🟡: Remaining days 7-30, needs attention
  • Red 🔴: Remaining days < 7, urgent
```

### Scheduled Tasks

- **Execution Time**: Daily at UTC 21:00 (Beijing Time 05:00)
- **Frequency**: Once per day
- **Manual Trigger**: Supported, can run manually on Actions page

## 📁 Project Structure

```
domain_keeper/
├── .github/
│   └── workflows/
│       └── main.yml          # GitHub Actions workflow config
├── scripts/
│   ├── renew_domain.py       # Main program: renewal and report
│   └── send_email.py         # Email sending module
├── .env.example              # Environment variables example
├── .gitignore                # Git ignore config
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

### Core Files

**scripts/renew_domain.py** - Main program
- Get all subdomains list
- Match target domains and get IDs
- Call API for renewal
- Generate detailed reports
- Send email and WeChat notifications

**.github/workflows/main.yml** - Workflow config
- Scheduled task
- Environment variables
- Python environment setup
- Dependencies installation

## ❓ FAQ

### Q: Why is domain not found?

**A:** Possible reasons:
1. Domain name mismatch - Check `DOMAIN_NAMES` configuration
2. Domain deleted - Confirm domain still exists
3. Insufficient API permissions - Check API Key permissions

**Solution:**
Check the `--- Available Subdomains from API ---` section in GitHub Actions logs to compare target domains with actual domains.

### Q: Email sending failed?

**A:** Check these configurations:
1. SMTP server address and port are correct
2. Using email app password instead of login password
3. SMTP service is enabled in email
4. Firewall is not blocking SMTP connection

### Q: How to add multiple WeChat push users?

**A:** Separate multiple UIDs with commas in `WXPUSHER_UIDS`:
```
WXPUSHER_UIDS=UID_xxxxx,UID_yyyyy,UID_zzzzz
```

### Q: How to resolve Node.js version warning?

**A:** Project is configured with `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` to automatically use Node.js 24.

### Q: How to view API response data structure?

**A:** Check debug output in GitHub Actions logs:
- `--- API Response Debug ---` - API response structure
- `--- Renewal Response Debug ---` - Renewal response structure

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Ways to Contribute

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Create Pull Request

### Development Guide

1. Clone repository
   ```bash
   git clone https://github.com/your-username/domain_keeper.git
   cd domain_keeper
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment
   ```bash
   cp .env.example .env
   # Edit .env file with actual values
   ```

4. Local test
   ```bash
   python scripts/renew_domain.py
   ```

## ☕ Sponsor

If this project helps you, consider sponsoring the developer!

### 💝 Sponsorship Methods

- [View sponsorship details](DONATE.md) - WeChat/Alipay QR codes
- [GitHub Sponsors](https://github.com/sponsors) - Official GitHub sponsorship

### 🎯 Usage of Funds

Your sponsorship will be used for:
- ☁️ Domain renewal fees
- 🖥️ Server maintenance costs
- ⏰ Development time

### 🙏 Other Support Methods

If you can't sponsor, you can also:
- ⭐ Star the project
- 🐛 Report bugs or suggest features
- 📖 Improve documentation
- 💻 Contribute code

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [DNSHE](https://www.dnshe.com) - Domain service and API
- [GitHub Actions](https://github.com/features/actions) - Automation platform
- [WxPusher](https://wxpusher.zjiecode.com) - WeChat push service

## 📮 Contact

- Project Home: [https://github.com/ActonMartin/domain_keeper](https://github.com/ActonMartin/domain_keeper)
- Issue Tracker: [Issues](https://github.com/ActonMartin/domain_keeper/issues)

---

⭐ If this project helps you, please give it a Star!
