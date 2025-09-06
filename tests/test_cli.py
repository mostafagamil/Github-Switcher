"""Tests for CLI interface."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from github_switcher.cli import app


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_config_dir():
    """Create temporary config directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_managers():
    """Mock all manager instances."""
    with patch('github_switcher.cli.profile_manager') as mock_profile, \
         patch('github_switcher.cli.ssh_manager') as mock_ssh, \
         patch('github_switcher.cli.git_manager') as mock_git, \
         patch('github_switcher.cli.wizard') as mock_wizard:

        yield {
            'profile': mock_profile,
            'ssh': mock_ssh,
            'git': mock_git,
            'wizard': mock_wizard
        }


class TestInteractiveSelection:
    """Test interactive profile selection functionality."""

    def test_interactive_profile_selection_by_number(self, runner, mock_managers):
        """Test selecting profile by number in interactive mode."""
        # Setup mock profiles
        mock_managers['profile'].list_profiles.return_value = {
            'work': {'email': 'john@company.com'},
            'personal': {'email': 'john@gmail.com'}
        }
        mock_managers['profile'].get_current_profile.return_value = 'work'
        mock_managers['profile'].switch_profile.return_value = True

        # Test switch command with number input
        with patch('github_switcher.cli.Prompt.ask', return_value='2'):
            result = runner.invoke(app, ['switch'])

        assert result.exit_code == 0
        mock_managers['profile'].switch_profile.assert_called_once()

    def test_interactive_profile_selection_by_name(self, runner, mock_managers):
        """Test selecting profile by name in interactive mode."""
        # Setup mock profiles
        mock_managers['profile'].list_profiles.return_value = {
            'work': {'email': 'john@company.com'},
            'personal': {'email': 'john@gmail.com'}
        }
        mock_managers['profile'].get_current_profile.return_value = 'work'
        mock_managers['profile'].switch_profile.return_value = True

        # Test switch command with name input
        with patch('github_switcher.cli.Prompt.ask', return_value='personal'):
            result = runner.invoke(app, ['switch'])

        assert result.exit_code == 0
        mock_managers['profile'].switch_profile.assert_called_once()

    def test_case_insensitive_matching(self, runner, mock_managers):
        """Test case-insensitive profile name matching."""
        # Setup mock profiles
        mock_managers['profile'].list_profiles.return_value = {
            'Work': {'email': 'john@company.com'},
            'Personal': {'email': 'john@gmail.com'}
        }
        mock_managers['profile'].switch_profile.return_value = True

        # Test with lowercase input
        result = runner.invoke(app, ['switch', 'work'])
        assert result.exit_code == 0
        mock_managers['profile'].switch_profile.assert_called_with('Work', mock_managers['git'], mock_managers['ssh'])

        # Test with uppercase input
        result = runner.invoke(app, ['switch', 'PERSONAL'])
        assert result.exit_code == 0

    def test_keyboard_interrupt_handling(self, runner, mock_managers):
        """Test graceful handling of keyboard interrupts."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}

        # Simulate KeyboardInterrupt during interactive selection
        with patch('github_switcher.cli.Prompt.ask', side_effect=KeyboardInterrupt):
            result = runner.invoke(app, ['switch'])

        assert result.exit_code == 1
        assert "Selection cancelled" in result.stdout


class TestVersionCallback:
    """Test version callback functionality."""

    def test_version_display(self, runner):
        """Test --version flag displays version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "GitHub Switcher v" in result.stdout


class TestCreateProfile:
    """Test profile creation command."""

    def test_create_profile_interactive_mode(self, runner, mock_managers):
        """Test interactive profile creation."""
        mock_managers['wizard'].create_profile_interactive.return_value = None

        result = runner.invoke(app, ["create"])
        assert result.exit_code == 0
        assert "Profile created successfully!" in result.stdout
        mock_managers['wizard'].create_profile_interactive.assert_called_once()

    def test_create_profile_quick_mode(self, runner, mock_managers):
        """Test quick profile creation with all parameters."""
        mock_managers['wizard'].create_profile_quick.return_value = None

        result = runner.invoke(app, [
            "create",
            "--name", "test-profile",
            "--fullname", "Test User",
            "--email", "test@example.com"
        ])
        assert result.exit_code == 0
        assert "Profile created successfully!" in result.stdout
        mock_managers['wizard'].create_profile_quick.assert_called_once_with(
            "test-profile", "Test User", "test@example.com", None
        )

    def test_create_profile_with_ssh_key(self, runner, mock_managers):
        """Test profile creation with existing SSH key."""
        mock_managers['wizard'].create_profile_quick.return_value = None

        result = runner.invoke(app, [
            "create",
            "--name", "test-profile",
            "--fullname", "Test User",
            "--email", "test@example.com",
            "--ssh-key", "/path/to/key",
        ])
        assert result.exit_code == 0
        mock_managers['wizard'].create_profile_quick.assert_called_once_with(
            "test-profile", "Test User", "test@example.com", "/path/to/key"
        )

    def test_create_profile_error_handling(self, runner, mock_managers):
        """Test error handling during profile creation."""
        mock_managers['wizard'].create_profile_interactive.side_effect = Exception("Creation failed")

        result = runner.invoke(app, ["create"])
        assert result.exit_code == 1
        assert "Error creating profile: Creation failed" in result.stdout


class TestListProfiles:
    """Test profile listing command."""

    def test_list_profiles_empty(self, runner, mock_managers):
        """Test listing when no profiles exist."""
        mock_managers['profile'].list_profiles.return_value = {}

        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No profiles configured yet." in result.stdout
        assert "Run ghsw create to create your first profile!" in result.stdout

    def test_list_profiles_with_data(self, runner, mock_managers):
        """Test listing existing profiles."""
        profiles = {
            "work": {"name": "Work User", "email": "work@example.com", "last_used": "2024-01-01"},
            "personal": {"name": "Personal User", "email": "personal@example.com", "last_used": "Never"}
        }
        mock_managers['profile'].list_profiles.return_value = profiles
        mock_managers['profile'].get_current_profile.return_value = "work"

        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "work" in result.stdout
        assert "personal" in result.stdout
        assert "Work User" in result.stdout
        assert "Personal User" in result.stdout

    def test_list_profiles_error_handling(self, runner, mock_managers):
        """Test error handling during profile listing."""
        mock_managers['profile'].list_profiles.side_effect = Exception("List failed")

        result = runner.invoke(app, ["list"])
        assert result.exit_code == 1
        assert "Error listing profiles: List failed" in result.stdout


class TestSwitchProfile:
    """Test profile switching command."""

    def test_switch_profile_success(self, runner, mock_managers):
        """Test successful profile switch."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['profile'].switch_profile.return_value = True

        result = runner.invoke(app, ["switch", "work"])
        assert result.exit_code == 0
        assert "Switched to profile 'work'" in result.stdout
        mock_managers['profile'].switch_profile.assert_called_once_with(
            "work", mock_managers['git'], mock_managers['ssh']
        )

    def test_switch_profile_failure(self, runner, mock_managers):
        """Test failed profile switch."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['profile'].switch_profile.return_value = False

        result = runner.invoke(app, ["switch", "work"])
        assert result.exit_code == 1
        assert "Failed to switch to profile 'work'" in result.stdout

    def test_switch_profile_error_handling(self, runner, mock_managers):
        """Test error handling during profile switch."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['profile'].switch_profile.side_effect = Exception("Switch failed")

        result = runner.invoke(app, ["switch", "work"])
        assert result.exit_code == 1
        assert "Error switching profile: Switch failed" in result.stdout


class TestCurrentProfile:
    """Test current profile command."""

    def test_current_profile_exists(self, runner, mock_managers):
        """Test showing current profile when one exists."""
        mock_managers['profile'].get_current_profile.return_value = "work"
        mock_managers['profile'].get_profile.return_value = {
            "name": "Work User",
            "email": "work@example.com"
        }

        result = runner.invoke(app, ["current"])
        assert result.exit_code == 0
        assert "Current profile: work" in result.stdout
        assert "Name: Work User" in result.stdout
        assert "Email: work@example.com" in result.stdout

    def test_current_profile_none(self, runner, mock_managers):
        """Test showing current profile when none is active."""
        mock_managers['profile'].get_current_profile.return_value = None

        result = runner.invoke(app, ["current"])
        assert result.exit_code == 0
        assert "No active profile set" in result.stdout

    def test_current_profile_error_handling(self, runner, mock_managers):
        """Test error handling when getting current profile."""
        mock_managers['profile'].get_current_profile.side_effect = Exception("Get failed")

        result = runner.invoke(app, ["current"])
        assert result.exit_code == 1
        assert "Error getting current profile: Get failed" in result.stdout


class TestDeleteProfile:
    """Test profile deletion command."""

    def test_delete_profile_with_confirmation(self, runner, mock_managers):
        """Test profile deletion with confirmation."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['profile'].delete_profile.return_value = True

        result = runner.invoke(app, ["delete", "work"], input="y\n")
        assert result.exit_code == 0
        assert "Profile 'work' deleted successfully" in result.stdout
        mock_managers['profile'].delete_profile.assert_called_once_with("work", mock_managers['ssh'])

    def test_delete_profile_skip_confirmation(self, runner, mock_managers):
        """Test profile deletion with --yes flag."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['profile'].delete_profile.return_value = True

        result = runner.invoke(app, ["delete", "work", "--yes"])
        assert result.exit_code == 0
        assert "Profile 'work' deleted successfully" in result.stdout

    def test_delete_profile_cancelled(self, runner, mock_managers):
        """Test profile deletion cancelled by user."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        result = runner.invoke(app, ["delete", "work"], input="n\n")
        assert result.exit_code == 0
        assert "Deletion cancelled" in result.stdout

    def test_delete_profile_failure(self, runner, mock_managers):
        """Test failed profile deletion."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['profile'].delete_profile.return_value = False

        result = runner.invoke(app, ["delete", "work", "--yes"])
        assert result.exit_code == 1
        assert "Failed to delete profile 'work'" in result.stdout

    def test_delete_profile_error_handling(self, runner, mock_managers):
        """Test error handling during profile deletion."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['profile'].delete_profile.side_effect = Exception("Delete failed")

        result = runner.invoke(app, ["delete", "work", "--yes"])
        assert result.exit_code == 1
        assert "Error deleting profile: Delete failed" in result.stdout


class TestCopySSHKey:
    """Test SSH key copying command."""

    def test_copy_ssh_key_success(self, runner, mock_managers):
        """Test successful SSH key copy."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['ssh'].copy_public_key_to_clipboard.return_value = True

        result = runner.invoke(app, ["copy-key", "work"])
        assert result.exit_code == 0
        assert "SSH key for 'work' copied to clipboard!" in result.stdout
        assert "Add this key to GitHub:" in result.stdout

    def test_copy_ssh_key_failure(self, runner, mock_managers):
        """Test failed SSH key copy."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['ssh'].copy_public_key_to_clipboard.return_value = False

        result = runner.invoke(app, ["copy-key", "work"])
        assert result.exit_code == 1
        assert "Failed to copy SSH key for 'work'" in result.stdout

    def test_copy_ssh_key_error_handling(self, runner, mock_managers):
        """Test error handling during SSH key copy."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['ssh'].copy_public_key_to_clipboard.side_effect = Exception("Copy failed")

        result = runner.invoke(app, ["copy-key", "work"])
        assert result.exit_code == 1
        assert "Error copying SSH key: Copy failed" in result.stdout


class TestSSHConnection:
    """Test SSH connection testing command."""

    def test_test_ssh_connection_success(self, runner, mock_managers):
        """Test successful SSH connection test."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['ssh'].test_connection.return_value = True

        result = runner.invoke(app, ["test", "work"])
        assert result.exit_code == 0
        assert "SSH connection successful for 'work'" in result.stdout

    def test_test_ssh_connection_failure(self, runner, mock_managers):
        """Test failed SSH connection test."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['ssh'].test_connection.return_value = False

        result = runner.invoke(app, ["test", "work"])
        assert result.exit_code == 1
        assert "SSH connection failed for 'work'" in result.stdout
        assert "Make sure you've added the SSH key" in result.stdout

    def test_test_ssh_connection_error_handling(self, runner, mock_managers):
        """Test error handling during SSH connection test."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['ssh'].test_connection.side_effect = Exception("Test failed")

        result = runner.invoke(app, ["test", "work"])
        assert result.exit_code == 1
        assert "Error testing SSH connection: Test failed" in result.stdout




class TestRegenerateSSHKey:
    """Test SSH key regeneration command."""

    def test_regenerate_ssh_key_success(self, runner, mock_managers):
        """Test successful SSH key regeneration."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['profile'].profile_exists.return_value = True
        mock_managers['profile'].get_profile.return_value = {"email": "work@example.com"}
        mock_managers['ssh'].regenerate_ssh_key.return_value = ("/path/key", "ssh-ed25519 ABC...")
        mock_managers['ssh'].copy_public_key_to_clipboard.return_value = True

        result = runner.invoke(app, ["regenerate-key", "work"], input="y\n")
        assert result.exit_code == 0
        assert "SSH key regenerated for 'work'" in result.stdout
        assert "New public key copied to clipboard!" in result.stdout

    def test_regenerate_ssh_key_profile_not_found(self, runner, mock_managers):
        """Test regenerating key for non-existent profile."""
        mock_managers['profile'].list_profiles.return_value = {}  # Empty profiles list
        mock_managers['profile'].profile_exists.return_value = False

        result = runner.invoke(app, ["regenerate-key", "work"])
        assert result.exit_code == 1
        assert "Profile 'work' not found" in result.stdout

    def test_regenerate_ssh_key_cancelled(self, runner, mock_managers):
        """Test SSH key regeneration cancelled by user."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['profile'].profile_exists.return_value = True
        mock_managers['profile'].get_profile.return_value = {"email": "work@example.com"}

        result = runner.invoke(app, ["regenerate-key", "work"], input="n\n")
        assert result.exit_code == 0
        assert "Key regeneration cancelled" in result.stdout

    def test_regenerate_ssh_key_profile_data_not_found(self, runner, mock_managers):
        """Test SSH key regeneration when profile data is None."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['profile'].profile_exists.return_value = True
        mock_managers['profile'].get_profile.return_value = None  # Profile data not found

        result = runner.invoke(app, ["regenerate-key", "work"])
        assert result.exit_code == 1
        assert "Profile 'work' data not found" in result.stdout

    def test_regenerate_ssh_key_error_handling(self, runner, mock_managers):
        """Test error handling during SSH key regeneration."""
        mock_managers['profile'].list_profiles.return_value = {'work': {'email': 'john@company.com'}}
        mock_managers['profile'].profile_exists.return_value = True
        mock_managers['profile'].get_profile.side_effect = Exception("Get failed")

        result = runner.invoke(app, ["regenerate-key", "work"])
        assert result.exit_code == 1
        assert "Error regenerating SSH key: Get failed" in result.stdout


class TestDetectExistingSetup:
    """Test existing SSH setup detection command."""

    def test_detect_existing_setup_with_github_config(self, runner, mock_managers):
        """Test detection when GitHub SSH config exists."""
        existing_setup = {
            "has_github_host": True,
            "github_keys": ["id_rsa", "id_ed25519"],
            "all_keys": [
                {
                    "name": "id_rsa",
                    "type": "ssh-rsa",
                    "comment": "user@example.com",
                    "has_github_indicators": True,
                    "likely_github": True,
                    "github_compatible": True
                },
                {
                    "name": "id_ed25519",
                    "type": "ssh-ed25519",
                    "comment": "user@example.com",
                    "has_github_indicators": False,
                    "likely_github": True,
                    "github_compatible": True
                }
            ],
            "config_entries": ["github.com", "github-work"],
            "github_connectivity": True,
            "default_key_works": False,
            "recommendations": ["✅ GitHub SSH access is configured and working"]
        }
        mock_managers['ssh'].detect_existing_github_setup.return_value = existing_setup

        result = runner.invoke(app, ["detect"])
        assert result.exit_code == 0
        assert "WORKING" in result.stdout
        assert "SSH Keys Found" in result.stdout

    def test_detect_existing_setup_no_github_config(self, runner, mock_managers):
        """Test detection when no GitHub SSH config exists."""
        existing_setup = {
            "has_github_host": False,
            "github_keys": [],
            "all_keys": [],
            "config_entries": [],
            "github_connectivity": False,
            "default_key_works": False,
            "recommendations": ["🖕 No SSH keys detected - GitHub Switcher can generate new ones"]
        }
        mock_managers['ssh'].detect_existing_github_setup.return_value = existing_setup

        result = runner.invoke(app, ["detect"])
        assert result.exit_code == 0
        assert "NOT WORKING" in result.stdout
        assert "No SSH keys found" in result.stdout

    def test_detect_existing_setup_error_handling(self, runner, mock_managers):
        """Test error handling during setup detection."""
        mock_managers['ssh'].detect_existing_github_setup.side_effect = Exception("Detect failed")

        result = runner.invoke(app, ["detect"])
        assert result.exit_code == 1
        assert "Error detecting existing setup: Detect failed" in result.stdout


class TestMainCallback:
    """Test main callback function."""

    def test_main_callback(self, runner):
        """Test main callback with no arguments."""
        result = runner.invoke(app, [])
        # CLI shows help when no subcommand is provided
        assert result.exit_code == 0

    def test_main_entry_point(self):
        """Test main entry point execution (line 392)."""
        import os

        # Run the CLI module directly to trigger the if __name__ == '__main__' block
        import pathlib
        import subprocess
        import sys
        project_root = pathlib.Path(__file__).parent.parent
        src_path = project_root / 'src'

        env = os.environ.copy()
        env['PYTHONPATH'] = str(src_path)

        # Use --help to avoid interactive prompts and ensure clean execution
        result = subprocess.run(
            [sys.executable, '-m', 'github_switcher.cli', '--help'],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            env=env,
            timeout=10  # Add timeout to prevent hanging
        )

        # Should exit with 0 and show help text
        assert result.returncode == 0
        assert "GitHub profile switcher" in result.stdout.lower() or "usage" in result.stdout.lower()
