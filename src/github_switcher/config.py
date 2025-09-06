"""Configuration management for GitHub Switcher."""

from datetime import datetime
from pathlib import Path
from typing import Any

import toml


class Config:
    """Manages configuration storage and retrieval."""

    def __init__(self) -> None:
        """Initialize configuration manager."""
        self.config_dir = Path.home() / ".config" / "github-switcher"
        self.profiles_file = self.config_dir / "profiles.toml"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_profiles(self) -> dict[str, Any]:
        """Load profiles from configuration file."""
        if not self.profiles_file.exists():
            return {"meta": {"version": "1.0", "active_profile": None}, "profiles": {}}

        try:
            with open(self.profiles_file, encoding="utf-8") as f:
                return toml.load(f)
        except (toml.TomlDecodeError, OSError) as e:
            raise ValueError(f"Failed to load profiles: {e}") from e

    def save_profiles(self, data: dict[str, Any]) -> None:
        """Save profiles to configuration file."""
        try:
            # Ensure config directory exists
            self._ensure_config_dir()

            # Create backup of existing config
            if self.profiles_file.exists():
                backup_file = self.profiles_file.with_suffix(".toml.backup")
                self.profiles_file.replace(backup_file)

            with open(self.profiles_file, "w", encoding="utf-8") as f:
                toml.dump(data, f)
        except OSError as e:
            raise ValueError(f"Failed to save profiles: {e}") from e

    def add_profile(
        self,
        name: str,
        fullname: str,
        email: str,
        ssh_key_path: str,
        ssh_public_key: str,
    ) -> None:
        """Add a new profile to configuration."""
        data = self.load_profiles()

        if name in data["profiles"]:
            raise ValueError(f"Profile '{name}' already exists")

        data["profiles"][name] = {
            "name": fullname,
            "email": email,
            "ssh_key_path": ssh_key_path,
            "ssh_key_public": ssh_public_key,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
        }

        self.save_profiles(data)

    def get_profile(self, name: str) -> dict[str, Any] | None:
        """Get profile data by name."""
        data = self.load_profiles()
        return data["profiles"].get(name)

    def get_all_profiles(self) -> dict[str, dict[str, Any]]:
        """Get all profiles."""
        data = self.load_profiles()
        return data["profiles"]

    def update_profile(self, name: str, updates: dict[str, Any]) -> None:
        """Update profile data."""
        data = self.load_profiles()

        if name not in data["profiles"]:
            raise ValueError(f"Profile '{name}' not found")

        data["profiles"][name].update(updates)
        self.save_profiles(data)

    def delete_profile(self, name: str) -> None:
        """Delete a profile."""
        data = self.load_profiles()

        if name not in data["profiles"]:
            raise ValueError(f"Profile '{name}' not found")

        # If this is the active profile, clear it
        if data["meta"].get("active_profile") == name:
            data["meta"]["active_profile"] = None

        del data["profiles"][name]
        self.save_profiles(data)

    def set_active_profile(self, name: str) -> None:
        """Set the active profile."""
        data = self.load_profiles()

        if name not in data["profiles"]:
            raise ValueError(f"Profile '{name}' not found")

        data["meta"]["active_profile"] = name
        data["profiles"][name]["last_used"] = datetime.now().isoformat()
        self.save_profiles(data)

    def get_active_profile(self) -> str | None:
        """Get the name of the active profile."""
        data = self.load_profiles()
        return data["meta"].get("active_profile")

    def export_profiles(self, include_private_keys: bool = False) -> dict[str, Any]:
        """Export profiles for backup/sharing."""
        data = self.load_profiles()

        export_data = {
            "meta": {
                "version": data["meta"]["version"],
                "exported_at": datetime.now().isoformat(),
                "exported_by": f"github-switcher v{self._get_version()}",
            },
            "profiles": {},
        }

        for name, profile in data["profiles"].items():
            export_profile = {
                "name": profile["name"],
                "email": profile["email"],
                "ssh_key_public": profile["ssh_key_public"],
                "created_at": profile["created_at"],
                "last_used": profile.get("last_used"),
            }

            if include_private_keys:
                export_profile["ssh_key_path"] = profile["ssh_key_path"]

            export_data["profiles"][name] = export_profile

        return export_data

    def import_profiles(
        self, import_data: dict[str, Any], overwrite: bool = False
    ) -> None:
        """Import profiles from backup/export."""
        data = self.load_profiles()

        for name, profile in import_data["profiles"].items():
            if name in data["profiles"] and not overwrite:
                continue  # Skip existing profiles if not overwriting

            # Import profile data
            data["profiles"][name] = {
                "name": profile["name"],
                "email": profile["email"],
                "ssh_key_public": profile["ssh_key_public"],
                "created_at": profile["created_at"],
                "last_used": profile.get("last_used"),
                "ssh_key_path": profile.get(
                    "ssh_key_path", f"~/.ssh/id_ed25519_{name}"
                ),
            }

        self.save_profiles(data)

    def _get_version(self) -> str:
        """Get application version."""
        from . import __version__

        return __version__
