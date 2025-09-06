"""Tests for utility functions and helpers."""

import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from github_switcher.utils import (
    copy_to_clipboard_fallback,
    ensure_directory,
    expand_path,
    format_time_ago,
    get_clipboard_command,
    get_config_directory,
    get_platform_info,
    get_ssh_directory,
    is_command_available,
    safe_remove_file,
    sanitize_filename,
    validate_ssh_key_format,
)


@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestGetPlatformInfo:
    """Test platform information retrieval."""

    @patch('github_switcher.utils.platform.system')
    @patch('github_switcher.utils.platform.release')
    def test_get_platform_info(self, mock_release, mock_system):
        """Test platform info formatting."""
        mock_system.return_value = "Darwin"
        mock_release.return_value = "23.1.0"

        result = get_platform_info()
        assert result == "Darwin 23.1.0"

        mock_system.assert_called_once()
        mock_release.assert_called_once()


class TestIsCommandAvailable:
    """Test command availability checking."""

    @patch('subprocess.run')
    def test_command_available_success(self, mock_run):
        """Test detecting available command."""
        mock_run.return_value = None  # Successful command

        result = is_command_available("git")

        assert result is True
        mock_run.assert_called_once_with(
            ["git", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

    @patch('subprocess.run')
    def test_command_available_subprocess_error(self, mock_run):
        """Test detecting unavailable command with subprocess error."""
        mock_run.side_effect = subprocess.SubprocessError("Command failed")

        result = is_command_available("nonexistent")
        assert result is False

    @patch('subprocess.run')
    def test_command_available_file_not_found(self, mock_run):
        """Test detecting unavailable command with FileNotFoundError."""
        mock_run.side_effect = FileNotFoundError("Command not found")

        result = is_command_available("nonexistent")
        assert result is False


class TestExpandPath:
    """Test path expansion."""

    def test_expand_path_regular(self):
        """Test expanding regular path."""
        result = expand_path("/tmp/test")
        assert result.is_absolute()
        # On macOS, /tmp may resolve to /private/tmp
        # On Windows, paths are different
        if platform.system() == 'Windows':
            assert str(result).endswith("\\tmp\\test")
        else:
            assert str(result).endswith("/tmp/test")

    def test_expand_path_with_tilde(self):
        """Test expanding path with tilde."""
        result = expand_path("~/test")
        # Should expand to the user's home directory + test
        assert result.is_absolute()
        assert result.name == "test"
        # Should contain the actual home directory path
        home_path = Path.home()
        assert str(result).startswith(str(home_path))

    def test_expand_path_relative(self):
        """Test expanding relative path."""
        result = expand_path("relative/path")
        assert result.is_absolute()
        # Should resolve to absolute path based on cwd


class TestEnsureDirectory:
    """Test directory creation."""

    def test_ensure_directory_new(self, temp_dir):
        """Test creating new directory."""
        new_dir = temp_dir / "new_directory"
        assert not new_dir.exists()

        ensure_directory(new_dir, mode=0o755)

        assert new_dir.exists()
        assert new_dir.is_dir()
        if platform.system() != 'Windows':
            assert oct(new_dir.stat().st_mode)[-3:] == '755'

    def test_ensure_directory_existing(self, temp_dir):
        """Test ensuring existing directory."""
        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()

        ensure_directory(existing_dir, mode=0o700)

        assert existing_dir.exists()
        if platform.system() != 'Windows':
            assert oct(existing_dir.stat().st_mode)[-3:] == '700'

    def test_ensure_directory_nested(self, temp_dir):
        """Test creating nested directories."""
        nested_dir = temp_dir / "level1" / "level2" / "level3"
        assert not nested_dir.exists()

        ensure_directory(nested_dir)

        assert nested_dir.exists()
        assert (temp_dir / "level1").exists()
        assert (temp_dir / "level1" / "level2").exists()


class TestSafeRemoveFile:
    """Test safe file removal."""

    def test_safe_remove_file_existing(self, temp_dir):
        """Test removing existing file."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()

        result = safe_remove_file(test_file)

        assert result is True
        assert not test_file.exists()

    def test_safe_remove_file_nonexistent(self, temp_dir):
        """Test removing non-existent file."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        assert not nonexistent_file.exists()

        result = safe_remove_file(nonexistent_file)
        assert result is True

    def test_safe_remove_file_permission_error(self, temp_dir):
        """Test removing file with permission error."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        with patch.object(Path, 'unlink') as mock_unlink:
            mock_unlink.side_effect = OSError("Permission denied")

            result = safe_remove_file(test_file)
            assert result is False


class TestGetSSHDirectory:
    """Test SSH directory path retrieval."""

    @patch('pathlib.Path.home')
    def test_get_ssh_directory(self, mock_home):
        """Test getting SSH directory path."""
        mock_home.return_value = Path("/home/user")

        result = get_ssh_directory()

        assert result == Path("/home/user/.ssh")
        mock_home.assert_called_once()


class TestGetConfigDirectory:
    """Test configuration directory path retrieval."""

    @patch('github_switcher.utils.platform.system')
    @patch('pathlib.Path.home')
    def test_get_config_directory_linux(self, mock_home, mock_system):
        """Test config directory on Linux."""
        mock_system.return_value = "Linux"
        mock_home.return_value = Path("/home/user")

        with patch.dict(os.environ, {}, clear=True):
            result = get_config_directory("myapp")

        assert result == Path("/home/user/.config/myapp")

    @patch('github_switcher.utils.platform.system')
    @patch('pathlib.Path.home')
    def test_get_config_directory_linux_xdg(self, mock_home, mock_system):
        """Test config directory on Linux with XDG_CONFIG_HOME."""
        mock_system.return_value = "Linux"
        mock_home.return_value = Path("/home/user")

        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/custom/config"}):
            result = get_config_directory("myapp")

        assert result == Path("/custom/config/myapp")

    @patch('github_switcher.utils.platform.system')
    @patch('pathlib.Path.home')
    def test_get_config_directory_macos(self, mock_home, mock_system):
        """Test config directory on macOS."""
        mock_system.return_value = "Darwin"
        mock_home.return_value = Path("/Users/user")

        result = get_config_directory("myapp")

        assert result == Path("/Users/user/Library/Application Support/myapp")

    @patch('github_switcher.utils.platform.system')
    @patch('pathlib.Path.home')
    def test_get_config_directory_windows(self, mock_home, mock_system):
        """Test config directory on Windows."""
        mock_system.return_value = "Windows"
        mock_home.return_value = Path("C:/Users/user")

        with patch.dict(os.environ, {}, clear=True):
            result = get_config_directory("myapp")

        assert result == Path("C:/Users/user/AppData/Roaming/myapp")

    @patch('github_switcher.utils.platform.system')
    def test_get_config_directory_windows_appdata(self, mock_system):
        """Test config directory on Windows with APPDATA."""
        mock_system.return_value = "Windows"

        with patch.dict(os.environ, {"APPDATA": "C:/Users/user/AppData/Roaming"}):
            result = get_config_directory("myapp")

        assert result == Path("C:/Users/user/AppData/Roaming/myapp")

    def test_get_config_directory_default_name(self):
        """Test config directory with default app name."""
        result = get_config_directory()
        assert result.name == "github-switcher"


class TestValidateSSHKeyFormat:
    """Test SSH key format validation."""

    def test_validate_ssh_key_format_rsa(self):
        """Test validating RSA SSH key."""
        key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC... user@example.com"
        assert validate_ssh_key_format(key) is True

    def test_validate_ssh_key_format_ed25519(self):
        """Test validating Ed25519 SSH key."""
        key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@example.com"
        assert validate_ssh_key_format(key) is True

    def test_validate_ssh_key_format_ecdsa(self):
        """Test validating ECDSA SSH keys."""
        keys = [
            "ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTY...",
            "ecdsa-sha2-nistp384 AAAAE2VjZHNhLXNoYTItbmlzdHAzODQ...",
            "ecdsa-sha2-nistp521 AAAAE2VjZHNhLXNoYTItbmlzdHA1MjE..."
        ]
        for key in keys:
            assert validate_ssh_key_format(key) is True

    def test_validate_ssh_key_format_dss(self):
        """Test validating DSS SSH key."""
        key = "ssh-dss AAAAB3NzaC1kc3MAAACBAI... user@example.com"
        assert validate_ssh_key_format(key) is True

    def test_validate_ssh_key_format_invalid(self):
        """Test validating invalid SSH key formats."""
        invalid_keys = [
            "",
            "not-an-ssh-key",
            "random text",
            "BEGIN RSA PRIVATE KEY",
            None
        ]

        for key in invalid_keys:
            assert validate_ssh_key_format(key) is False

    def test_validate_ssh_key_format_whitespace(self):
        """Test validating SSH key with whitespace."""
        key = "  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@example.com  "
        assert validate_ssh_key_format(key) is True


class TestSanitizeFilename:
    """Test filename sanitization."""

    def test_sanitize_filename_normal(self):
        """Test sanitizing normal filename."""
        result = sanitize_filename("normal_filename.txt")
        assert result == "normal_filename.txt"

    def test_sanitize_filename_invalid_chars(self):
        """Test sanitizing filename with invalid characters."""
        result = sanitize_filename('file<name>with:invalid"chars/\\|?*')
        assert result == "file_name_with_invalid_chars_____"

    def test_sanitize_filename_leading_trailing(self):
        """Test sanitizing filename with leading/trailing dots and spaces."""
        result = sanitize_filename("  ..filename..  ")
        assert result == "filename"

    def test_sanitize_filename_empty(self):
        """Test sanitizing empty filename."""
        result = sanitize_filename("")
        assert result == "unnamed"

    def test_sanitize_filename_only_invalid(self):
        """Test sanitizing filename with only invalid characters."""
        result = sanitize_filename("...")
        assert result == "unnamed"


class TestGetClipboardCommand:
    """Test clipboard command detection."""

    @patch('github_switcher.utils.platform.system')
    def test_get_clipboard_command_macos(self, mock_system):
        """Test clipboard command on macOS."""
        mock_system.return_value = "Darwin"

        result = get_clipboard_command()
        assert result == "pbcopy"

    @patch('github_switcher.utils.platform.system')
    def test_get_clipboard_command_windows(self, mock_system):
        """Test clipboard command on Windows."""
        mock_system.return_value = "Windows"

        result = get_clipboard_command()
        assert result == "clip"

    @patch('github_switcher.utils.platform.system')
    @patch('github_switcher.utils.is_command_available')
    def test_get_clipboard_command_linux_xclip(self, mock_available, mock_system):
        """Test clipboard command on Linux with xclip."""
        mock_system.return_value = "Linux"
        mock_available.side_effect = lambda cmd: cmd == "xclip"

        result = get_clipboard_command()
        assert result == "xclip"

    @patch('github_switcher.utils.platform.system')
    @patch('github_switcher.utils.is_command_available')
    def test_get_clipboard_command_linux_xsel(self, mock_available, mock_system):
        """Test clipboard command on Linux with xsel."""
        mock_system.return_value = "Linux"
        mock_available.side_effect = lambda cmd: cmd == "xsel"

        result = get_clipboard_command()
        assert result == "xsel"

    @patch('github_switcher.utils.platform.system')
    @patch('github_switcher.utils.is_command_available')
    def test_get_clipboard_command_linux_none(self, mock_available, mock_system):
        """Test clipboard command on Linux with no utilities."""
        mock_system.return_value = "Linux"
        mock_available.return_value = False

        result = get_clipboard_command()
        assert result is None

    @patch('github_switcher.utils.platform.system')
    def test_get_clipboard_command_unknown(self, mock_system):
        """Test clipboard command on unknown platform."""
        mock_system.return_value = "Unknown"

        result = get_clipboard_command()
        assert result is None


class TestCopyToClipboardFallback:
    """Test fallback clipboard copying."""

    @patch('github_switcher.utils.get_clipboard_command')
    def test_copy_to_clipboard_fallback_no_command(self, mock_get_cmd):
        """Test fallback copy when no command available."""
        mock_get_cmd.return_value = None

        result = copy_to_clipboard_fallback("test text")
        assert result is False

    @patch('github_switcher.utils.get_clipboard_command')
    @patch('subprocess.run')
    def test_copy_to_clipboard_fallback_pbcopy(self, mock_run, mock_get_cmd):
        """Test fallback copy with pbcopy."""
        mock_get_cmd.return_value = "pbcopy"
        mock_run.return_value = None

        result = copy_to_clipboard_fallback("test text")

        assert result is True
        mock_run.assert_called_once_with(
            ["pbcopy"], input="test text", text=True, check=True
        )

    @patch('github_switcher.utils.get_clipboard_command')
    @patch('subprocess.run')
    def test_copy_to_clipboard_fallback_xclip(self, mock_run, mock_get_cmd):
        """Test fallback copy with xclip."""
        mock_get_cmd.return_value = "xclip"
        mock_run.return_value = None

        result = copy_to_clipboard_fallback("test text")

        assert result is True
        mock_run.assert_called_once_with(
            ["xclip", "-selection", "clipboard"],
            input="test text", text=True, check=True
        )

    @patch('github_switcher.utils.get_clipboard_command')
    @patch('subprocess.run')
    def test_copy_to_clipboard_fallback_xsel(self, mock_run, mock_get_cmd):
        """Test fallback copy with xsel."""
        mock_get_cmd.return_value = "xsel"
        mock_run.return_value = None

        result = copy_to_clipboard_fallback("test text")

        assert result is True
        mock_run.assert_called_once_with(
            ["xsel", "--clipboard", "--input"],
            input="test text", text=True, check=True
        )

    @patch('github_switcher.utils.get_clipboard_command')
    @patch('subprocess.run')
    def test_copy_to_clipboard_fallback_clip(self, mock_run, mock_get_cmd):
        """Test fallback copy with clip."""
        mock_get_cmd.return_value = "clip"
        mock_run.return_value = None

        result = copy_to_clipboard_fallback("test text")

        assert result is True
        mock_run.assert_called_once_with(
            ["clip"], input="test text", text=True, check=True
        )

    @patch('github_switcher.utils.get_clipboard_command')
    @patch('subprocess.run')
    def test_copy_to_clipboard_fallback_error(self, mock_run, mock_get_cmd):
        """Test fallback copy with subprocess error."""
        mock_get_cmd.return_value = "pbcopy"
        mock_run.side_effect = subprocess.SubprocessError("Command failed")

        result = copy_to_clipboard_fallback("test text")
        assert result is False


class TestFormatTimeAgo:
    """Test time formatting functionality."""

    def test_format_time_ago_none(self):
        """Test formatting None datetime."""
        result = format_time_ago(None)
        assert result == "Never"

    def test_format_time_ago_empty(self):
        """Test formatting empty datetime."""
        result = format_time_ago("")
        assert result == "Never"

    def test_format_time_ago_just_now(self):
        """Test formatting very recent time."""
        from datetime import datetime, timezone

        # Create a time string that's just a few seconds ago
        now = datetime.now(timezone.utc)
        recent = now.replace(second=max(0, now.second - 30))  # 30 seconds ago
        recent_str = recent.isoformat().replace('+00:00', 'Z')

        result = format_time_ago(recent_str)
        assert result == "Just now"

    def test_format_time_ago_minutes(self):
        """Test formatting minutes ago."""
        from datetime import datetime, timedelta, timezone

        # Create a time that's 15 minutes ago
        now = datetime.now(timezone.utc)
        past = now - timedelta(minutes=15)
        past_str = past.isoformat().replace('+00:00', 'Z')

        result = format_time_ago(past_str)
        # Should contain "minute" and "ago"
        assert "minute" in result and "ago" in result

    def test_format_time_ago_one_minute(self):
        """Test formatting one minute ago."""
        from datetime import datetime, timedelta, timezone

        # Create a time that's 1 minute ago
        now = datetime.now(timezone.utc)
        past = now - timedelta(minutes=1)
        past_str = past.isoformat().replace('+00:00', 'Z')

        result = format_time_ago(past_str)
        assert "1 minute ago" == result

    def test_format_time_ago_hours(self):
        """Test formatting hours ago."""
        from datetime import datetime, timedelta, timezone

        # Create a time that's 3 hours ago
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=3)
        past_str = past.isoformat().replace('+00:00', 'Z')

        result = format_time_ago(past_str)
        assert "hour" in result and "ago" in result

    def test_format_time_ago_one_hour(self):
        """Test formatting one hour ago."""
        from datetime import datetime, timedelta, timezone

        # Create a time that's 1 hour ago
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=1)
        past_str = past.isoformat().replace('+00:00', 'Z')

        result = format_time_ago(past_str)
        assert "1 hour ago" == result

    def test_format_time_ago_days(self):
        """Test formatting days ago."""
        from datetime import datetime, timedelta, timezone

        # Create a time that's 4 days ago
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=4)
        past_str = past.isoformat().replace('+00:00', 'Z')

        result = format_time_ago(past_str)
        assert "day" in result and "ago" in result

    def test_format_time_ago_one_day(self):
        """Test formatting one day ago."""
        from datetime import datetime, timedelta, timezone

        # Create a time that's 1 day ago
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=1)
        past_str = past.isoformat().replace('+00:00', 'Z')

        result = format_time_ago(past_str)
        assert "1 day ago" == result

    def test_format_time_ago_invalid_format(self):
        """Test formatting invalid datetime string."""
        result = format_time_ago("invalid-date")
        assert result == "Unknown"

    def test_format_time_ago_z_suffix(self):
        """Test formatting datetime with Z suffix."""
        from datetime import datetime, timedelta, timezone

        # Create a time that's 1 hour ago with Z suffix
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=1)
        past_str = past.isoformat().replace('+00:00', 'Z')

        result = format_time_ago(past_str)
        assert "1 hour ago" == result


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_ensure_directory_with_file_conflict(self, temp_dir):
        """Test ensure directory when path exists as file."""
        file_path = temp_dir / "conflict"
        file_path.write_text("test")

        # This should raise an exception since we can't create a directory
        # where a file already exists
        with pytest.raises(FileExistsError):
            ensure_directory(file_path)

    def test_expand_path_special_characters(self):
        """Test path expansion with special characters."""
        result = expand_path("path with spaces/and-special_chars")
        assert result.is_absolute()
        assert "path with spaces" in str(result)

    def test_sanitize_filename_unicode(self):
        """Test filename sanitization with unicode characters."""
        result = sanitize_filename("file_name_测试.txt")
        assert result == "file_name_测试.txt"  # Unicode should be preserved

    @patch('subprocess.run')
    def test_is_command_available_imports(self, mock_run):
        """Test that subprocess module is properly imported."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, ["cmd"])

        result = is_command_available("test")
        assert result is False
