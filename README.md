# GitHub Switcher

[![Tests](https://github.com/mostafagamil/Github-Switcher/workflows/CI/badge.svg)](https://github.com/mostafagamil/Github-Switcher/actions)
[![PyPI](https://img.shields.io/pypi/v/github-switcher.svg)](https://pypi.org/project/github-switcher/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Professional CLI for managing multiple GitHub identities with automated SSH key management and seamless profile switching**

## ✨ Key Features

- 🔐 **Automated SSH Key Management** - Generate, import, and manage SSH keys seamlessly
- ⚡ **Seamless Profile Switching** - Switch Git identities in seconds with intelligent matching
- 🎯 **Interactive Commands** - Smart wizards with case-insensitive profile matching
- 🔍 **SSH Detection** - Automatically detect and integrate existing GitHub SSH setup
- 🌐 **Cross-Platform** - Full support for macOS, Linux, and Windows
- 🏢 **Enterprise-Ready** - Secure, reliable, comprehensively tested

## 📦 Installation

### Recommended: UV (Modern & Fast)

[UV](https://github.com/astral-sh/uv) is a modern, fast Python package and project manager written in Rust. It's 10-100x faster than pip and provides better dependency resolution.

First, install UV if you don't have it:

**macOS**:
```bash
brew install uv
```

**Linux/WSL**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows** (PowerShell):
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative** (any platform):
```bash
pip install uv
```

Then install GitHub Switcher:
```bash
uv tool install github-switcher
```

*UV provides faster installation (10x+ faster), better dependency resolution, and isolated tool management*

### Standard: pip
```bash
pip install github-switcher
```

### macOS/Linux: Homebrew
```bash
brew tap mostafagamil/github-switcher
brew install github-switcher
```

## 🔧 System Requirements

- **Python 3.10+** - Modern Python runtime
- **Git** - Required for SSH operations and profile management
  - **macOS**: `xcode-select --install` or `brew install git`
  - **Windows**: [Git for Windows](https://git-scm.com/download/win) (includes Git Bash)
  - **Linux**: Usually pre-installed (`sudo apt install git` if needed)
- **SSH client** - For secure GitHub connectivity (included with Git)

## 🚀 Quick Start

```bash
# Verify installation
ghsw --version

# Create your first profile (interactive wizard)
ghsw create

# List all profiles
ghsw list

# Switch between profiles
ghsw switch work
ghsw switch personal

# Test SSH connection
ghsw test work
```

## 💻 Interactive Commands

All commands support interactive mode when no arguments are provided:

```bash
# Interactive profile creation - detects existing SSH keys
ghsw create

# Interactive switching - shows numbered profile list
ghsw switch
# 🔧 Select a profile to switch to:
#   1. work - john@company.com 🟢 Active
#   2. personal - john@gmail.com ⚪ Inactive
# 🎯 Enter profile number or name: 2

# Interactive profile management
ghsw delete          # Choose from list
ghsw copy-key        # Copy SSH public key to clipboard
ghsw test            # Test GitHub connection
ghsw regenerate-key  # Generate new SSH key
```

## 🔍 SSH Key Intelligence

GitHub Switcher automatically detects your existing SSH setup:

```bash
ghsw detect
# 🔍 Detecting existing GitHub setup...
# ✅ GitHub SSH connection is working
# 🔑 Found 2 SSH key(s):
#   ✅ id_ed25519_work (john@company.com) → used by 'work' profile
#   ✅ id_ed25519 (john@gmail.com)
# ⚙️ SSH config has 3 GitHub entries
```

**Smart SSH Strategy:**
- **Import Existing Keys** - Reuse and rename your SSH keys (prevents duplicates)
- **Generate New Keys** - Create fresh Ed25519 keys for clean separation
- **Duplicate Prevention** - Never shows already-imported keys
- **Profile Association** - Track which profile uses which SSH key

## 📋 Command Reference

| Command | Description |
|---------|-------------|
| `ghsw create [options]` | Create new profile with interactive wizard |
| `ghsw list` | Show all configured profiles with status |
| `ghsw switch [profile]` | Switch to profile (interactive if no argument) |
| `ghsw current` | Display currently active profile |
| `ghsw delete [profile]` | Remove profile and clean up SSH keys |
| `ghsw copy-key [profile]` | Copy SSH public key to clipboard |
| `ghsw test [profile]` | Test SSH connection to GitHub |
| `ghsw regenerate-key [profile]` | Generate new SSH key for profile |
| `ghsw detect` | Analyze existing GitHub SSH configuration |

## 🏢 Enterprise Features

- **Security Best Practices** - Ed25519 keys, proper file permissions, secure defaults
- **Comprehensive Testing** - 237 tests ensuring reliability across all platforms
- **Error Handling** - Robust error recovery and clear troubleshooting guidance
- **Cross-Platform** - Automated testing on macOS, Linux, and Windows
- **Type Safety** - Full type hints and static analysis validation
- **Professional Documentation** - Complete guides for installation, usage, and troubleshooting

## 📖 Documentation

- [Installation Guide](docs/installation.md) - Comprehensive setup instructions
- [Usage Guide](docs/usage.md) - Complete feature documentation
- [SSH Key Management](docs/existing-ssh-keys.md) - Working with existing SSH keys
- [API Reference](docs/api-reference.md) - Programmatic usage
- [Contributing](docs/contributing.md) - Development and contribution guidelines
- [Security Policy](SECURITY.md) - Vulnerability reporting and security practices

## 🤝 Support & Contributing

- **Issues & Bug Reports** - [GitHub Issues](https://github.com/mostafagamil/Github-Switcher/issues)
- **Feature Requests** - [GitHub Discussions](https://github.com/mostafagamil/Github-Switcher/discussions)
- **Contributing** - See [Contributing Guidelines](docs/contributing.md)
- **Security** - See [Security Policy](SECURITY.md)

## 💡 Example Workflows

### Development Teams
```bash
# Set up work and personal profiles
ghsw create --name work --fullname "John Doe" --email john@company.com
ghsw create --name personal --fullname "John Doe" --email john.personal@gmail.com

# Switch contexts quickly
ghsw switch work      # Work on company projects
ghsw switch personal  # Contribute to open source
```

### Freelancers
```bash
# Manage multiple clients
ghsw create --name client-a --email john@client-a.com
ghsw create --name client-b --email john@client-b.com
ghsw create --name personal --email john@personal.com

# Quick client switching
ghsw switch client-a  # Work on Client A projects
ghsw switch client-b  # Switch to Client B work
```

## 📊 Quality Metrics

- **Test Coverage** - Comprehensive test suite with 237 tests
- **Cross-Platform** - Automated CI testing on macOS, Linux, Windows
- **Type Safety** - Full mypy validation with strict settings
- **Code Quality** - Linted with ruff, formatted consistently
- **Security** - Ed25519 keys, proper permissions, input validation

## 🌟 Support the Project

If GitHub Switcher helps improve your workflow, consider supporting its development:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/mgamil)

Your support helps maintain and enhance GitHub Switcher with new features and improvements!

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Made with ❤️ for developers managing multiple GitHub identities**