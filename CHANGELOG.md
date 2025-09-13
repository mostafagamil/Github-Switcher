# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- GPG key support for signed commits
- GitHub CLI token management
- Profile templates and presets
- Shell integration and completion
- Web-based configuration UI

## [0.2.0] - 2025-09-13

### Added
- **🔒 Passphrase-Protected SSH Keys**: Generate and manage encrypted SSH keys for enhanced security
- **🔍 SSH Key Fingerprinting**: SHA256 fingerprint generation for unique key identification and deduplication
- **🔌 SSH Agent Integration**: Intelligent detection and management of keys loaded in ssh-agent
- **🛡️ Advanced Connection Testing**: Comprehensive SSH diagnostics with specific error guidance and recovery suggestions
- **📊 Enhanced Detection Command**: Rich SSH environment analysis with security insights and key metadata
- **🔧 Non-Destructive Key Operations**: Copy (don't move/rename) existing keys to preserve original SSH setup
- **📈 Profile Metadata Tracking**: Enhanced profile storage with SSH key attributes, usage history, and security status

### Enhanced
- **CLI Commands**: All SSH-related commands now provide richer feedback and intelligent error guidance
- **Interactive Wizards**: Streamlined key creation flow with security options and better user experience
- **List Command**: Now displays SSH security status (🔐 Protected/🔓 Unprotected) for all profiles  
- **SSH Configuration Management**: Improved handling of complex SSH setups with conflict detection
- **Error Handling**: More specific error messages with actionable solutions for SSH connectivity issues

### Technical Improvements
- **Test Coverage**: Expanded from basic testing to 260+ comprehensive tests with 80%+ coverage
- **Type Safety**: Enhanced type annotations and mypy validation across all SSH management code
- **Security**: Implemented industry-standard SSH key security practices and validation
- **Performance**: Optimized key detection and SSH operations for better responsiveness

### Commands Updated
- `ghsw regenerate-key [profile]` - Now supports passphrase protection options
- `ghsw test [profile]` - Comprehensive connection testing with detailed diagnostics
- `ghsw detect` - Rich SSH environment analysis with security insights
- `ghsw create` - Enhanced wizard with advanced SSH options and better key detection

## [0.1.0] - 2025-09-06

### Added
- **Interactive Profile Creation**: Rich wizard with colorful terminal UI and automatic SSH key detection
- **SSH Key Management**: Ed25519 key generation, import existing keys, clipboard integration, and connection testing
- **Seamless Profile Switching**: Automatic git config and SSH configuration management
- **Profile Management**: Create, list, switch, delete, and test profiles with case-insensitive matching
- **Existing Setup Detection**: Intelligent analysis of current GitHub SSH configuration
- **Cross-Platform Support**: Full compatibility with macOS, Linux, and Windows

### Commands
- `ghsw create` - Interactive profile creation wizard
- `ghsw list` - Show all profiles with status indicators
- `ghsw switch [profile]` - Switch profiles (interactive if no argument)
- `ghsw current` - Display active profile information
- `ghsw delete [profile]` - Remove profiles safely with confirmation
- `ghsw copy-key [profile]` - Copy SSH public key to clipboard
- `ghsw test [profile]` - Test SSH connection to GitHub
- `ghsw regenerate-key [profile]` - Generate new SSH key for profile
- `ghsw detect` - Analyze existing GitHub SSH setup

### Technical Implementation
- **Modern Python Stack**: Python 3.10+, Typer CLI framework, Rich terminal UI
- **Package Management**: UV for fast dependency management and tool installation
- **Configuration**: TOML format stored in `~/.config/github-switcher/`
- **SSH Security**: Ed25519 keys with proper file permissions (600/644)
- **Testing**: Comprehensive test suite with high coverage
- **Code Quality**: Type hints throughout, ruff linting, mypy type checking

### Documentation
- Complete installation guide with system requirements
- Comprehensive usage documentation with examples
- Professional README with multiple installation methods
- Security policy and vulnerability reporting process

### Distribution
- **PyPI**: Available via `pip install github-switcher`
- **UV**: Recommended installation via `uv tool install github-switcher`
- **Source**: Development installation support