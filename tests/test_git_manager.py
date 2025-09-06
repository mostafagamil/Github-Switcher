"""Tests for git configuration management."""

import subprocess
from unittest.mock import Mock, call, patch

import pytest

from github_switcher.git_manager import GitManager


class TestGitManager:
    """Test git configuration management functionality."""

    @pytest.fixture
    def git_manager(self):
        """Create a GitManager instance."""
        return GitManager()

    @patch("subprocess.run")
    def test_get_current_git_config(self, mock_run, git_manager):
        """Test getting current git configuration."""
        # Mock successful git config commands
        mock_run.side_effect = [
            Mock(returncode=0, stdout="John Doe\n"),  # user.name
            Mock(returncode=0, stdout="john@example.com\n"),  # user.email
        ]

        name, email = git_manager.get_current_git_config()

        assert name == "John Doe"
        assert email == "john@example.com"

        # Verify the correct git commands were called
        expected_calls = [
            call(
                ["git", "config", "--global", "user.name"],
                capture_output=True,
                text=True,
                check=False,
            ),
            call(
                ["git", "config", "--global", "user.email"],
                capture_output=True,
                text=True,
                check=False,
            ),
        ]
        mock_run.assert_has_calls(expected_calls)

    @patch("subprocess.run")
    def test_get_current_git_config_not_set(self, mock_run, git_manager):
        """Test getting git configuration when not set."""
        # Mock git config commands returning error (not set)
        mock_run.side_effect = [
            Mock(returncode=1, stdout=""),  # user.name not set
            Mock(returncode=1, stdout=""),  # user.email not set
        ]

        name, email = git_manager.get_current_git_config()

        assert name is None
        assert email is None

    @patch("subprocess.run")
    def test_get_current_git_config_subprocess_error(self, mock_run, git_manager):
        """Test getting git configuration with subprocess error."""
        # Mock subprocess error
        mock_run.side_effect = subprocess.SubprocessError("Command failed")

        name, email = git_manager.get_current_git_config()

        assert name is None
        assert email is None

    @patch("subprocess.run")
    def test_set_git_config(self, mock_run, git_manager):
        """Test setting git configuration."""
        # Mock successful git config commands
        mock_run.return_value = Mock(returncode=0)

        git_manager.set_git_config("Jane Doe", "jane@example.com")

        # Verify the correct git commands were called
        expected_calls = [
            call(
                ["git", "config", "--global", "user.name", "Jane Doe"],
                check=True,
                capture_output=True,
            ),
            call(
                ["git", "config", "--global", "user.email", "jane@example.com"],
                check=True,
                capture_output=True,
            ),
        ]
        mock_run.assert_has_calls(expected_calls)

    @patch("subprocess.run")
    def test_set_git_config_failure(self, mock_run, git_manager):
        """Test setting git configuration when command fails."""
        from subprocess import SubprocessError

        # Mock git command failure
        mock_run.side_effect = SubprocessError("Git command failed")

        with pytest.raises(RuntimeError, match="Failed to set git configuration"):
            git_manager.set_git_config("Jane Doe", "jane@example.com")

    @patch("subprocess.run")
    def test_validate_git_config(self, mock_run, git_manager):
        """Test validating git configuration."""
        # Mock git config commands returning the expected values
        mock_run.side_effect = [
            Mock(returncode=0, stdout="Jane Doe\n"),  # user.name
            Mock(returncode=0, stdout="jane@example.com\n"),  # user.email
        ]

        result = git_manager.validate_git_config("Jane Doe", "jane@example.com")

        assert result is True

    @patch("subprocess.run")
    def test_validate_git_config_mismatch(self, mock_run, git_manager):
        """Test validating git configuration when values don't match."""
        # Mock git config commands returning different values
        mock_run.side_effect = [
            Mock(returncode=0, stdout="John Doe\n"),  # user.name
            Mock(returncode=0, stdout="john@example.com\n"),  # user.email
        ]

        result = git_manager.validate_git_config("Jane Doe", "jane@example.com")

        assert result is False

    @patch("subprocess.run")
    def test_is_git_available(self, mock_run, git_manager):
        """Test checking if git is available."""
        # Mock successful git --version command
        mock_run.return_value = Mock(returncode=0)

        result = git_manager.is_git_available()

        assert result is True
        mock_run.assert_called_once_with(
            ["git", "--version"], check=True, capture_output=True
        )

    @patch("subprocess.run")
    def test_is_git_available_not_found(self, mock_run, git_manager):
        """Test checking if git is available when not found."""
        # Mock FileNotFoundError (git command not found)
        mock_run.side_effect = FileNotFoundError("Git not found")

        result = git_manager.is_git_available()

        assert result is False

    @patch("subprocess.run")
    def test_get_git_version(self, mock_run, git_manager):
        """Test getting git version."""
        # Mock git --version command
        mock_run.return_value = Mock(returncode=0, stdout="git version 2.39.0\n")

        version = git_manager.get_git_version()

        assert version == "git version 2.39.0"
        mock_run.assert_called_once_with(
            ["git", "--version"], capture_output=True, text=True, check=True
        )

    @patch("subprocess.run")
    def test_get_git_version_not_available(self, mock_run, git_manager):
        """Test getting git version when git is not available."""
        # Mock FileNotFoundError (git command not found)
        mock_run.side_effect = FileNotFoundError("Git not found")

        version = git_manager.get_git_version()

        assert version is None

    @patch("subprocess.run")
    def test_restore_git_config(self, mock_run, git_manager):
        """Test restoring git configuration."""
        # Mock successful git config commands
        mock_run.return_value = Mock(returncode=0)

        git_manager.restore_git_config("Original User", "original@example.com")

        # Verify the correct git commands were called
        expected_calls = [
            call(
                ["git", "config", "--global", "user.name", "Original User"],
                check=True,
                capture_output=True,
            ),
            call(
                ["git", "config", "--global", "user.email", "original@example.com"],
                check=True,
                capture_output=True,
            ),
        ]
        mock_run.assert_has_calls(expected_calls)

    @patch("subprocess.run")
    def test_restore_git_config_unset_values(self, mock_run, git_manager):
        """Test restoring git configuration with None values (unset)."""
        # Mock git config commands
        mock_run.return_value = Mock(returncode=0)

        git_manager.restore_git_config(None, None)

        # Verify the correct git unset commands were called
        expected_calls = [
            call(
                ["git", "config", "--global", "--unset", "user.name"],
                check=False,
                capture_output=True,
            ),
            call(
                ["git", "config", "--global", "--unset", "user.email"],
                check=False,
                capture_output=True,
            ),
        ]
        mock_run.assert_has_calls(expected_calls)

    @patch("subprocess.run")
    def test_is_git_available_subprocess_error(self, mock_run, git_manager):
        """Test git availability when git command fails."""
        mock_run.side_effect = subprocess.SubprocessError()
        assert git_manager.is_git_available() is False

    @patch("subprocess.run")
    def test_get_git_version_subprocess_error(self, mock_run, git_manager):
        """Test git version with subprocess error."""
        mock_run.side_effect = subprocess.SubprocessError()
        assert git_manager.get_git_version() is None

    @patch("subprocess.run")
    def test_backup_git_config(self, mock_run, git_manager):
        """Test backing up git configuration."""
        # Mock git config commands
        mock_run.side_effect = [
            Mock(returncode=0, stdout="John Doe\n"),  # user.name
            Mock(returncode=0, stdout="john@example.com\n"),  # user.email
        ]

        name, email = git_manager.backup_git_config()

        assert name == "John Doe"
        assert email == "john@example.com"

    @patch("subprocess.run")
    def test_restore_git_config_error(self, mock_run, git_manager):
        """Test restore git config with error."""
        mock_run.side_effect = subprocess.SubprocessError("Command failed")
        with pytest.raises(RuntimeError, match="Failed to restore git configuration"):
            git_manager.restore_git_config("Test User", "test@example.com")
