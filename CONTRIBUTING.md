# Contributing to AuraChat Data Extraction

We welcome contributions to the AuraChat Data Extraction project! This guide will help you get started.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- CUDA-capable GPU (recommended)
- Reddit API credentials
- SLURM cluster access (for large-scale extraction)

### Quick Setup
```bash
git clone https://github.com/rxl895/AuraChat_Data.git
cd AuraChat_Data
chmod +x setup.sh
./setup.sh
```

## 🤝 How to Contribute

### 1. Fork the Repository
- Click the "Fork" button on GitHub
- Clone your fork locally
- Add upstream remote: `git remote add upstream https://github.com/rxl895/AuraChat_Data.git`

### 2. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 4. Submit a Pull Request
- Push your branch to your fork
- Create a Pull Request with a clear description
- Reference any related issues

## 🐛 Reporting Issues

Found a bug? Please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)

## 💡 Feature Requests

Have an idea? We'd love to hear it! Please:
- Check existing issues first
- Provide detailed use case
- Explain the benefit to the project

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small

### Testing
- Write unit tests for new features
- Ensure all tests pass: `python -m pytest`
- Test on different environments when possible

### Documentation
- Update README.md for new features
- Add inline comments for complex logic
- Update this CONTRIBUTING.md as needed

## 🏆 Recognition

Contributors will be:
- Listed in the README.md
- Thanked in release notes
- Given credit in academic papers (if applicable)

## 📞 Getting Help

- Open an issue for questions
- Join discussions in the Issues tab
- Contact maintainers directly for sensitive matters

## 📄 Code of Conduct

Please be respectful and constructive in all interactions. We're building something amazing together!

---

Thank you for contributing to AuraChat Data Extraction! 🙏
