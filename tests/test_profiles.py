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


    def test_create_profile_with_full_metadata(self, profile_manager):
        """Test creating profile with complete SSH metadata."""
        profile_manager.create_profile(
            name="work",
            fullname="Work User",
            email="work@example.com",
            ssh_key_path="/path/to/key",
            ssh_public_key="ssh-ed25519 ABC123",
            ssh_key_fingerprint="SHA256:abcd1234",
            ssh_key_passphrase_protected=True,
            ssh_key_source="imported",
            ssh_key_type="ed25519"
        )

        profile = profile_manager.get_profile("work")
        assert profile is not None
        assert profile["ssh_key_fingerprint"] == "SHA256:abcd1234"
        assert profile["ssh_key_passphrase_protected"] is True
        assert profile["ssh_key_source"] == "imported"
        assert profile["ssh_key_type"] == "ed25519"

    def test_create_profile_with_default_metadata(self, profile_manager):
        """Test creating profile with default SSH metadata."""
        profile_manager.create_profile(
            name="personal",
            fullname="Personal User",
            email="personal@example.com",
            ssh_key_path="/path/to/personal",
            ssh_public_key="ssh-ed25519 DEF456"
        )

        profile = profile_manager.get_profile("personal")
        assert profile is not None
        assert profile.get("ssh_key_fingerprint") is None
        assert profile["ssh_key_passphrase_protected"] is False
        assert profile["ssh_key_source"] == "generated"
        assert profile["ssh_key_type"] == "ed25519"

    def test_update_profile_metadata(self, profile_manager):
        """Test updating profile with SSH metadata."""
        # Create initial profile
        profile_manager.create_profile(
            "test", "Test User", "test@example.com", "/path/key", "ssh-ed25519 TEST"
        )

        # Update with metadata
        profile_manager.update_profile(
            "test",
            ssh_key_fingerprint="SHA256:newfingerprint",
            ssh_key_passphrase_protected=True,
            ssh_key_source="imported"
        )

        profile = profile_manager.get_profile("test")
        assert profile["ssh_key_fingerprint"] == "SHA256:newfingerprint"
        assert profile["ssh_key_passphrase_protected"] is True
        assert profile["ssh_key_source"] == "imported"

    def test_export_profiles_with_metadata(self, profile_manager):
        """Test exporting profiles includes metadata."""
        profile_manager.create_profile(
            name="export_test",
            fullname="Export User",
            email="export@example.com",
            ssh_key_path="/path/export",
            ssh_public_key="ssh-ed25519 EXPORT123",
            ssh_key_fingerprint="SHA256:export1234",
            ssh_key_passphrase_protected=True,
            ssh_key_source="generated",
            ssh_key_type="rsa"
        )

        exported_str = profile_manager.export_profiles()
        # Parse the TOML string
        import toml
        exported = toml.loads(exported_str)
        profile_data = exported["profiles"]["export_test"]

        assert profile_data["ssh_key_fingerprint"] == "SHA256:export1234"
        assert profile_data["ssh_key_passphrase_protected"] is True
        assert profile_data["ssh_key_source"] == "generated"
        assert profile_data["ssh_key_type"] == "rsa"

    def test_import_profiles_with_metadata(self, profile_manager):
        """Test importing profiles with metadata."""
        import_data_str = '''[profiles.imported]
name = "Imported User"
email = "imported@example.com"
ssh_key_public = "ssh-ed25519 IMPORTED123"
ssh_key_fingerprint = "SHA256:imported1234"
ssh_key_passphrase_protected = false
ssh_key_source = "imported"
ssh_key_type = "ed25519"
created_at = "2024-01-01T00:00:00"
'''

        profile_manager.import_profiles(import_data_str)

        profile = profile_manager.get_profile("imported")
        assert profile is not None
        assert profile["ssh_key_fingerprint"] == "SHA256:imported1234"
        assert profile["ssh_key_passphrase_protected"] is False
        assert profile["ssh_key_source"] == "imported"
        assert profile["ssh_key_type"] == "ed25519"

    def test_import_legacy_profiles_without_metadata(self, profile_manager):
        """Test importing old profile format without metadata (backward compatibility)."""
        legacy_data_str = '''[profiles.legacy]
name = "Legacy User"
email = "legacy@example.com"
ssh_key_public = "ssh-rsa LEGACY123"
created_at = "2023-01-01T00:00:00"
# No metadata fields
'''

        profile_manager.import_profiles(legacy_data_str)

        profile = profile_manager.get_profile("legacy")
        assert profile is not None
        # Should have default values
        assert profile.get("ssh_key_fingerprint") is None
        assert profile["ssh_key_passphrase_protected"] is False
        assert profile["ssh_key_source"] == "generated"
        assert profile["ssh_key_type"] == "ed25519"

    def test_export_profiles_json_format(self, profile_manager):
        """Test exporting profiles in JSON format."""
        profile_manager.create_profile(
            "json_test", "JSON User", "json@example.com", "/path/json", "ssh-ed25519 JSON123"
        )

        exported_json = profile_manager.export_profiles(format="json")

        # Parse the JSON
        import json
        exported = json.loads(exported_json)

        assert "profiles" in exported
        assert "json_test" in exported["profiles"]
        profile_data = exported["profiles"]["json_test"]
        assert profile_data["name"] == "JSON User"
        assert profile_data["email"] == "json@example.com"

    def test_export_profiles_yaml_format_without_pyyaml(self, profile_manager):
        """Test exporting profiles in YAML format when PyYAML is not available."""
        profile_manager.create_profile(
            "yaml_test", "YAML User", "yaml@example.com", "/path/yaml", "ssh-ed25519 YAML123"
        )

        # Mock yaml import to raise ImportError
        import sys
        original_modules = sys.modules.copy()

        # Remove yaml from modules if it exists
        if 'yaml' in sys.modules:
            del sys.modules['yaml']

        # Mock import to always fail for yaml
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == 'yaml':
                raise ImportError("No module named 'yaml'")
            return original_import(name, *args, **kwargs)

        builtins.__import__ = mock_import

        try:
            with pytest.raises(ValueError, match="PyYAML not installed"):
                profile_manager.export_profiles(format="yaml")
        finally:
            # Restore original state
            builtins.__import__ = original_import
            sys.modules.update(original_modules)

    def test_import_profiles_json_format(self, profile_manager):
        """Test importing profiles from JSON format."""
        json_data = '''
        {
            "profiles": {
                "json_import": {
                    "name": "JSON Import User",
                    "email": "json@import.com",
                    "ssh_key_public": "ssh-ed25519 JSONIMPORT123",
                    "created_at": "2024-01-01T00:00:00"
                }
            }
        }
        '''

        profile_manager.import_profiles(json_data, format="json")

        profile = profile_manager.get_profile("json_import")
        assert profile is not None
        assert profile["name"] == "JSON Import User"
        assert profile["email"] == "json@import.com"

    def test_import_profiles_yaml_format_without_pyyaml(self, profile_manager):
        """Test importing profiles from YAML format when PyYAML is not available."""
        yaml_data = '''
        profiles:
          yaml_import:
            name: "YAML Import User"
            email: "yaml@import.com"
            ssh_key_public: "ssh-ed25519 YAMLIMPORT123"
            created_at: "2024-01-01T00:00:00"
        '''

        # Mock yaml import to raise ImportError
        import sys
        original_modules = sys.modules.copy()

        # Remove yaml from modules if it exists
        if 'yaml' in sys.modules:
            del sys.modules['yaml']

        # Mock import to always fail for yaml
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == 'yaml':
                raise ImportError("No module named 'yaml'")
            return original_import(name, *args, **kwargs)

        builtins.__import__ = mock_import

        try:
            with pytest.raises(ValueError, match="PyYAML not installed"):
                profile_manager.import_profiles(yaml_data, format="yaml")
        finally:
            # Restore original state
            builtins.__import__ = original_import
            sys.modules.update(original_modules)

    def test_export_profiles_yaml_format_with_pyyaml(self, profile_manager):
        """Test exporting profiles in YAML format when PyYAML is available."""
        from unittest.mock import Mock

        profile_manager.create_profile(
            "yaml_test", "YAML User", "yaml@example.com", "/path/yaml", "ssh-ed25519 YAML123"
        )

        # Mock yaml module to be available
        mock_yaml = Mock()
        mock_yaml.dump.return_value = "mocked_yaml_output"

        import sys
        original_modules = sys.modules.copy()
        sys.modules['yaml'] = mock_yaml

        try:
            result = profile_manager.export_profiles(format="yaml")
            assert result == "mocked_yaml_output"
            mock_yaml.dump.assert_called_once()
        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_import_profiles_yaml_format_with_pyyaml(self, profile_manager):
        """Test importing profiles from YAML format when PyYAML is available."""
        from unittest.mock import Mock

        yaml_data = '''
        profiles:
          yaml_import:
            name: "YAML Import User"
            email: "yaml@import.com"
            ssh_key_public: "ssh-ed25519 YAMLIMPORT123"
            created_at: "2024-01-01T00:00:00"
        '''

        # Mock yaml module to be available
        mock_yaml = Mock()
        mock_yaml.safe_load.return_value = {
            "profiles": {
                "yaml_import": {
                    "name": "YAML Import User",
                    "email": "yaml@import.com",
                    "ssh_key_public": "ssh-ed25519 YAMLIMPORT123",
                    "created_at": "2024-01-01T00:00:00"
                }
            }
        }

        import sys
        original_modules = sys.modules.copy()
        sys.modules['yaml'] = mock_yaml

        try:
            profile_manager.import_profiles(yaml_data, format="yaml")

            profile = profile_manager.get_profile("yaml_import")
            assert profile is not None
            assert profile["name"] == "YAML Import User"
            assert profile["email"] == "yaml@import.com"
            mock_yaml.safe_load.assert_called_once_with(yaml_data)
        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)

