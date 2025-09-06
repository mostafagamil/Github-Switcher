"""Tests for SSH key generation and management functionality."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from github_switcher.ssh_manager import SSHManager


@pytest.fixture
def temp_ssh_dir():
    """Create temporary SSH directory."""
    temp_dir = tempfile.mkdtemp()
    ssh_dir = Path(temp_dir) / ".ssh"
    ssh_dir.mkdir(mode=0o700)
    yield ssh_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def ssh_manager(temp_ssh_dir):
    """Create SSH manager with temporary directory."""
    with patch('pathlib.Path.home') as mock_home:
        mock_home.return_value = temp_ssh_dir.parent
        manager = SSHManager()
        return manager


class TestSSHManagerInit:
    """Test SSH manager initialization."""

    def test_init_creates_ssh_dir(self, temp_ssh_dir):
        """Test SSH manager creates .ssh directory."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_ssh_dir.parent
            manager = SSHManager()
            assert manager.ssh_dir.exists()
            assert oct(manager.ssh_dir.stat().st_mode)[-3:] == '700'

    @patch('shutil.copy2')
    def test_init_creates_backup(self, mock_copy, temp_ssh_dir):
        """Test SSH manager creates config backup."""
        config_file = temp_ssh_dir / "config"
        config_file.write_text("Host github.com\n    User git\n")

        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_ssh_dir.parent
            SSHManager()

        # Should create backup on first run
        backup_file = temp_ssh_dir / "config.config.github-switcher-backup"
        mock_copy.assert_called_once_with(config_file, backup_file)


class TestDetectExistingGitHubSetup:
    """Test detection of existing GitHub SSH configuration."""

    def test_detect_no_config_file(self, ssh_manager):
        """Test detection when no SSH config exists."""
        with patch.object(ssh_manager, '_test_github_connectivity') as mock_test:
            mock_test.return_value = False  # No GitHub connectivity
            with patch('pathlib.Path.glob') as mock_glob:
                mock_glob.return_value = []  # No SSH keys

                result = ssh_manager.detect_existing_github_setup()

                assert result["has_github_host"] is False
                assert result["github_keys"] == []
                assert result["config_entries"] == []
                assert result["all_keys"] == []
                assert result["github_connectivity"] is False
                assert result["default_key_works"] is False
                assert "recommendations" in result

    def test_detect_with_github_config(self, ssh_manager):
        """Test detection with GitHub entries in SSH config."""
        config_content = """Host github.com
    HostName github.com
    User git

Host github-work
    HostName github.com
    User git
"""
        ssh_manager.ssh_config_file.write_text(config_content)

        result = ssh_manager.detect_existing_github_setup()

        assert result["has_github_host"] is True
        assert "github.com" in result["config_entries"]
        assert "github-work" in result["config_entries"]

    def test_detect_github_keys(self, ssh_manager):
        """Test detection of GitHub SSH keys with enhanced logic."""
        # Create mock SSH keys
        key1 = ssh_manager.ssh_dir / "id_rsa"
        key1_pub = ssh_manager.ssh_dir / "id_rsa.pub"
        key2 = ssh_manager.ssh_dir / "id_ed25519"
        key2_pub = ssh_manager.ssh_dir / "id_ed25519.pub"

        key1.write_text("private key")
        key1_pub.write_text("ssh-rsa ABC... github@example.com")
        key2.write_text("private key")
        key2_pub.write_text("ssh-ed25519 XYZ... regular@example.com")

        with patch.object(ssh_manager, '_test_github_connectivity', return_value=False):
            result = ssh_manager.detect_existing_github_setup()

        # Check new fields exist
        assert "all_keys" in result
        assert "github_connectivity" in result
        assert "default_key_works" in result
        assert "recommendations" in result

        # Check key analysis
        assert len(result["all_keys"]) == 2

        # id_rsa should be detected as GitHub key (has "github" in comment)
        rsa_key = next((k for k in result["all_keys"] if k["name"] == "id_rsa"), None)
        assert rsa_key is not None
        assert rsa_key["has_github_indicators"] is True

        # id_ed25519 should still be detected as potentially working (likely_github=True for default keys)
        ed25519_key = next((k for k in result["all_keys"] if k["name"] == "id_ed25519"), None)
        assert ed25519_key is not None
        assert ed25519_key["likely_github"] is True  # Default key name

    def test_detect_handles_file_errors(self, ssh_manager):
        """Test detection handles file read errors gracefully."""
        # Create config file but make it unreadable
        ssh_manager.ssh_config_file.write_text("test")
        ssh_manager.ssh_config_file.chmod(0o000)

        result = ssh_manager.detect_existing_github_setup()

        assert result["has_github_host"] is False
        ssh_manager.ssh_config_file.chmod(0o644)  # Restore for cleanup

    def test_detect_handles_key_file_read_errors(self, ssh_manager):
        """Test detection handles key file read errors gracefully."""
        # Create a directory that looks like a key file (will cause read error)
        fake_key = ssh_manager.ssh_dir / "id_rsa.pub"
        fake_key.mkdir()  # This will cause OSError when trying to read

        try:
            # Should not raise an error, just continue
            with patch.object(ssh_manager, '_test_github_connectivity', return_value=False):
                result = ssh_manager.detect_existing_github_setup()

            assert "github_keys" in result
            assert "all_keys" in result
            assert "github_connectivity" in result
            assert isinstance(result["github_keys"], list)
            assert isinstance(result["all_keys"], list)
        finally:
            # Clean up the directory
            if fake_key.exists():
                fake_key.rmdir()

    def test_github_connectivity_detection(self, ssh_manager):
        """Test GitHub connectivity detection."""
        # Test successful connection
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1  # SSH auth test returns 1 for success
            mock_result.stderr = "Hi user! You've successfully authenticated"
            mock_run.return_value = mock_result

            result = ssh_manager._test_github_connectivity()
            assert result is True

        # Test failed connection
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 255  # Connection failed
            mock_result.stderr = "Permission denied"
            mock_run.return_value = mock_result

            result = ssh_manager._test_github_connectivity()
            assert result is False

    def test_ssh_key_analysis(self, ssh_manager):
        """Test SSH key analysis functionality."""
        # Create test keys with different properties
        github_key = ssh_manager.ssh_dir / "id_github"
        github_pub = ssh_manager.ssh_dir / "id_github.pub"

        default_key = ssh_manager.ssh_dir / "id_ed25519"
        default_pub = ssh_manager.ssh_dir / "id_ed25519.pub"

        regular_key = ssh_manager.ssh_dir / "id_custom"
        regular_pub = ssh_manager.ssh_dir / "id_custom.pub"

        # Write key files
        github_key.write_text("private key")
        github_pub.write_text("ssh-rsa AAAAB3... github@company.com")

        default_key.write_text("private key")
        default_pub.write_text("ssh-ed25519 AAAAC3... user@domain.com")

        regular_key.write_text("private key")
        regular_pub.write_text("ssh-rsa AAAAB3... custom@example.com")

        # Test GitHub key analysis
        github_analysis = ssh_manager._analyze_ssh_key(github_key)
        assert github_analysis is not None
        assert github_analysis["name"] == "id_github"
        assert github_analysis["type"] == "ssh-rsa"
        assert github_analysis["has_github_indicators"] is True
        assert github_analysis["github_compatible"] is True

        # Test default key analysis
        default_analysis = ssh_manager._analyze_ssh_key(default_key)
        assert default_analysis is not None
        assert default_analysis["name"] == "id_ed25519"
        assert default_analysis["type"] == "ssh-ed25519"
        assert default_analysis["likely_github"] is True  # Default key name
        assert default_analysis["has_github_indicators"] is False

        # Test regular key analysis
        regular_analysis = ssh_manager._analyze_ssh_key(regular_key)
        assert regular_analysis is not None
        assert regular_analysis["likely_github"] is False
        assert regular_analysis["has_github_indicators"] is False

    def test_enhanced_detection_with_working_setup(self, ssh_manager):
        """Test enhanced detection with a working GitHub setup."""
        # Create a default key that works with GitHub
        key = ssh_manager.ssh_dir / "id_ed25519"
        pub = ssh_manager.ssh_dir / "id_ed25519.pub"

        key.write_text("private key")
        pub.write_text("ssh-ed25519 AAAAC3... user@domain.com")

        # Mock successful GitHub connectivity
        with patch.object(ssh_manager, '_test_github_connectivity', return_value=True):
            result = ssh_manager.detect_existing_github_setup()

        # Should detect working setup
        assert result["github_connectivity"] is True
        assert result["default_key_works"] is True  # No config entries, but connectivity works
        assert len(result["all_keys"]) == 1
        assert result["all_keys"][0]["name"] == "id_ed25519"

        # Should have positive recommendations
        recommendations = result["recommendations"]
        assert any("current SSH setup works" in rec for rec in recommendations)

    def test_enhanced_detection_no_keys(self, ssh_manager):
        """Test enhanced detection when no SSH keys exist."""
        # Mock no GitHub connectivity
        with patch.object(ssh_manager, '_test_github_connectivity', return_value=False):
            result = ssh_manager.detect_existing_github_setup()

        assert result["github_connectivity"] is False
        assert result["default_key_works"] is False
        assert len(result["all_keys"]) == 0
        assert len(result["github_keys"]) == 0

        # Should recommend key generation
        recommendations = result["recommendations"]
        assert any("No SSH keys detected" in rec for rec in recommendations)


class TestImportExistingKey:
    """Test importing existing SSH keys."""

    def test_import_existing_key_success(self, ssh_manager, temp_ssh_dir):
        """Test successful key import."""
        # Create existing key files
        existing_dir = temp_ssh_dir.parent / "existing"
        existing_dir.mkdir()
        existing_key = existing_dir / "id_ed25519"
        existing_pub = existing_dir / "id_ed25519.pub"

        existing_key.write_text("existing private key")
        existing_pub.write_text("ssh-ed25519 ABC... test@example.com")

        result = ssh_manager.import_existing_key("work", str(existing_key), "test@example.com")

        profile_key = ssh_manager.ssh_dir / "id_ed25519_work"
        profile_pub = ssh_manager.ssh_dir / "id_ed25519_work.pub"

        assert result[0] == str(profile_key)
        assert result[1] == "ssh-ed25519 ABC... test@example.com"
        assert profile_key.exists()
        assert profile_pub.exists()
        assert oct(profile_key.stat().st_mode)[-3:] == '600'
        assert oct(profile_pub.stat().st_mode)[-3:] == '644'

    def test_import_existing_key_not_found(self, ssh_manager):
        """Test import when key files don't exist."""
        with pytest.raises(ValueError, match="SSH key files not found"):
            ssh_manager.import_existing_key("work", "/nonexistent/key", "test@example.com")

    def test_import_existing_key_already_exists(self, ssh_manager):
        """Test import when profile key already exists."""
        # Create existing profile key
        profile_key = ssh_manager.ssh_dir / "id_ed25519_work"
        profile_key.write_text("existing")

        # Create source key
        source_key = ssh_manager.ssh_dir / "source_key"
        source_pub = ssh_manager.ssh_dir / "source_key.pub"
        source_key.write_text("source private")
        source_pub.write_text("ssh-ed25519 ABC...")

        with pytest.raises(ValueError, match="Profile SSH key already exists"):
            ssh_manager.import_existing_key("work", str(source_key), "test@example.com")


class TestGenerateSSHKey:
    """Test SSH key generation."""

    @patch('github_switcher.ssh_manager.ed25519.Ed25519PrivateKey.generate')
    def test_generate_ssh_key_success(self, mock_generate, ssh_manager):
        """Test successful SSH key generation."""
        # Mock cryptography objects
        mock_private_key = MagicMock()
        mock_public_key = MagicMock()
        mock_generate.return_value = mock_private_key
        mock_private_key.public_key.return_value = mock_public_key

        mock_private_key.private_bytes.return_value = b"private_key_data"
        mock_public_key.public_bytes.return_value = b"ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI"

        result = ssh_manager.generate_ssh_key("work", "work@example.com")

        private_key_path = ssh_manager.ssh_dir / "id_ed25519_work"
        public_key_path = ssh_manager.ssh_dir / "id_ed25519_work.pub"

        assert result[0] == str(private_key_path)
        assert "work@example.com" in result[1]
        assert private_key_path.exists()
        assert public_key_path.exists()
        assert oct(private_key_path.stat().st_mode)[-3:] == '600'
        assert oct(public_key_path.stat().st_mode)[-3:] == '644'

    def test_generate_ssh_key_already_exists(self, ssh_manager):
        """Test generation when key already exists."""
        existing_key = ssh_manager.ssh_dir / "id_ed25519_work"
        existing_key.write_text("existing key")

        with pytest.raises(ValueError, match="SSH key already exists for profile 'work'"):
            ssh_manager.generate_ssh_key("work", "work@example.com")

    @patch('github_switcher.ssh_manager.ed25519.Ed25519PrivateKey.generate')
    def test_generate_ssh_key_cleanup_on_error(self, mock_generate, ssh_manager):
        """Test cleanup of partial files on generation error."""
        # Mock the key generation to fail after files would be created
        mock_generate.side_effect = Exception("Generation failed")

        private_key_path = ssh_manager.ssh_dir / "id_ed25519_work"
        public_key_path = ssh_manager.ssh_dir / "id_ed25519_work.pub"

        # Ensure files don't exist initially
        if private_key_path.exists():
            private_key_path.unlink()
        if public_key_path.exists():
            public_key_path.unlink()

        with pytest.raises(RuntimeError, match="Failed to generate SSH key"):
            ssh_manager.generate_ssh_key("work", "work@example.com")

        # Files should not exist after cleanup
        assert not private_key_path.exists()
        assert not public_key_path.exists()
        assert not public_key_path.exists()


class TestGetPublicKey:
    """Test public key retrieval."""

    def test_get_public_key_success(self, ssh_manager):
        """Test successful public key retrieval."""
        public_key_path = ssh_manager.ssh_dir / "id_ed25519_work.pub"
        public_key_content = "ssh-ed25519 ABC... work@example.com"
        public_key_path.write_text(public_key_content + "\n")

        result = ssh_manager.get_public_key("work")
        assert result == public_key_content

    def test_get_public_key_not_found(self, ssh_manager):
        """Test public key retrieval when file doesn't exist."""
        result = ssh_manager.get_public_key("nonexistent")
        assert result is None

    def test_get_public_key_read_error(self, ssh_manager):
        """Test public key retrieval with read error."""
        public_key_path = ssh_manager.ssh_dir / "id_ed25519_work.pub"
        public_key_path.write_text("test")
        public_key_path.chmod(0o000)  # Make unreadable

        result = ssh_manager.get_public_key("work")
        assert result is None

        public_key_path.chmod(0o644)  # Restore for cleanup


class TestCopyPublicKeyToClipboard:
    """Test copying public key to clipboard."""

    @patch('github_switcher.ssh_manager.pyperclip.copy')
    def test_copy_public_key_success(self, mock_copy, ssh_manager):
        """Test successful clipboard copy."""
        public_key_path = ssh_manager.ssh_dir / "id_ed25519_work.pub"
        public_key_content = "ssh-ed25519 ABC... work@example.com"
        public_key_path.write_text(public_key_content)

        result = ssh_manager.copy_public_key_to_clipboard("work")

        assert result is True
        mock_copy.assert_called_once_with(public_key_content)

    def test_copy_public_key_not_found(self, ssh_manager):
        """Test clipboard copy when key doesn't exist."""
        result = ssh_manager.copy_public_key_to_clipboard("nonexistent")
        assert result is False

    @patch('github_switcher.ssh_manager.pyperclip.copy')
    def test_copy_public_key_clipboard_error(self, mock_copy, ssh_manager):
        """Test clipboard copy with pyperclip error."""
        public_key_path = ssh_manager.ssh_dir / "id_ed25519_work.pub"
        public_key_path.write_text("ssh-ed25519 ABC...")
        mock_copy.side_effect = Exception("Clipboard error")

        result = ssh_manager.copy_public_key_to_clipboard("work")
        assert result is False


class TestActivateSSHKey:
    """Test SSH key activation."""

    def test_activate_ssh_key(self, ssh_manager):
        """Test SSH key activation adds config entry."""
        ssh_manager.activate_ssh_key("work", "/path/to/key")

        config_content = ssh_manager.ssh_config_file.read_text()
        assert "# GitHub Switcher - work profile" in config_content
        assert "Host github-work" in config_content
        assert "HostName github.com" in config_content
        assert "User git" in config_content
        assert "IdentityFile /path/to/key" in config_content
        assert "IdentitiesOnly yes" in config_content

    def test_activate_ssh_key_updates_existing(self, ssh_manager):
        """Test SSH key activation updates existing entry."""
        # Add initial config entry
        ssh_manager._add_ssh_config_entry("work", "/old/path")

        # Update with new path
        ssh_manager.activate_ssh_key("work", "/new/path")

        config_content = ssh_manager.ssh_config_file.read_text()
        assert "IdentityFile /new/path" in config_content
        assert "/old/path" not in config_content
        # Should only have one entry for this profile
        assert config_content.count("# GitHub Switcher - work profile") == 1

    def test_activate_ssh_key_preserves_other_config(self, ssh_manager):
        """Test SSH key activation preserves other SSH config."""
        # Add some existing config
        existing_config = """Host example.com
    HostName example.com
    User testuser

# Some comment
Host another
    Port 2222
"""
        ssh_manager.ssh_config_file.write_text(existing_config)

        ssh_manager.activate_ssh_key("work", "/path/to/key")

        config_content = ssh_manager.ssh_config_file.read_text()
        assert "Host example.com" in config_content
        assert "Host another" in config_content
        assert "# Some comment" in config_content
        assert "github-work" in config_content


class TestRemoveSSHConfigEntry:
    """Test SSH config entry removal."""

    def test_remove_ssh_config_entry(self, ssh_manager):
        """Test removing SSH config entry."""
        # Add config entry
        ssh_manager._add_ssh_config_entry("work", "/path/to/key")
        assert "github-work" in ssh_manager.ssh_config_file.read_text()

        # Remove it
        ssh_manager.remove_ssh_config_entry("work")

        config_content = ssh_manager.ssh_config_file.read_text()
        assert "github-work" not in config_content
        assert "# GitHub Switcher - work profile" not in config_content

    def test_remove_ssh_config_entry_no_config_file(self, ssh_manager):
        """Test removing entry when no config file exists."""
        ssh_manager.ssh_config_file.unlink(missing_ok=True)

        # Should not raise error
        ssh_manager.remove_ssh_config_entry("work")

    def test_remove_ssh_config_entry_preserves_others(self, ssh_manager):
        """Test removing entry preserves other config."""
        # Add multiple entries
        ssh_manager._add_ssh_config_entry("work", "/work/key")
        ssh_manager._add_ssh_config_entry("personal", "/personal/key")

        # Remove one
        ssh_manager.remove_ssh_config_entry("work")

        config_content = ssh_manager.ssh_config_file.read_text()
        assert "github-work" not in config_content
        assert "github-personal" in config_content


class TestRemoveSSHKey:
    """Test SSH key removal."""

    def test_remove_ssh_key_success(self, ssh_manager):
        """Test successful SSH key removal."""
        private_key = ssh_manager.ssh_dir / "id_ed25519_work"
        public_key = ssh_manager.ssh_dir / "id_ed25519_work.pub"

        private_key.write_text("private key")
        public_key.write_text("public key")

        ssh_manager.remove_ssh_key(str(private_key))

        assert not private_key.exists()
        assert not public_key.exists()

    def test_remove_ssh_key_not_found(self, ssh_manager):
        """Test SSH key removal when files don't exist."""
        # Should not raise error
        ssh_manager.remove_ssh_key("/nonexistent/key")

    def test_remove_ssh_key_permission_error(self, ssh_manager):
        """Test SSH key removal with permission error."""
        private_key = ssh_manager.ssh_dir / "id_ed25519_work"
        private_key.write_text("private key")

        with patch('pathlib.Path.unlink') as mock_unlink:
            mock_unlink.side_effect = OSError("Permission denied")

            # Should not raise error
            ssh_manager.remove_ssh_key(str(private_key))


class TestTestConnection:
    """Test SSH connection testing."""

    @patch('subprocess.run')
    def test_test_connection_success(self, mock_run, ssh_manager):
        """Test successful SSH connection."""
        mock_result = MagicMock()
        mock_result.returncode = 1  # GitHub returns 1 on successful auth
        mock_result.stderr = "Hi user! You've successfully authenticated"
        mock_run.return_value = mock_result

        result = ssh_manager.test_connection("work")

        assert result is True
        mock_run.assert_called_once_with(
            ["ssh", "-T", "github-work"],
            capture_output=True,
            text=True,
            timeout=10
        )

    @patch('subprocess.run')
    def test_test_connection_failure(self, mock_run, ssh_manager):
        """Test failed SSH connection."""
        mock_result = MagicMock()
        mock_result.returncode = 255  # Connection error
        mock_result.stderr = "Connection refused"
        mock_run.return_value = mock_result

        result = ssh_manager.test_connection("work")
        assert result is False

    @patch('subprocess.run')
    def test_test_connection_timeout(self, mock_run, ssh_manager):
        """Test SSH connection timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(["ssh"], 10)

        result = ssh_manager.test_connection("work")
        assert result is False

    @patch('subprocess.run')
    def test_test_connection_subprocess_error(self, mock_run, ssh_manager):
        """Test SSH connection with subprocess error."""
        mock_run.side_effect = subprocess.SubprocessError("Process error")

        result = ssh_manager.test_connection("work")
        assert result is False


class TestRegenerateSSHKey:
    """Test SSH key regeneration."""

    @patch('github_switcher.ssh_manager.ed25519.Ed25519PrivateKey.generate')
    def test_regenerate_ssh_key_success(self, mock_generate, ssh_manager):
        """Test successful SSH key regeneration."""
        # Create existing keys
        private_key = ssh_manager.ssh_dir / "id_ed25519_work"
        public_key = ssh_manager.ssh_dir / "id_ed25519_work.pub"
        private_key.write_text("old private key")
        public_key.write_text("old public key")

        # Mock new key generation
        mock_private_key = MagicMock()
        mock_public_key = MagicMock()
        mock_generate.return_value = mock_private_key
        mock_private_key.public_key.return_value = mock_public_key
        mock_private_key.private_bytes.return_value = b"new private key"
        mock_public_key.public_bytes.return_value = b"ssh-ed25519 NEW_KEY"

        result = ssh_manager.regenerate_ssh_key("work", "work@example.com")

        assert result[0] == str(private_key)
        assert "work@example.com" in result[1]
        assert private_key.exists()
        assert public_key.exists()

        # Should contain new key data
        assert "new private key" in private_key.read_text()
        assert "NEW_KEY" in public_key.read_text()

    def test_regenerate_ssh_key_no_existing_keys(self, ssh_manager):
        """Test regeneration when no existing keys."""
        with patch.object(ssh_manager, 'generate_ssh_key') as mock_generate:
            mock_generate.return_value = ("/path/key", "ssh-ed25519 ABC...")

            result = ssh_manager.regenerate_ssh_key("work", "work@example.com")

            mock_generate.assert_called_once_with("work", "work@example.com")
            assert result == ("/path/key", "ssh-ed25519 ABC...")


class TestSSHConfigFile:
    """Test SSH config file operations."""

    def test_ssh_config_file_permissions(self, ssh_manager):
        """Test SSH config file gets correct permissions."""
        ssh_manager._add_ssh_config_entry("work", "/path/to/key")

        config_stat = ssh_manager.ssh_config_file.stat()
        assert oct(config_stat.st_mode)[-3:] == '600'

    def test_ssh_config_entry_format(self, ssh_manager):
        """Test SSH config entry has correct format."""
        ssh_manager._add_ssh_config_entry("work", "/path/to/key")

        config_content = ssh_manager.ssh_config_file.read_text()
        lines = config_content.strip().split('\n')

        assert "# GitHub Switcher - work profile" in lines
        assert "Host github-work" in lines
        assert "    HostName github.com" in lines
        assert "    User git" in lines
        assert "    IdentityFile /path/to/key" in lines
        assert "    IdentitiesOnly yes" in lines

    def test_ssh_config_handles_missing_newline(self, ssh_manager):
        """Test SSH config handles existing config without trailing newline."""
        # Create config without trailing newline
        ssh_manager.ssh_config_file.write_text("Host example.com")

        ssh_manager._add_ssh_config_entry("work", "/path/to/key")

        config_content = ssh_manager.ssh_config_file.read_text()
        lines = config_content.split('\n')

        # Should add newline before new entry
        assert "Host example.com" in lines[0]
        assert any("# GitHub Switcher - work profile" in line for line in lines)
