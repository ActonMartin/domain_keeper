# 贡献指南

感谢你考虑为 Domain Keeper 项目做出贡献！

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发指南](#开发指南)
- [提交规范](#提交规范)
- [代码规范](#代码规范)

## 行为准则

本项目采用贡献者公约作为行为准则。参与此项目即表示你同意遵守其条款。请阅读 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) 了解详情。

## 如何贡献

### 报告 Bug

如果你发现了 bug，请创建一个 Issue 并包含以下信息：

1. **Bug 描述** - 清晰简洁地描述 bug
2. **复现步骤** - 详细的复现步骤
3. **预期行为** - 描述你期望发生什么
4. **实际行为** - 描述实际发生了什么
5. **环境信息** - 操作系统、Python 版本等
6. **日志输出** - 相关的错误日志或截图

### 建议新功能

如果你有新功能的建议，请创建一个 Issue 并包含：

1. **功能描述** - 详细描述你希望添加的功能
2. **使用场景** - 描述这个功能的使用场景
3. **实现建议** - 如果有实现想法，请分享

### 提交代码

1. **Fork 仓库**
   ```bash
   点击 GitHub 页面右上角的 Fork 按钮
   ```

2. **克隆你的 Fork**
   ```bash
   git clone https://github.com/your-username/domain_keeper.git
   cd domain_keeper
   ```

3. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **进行修改**
   - 编写代码
   - 添加测试
   - 更新文档

5. **提交更改**
   ```bash
   git add .
   git commit -m 'feat: 添加某个功能'
   ```

6. **推送到 GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**
   - 在 GitHub 上创建 Pull Request
   - 填写 PR 模板
   - 等待审核

## 开发指南

### 环境设置

1. **安装 Python 3.11+**
   ```bash
   # 使用 pyenv 或直接安装
   python --version  # 确保版本 >= 3.11
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入测试配置
   ```

### 本地测试

1. **运行主程序**
   ```bash
   python scripts/renew_domain.py
   ```

2. **测试邮件发送**
   ```bash
   python scripts/send_email.py
   ```

3. **检查代码风格**
   ```bash
   pip install flake8
   flake8 scripts/
   ```

### 项目结构

```
domain_keeper/
├── .github/
│   └── workflows/
│       └── main.yml          # GitHub Actions 配置
├── scripts/
│   ├── renew_domain.py       # 主程序
│   └── send_email.py         # 邮件模块
├── .env.example              # 环境变量示例
├── requirements.txt          # 依赖列表
└── README.md                 # 项目文档
```

## 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

### 提交格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

### 示例

```bash
# 新功能
git commit -m 'feat: 添加微信推送功能'

# Bug 修复
git commit -m 'fix: 修复域名匹配逻辑错误'

# 文档更新
git commit -m 'docs: 更新 README 配置说明'

# 重构
git commit -m 'refactor: 优化 API 请求重试逻辑'
```

## 代码规范

### Python 代码规范

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 风格
- 使用 4 个空格缩进
- 行长度不超过 100 字符
- 使用有意义的变量名

### 代码质量

1. **类型提示**
   ```python
   def get_all_subdomains(api_key: str, api_secret: str) -> list:
       ...
   ```

2. **文档字符串**
   ```python
   def send_email(subject: str, body: str) -> bool:
       """
       发送邮件通知
       
       Args:
           subject: 邮件主题
           body: 邮件内容
       
       Returns:
           bool: 发送是否成功
       """
       ...
   ```

3. **错误处理**
   ```python
   try:
       response = requests.get(url)
       response.raise_for_status()
   except requests.exceptions.RequestException as e:
       print(f"Error: {e}")
       return None
   ```

4. **日志输出**
   ```python
   # 使用清晰的日志格式
   print(f"✅ 成功续期域名: {domain}")
   print(f"❌ 续期失败: {error}")
   print(f"⚠️  警告: 配置不完整")
   ```

### 测试要求

- 为新功能添加测试
- 确保所有测试通过
- 测试覆盖率不低于 80%

## Pull Request 检查清单

提交 PR 前，请确认：

- [ ] 代码遵循项目代码规范
- [ ] 已添加必要的文档
- [ ] 已添加必要的测试
- [ ] 所有测试通过
- [ ] 提交信息符合规范
- [ ] PR 描述清晰完整

## 获取帮助

如果你有任何问题，可以：

1. 查阅 [README.md](README.md)
2. 查看 [Issues](https://github.com/ActonMartin/domain_keeper/issues)
3. 创建新的 Issue 提问

## 许可证

通过贡献代码，你同意你的代码将根据项目的 MIT 许可证进行授权。

---

再次感谢你的贡献！🎉
