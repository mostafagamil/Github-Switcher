"""Tests for profile management."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from github_switcher.profiles import ProfileManager


class TestProfileManager:
    """Test profile management functionality."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary configuration directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def profile_manager(self, temp_config_dir, monkeypatch):
        """Create a ProfileManager instance with temporary directory."""
        monkeypatch.setattr("pathlib.Path.home", lambda: temp_config_dir.parent)
        manager = ProfileManager()
        manager.config.config_dir = temp_config_dir / "github-switcher"
        manager.config.profiles_file = manager.config.config_dir / "profiles.toml"
        return manager

    def test_list_empty_profiles(self, profile_manager):
        """Test listing profiles when none exist."""
        profiles = profile_manager.list_profiles()
        assert profiles == {}

    def test_profile_exists(self, profile_manager):
        """Test checking if profile exists."""
        assert not profile_manager.profile_exists("test-profile")

        profile_manager.create_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        assert profile_manager.profile_exists("test-profile")

    def test_create_profile(self, profile_manager):
        """Test creating a new profile."""
        profile_manager.create_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        profile = profile_manager.get_profile("test-profile")
        assert profile is not None
        assert profile["name"] == "Test User"
        assert profile["email"] == "test@example.com"

    def test_create_profile_invalid_name(self, profile_manager):
        """Test creating profile with invalid name."""
        with pytest.raises(ValueError, match="Profile name must contain only"):
            profile_manager.create_profile(
                "invalid name!",
                "Test User",
                "test@example.com",
                "/path/to/key",
                "ssh-ed25519 AAAAC3... test@example.com",
            )

    def test_create_profile_invalid_email(self, profile_manager):
        """Test creating profile with invalid email."""
        with pytest.raises(ValueError, match="Invalid email format"):
            profile_manager.create_profile(
                "test-profile",
                "Test User",
                "invalid-email",
                "/path/to/key",
                "ssh-ed25519 AAAAC3... test@example.com",
            )

    def test_switch_profile(self, profile_manager):
        """Test switching to a profile."""
        profile_manager.create_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        # Mock the managers
        mock_git_manager = Mock()
        mock_ssh_manager = Mock()

        result = profile_manager.switch_profile(
            "test-profile", mock_git_manager, mock_ssh_manager
        )

        assert result is True
        mock_git_manager.set_git_config.assert_called_once_with(
            "Test User", "test@example.com"
        )
        mock_ssh_manager.activate_ssh_key.assert_called_once_with(
            "test-profile", "/path/to/key"
        )

        # Check active profile was set
        assert profile_manager.get_current_profile() == "test-profile"

    def test_switch_nonexistent_profile(self, profile_manager):
        """Test switching to a profile that doesn't exist."""
        mock_git_manager = Mock()
        mock_ssh_manager = Mock()

        with pytest.raises(ValueError, match="not found"):
            profile_manager.switch_profile(
                "nonexistent", mock_git_manager, mock_ssh_manager
            )

    def test_update_profile(self, profile_manager):
        """Test updating profile information."""
        profile_manager.create_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        profile_manager.update_profile("test-profile", name="Updated User")

        profile = profile_manager.get_profile("test-profile")
        assert profile["name"] == "Updated User"

    def test_update_profile_invalid_email(self, profile_manager):
        """Test updating profile with invalid email."""
        profile_manager.create_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        with pytest.raises(ValueError, match="Invalid email format"):
            profile_manager.update_profile("test-profile", email="invalid-email")

    def test_delete_profile(self, profile_manager):
        """Test deleting a profile."""
        profile_manager.create_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        mock_ssh_manager = Mock()

        result = profile_manager.delete_profile("test-profile", mock_ssh_manager)

        assert result is True
        assert not profile_manager.profile_exists("test-profile")
        mock_ssh_manager.remove_ssh_key.assert_called_once_with("/path/to/key")
        mock_ssh_manager.remove_ssh_config_entry.assert_called_once_with("test-profile")


    def test_validate_profile_name(self, profile_manager):
        """Test profile name validation."""
        assert profile_manager._validate_profile_name("valid-name")
        assert profile_manager._validate_profile_name("valid_name")
        assert profile_manager._validate_profile_name("validname123")
        assert not profile_manager._validate_profile_name("invalid name")
        assert not profile_manager._validate_profile_name("invalid@name")
        assert not profile_manager._validate_profile_name("")

    def test_validate_email(self, profile_manager):
        """Test email validation."""
        assert profile_manager._validate_email("test@example.com")
        assert profile_manager._validate_email("user.name@domain.co.uk")
        assert not profile_manager._validate_email("invalid-email")
        assert not profile_manager._validate_email("@example.com")
        assert not profile_manager._validate_email("test@")
        assert not profile_manager._validate_email("")


    def test_switch_profile_error(self, profile_manager):
        """Test switch profile with error."""
        profile_manager.create_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        # Mock managers that will raise errors
        mock_git = Mock()
        mock_ssh = Mock()
        mock_git.set_git_config.side_effect = Exception("Git error")

        with pytest.raises(RuntimeError, match="Failed to switch profile"):
            profile_manager.switch_profile("test-profile", mock_git, mock_ssh)

    def test_delete_profile_error(self, profile_manager):
        """Test delete profile with error."""
        profile_manager.create_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        # Mock ssh manager that will raise error
        mock_ssh = Mock()
        mock_ssh.remove_ssh_key.side_effect = Exception("SSH error")

        with pytest.raises(RuntimeError, match="Failed to delete profile"):
            profile_manager.delete_profile("test-profile", mock_ssh)

    def test_update_nonexistent_profile(self, profile_manager):
        """Test updating profile that doesn't exist (line 73)."""
        with pytest.raises(ValueError, match="Profile 'nonexistent' not found"):
            profile_manager.update_profile("nonexistent", name="Test")

    def test_delete_nonexistent_profile(self, profile_manager):
        """Test deleting profile that doesn't exist (line 84)."""
        mock_ssh = Mock()
        with pytest.raises(ValueError, match="Profile 'nonexistent' not found"):
            profile_manager.delete_profile("nonexistent", mock_ssh)

