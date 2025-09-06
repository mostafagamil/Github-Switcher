"""GitHub Switcher - Professional CLI for managing multiple GitHub identities.

A comprehensive command-line tool for managing multiple GitHub profiles with
seamless identity switching, SSH key management, and git configuration.

Key Features:
- Multiple GitHub profile management
- Automated SSH key generation and configuration
- Git global configuration switching
- Rich terminal interface with progress indicators
- Cross-platform compatibility (Windows, macOS, Linux)
- Comprehensive error handling and validation

Security & Best Practices:
- Ed25519 SSH keys (GitHub recommended)
- Proper file permissions (600 for private keys)
- No plaintext credential storage
- Atomic configuration updates
- Backup creation before modifications

Testing & Quality:
- High test coverage with comprehensive test suite
- Cross-platform compatibility testing
- Error condition and edge case coverage
- Performance and security validation

For documentation and examples, visit:
https://github.com/mostafagamil/Github-Switcher
"""

__version__ = "0.1.0"
__author__ = "Mostafa Gamil"
__email__ = "mostafa_gamil@yahoo.com"
__description__ = "Professional CLI for managing multiple GitHub identities"
__url__ = "https://github.com/mostafagamil/Github-Switcher"
__license__ = "MIT"

# Expose main classes for programmatic use
from .cli import app
from .config import Config
from .git_manager import GitManager
from .profiles import ProfileManager
from .ssh_manager import SSHManager
from .wizard import ProfileWizard

__all__ = [
    "app",
    "ProfileManager",
    "GitManager",
    "SSHManager",
    "Config",
    "ProfileWizard",
    "__version__",
]
