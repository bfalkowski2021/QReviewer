# 🚀 QReviewer

**Production-ready automated code review system with AI-powered analysis**

QReviewer is an intelligent code review tool that integrates with GitHub Pull Requests to provide automated, context-aware code analysis using multiple LLM backends including Kiro, Amazon Q, and OpenAI.

## ✨ Features

- **🤖 AI-Powered Analysis**: Intelligent code review using Kiro, Amazon Q, Bedrock, or OpenAI
- **🔗 GitHub Integration**: Seamless PR fetching, analysis, and automated review posting
- **🎯 Multiple Entry Points**: Python script, shell script, Makefile, and API
- **📊 Confidence Scoring**: AI findings rated by confidence level
- **🔍 Inline Comments**: Precise line-by-line feedback on code changes
- **🛡️ Security Focus**: Built-in security pattern detection
- **📚 Learning System**: Adaptive AI that learns from your codebase patterns
- **🔧 Configurable**: Support for multiple LLM backends and custom standards

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Quick install
./install.sh

# Or manual install
pip3 install typer rich requests pydantic
```

### 2. Set GitHub Token
```bash
export GITHUB_TOKEN="your_github_token_here"
```

### 3. Run Your First Review
```bash
# Analyze a PR (dry run)
python qreview.py https://github.com/owner/repo/pull/123

# Analyze and post review to GitHub
python qreview.py https://github.com/owner/repo/pull/123 --post
```

## 📖 Usage Examples

### Basic Analysis
```bash
# Analyze PR without posting
python qreview.py https://github.com/owner/repo/pull/123

# Analyze with specific LLM backend
python qreview.py https://github.com/owner/repo/pull/123 --backend kiro

# Post review to GitHub
python qreview.py https://github.com/owner/repo/pull/123 --post
```

### Shell Script
```bash
# Make executable
chmod +x qreview.sh

# Run review
./qreview.sh https://github.com/owner/repo/pull/123
```

### Makefile
```bash
# Review specific PR
make review PR_URL=https://github.com/owner/repo/pull/123

# Review and post
make review-post PR_URL=https://github.com/owner/repo/pull/123
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
export GITHUB_TOKEN="your_github_token_here"

# Optional - LLM Backend
export QREVIEWER_LLM_BACKEND="kiro"  # kiro, amazon_q, bedrock, openai

# Kiro Configuration
export KIRO_API_URL="http://localhost:3000"
export KIRO_API_KEY="your_kiro_key"

# Amazon Q Configuration  
export Q_CLI_HOST="192.168.1.100"
export Q_CLI_USER="your_username"
export Q_CLI_PORT="22"
```

### Supported Backends
- **Kiro**: Local AI assistant integration
- **Amazon Q**: AWS-powered code analysis
- **Bedrock**: AWS Bedrock Claude models
- **OpenAI**: GPT-4 and other OpenAI models

## 📁 Project Structure

```
QReviewer/
├── qreview.py              # 🚀 Main unified workflow
├── qreview.sh              # 🐚 Shell script wrapper
├── install.sh              # 🔧 Quick dependency installer
├── setup.py                # 🛠️ Python setup script
├── requirements.txt        # 📦 Python dependencies
├── qrev/                   # 📁 Core QReviewer modules
│   ├── cli.py             # 🖥️ CLI interface
│   ├── llm_client.py      # 🤖 LLM backend integration
│   ├── github_api.py      # 🐙 GitHub API client
│   ├── config.py          # ⚙️ Configuration management
│   └── ...                # 📄 Other core modules
├── standards/              # 📋 Code quality standards
├── tests/                  # 🧪 Test suite
├── docs/                   # 📚 Additional documentation
└── examples/               # 💡 Usage examples
```

## 🛠️ Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/bfalkowski2021/QReviewer.git
cd QReviewer

# Install dependencies
./install.sh

# Run tests
python -m pytest tests/
```

### Adding New LLM Backends
1. Create new client in `qrev/llm_client.py`
2. Add configuration in `qrev/config.py`
3. Update CLI options in `qrev/cli.py`
4. Add tests in `tests/`

## 📚 Documentation

- **[Getting Started](GETTING_STARTED.md)**: Detailed setup and first steps
- **[Workflow Guide](WORKFLOW_README.md)**: Complete workflow documentation
- **[Entry Points](ENTRY_POINTS.md)**: All usage methods and examples
- **[API Documentation](docs/)**: API reference and integration guides

## 🔒 Security

- **No Hardcoded Secrets**: All tokens use environment variables
- **Secure API Calls**: Proper authentication and error handling
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: Built-in GitHub API rate limit handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/bfalkowski2021/QReviewer/issues)
- **Documentation**: Check the `docs/` directory
- **Examples**: See `examples/` for usage patterns

## 🎯 Roadmap

- [ ] VS Code extension
- [ ] GitLab integration
- [ ] Bitbucket support
- [ ] Custom rule engine
- [ ] Team analytics dashboard
- [ ] CI/CD pipeline templates

---

**Made with ❤️ for better code reviews**