"""Tests for interactive wizard for profile creation."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import typer

from github_switcher.git_manager import GitManager
from github_switcher.profiles import ProfileManager
from github_switcher.ssh_manager import SSHManager
from github_switcher.wizard import ProfileWizard


@pytest.fixture
def mock_managers():
    """Create mock managers."""
    profile_manager = Mock(spec=ProfileManager)
    ssh_manager = Mock(spec=SSHManager)
    git_manager = Mock(spec=GitManager)

    # Default setup for ssh_manager with new structure
    ssh_manager.ssh_dir = Path("/mock/.ssh")
    ssh_manager.detect_existing_github_setup.return_value = {
        "github_connectivity": False,
        "default_key_works": False,
        "all_keys": [],
        "config_entries": []
    }

    return {
        'profile': profile_manager,
        'ssh': ssh_manager,
        'git': git_manager
    }


@pytest.fixture
def wizard(mock_managers):
    """Create ProfileWizard with mock managers."""
    return ProfileWizard(
        mock_managers['profile'],
        mock_managers['ssh'],
        mock_managers['git']
    )


@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestProfileWizardInit:
    """Test ProfileWizard initialization."""

    def test_init(self, mock_managers):
        """Test wizard initialization."""
        wizard = ProfileWizard(
            mock_managers['profile'],
            mock_managers['ssh'],
            mock_managers['git']
        )

        assert wizard.profile_manager == mock_managers['profile']
        assert wizard.ssh_manager == mock_managers['ssh']
        assert wizard.git_manager == mock_managers['git']
        assert wizard.console is not None


class TestSSHDetectionAndDuplicatePrevention:
    """Test SSH detection and duplicate prevention functionality."""

    def test_ssh_detection_with_existing_keys(self, wizard, mock_managers):
        """Test SSH detection shows existing keys with profile associations."""
        # Setup SSH detection with existing keys
        mock_managers['ssh'].detect_existing_github_setup.return_value = {
            "github_connectivity": True,
            "default_key_works": True,
            "all_keys": [
                {
                    "name": "id_ed25519_work",
                    "comment": "john@company.com",
                    "type": "Ed25519",
                    "github_compatible": True,
                    "public_content": "ssh-ed25519 AAAAC3...work-key... john@company.com"
                },
                {
                    "name": "id_ed25519_personal",
                    "comment": "john@gmail.com",
                    "type": "Ed25519",
                    "github_compatible": True,
                    "public_content": "ssh-ed25519 AAAAC3...personal-key... john@gmail.com"
                }
            ],
            "config_entries": ["github-work", "github-personal"]
        }

        # Setup existing profiles
        mock_managers['profile'].list_profiles.return_value = {
            'work': {'ssh_key_public': 'ssh-ed25519 AAAAC3...work-key... john@company.com'}
        }

        # Test that profile associations are added to keys
        setup_data = mock_managers['ssh'].detect_existing_github_setup.return_value
        wizard._add_profile_associations_to_keys(setup_data)

        # Verify that keys have profile associations added
        assert setup_data["all_keys"][0].get("used_by_profile") == "work"

    def test_duplicate_prevention_in_key_selection(self, wizard, mock_managers):
        """Test that already-imported keys are filtered out of selection."""
        # Setup existing keys with one already used by a profile
        existing_setup = {
            "all_keys": [
                {"name": "id_ed25519_work", "used_by_profile": "work"},  # Already used
                {"name": "id_ed25519_unused"}  # Available for import
            ]
        }

        mock_managers['profile'].list_profiles.return_value = {
            'work': {'ssh_key_public': 'ssh-ed25519 AAAAC3...work-key... john@company.com'}
        }

        # Mock the interactive selection to return None (no selection made)
        with patch('github_switcher.wizard.Prompt.ask', return_value='1'):
            result = wizard._select_key_to_import(existing_setup)

        # Should only show unused keys
        assert result is None or result["name"] == "id_ed25519_unused"

    def test_no_import_option_when_all_keys_used(self, wizard, mock_managers):
        """Test that import option is hidden when all SSH keys are used by profiles."""
        # Setup detection where all keys are used by profiles
        existing_setup = {
            "all_keys": [
                {"name": "id_ed25519_work", "used_by_profile": "work"},
                {"name": "id_ed25519_personal", "used_by_profile": "personal"}
            ],
            "github_connectivity": True
        }

        # Test SSH strategy selection should return "new" when no keys available
        strategy = wizard._choose_ssh_strategy(existing_setup)
        assert strategy == "new"


class TestCreateProfileInteractive:
    """Test interactive profile creation."""

    @patch('github_switcher.wizard.Confirm.ask')
    @patch('github_switcher.wizard.Prompt.ask')
    def test_create_profile_interactive_success(self, mock_prompt, mock_confirm, wizard, mock_managers):
        """Test successful interactive profile creation."""
        # Mock user inputs
        mock_prompt.side_effect = ["work", "Work User", "work@example.com"]
        mock_confirm.return_value = True

        # Mock managers
        mock_managers['profile'].profile_exists.return_value = False
        mock_managers['ssh'].generate_ssh_key.return_value = ("/path/key", "ssh-ed25519 ABC...")
        mock_managers['ssh'].copy_public_key_to_clipboard.return_value = True

        wizard.create_profile_interactive()

        # Verify profile creation was called
        mock_managers['profile'].create_profile.assert_called_once_with(
            "work", "Work User", "work@example.com", "/path/key", "ssh-ed25519 ABC..."
        )
        mock_managers['ssh'].generate_ssh_key.assert_called_once_with("work", "work@example.com")

    @patch('github_switcher.wizard.Confirm.ask')
    @patch('github_switcher.wizard.Prompt.ask')
    def test_create_profile_interactive_cancelled(self, mock_prompt, mock_confirm, wizard, mock_managers):
        """Test cancelled interactive profile creation."""
        # Mock user inputs
        mock_prompt.side_effect = ["work", "Work User", "work@example.com"]
        mock_confirm.return_value = False  # User cancels

        mock_managers['profile'].profile_exists.return_value = False

        wizard.create_profile_interactive()

        # Verify no profile was created
        mock_managers['profile'].create_profile.assert_not_called()

    @patch('github_switcher.wizard.Confirm.ask')
    @patch('github_switcher.wizard.Prompt.ask')
    def test_create_profile_interactive_existing_profile(self, mock_prompt, mock_confirm, wizard, mock_managers):
        """Test interactive creation with existing profile name."""
        # Mock user inputs - first name exists, second doesn't
        mock_prompt.side_effect = [
            "existing",  # First attempt - exists
            "new-profile",  # Second attempt - doesn't exist
            "New User", "new@example.com"
        ]
        mock_confirm.return_value = True

        # Mock profile existence check
        mock_managers['profile'].profile_exists.side_effect = [True, False]
        mock_managers['ssh'].generate_ssh_key.return_value = ("/path/key", "ssh-ed25519 ABC...")
        mock_managers['ssh'].copy_public_key_to_clipboard.return_value = True

        wizard.create_profile_interactive()

        # Verify profile was created with second name
        mock_managers['profile'].create_profile.assert_called_once_with(
            "new-profile", "New User", "new@example.com", "/path/key", "ssh-ed25519 ABC..."
        )

    @patch('github_switcher.wizard.Confirm.ask')
    @patch('github_switcher.wizard.Prompt.ask')
    def test_create_profile_interactive_invalid_inputs(self, mock_prompt, mock_confirm, wizard, mock_managers):
        """Test interactive creation with invalid inputs."""
        # Mock user inputs with invalid values first
        mock_prompt.side_effect = [
            "",  # Empty profile name
            "valid-name",  # Valid profile name
            "A",  # Too short full name
            "Valid User",  # Valid full name
            "invalid-email",  # Invalid email
            "valid@example.com"  # Valid email
        ]
        mock_confirm.return_value = True

        mock_managers['profile'].profile_exists.return_value = False
        mock_managers['ssh'].generate_ssh_key.return_value = ("/path/key", "ssh-ed25519 ABC...")
        mock_managers['ssh'].copy_public_key_to_clipboard.return_value = True

        wizard.create_profile_interactive()

        mock_managers['profile'].create_profile.assert_called_once_with(
            "valid-name", "Valid User", "valid@example.com", "/path/key", "ssh-ed25519 ABC..."
        )


class TestCreateProfileQuick:
    """Test quick profile creation."""

    def test_create_profile_quick_success(self, wizard, mock_managers):
        """Test successful quick profile creation."""
        mock_managers['profile'].profile_exists.return_value = False
        mock_managers['ssh'].generate_ssh_key.return_value = ("/path/key", "ssh-ed25519 ABC...")
        mock_managers['ssh'].copy_public_key_to_clipboard.return_value = True

        wizard.create_profile_quick("work", "Work User", "work@example.com")

        mock_managers['profile'].create_profile.assert_called_once_with(
            "work", "Work User", "work@example.com", "/path/key", "ssh-ed25519 ABC..."
        )

    def test_create_profile_quick_with_ssh_key(self, wizard, mock_managers):
        """Test quick profile creation with existing SSH key."""
        mock_managers['profile'].profile_exists.return_value = False
        mock_managers['ssh'].import_existing_key.return_value = ("/imported/key", "ssh-ed25519 IMPORTED...")
        mock_managers['ssh'].copy_public_key_to_clipboard.return_value = True

        wizard.create_profile_quick("work", "Work User", "work@example.com", "/path/to/existing/key")

        mock_managers['ssh'].import_existing_key.assert_called_once_with(
            "work", "/path/to/existing/key", "work@example.com"
        )
        mock_managers['profile'].create_profile.assert_called_once_with(
            "work", "Work User", "work@example.com", "/imported/key", "ssh-ed25519 IMPORTED..."
        )

    def test_create_profile_quick_invalid_name(self, wizard, mock_managers):
        """Test quick creation with invalid profile name."""
        with pytest.raises(typer.BadParameter, match="Profile name must contain only letters"):
            wizard.create_profile_quick("invalid name!", "Work User", "work@example.com")

    def test_create_profile_quick_invalid_email(self, wizard, mock_managers):
        """Test quick creation with invalid email."""
        mock_managers['profile'].profile_exists.return_value = False

        with pytest.raises(typer.BadParameter, match="Invalid email format"):
            wizard.create_profile_quick("work", "Work User", "invalid-email")

    def test_create_profile_quick_existing_profile(self, wizard, mock_managers):
        """Test quick creation with existing profile."""
        mock_managers['profile'].profile_exists.return_value = True

        with pytest.raises(typer.BadParameter, match="Profile 'work' already exists"):
            wizard.create_profile_quick("work", "Work User", "work@example.com")


class TestCreateProfileWithExistingKey:
    """Test profile creation with existing SSH key."""

    def test_create_profile_with_existing_key_success(self, wizard, mock_managers):
        """Test successful creation with existing key."""
        mock_managers['ssh'].import_existing_key.return_value = ("/path/key", "ssh-ed25519 ABC...")
        mock_managers['ssh'].copy_public_key_to_clipboard.return_value = True

        wizard._create_profile_with_existing_key("work", "Work User", "work@example.com", "/existing/key")

        mock_managers['ssh'].import_existing_key.assert_called_once_with(
            "work", "/existing/key", "work@example.com"
        )
        mock_managers['profile'].create_profile.assert_called_once_with(
            "work", "Work User", "work@example.com", "/path/key", "ssh-ed25519 ABC..."
        )

    def test_create_profile_with_existing_key_error(self, wizard, mock_managers):
        """Test creation with existing key error."""
        mock_managers['ssh'].import_existing_key.side_effect = Exception("Import failed")

        with pytest.raises(typer.Exit):
            wizard._create_profile_with_existing_key("work", "Work User", "work@example.com", "/existing/key")


class TestValidateProfileName:
    """Test profile name validation."""

    def test_validate_profile_name_valid(self, wizard):
        """Test valid profile names."""
        valid_names = ["work", "personal", "work-profile", "profile_1", "Profile123", "my-work"]
        for name in valid_names:
            assert wizard._validate_profile_name(name) is True

    def test_validate_profile_name_invalid(self, wizard):
        """Test invalid profile names."""
        invalid_names = ["", "work profile", "work@profile", "profile!", "work.profile", "profile/name"]
        for name in invalid_names:
            assert wizard._validate_profile_name(name) is False


class TestValidateEmail:
    """Test email validation."""

    def test_validate_email_valid(self, wizard):
        """Test valid email addresses."""
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "user+tag@example.org",
            "user123@test-domain.com"
        ]
        for email in valid_emails:
            assert wizard._validate_email(email) is True

    def test_validate_email_invalid(self, wizard):
        """Test invalid email addresses."""
        invalid_emails = [
            "",
            "invalid",
            "@example.com",
            "user@",
            "user@.com",
            "user@example",
            "user space@example.com"
        ]
        for email in invalid_emails:
            assert wizard._validate_email(email) is False


class TestShowWelcomeMessage:
    """Test welcome message display."""

    def test_show_welcome_message(self, wizard):
        """Test welcome message is displayed."""
        # This mainly tests that no exceptions are raised
        wizard._show_welcome_message()
        # If we get here without exception, the method worked


class TestGetProfileName:
    """Test profile name input."""

    @patch('github_switcher.wizard.Prompt.ask')
    def test_get_profile_name_valid(self, mock_prompt, wizard, mock_managers):
        """Test getting valid profile name."""
        mock_prompt.return_value = "valid-profile"
        mock_managers['profile'].profile_exists.return_value = False

        result = wizard._get_profile_name()
        assert result == "valid-profile"

    @patch('github_switcher.wizard.Prompt.ask')
    def test_get_profile_name_empty_then_valid(self, mock_prompt, wizard, mock_managers):
        """Test getting profile name with empty input first."""
        mock_prompt.side_effect = ["", "valid-profile"]
        mock_managers['profile'].profile_exists.return_value = False

        result = wizard._get_profile_name()
        assert result == "valid-profile"
        assert mock_prompt.call_count == 2

    @patch('github_switcher.wizard.Prompt.ask')
    def test_get_profile_name_invalid_then_valid(self, mock_prompt, wizard, mock_managers):
        """Test getting profile name with invalid input first."""
        mock_prompt.side_effect = ["invalid name!", "valid-profile"]
        mock_managers['profile'].profile_exists.return_value = False

        result = wizard._get_profile_name()
        assert result == "valid-profile"


class TestGetFullname:
    """Test full name input."""

    @patch('github_switcher.wizard.Prompt.ask')
    def test_get_fullname_valid(self, mock_prompt, wizard):
        """Test getting valid full name."""
        mock_prompt.return_value = "Valid User"

        result = wizard._get_fullname()
        assert result == "Valid User"

    @patch('github_switcher.wizard.Prompt.ask')
    def test_get_fullname_empty_then_valid(self, mock_prompt, wizard):
        """Test getting full name with empty input first."""
        mock_prompt.side_effect = ["", "Valid User"]

        result = wizard._get_fullname()
        assert result == "Valid User"

    @patch('github_switcher.wizard.Prompt.ask')
    def test_get_fullname_too_short_then_valid(self, mock_prompt, wizard):
        """Test getting full name with too short input first."""
        mock_prompt.side_effect = ["A", "Valid User"]

        result = wizard._get_fullname()
        assert result == "Valid User"


class TestGetEmail:
    """Test email input."""

    @patch('github_switcher.wizard.Prompt.ask')
    def test_get_email_valid(self, mock_prompt, wizard):
        """Test getting valid email."""
        mock_prompt.return_value = "USER@EXAMPLE.COM"

        result = wizard._get_email()
        assert result == "user@example.com"  # Should be lowercased

    @patch('github_switcher.wizard.Prompt.ask')
    def test_get_email_empty_then_valid(self, mock_prompt, wizard):
        """Test getting email with empty input first."""
        mock_prompt.side_effect = ["", "user@example.com"]

        result = wizard._get_email()
        assert result == "user@example.com"

    @patch('github_switcher.wizard.Prompt.ask')
    def test_get_email_invalid_then_valid(self, mock_prompt, wizard):
        """Test getting email with invalid input first."""
        mock_prompt.side_effect = ["invalid", "user@example.com"]

        result = wizard._get_email()
        assert result == "user@example.com"


class TestShowSummaryAndConfirm:
    """Test summary display and confirmation."""

    @patch('github_switcher.wizard.Confirm.ask')
    def test_show_summary_and_confirm_yes(self, mock_confirm, wizard):
        """Test summary with user confirmation."""
        mock_confirm.return_value = True

        result = wizard._show_summary_and_confirm("work", "Work User", "work@example.com")
        assert result is True

    @patch('github_switcher.wizard.Confirm.ask')
    def test_show_summary_and_confirm_no(self, mock_confirm, wizard):
        """Test summary with user rejection."""
        mock_confirm.return_value = False

        result = wizard._show_summary_and_confirm("work", "Work User", "work@example.com")
        assert result is False


class TestHandleSSHKeyCreation:
    """Test SSH key creation handling."""

    def test_handle_ssh_key_creation_no_existing(self, wizard, mock_managers):
        """Test SSH key creation with no existing setup."""
        existing_setup = {"has_github_host": False, "github_keys": []}
        mock_managers['ssh'].generate_ssh_key.return_value = ("/path/key", "ssh-ed25519 ABC...")

        result = wizard._handle_ssh_key_creation("work", "work@example.com", existing_setup)

        assert result == ("/path/key", "ssh-ed25519 ABC...")
        mock_managers['ssh'].generate_ssh_key.assert_called_once_with("work", "work@example.com")

    @patch('github_switcher.wizard.Prompt.ask')
    def test_handle_ssh_key_creation_existing_new_choice(self, mock_prompt, wizard, mock_managers):
        """Test SSH key creation with existing setup, choosing new key."""
        existing_setup = {"has_github_host": True, "github_keys": ["id_rsa"]}
        mock_prompt.return_value = "new"
        mock_managers['ssh'].generate_ssh_key.return_value = ("/path/key", "ssh-ed25519 ABC...")

        result = wizard._handle_ssh_key_creation("work", "work@example.com", existing_setup)

        assert result == ("/path/key", "ssh-ed25519 ABC...")
        mock_managers['ssh'].generate_ssh_key.assert_called_once_with("work", "work@example.com")

    @patch('github_switcher.wizard.Prompt.ask')
    def test_handle_ssh_key_creation_existing_skip_choice(self, mock_prompt, wizard, mock_managers):
        """Test SSH key creation with existing setup, choosing skip."""
        existing_setup = {"has_github_host": True, "github_keys": ["id_rsa"]}
        mock_prompt.return_value = "skip"

        result = wizard._handle_ssh_key_creation("work", "work@example.com", existing_setup)

        expected_key = "~/.ssh/id_ed25519_work"
        expected_pub = "# SSH key will be set up manually"
        assert result == (expected_key, expected_pub)

    @patch('github_switcher.wizard.Prompt.ask')
    def test_handle_ssh_key_creation_existing_import_choice(self, mock_prompt, wizard, mock_managers):
        """Test SSH key creation with existing setup, choosing import."""
        existing_setup = {"has_github_host": True, "github_keys": ["id_rsa"]}
        mock_prompt.return_value = "import"

        with patch.object(wizard, '_import_existing_ssh_key') as mock_import:
            mock_import.return_value = ("/imported/key", "ssh-ed25519 IMPORTED...")

            result = wizard._handle_ssh_key_creation("work", "work@example.com", existing_setup)

            assert result == ("/imported/key", "ssh-ed25519 IMPORTED...")
            mock_import.assert_called_once_with("work", "work@example.com", existing_setup)


class TestImportExistingSSHKey:
    """Test existing SSH key import."""

    @patch('github_switcher.wizard.Prompt.ask')
    def test_import_existing_ssh_key_success(self, mock_prompt, wizard, mock_managers, temp_dir):
        """Test successful SSH key import."""
        # Create mock keys
        key1 = temp_dir / "id_rsa"
        key2 = temp_dir / "id_ed25519"
        key1.write_text("private key 1")
        key2.write_text("private key 2")

        mock_managers['ssh'].ssh_dir = temp_dir
        mock_prompt.return_value = "1"  # Select first key
        mock_managers['ssh'].import_existing_key.return_value = ("/imported/key", "ssh-ed25519 IMPORTED...")

        result = wizard._import_existing_ssh_key("work", "work@example.com", {})

        assert result == ("/imported/key", "ssh-ed25519 IMPORTED...")
        mock_managers['ssh'].import_existing_key.assert_called_once_with(
            "work", str(key2), "work@example.com"
        )

    @patch('github_switcher.wizard.Prompt.ask')
    def test_import_existing_ssh_key_no_keys(self, mock_prompt, wizard, mock_managers, temp_dir):
        """Test SSH key import with no available keys."""
        mock_managers['ssh'].ssh_dir = temp_dir
        mock_managers['ssh'].generate_ssh_key.return_value = ("/path/key", "ssh-ed25519 ABC...")

        result = wizard._import_existing_ssh_key("work", "work@example.com", {})

        # Should fall back to generating new key
        assert result == ("/path/key", "ssh-ed25519 ABC...")
        mock_managers['ssh'].generate_ssh_key.assert_called_once_with("work", "work@example.com")

    @patch('github_switcher.wizard.Prompt.ask')
    def test_import_existing_ssh_key_choose_new(self, mock_prompt, wizard, mock_managers, temp_dir):
        """Test SSH key import choosing to generate new."""
        # Create mock key
        key1 = temp_dir / "id_rsa"
        key1.write_text("private key")

        mock_managers['ssh'].ssh_dir = temp_dir
        mock_prompt.return_value = "new"  # Choose to generate new
        mock_managers['ssh'].generate_ssh_key.return_value = ("/path/key", "ssh-ed25519 ABC...")

        result = wizard._import_existing_ssh_key("work", "work@example.com", {})

        assert result == ("/path/key", "ssh-ed25519 ABC...")
        mock_managers['ssh'].generate_ssh_key.assert_called_once_with("work", "work@example.com")

    @patch('github_switcher.wizard.Prompt.ask')
    def test_import_existing_ssh_key_invalid_selection(self, mock_prompt, wizard, mock_managers, temp_dir):
        """Test SSH key import with invalid selection."""
        # Create mock key
        key1 = temp_dir / "id_rsa"
        key1.write_text("private key")

        mock_managers['ssh'].ssh_dir = temp_dir
        mock_prompt.return_value = "99"  # Invalid selection
        mock_managers['ssh'].generate_ssh_key.return_value = ("/path/key", "ssh-ed25519 ABC...")

        result = wizard._import_existing_ssh_key("work", "work@example.com", {})

        # Should fall back to generating new key
        assert result == ("/path/key", "ssh-ed25519 ABC...")
        mock_managers['ssh'].generate_ssh_key.assert_called_once_with("work", "work@example.com")


class TestCreateProfileInternal:
    """Test internal profile creation."""

    def test_create_profile_internal_success(self, wizard, mock_managers):
        """Test successful internal profile creation."""
        existing_setup = {"has_github_host": False, "github_keys": []}
        mock_managers['ssh'].detect_existing_github_setup.return_value = existing_setup
        mock_managers['ssh'].generate_ssh_key.return_value = ("/path/key", "ssh-ed25519 ABC...")
        mock_managers['ssh'].copy_public_key_to_clipboard.return_value = True

        wizard._create_profile_internal("work", "Work User", "work@example.com")

        mock_managers['profile'].create_profile.assert_called_once_with(
            "work", "Work User", "work@example.com", "/path/key", "ssh-ed25519 ABC..."
        )

    def test_create_profile_internal_error(self, wizard, mock_managers):
        """Test internal profile creation with error."""
        mock_managers['ssh'].detect_existing_github_setup.side_effect = Exception("Setup failed")

        with pytest.raises(typer.Exit):
            wizard._create_profile_internal("work", "Work User", "work@example.com")


class TestShowExistingSetupDetected:
    """Test existing setup detection display."""

    def test_show_existing_setup_detected(self, wizard):
        """Test existing setup detection display."""
        existing_setup = {
            "has_github_host": True,
            "github_keys": ["id_rsa", "id_ed25519"],
            "config_entries": ["github.com"]
        }

        # This mainly tests that no exceptions are raised
        wizard._show_existing_setup_detected(existing_setup)


class TestShowSuccessMessage:
    """Test success message display."""

    def test_show_success_message(self, wizard):
        """Test success message is displayed."""
        # This mainly tests that no exceptions are raised
        wizard._show_success_message("work")


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @patch('github_switcher.wizard.Prompt.ask')
    def test_get_profile_name_whitespace_handling(self, mock_prompt, wizard, mock_managers):
        """Test profile name input with whitespace."""
        mock_prompt.return_value = "  work  "  # Extra whitespace
        mock_managers['profile'].profile_exists.return_value = False

        result = wizard._get_profile_name()
        assert result == "work"  # Should be stripped

    @patch('github_switcher.wizard.Prompt.ask')
    def test_get_email_case_handling(self, mock_prompt, wizard):
        """Test email input case handling."""
        mock_prompt.return_value = "  USER@EXAMPLE.COM  "

        result = wizard._get_email()
        assert result == "user@example.com"  # Should be lowercased and stripped

    @patch('github_switcher.wizard.Prompt.ask')
    def test_get_fullname_whitespace_handling(self, mock_prompt, wizard):
        """Test full name input with whitespace."""
        mock_prompt.return_value = "  Work User  "

        result = wizard._get_fullname()
        assert result == "Work User"  # Should be stripped

    def test_validate_profile_name_edge_cases(self, wizard):
        """Test profile name validation edge cases."""
        assert wizard._validate_profile_name("a") is True  # Single character
        assert wizard._validate_profile_name("123") is True  # Only numbers
        assert wizard._validate_profile_name("_") is True  # Only underscore
        assert wizard._validate_profile_name("-") is True  # Only hyphen

    def test_validate_email_edge_cases(self, wizard):
        """Test email validation edge cases."""
        assert wizard._validate_email("a@b.co") is True  # Minimal valid email
        assert wizard._validate_email("user@domain.museum") is True  # Long TLD
        assert wizard._validate_email("user@sub.domain.com") is True  # Subdomain
