"""Tests for configuration management."""

import platform
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from github_switcher.config import Config


class TestConfig:
    """Test configuration management functionality."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary configuration directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def config(self, temp_config_dir, monkeypatch):
        """Create a Config instance with temporary directory."""
        monkeypatch.setattr("pathlib.Path.home", lambda: temp_config_dir.parent)
        config_instance = Config()
        config_instance.config_dir = temp_config_dir / "github-switcher"
        config_instance.profiles_file = config_instance.config_dir / "profiles.toml"
        return config_instance

    def test_load_empty_profiles(self, config):
        """Test loading profiles when no config file exists."""
        profiles = config.load_profiles()

        assert "meta" in profiles
        assert "profiles" in profiles
        assert profiles["meta"]["version"] == "1.0"
        assert profiles["meta"]["active_profile"] is None
        assert profiles["profiles"] == {}

    def test_add_profile(self, config):
        """Test adding a new profile."""
        config.add_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        profile = config.get_profile("test-profile")
        assert profile is not None
        assert profile["name"] == "Test User"
        assert profile["email"] == "test@example.com"
        assert profile["ssh_key_path"] == "/path/to/key"
        assert "created_at" in profile

    def test_add_duplicate_profile(self, config):
        """Test adding duplicate profile raises error."""
        config.add_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        with pytest.raises(ValueError, match="already exists"):
            config.add_profile(
                "test-profile",
                "Another User",
                "another@example.com",
                "/path/to/another/key",
                "ssh-ed25519 AAAAC3... another@example.com",
            )

    def test_get_nonexistent_profile(self, config):
        """Test getting a profile that doesn't exist."""
        profile = config.get_profile("nonexistent")
        assert profile is None

    def test_update_profile(self, config):
        """Test updating an existing profile."""
        config.add_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        config.update_profile("test-profile", {"name": "Updated User"})

        profile = config.get_profile("test-profile")
        assert profile["name"] == "Updated User"
        assert profile["email"] == "test@example.com"  # Should remain unchanged

    def test_update_nonexistent_profile(self, config):
        """Test updating a profile that doesn't exist."""
        with pytest.raises(ValueError, match="not found"):
            config.update_profile("nonexistent", {"name": "Test"})

    def test_delete_profile(self, config):
        """Test deleting a profile."""
        config.add_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        config.delete_profile("test-profile")

        profile = config.get_profile("test-profile")
        assert profile is None

    def test_delete_active_profile(self, config):
        """Test deleting the currently active profile."""
        config.add_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        # Set as active profile
        config.set_active_profile("test-profile")
        assert config.get_active_profile() == "test-profile"

        # Delete the active profile
        config.delete_profile("test-profile")

        # Active profile should be cleared
        assert config.get_active_profile() is None

    def test_delete_nonexistent_profile(self, config):
        """Test deleting a profile that doesn't exist."""
        with pytest.raises(ValueError, match="not found"):
            config.delete_profile("nonexistent")

    def test_set_active_profile(self, config):
        """Test setting active profile."""
        config.add_profile(
            "test-profile",
            "Test User",
            "test@example.com",
            "/path/to/key",
            "ssh-ed25519 AAAAC3... test@example.com",
        )

        config.set_active_profile("test-profile")

        active = config.get_active_profile()
        assert active == "test-profile"

        # Check that last_used was updated
        profile = config.get_profile("test-profile")
        assert profile["last_used"] is not None

    def test_set_nonexistent_active_profile(self, config):
        """Test setting active profile that doesn't exist."""
        with pytest.raises(ValueError, match="not found"):
            config.set_active_profile("nonexistent")


    def test_import_profiles(self, config):
        """Test importing profiles."""
        import_data = {
            "meta": {"version": "1.0"},
            "profiles": {
                "imported-profile": {
                    "name": "Imported User",
                    "email": "imported@example.com",
                    "ssh_key_public": "ssh-ed25519 AAAAC3... imported@example.com",
                    "created_at": "2024-01-01T00:00:00",
                }
            },
        }

        config.import_profiles(import_data)

        profile = config.get_profile("imported-profile")
        assert profile is not None
        assert profile["name"] == "Imported User"
        assert profile["email"] == "imported@example.com"

    def test_load_profiles_toml_decode_error(self, temp_config_dir):
        """Test loading profiles with invalid TOML."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_dir.parent
            config = Config()
            config.config_dir = temp_config_dir / "github-switcher"
            config.profiles_file = config.config_dir / "profiles.toml"

            # Create invalid TOML file
            config.profiles_file.parent.mkdir(parents=True, exist_ok=True)
            config.profiles_file.write_text("invalid [[ toml")

            with pytest.raises(ValueError, match="Failed to load profiles"):
                config.load_profiles()

    def test_load_profiles_os_error(self, temp_config_dir):
        """Test loading profiles with OS error."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_dir.parent
            config = Config()
            config.config_dir = temp_config_dir / "github-switcher"
            config.profiles_file = config.config_dir / "profiles.toml"

            # Create file with no read permissions
            config.profiles_file.parent.mkdir(parents=True, exist_ok=True)
            config.profiles_file.write_text("{}")
            config.profiles_file.chmod(0o000)

            try:
                with pytest.raises(ValueError, match="Failed to load profiles"):
                    config.load_profiles()
            finally:
                config.profiles_file.chmod(0o644)  # Restore for cleanup

    def test_save_profiles_os_error(self, temp_config_dir):
        """Test saving profiles with OS error."""
        if platform.system() == 'Windows':
            pytest.skip("Permission tests don't work reliably on Windows")

        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_dir.parent
            config = Config()
            config.config_dir = temp_config_dir / "github-switcher"
            config.profiles_file = config.config_dir / "profiles.toml"

            # Create directory without write permissions
            config.profiles_file.parent.mkdir(parents=True, exist_ok=True)
            config.profiles_file.parent.chmod(0o555)

            try:
                with pytest.raises(ValueError, match="Failed to save profiles"):
                    config.save_profiles({"test": "data"})
            finally:
                config.profiles_file.parent.chmod(0o755)  # Restore for cleanup

    def test_save_profiles_with_backup(self, temp_config_dir):
        """Test saving profiles creates backup of existing file."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_dir.parent
            config = Config()
            config.config_dir = temp_config_dir / "github-switcher"
            config.profiles_file = config.config_dir / "profiles.toml"
            config.profiles_file.parent.mkdir(parents=True, exist_ok=True)

            # Create existing config file
            original_data = {"existing": "data"}
            config.save_profiles(original_data)

            # Save new data
            new_data = {"new": "data"}
            config.save_profiles(new_data)

            # Check backup was created
            backup_file = config.profiles_file.with_suffix(".toml.backup")
            assert backup_file.exists()

            # Verify backup contains original data
            import toml
            with open(backup_file, encoding="utf-8") as f:
                backup_data = toml.load(f)
            assert backup_data == original_data

    def test_import_profiles_overwrite(self, temp_config_dir):
        """Test importing profiles with overwrite option."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_dir.parent
            config = Config()
            config.config_dir = temp_config_dir / "github-switcher"
            config.profiles_file = config.config_dir / "profiles.toml"

            # Add existing profile
            config.add_profile("test", "Original", "original@example.com", "/key", "ssh-key")

            # Import data with same profile name
            import_data = {
                "meta": {"version": "1.0"},
                "profiles": {
                    "test": {
                        "name": "Imported User",
                        "email": "imported@example.com",
                        "ssh_key_public": "ssh-ed25519 imported",
                        "created_at": "2024-01-01T00:00:00",
                    }
                },
            }

            config.import_profiles(import_data, overwrite=True)

            profile = config.get_profile("test")
            assert profile["name"] == "Imported User"  # Should be overwritten
            assert profile["email"] == "imported@example.com"

    def test_import_profiles_no_overwrite(self, temp_config_dir):
        """Test importing profiles without overwrite."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_dir.parent
            config = Config()
            config.config_dir = temp_config_dir / "github-switcher"
            config.profiles_file = config.config_dir / "profiles.toml"

            # Add existing profile
            config.add_profile("test", "Original", "original@example.com", "/key", "ssh-key")

            # Import data with same profile name
            import_data = {
                "meta": {"version": "1.0"},
                "profiles": {
                    "test": {
                        "name": "Imported User",
                        "email": "imported@example.com",
                        "ssh_key_public": "ssh-ed25519 imported",
                        "created_at": "2024-01-01T00:00:00",
                    }
                },
            }

            config.import_profiles(import_data, overwrite=False)

            profile = config.get_profile("test")
            assert profile["name"] == "Original"  # Should NOT be overwritten
            assert profile["email"] == "original@example.com"
