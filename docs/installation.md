# Installation Guide

## System Requirements

GitHub Switcher requires the following components to function properly:

### Essential Dependencies
- **Python 3.10+** - Modern Python runtime
- **Git** - Version control system (required for SSH operations)
- **SSH client** - Secure shell client for GitHub connectivity

### Verify Requirements

Before installation, ensure all dependencies are available:

```bash
# Check Python version (must be 3.10+)
python --version
# or
python3 --version

# Check Git installation (required)
git --version

# Check SSH client (usually included with Git)
ssh -V
```

## Git Installation (Required)

GitHub Switcher requires Git for SSH key management and profile operations. Install Git if not already available:

### macOS
```bash
# Option 1: Xcode Command Line Tools (recommended)
xcode-select --install

# Option 2: Homebrew
brew install git

# Option 3: Direct download
# Download from https://git-scm.com/download/mac
```

### Windows
```bash
# Download and install Git for Windows
# https://git-scm.com/download/win
# 
# Includes:
# - Git Bash (recommended terminal)
# - SSH client
# - Integration with Windows Terminal
```

### Linux
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install git

# Fedora/RHEL/CentOS
sudo dnf install git
# or (older versions)
sudo yum install git

# Arch Linux
sudo pacman -S git

# Alpine Linux
sudo apk add git
```

## Installation Methods

### Method 1: UV (Recommended - Modern & Fast)

UV is the fastest Python package manager, providing superior performance and dependency management:

```bash
# Install UV if not already available
curl -LsSf https://astral.sh/uv/install.sh | sh
# or on Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install GitHub Switcher globally
uv tool install github-switcher

# Verify installation
ghsw --version
```

**UV Advantages:**
- ⚡ **10-100x faster** than traditional pip
- 🔒 **Isolated environments** - No dependency conflicts
- 🚀 **Better dependency resolution** - Handles complex dependencies
- 📦 **Global tool management** - Easy updates and removal

### Method 2: pip (Standard Python Package Manager)

```bash
# System-wide installation
pip install github-switcher

# User installation (recommended for personal use)
pip install --user github-switcher

# Verify installation
ghsw --version
```

### Method 3: pipx (Isolated CLI Tools)

pipx provides isolation similar to UV but uses pip under the hood:

```bash
# Install pipx if not available
python -m pip install --user pipx

# Install GitHub Switcher
pipx install github-switcher

# Verify installation
ghsw --version
```

### Method 4: Homebrew (macOS/Linux)

```bash
# Add tap and install
brew tap mostafagamil/github-switcher
brew install github-switcher

# Verify installation
ghsw --version
```

### Method 5: From Source (Development)

```bash
# Clone repository
git clone https://github.com/mostafagamil/Github-Switcher.git
cd Github-Switcher

# Install with UV (recommended)
uv sync
uv run ghsw --version

# Or install in development mode
uv tool install .

# Or with pip
pip install -e .
```

## Post-Installation Verification

After installation, verify all components are working:

```bash
# 1. Check GitHub Switcher version
ghsw --version

# 2. Verify system requirements
ghsw detect  # This will check Git and SSH availability

# 3. Show help (verify command works)
ghsw --help

# 4. List profiles (should be empty initially)
ghsw list

# 5. Test profile creation help
ghsw create --help
```

## Platform-Specific Configuration

### macOS
- **SSH Directory**: `~/.ssh/`
- **Config Directory**: `~/.config/github-switcher/`
- **Clipboard**: Uses `pbcopy` (built-in)
- **Git**: Install via Xcode Command Line Tools or Homebrew

### Linux
- **SSH Directory**: `~/.ssh/`
- **Config Directory**: `~/.config/github-switcher/`
- **Clipboard**: Requires `xclip` or `xsel`
- **Git**: Usually pre-installed

```bash
# Install clipboard utility (Linux)
# Ubuntu/Debian
sudo apt install xclip xsel

# Fedora/RHEL
sudo dnf install xclip xsel

# Arch Linux
sudo pacman -S xclip xsel
```

### Windows
- **SSH Directory**: `%USERPROFILE%\.ssh\`
- **Config Directory**: `%APPDATA%\github-switcher\`
- **Clipboard**: Uses `clip` (built-in)
- **Git**: Install Git for Windows
- **Recommended**: Use Git Bash or Windows Terminal

## Troubleshooting

### Python Version Issues
```bash
# Check Python version
python --version  # Should be 3.10+

# If using multiple Python versions
python3 --version
python3.10 --version

# Update PATH (Linux/macOS)
export PATH="/usr/local/bin:$PATH"

# Check Python installation location
which python
which python3
```

### Git Not Found
```bash
# Verify Git installation
git --version

# If not installed, install Git:
# macOS: xcode-select --install
# Linux: sudo apt install git
# Windows: Download from https://git-scm.com/download/win
```

### Permission Errors
```bash
# Use user installation
pip install --user github-switcher

# Or use UV (recommended)
uv tool install github-switcher

# Fix PATH (macOS/Linux)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### SSH Issues
```bash
# Check SSH directory permissions
ls -la ~/.ssh/
chmod 700 ~/.ssh/

# Test SSH key generation
ssh-keygen -t ed25519 -f /tmp/test_key -N ""
rm /tmp/test_key*

# Verify SSH client
ssh -V
```

### UV Installation Issues
```bash
# Manual UV installation
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Alternative: Use cargo (if Rust installed)
cargo install --git https://github.com/astral-sh/uv uv
```

### Clipboard Integration Issues
```bash
# Linux: Install clipboard utilities
sudo apt install xclip xsel  # Ubuntu/Debian
sudo dnf install xclip xsel  # Fedora

# Test clipboard
echo "test" | xclip -selection clipboard
xclip -o -selection clipboard

# macOS: Should work with pbcopy (built-in)
echo "test" | pbcopy
pbpaste

# Windows: Should work with clip (built-in)
echo "test" | clip
```

## Updating GitHub Switcher

### UV
```bash
uv tool upgrade github-switcher
```

### pip
```bash
pip install --upgrade github-switcher
```

### pipx
```bash
pipx upgrade github-switcher
```

### Homebrew
```bash
brew update
brew upgrade github-switcher
```

## Uninstallation

### UV
```bash
uv tool uninstall github-switcher
```

### pip
```bash
pip uninstall github-switcher
```

### pipx
```bash
pipx uninstall github-switcher
```

### Homebrew
```bash
brew uninstall github-switcher
```

### Manual Cleanup
```bash
# Remove configuration (optional)
rm -rf ~/.config/github-switcher/

# SSH keys remain in ~/.ssh/ for safety
# Remove manually if needed:
# rm ~/.ssh/id_ed25519_*profile-name**
```

## Directory Structure

After installation and first use:

```
~/.config/github-switcher/
├── profiles.toml          # Profile configurations
└── profiles.toml.backup   # Automatic backup

~/.ssh/
├── config                 # SSH configuration (managed)
├── config.github-switcher-backup  # Original backup
├── id_ed25519_profile1    # Profile SSH keys
├── id_ed25519_profile1.pub
├── id_ed25519_profile2
└── id_ed25519_profile2.pub
```

## Next Steps

After successful installation:

1. **Create your first profile**: `ghsw create`
2. **Read the Usage Guide**: [docs/usage.md](usage.md)
3. **Configure SSH keys**: Follow the interactive wizard
4. **Test SSH connection**: `ghsw test profile-name`
5. **Switch profiles**: `ghsw switch profile-name`

## Support

If you encounter installation issues:

1. **Check Requirements**: Ensure Python 3.10+, Git, and SSH are installed
2. **Verify Installation**: Run `ghsw detect` to check system configuration
3. **Read Troubleshooting**: Review the troubleshooting section above
4. **GitHub Issues**: Report bugs at https://github.com/mostafagamil/Github-Switcher/issues
5. **Discussions**: Ask questions at https://github.com/mostafagamil/Github-Switcher/discussions