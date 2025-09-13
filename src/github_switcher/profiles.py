"""Profile management functionality."""

from typing import Any

from .config import Config


class ProfileManager:
    """Manages GitHub profiles and their operations."""

    def __init__(self) -> None:
        """Initialize profile manager."""
        self.config = Config()

    def list_profiles(self) -> dict[str, dict[str, Any]]:
        """Get all configured profiles."""
        return self.config.get_all_profiles()

    def get_profile(self, name: str) -> dict[str, Any] | None:
        """Get a specific profile by name."""
        return self.config.get_profile(name)

    def get_current_profile(self) -> str | None:
        """Get the currently active profile name."""
        return self.config.get_active_profile()

    def profile_exists(self, name: str) -> bool:
        """Check if a profile exists."""
        return self.config.get_profile(name) is not None

    def create_profile(
        self,
        name: str,
        fullname: str,
        email: str,
        ssh_key_path: str,
        ssh_public_key: str,
        ssh_key_fingerprint: str | None = None,
        ssh_key_passphrase_protected: bool = False,
        ssh_key_source: str = "generated",
        ssh_key_type: str = "ed25519",
    ) -> None:
        """Create a new profile with enhanced SSH metadata."""
        if not self._validate_profile_name(name):
            raise ValueError(
                "Profile name must contain only letters, numbers, hyphens, and underscores"
            )

        if not self._validate_email(email):
            raise ValueError("Invalid email format")

        self.config.add_profile(
            name=name,
            fullname=fullname,
            email=email,
            ssh_key_path=ssh_key_path,
            ssh_public_key=ssh_public_key,
            ssh_key_fingerprint=ssh_key_fingerprint,
            ssh_key_passphrase_protected=ssh_key_passphrase_protected,
            ssh_key_source=ssh_key_source,
            ssh_key_type=ssh_key_type,
        )

    def switch_profile(self, name: str, git_manager, ssh_manager) -> bool:
        """Switch to a specific GitHub profile with full configuration update.

        Atomically switches the current GitHub identity by updating both
        Git global configuration and SSH configuration. Updates last_used
        timestamp and sets the profile as active.

        Args:
            name: Profile name to switch to
            git_manager: Git configuration manager instance
            ssh_manager: SSH key manager instance

        Returns:
            bool: True on successful switch

        Raises:
            ValueError: If profile doesn't exist
            RuntimeError: If switching fails (git/ssh configuration error)

        Note:
            This operation is atomic - if any step fails, the profile
            is not marked as active and an exception is raised.

        Example:
            >>> profile_manager.switch_profile('work', git_mgr, ssh_mgr)
            True
        """
        profile = self.config.get_profile(name)
        if not profile:
            raise ValueError(f"Profile '{name}' not found")

        try:
            # Update git configuration
            git_manager.set_git_config(profile["name"], profile["email"])

            # Update SSH configuration
            ssh_manager.activate_ssh_key(name, profile["ssh_key_path"])

            # Set as active profile
            self.config.set_active_profile(name)

            return True
        except Exception as e:
            raise RuntimeError(f"Failed to switch profile: {e}") from e

    def update_profile(self, profile_name: str, **updates: Any) -> None:
        """Update profile information."""
        if not self.profile_exists(profile_name):
            raise ValueError(f"Profile '{profile_name}' not found")

        # Validate email if provided
        if "email" in updates and not self._validate_email(updates["email"]):
            raise ValueError("Invalid email format")

        self.config.update_profile(profile_name, updates)

    def delete_profile(self, name: str, ssh_manager) -> bool:
        """Delete a profile and its SSH keys."""
        if not self.profile_exists(name):
            raise ValueError(f"Profile '{name}' not found")

        try:
            # Get profile data before deletion
            profile = self.config.get_profile(name)

            # Remove SSH key and config
            if profile and "ssh_key_path" in profile:
                ssh_manager.remove_ssh_key(profile["ssh_key_path"])
                ssh_manager.remove_ssh_config_entry(name)

            # Delete profile from config
            self.config.delete_profile(name)

            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete profile: {e}") from e

    def export_profiles(self, format: str = "toml") -> str:
        """Export all profiles to specified format."""
        data = self.config.export_profiles()

        if format.lower() == "json":
            import json

            return json.dumps(data, indent=2)
        elif format.lower() == "yaml":
            try:
                import yaml

                return yaml.dump(data, default_flow_style=False)
            except ImportError:
                raise ValueError(
                    "PyYAML not installed. Use 'toml' or 'json' format instead"
                )
        else:  # Default to TOML
            import toml

            return toml.dumps(data)

    def import_profiles(
        self, data: str, format: str = "toml", overwrite: bool = False
    ) -> None:
        """Import profiles from string data."""
        if format.lower() == "json":
            import json

            parsed_data = json.loads(data)
        elif format.lower() == "yaml":
            try:
                import yaml

                parsed_data = yaml.safe_load(data)
            except ImportError:
                raise ValueError(
                    "PyYAML not installed. Use 'toml' or 'json' format instead"
                )
        else:  # Default to TOML
            import toml

            parsed_data = toml.loads(data)

        self.config.import_profiles(parsed_data, overwrite)

    def _validate_profile_name(self, name: str) -> bool:
        """Validate profile name format."""
        if not name:
            return False
        # Allow letters, numbers, hyphens, underscores
        return all(c.isalnum() or c in "-_" for c in name)

    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        if not email or "@" not in email:
            return False
        # Basic email validation
        parts = email.split("@")
        return len(parts) == 2 and all(part.strip() for part in parts)
