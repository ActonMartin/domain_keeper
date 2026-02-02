# DNSHE 域名自动续期

本项目使用 GitHub Actions 实现 DNSHE 域名的自动续期。

## 功能特性

- 每日自动检查域名剩余有效期
- 当剩余时间≤30天时自动触发续期
- 使用 GitHub Secrets 安全存储敏感信息
- 支持 DNSHE API v1

## 配置步骤

1. **获取 API 凭证**:
   - 登录 DNSHE 域名管理页面 -> [API 管理]
   - 创建 API Key 和 Secret
   - 在 GitHub 仓库中添加以下 Secrets:
     - `DOMAIN_NAMES`: 逗号分隔的域名列表（例如："1.de5.net,2.de5.net,3.de5.net"）
     - `API_KEY`: DNSHE X-API-Key
     - `API_SECRET`: DNSHE X-API-Secret
     - `EMAIL_TO`: 接收报告的邮箱地址（例如："xxx@88.com"）
     - `SMTP_SERVER`: SMTP 服务器地址（例如："smtp.88.com"）
     - `SMTP_PORT`: SMTP 端口（通常为 465）
     - `SMTP_USER`: 发件人邮箱账号
     - `SMTP_PASSWORD`: 邮箱授权码

## 工作流程

- 每日 UTC 时间 00:00 自动运行
- 支持手动触发执行

## API 执行流程

1. **获取域名 ID**: 自动调用 API 获取所有域名列表，找到目标域名的 subdomain_id
2. **检查有效期**: 使用 python-whois 库查询域名剩余天数
3. **自动续期**: 当剩余≤30天时，自动提交续期请求

## 脚本说明

- `scripts/check_domain_expiration.py`: 检查所有域名的剩余有效期
- `scripts/renew_domain.py`: 通过 DNSHE API 自动续期域名

## 续期详情

- 自动续期 1 年
- 免费域名显示 charged_amount: 0
- 返回续期前后的到期时间和剩余天数 