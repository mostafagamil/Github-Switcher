# GitHub Switcher

[![CI](https://github.com/mostafagamil/Github-Switcher/workflows/CI/badge.svg)](https://github.com/mostafagamil/Github-Switcher/actions)
[![PyPI](https://img.shields.io/pypi/v/github-switcher.svg)](https://pypi.org/project/github-switcher/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Professional CLI for managing multiple GitHub identities with automated SSH key management and seamless profile switching**

## ✨ Key Features

- 🔐 **Advanced SSH Management** - Generate, import, fingerprint, and manage SSH keys with passphrase support
- ⚡ **Seamless Profile Switching** - Switch Git identities in seconds with intelligent matching
- 🎯 **Interactive Commands** - Smart wizards with case-insensitive profile matching and rich feedback
- 🔍 **Intelligent SSH Detection** - Auto-detect existing setup with deduplication and ssh-agent integration  
- 🛡️ **Enterprise Security** - Passphrase-protected keys, ssh-agent integration, comprehensive connection testing
- 🌐 **Cross-Platform** - Full support for macOS, Linux, and Windows with optimal performance
- 🏢 **Production-Ready** - 260+ tests, 80%+ coverage, type-safe, professionally maintained

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

## 🔍 Advanced SSH Intelligence

GitHub Switcher provides enterprise-grade SSH key management with comprehensive analysis:

```bash
ghsw detect
# 🔍 Analyzing SSH environment...
# 📊 SSH Key Analysis:
#   🔑 Total keys found: 4
#   ✅ Ed25519 keys: 2 (recommended)
#   🔐 Passphrase-protected: 1
#   🔓 Unencrypted: 3
# 🏷️ Profile Associations:
#   ✅ work → id_ed25519_work (SHA256:abc123...)
#   ✅ personal → id_ed25519_personal (SHA256:def456...)
# 🔌 SSH Agent Status:
#   ✅ ssh-agent running
#   🔑 2 keys loaded in agent
# 🌐 GitHub Connectivity: ✅ All connections optimal
```

**Enterprise SSH Features:**
- **Key Fingerprinting** - SHA256 fingerprints for unique identification and deduplication
- **Passphrase Protection** - Generate and detect encrypted SSH keys for enhanced security
- **SSH Agent Integration** - Intelligent detection and management of ssh-agent loaded keys
- **Advanced Connection Testing** - Comprehensive diagnostics with specific error guidance
- **Non-Destructive Operations** - Copy (don't move) existing keys, preserve original setup
- **Profile Metadata Tracking** - Enhanced profile storage with SSH key attributes and usage history

## 📋 Command Reference

| Command | Description |
|---------|-------------|
| `ghsw create [options]` | Create new profile with interactive wizard |
| `ghsw list` | Show all profiles with SSH security status and activity |
| `ghsw switch [profile]` | Switch to profile (interactive if no argument) |
| `ghsw current` | Display currently active profile |
| `ghsw delete [profile]` | Remove profile and clean up SSH keys |
| `ghsw copy-key [profile]` | Copy SSH public key to clipboard |
| `ghsw test [profile]` | Test SSH connection to GitHub |
| `ghsw regenerate-key [profile]` | Generate new SSH key with optional passphrase protection |
| `ghsw detect` | Comprehensive SSH environment analysis with security insights |

## 🏢 Enterprise Features

- **Advanced Security** - Passphrase-protected keys, fingerprinting, ssh-agent integration, secure defaults
- **Comprehensive Testing** - 260+ tests with 80%+ coverage ensuring reliability across all platforms  
- **Intelligent Error Handling** - Robust error recovery with specific guidance for SSH issues
- **Cross-Platform Excellence** - Automated testing on macOS, Linux, and Windows with platform optimizations
- **Type Safety** - Full type hints and static analysis validation with mypy
- **Enterprise Documentation** - Complete guides covering advanced SSH features and security practices

## 📖 Documentation

- [Installation Guide](docs/installation.md) - Comprehensive setup instructions
- [Usage Guide](docs/usage.md) - Complete feature documentation
- [Advanced SSH Management](docs/existing-ssh-keys.md) - Comprehensive SSH key features including passphrase protection and ssh-agent integration
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

- **Test Coverage** - Enterprise-grade test suite with 260+ tests and 80%+ coverage
- **Cross-Platform** - Automated CI testing on macOS, Linux, Windows with performance optimization
- **Type Safety** - Full mypy validation with strict settings and comprehensive type coverage
- **Code Quality** - Linted with ruff, formatted consistently, maintained to professional standards
- **Security** - Passphrase-protected Ed25519 keys, ssh-agent integration, fingerprinting, proper permissions

## 🌟 Support the Project

If GitHub Switcher helps improve your workflow, consider supporting its development:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/mgamil)

Your support helps maintain and enhance GitHub Switcher with new features and improvements!

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Made with ❤️ for developers managing multiple GitHub identities**